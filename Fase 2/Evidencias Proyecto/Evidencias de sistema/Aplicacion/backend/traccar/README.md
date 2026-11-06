# Servidor Traccar para la pulsera (Sprint 5)

Traccar es el servidor que habla con la pulsera GPS. Cada vez que recibe una posición, la reenvía a la API (`POST /traccar/posiciones`), y la API crea las alertas (SOS, caída, batería baja, salida de geocerca, inactividad).

## Qué está verificado y qué no

- **Verificado**: el lado de la API. Las pruebas automáticas y el simulador (`backend/scripts/simular_pulsera.py`) envían lecturas en los dos formatos que acepta, y se comprobó con PostgreSQL que se crean los eventos.
- **Sin verificar**: este contenedor de Traccar. No se pudo levantar Docker al preparar el sprint. Dos cosas dependen de la versión de Traccar y hay que comprobarlas la primera vez:
  1. Que las claves `forward.enable`, `forward.url` y `forward.json` sean las de la versión de la imagen (revisar la documentación de la versión que se baje).
  2. Los **nombres de los campos del JSON** que envía Traccar. La API busca `position.latitude`, `position.longitude`, `position.speed` (nudos), `position.fixTime`, `position.attributes.batteryLevel`, `position.attributes.alarm` y `device.uniqueId`, y es tolerante, pero no se vio un envío real. Si algo no calza, se ajusta `extraer_lectura()` en `app/api/routes/traccar.py` (una función corta) con la captura real.

## Pasos

1. En `backend/.env` agrega `TRACCAR_TOKEN=` con una clave larga (por ejemplo, el resultado de `openssl rand -hex 24`).
2. Pon esa misma clave en `traccar/traccar.xml`, en `forward.url`, en lugar de `CAMBIAR_POR_TRACCAR_TOKEN`.
3. Desde `backend`: `docker compose -f docker-compose.yml -f traccar/docker-compose.traccar.yml up --build`.
4. Abre `http://localhost:8082`. Con Traccar 6 el primer usuario que se registra queda como administrador.
5. En Perfil Médico+ registra la pulsera del perfil (`POST /perfiles/{id}/pulseras`) con el **mismo identificador** (IMEI) que usará el dispositivo, y en Traccar agrega un dispositivo con ese identificador.
6. Prueba sin hardware: el protocolo OsmAnd escucha en el puerto 5055. Con el celular o con curl:
   `curl "http://localhost:5055/?id=356938035643809&lat=-33.4489&lon=-70.6693&timestamp=$(date +%s)&batt=80"`
7. Captura lo que Traccar envía a la API (log del contenedor `api`, o `docker compose logs traccar`) y guárdalo como evidencia: es la prueba de que los formatos calzan.
8. Con la pulsera real: configura en el dispositivo el servidor (IP pública o dominio de la máquina que corre Traccar) y el puerto del protocolo que indique el fabricante. Hay que abrir ese puerto en el router, o usar un túnel.

## Seguridad

- No subas al repositorio un `traccar.xml` con el token real; deja `CAMBIAR_POR_TRACCAR_TOKEN`.
- Si Traccar quedará accesible desde internet, cambia la contraseña del administrador y no expongas el puerto 8082 sin protección.
