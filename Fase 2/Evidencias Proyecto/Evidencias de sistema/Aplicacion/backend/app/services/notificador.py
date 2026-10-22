"""
Entrega de avisos al dispositivo (HU 9).

El resto del sistema solo llama a `notificar(...)`; cómo llega el aviso al
celular depende del notificador configurado (`NOTIFICADOR` en el .env):

- "log": registra en el log del servidor a qué dispositivos se enviaría. Es el
  modo por defecto, no necesita credenciales y sirve para desarrollo y pruebas.

Para enviar notificaciones push reales (con la app cerrada) hay que agregar aquí
una clase con el mismo método `enviar` que use el servicio elegido por el equipo
(por ejemplo Firebase Cloud Messaging) y registrarla en `_NOTIFICADORES`. Esa
decisión y sus credenciales están pendientes. Mientras tanto la app consulta
`GET /alertas`, que siempre tiene todos los avisos.
"""
import logging
from typing import Protocol

from app.core.config import settings

logger = logging.getLogger("perfil_medico.notificador")


class Notificador(Protocol):
    def enviar(self, tokens: list[str], titulo: str, cuerpo: str, datos: dict) -> None: ...


class NotificadorLog:
    def enviar(self, tokens: list[str], titulo: str, cuerpo: str, datos: dict) -> None:
        logger.info("Aviso para %d dispositivo(s): %s — %s %s", len(tokens), titulo, cuerpo, datos)


_NOTIFICADORES: dict[str, type] = {"log": NotificadorLog}


def obtener_notificador() -> Notificador:
    clase = _NOTIFICADORES.get(settings.NOTIFICADOR, NotificadorLog)
    return clase()
