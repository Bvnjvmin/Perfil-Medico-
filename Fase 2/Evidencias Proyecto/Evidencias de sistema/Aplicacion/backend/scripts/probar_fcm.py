#!/usr/bin/env python3
"""
Envía una notificación de prueba a un celular, sin esperar a que se genere una alerta.

Sirve para comprobar de extremo a extremo el push con Firebase (HU 9): la cuenta de servicio,
el proyecto y el token del celular. Se ejecuta DENTRO del contenedor de la API:

    docker compose -f docker-compose.yml -f docker-compose.fcm.yml exec api \
        python scripts/probar_fcm.py TOKEN_DEL_CELULAR

El token del celular se obtiene de la tabla `dispositivo_push` (columna `token`) después de iniciar
sesión en la app, o de la consola de depuración de la app.
Si algo falla (credenciales, proyecto, token inválido), el motivo aparece como WARNING o ERROR.
"""
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.services.notificador import NotificadorFCM  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    token = sys.argv[1]
    print(f"NOTIFICADOR={settings.NOTIFICADOR}  FCM_PROYECTO_ID={settings.FCM_PROYECTO_ID or '(vacío)'}")
    ruta = settings.FCM_CREDENCIALES
    print(f"FCM_CREDENCIALES={ruta or '(vacío)'}  existe={os.path.isfile(ruta) if ruta else False}")
    if not settings.FCM_PROYECTO_ID or not ruta or not os.path.isfile(ruta):
        print("Falta configurar FCM_PROYECTO_ID o la clave de la cuenta de servicio. No se envió nada.")
        return 1
    NotificadorFCM().enviar(
        [token],
        "Prueba de Perfil Médico+",
        "Si ves este mensaje, el push con FCM funciona.",
        {"tipo": "prueba"},
    )
    print("Terminó. Si arriba hay un ERROR o WARNING, el envío falló (ese es el motivo). Si no, revisa el celular.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
