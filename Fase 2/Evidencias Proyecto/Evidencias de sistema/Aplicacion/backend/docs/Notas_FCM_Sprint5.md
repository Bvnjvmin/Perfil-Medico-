# FCM (push real) — qué se hizo y qué queda

## Hecho en el backend (código listo, apagado por defecto)
- `NotificadorFCM` en `app/services/notificador.py`: se activa con `NOTIFICADOR=fcm`, usa la API HTTP v1 de Firebase y no cambia nada mientras el valor siga en `log`.
- Variables nuevas: `FCM_CREDENCIALES` (ruta al JSON de la cuenta de servicio, fuera del repositorio) y `FCM_PROYECTO_ID`.
- 6 pruebas (`test_fcm.py`) con respuestas simuladas: un mensaje por dispositivo, datos convertidos a texto, un rechazo no detiene a los demás, y la falta de credenciales o un error de red no rompen el flujo.

## No hecho / no verificado
- **No se probó contra Firebase real**: no hay proyecto ni credenciales. Hasta que alguien lo pruebe con un celular real, hay que presentarlo como "implementado, sin verificar de extremo a extremo".
- Requiere instalar `google-auth` (agregar `google-auth` a `requirements.txt` y reconstruir la imagen); no se agregó porque no se pudo probar la instalación en Docker.
- **Falta la parte de la app (Matías):** agregar `firebase_messaging`, pedir permiso de notificaciones, obtener el token del dispositivo y enviarlo a `POST /dispositivos` (ya existe). Eso necesita el archivo `google-services.json` del proyecto de Firebase.
- Falta crear el proyecto de Firebase y guardar la cuenta de servicio (decisión y responsable del equipo).

## Si el equipo decide NO hacerlo (texto para README y contrato)
> **Límite conocido:** los avisos no llegan como notificación push con la app cerrada. El backend los genera y los registra, y la app los muestra al abrir la pantalla Avisos (`GET /alertas`). El envío push con FCM está implementado en el backend pero desactivado y sin verificar con Firebase real; queda como trabajo futuro.
