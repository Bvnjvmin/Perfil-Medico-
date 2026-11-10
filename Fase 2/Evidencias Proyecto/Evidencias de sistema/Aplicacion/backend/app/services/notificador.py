"""
Entrega de avisos al dispositivo (HU 9).

El resto del sistema solo llama a `notificar(...)`; cómo llega el aviso al
celular depende del notificador configurado (`NOTIFICADOR` en el .env):

- "log": registra en el log del servidor a qué dispositivos se enviaría. Es el
  modo por defecto, no necesita credenciales y sirve para desarrollo y pruebas.

- "fcm": envía notificaciones push reales con Firebase Cloud Messaging (API HTTP v1). Necesita
  `FCM_CREDENCIALES` (ruta al JSON de la cuenta de servicio, fuera del repositorio), `FCM_PROYECTO_ID`
  y la biblioteca `google-auth`. Si falta algo, no se rompe nada: se registra el problema en el log.
  Está apagado por defecto y se probó solo con respuestas simuladas, no contra Firebase real.

Un fallo de envío nunca detiene al resto de los avisos. La app, además, consulta `GET /alertas`,
que siempre tiene todos los avisos.
"""
import logging
from typing import Callable, Optional, Protocol

import httpx

from app.core.config import settings

logger = logging.getLogger("perfil_medico.notificador")


class Notificador(Protocol):
    def enviar(self, tokens: list[str], titulo: str, cuerpo: str, datos: dict) -> None: ...


class NotificadorLog:
    def enviar(self, tokens: list[str], titulo: str, cuerpo: str, datos: dict) -> None:
        logger.info("Aviso para %d dispositivo(s): %s — %s %s", len(tokens), titulo, cuerpo, datos)


FCM_URL = "https://fcm.googleapis.com/v1/projects/{proyecto}/messages:send"
FCM_ALCANCE = "https://www.googleapis.com/auth/firebase.messaging"


def _token_google(ruta_credenciales: str) -> str:
    """Token de acceso OAuth2 de la cuenta de servicio (requiere `pip install google-auth`)."""
    from google.auth.transport.requests import Request  # importación tardía: solo con NOTIFICADOR=fcm
    from google.oauth2 import service_account

    credenciales = service_account.Credentials.from_service_account_file(ruta_credenciales, scopes=[FCM_ALCANCE])
    credenciales.refresh(Request())
    return credenciales.token


class NotificadorFCM:
    """Push con Firebase Cloud Messaging. `cliente` y `obtener_token` se pueden reemplazar en las pruebas."""

    def __init__(self, proyecto: Optional[str] = None, credenciales: Optional[str] = None,
                 cliente: Optional[httpx.Client] = None,
                 obtener_token: Optional[Callable[[str], str]] = None) -> None:
        self.proyecto = settings.FCM_PROYECTO_ID if proyecto is None else proyecto
        self.credenciales = settings.FCM_CREDENCIALES if credenciales is None else credenciales
        self.cliente = cliente
        self.obtener_token = obtener_token or _token_google

    def enviar(self, tokens: list[str], titulo: str, cuerpo: str, datos: dict) -> None:
        if not self.proyecto or not self.credenciales:
            logger.warning("NOTIFICADOR=fcm sin FCM_PROYECTO_ID o FCM_CREDENCIALES: no se envió el aviso")
            return
        try:
            acceso = self.obtener_token(self.credenciales)
        except Exception:
            logger.exception("No se pudo obtener el token de acceso de Firebase")
            return
        # FCM exige que todos los valores de `data` sean texto.
        datos_texto = {str(k): str(v) for k, v in datos.items()}
        cliente = self.cliente or httpx.Client(timeout=10)
        try:
            for token in tokens:
                cuerpo_fcm = {"message": {"token": token, "notification": {"title": titulo, "body": cuerpo},
                                          "data": datos_texto}}
                try:
                    r = cliente.post(FCM_URL.format(proyecto=self.proyecto), json=cuerpo_fcm,
                                     headers={"Authorization": f"Bearer {acceso}"})
                except httpx.HTTPError:
                    logger.exception("Falló la conexión con FCM")
                    continue
                if r.status_code >= 400:
                    logger.warning("FCM rechazó un envío (HTTP %s): %s", r.status_code, r.text[:200])
        finally:
            if self.cliente is None:
                cliente.close()


_NOTIFICADORES: dict[str, type] = {"log": NotificadorLog, "fcm": NotificadorFCM}


def obtener_notificador() -> Notificador:
    clase = _NOTIFICADORES.get(settings.NOTIFICADOR, NotificadorLog)
    return clase()
