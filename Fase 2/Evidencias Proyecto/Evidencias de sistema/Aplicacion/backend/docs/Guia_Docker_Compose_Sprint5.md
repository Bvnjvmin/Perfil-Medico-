# Guía de prueba con Docker Compose completo (Benjamín, Sprint 5)

**Estado:** el archivo `docker-compose.yml` (y con el de Traccar) pasó `docker compose config` sin errores, pero **las imágenes no se construyeron ni se levantaron**: en el entorno donde se preparó no hay servicio de Docker activo. Esta prueba la hace Benjamín en su computador; sirve de evidencia para el Sprint 5.

## Pasos (desde `Aplicacion/backend`)
1. `cp .env.example .env` y, para probar la pulsera, agregar `TRACCAR_TOKEN=un-valor-largo-de-prueba`.
2. `docker compose up --build -d`
3. Capturas y comandos:
   - `docker compose ps` → `db` (healthy) y `api` en ejecución. **Captura S5_D1.**
   - `docker compose exec api alembic current` → `a5b6c7d8e9f0 (head)`. **S5_D2.**
   - `curl http://localhost:8000/health` y abrir `http://localhost:8000/docs` (deben verse las rutas de indicadores, cumplimiento, asistencia, pulsera, Traccar e IA). **S5_D3.**
   - `docker compose exec api python -m pytest -q` (pytest viene en `requirements.txt`, así que debería funcionar dentro del contenedor; no se probó). Resultado esperado: 216 pruebas (210 + 6 de FCM) con el código nuevo, o 210 sin él. Si falla dentro del contenedor, correrlo en el entorno virtual local. **S5_D4.**
   - Prueba de humo: `python scripts/prueba_humo_sprint5.py` con la API en `http://localhost:8000` (el script espera el puerto 8010 y el token `tok-humo`; ajustar las constantes `B` y `TOK` de su cabecera, y poner el mismo token en el `.env`). **S5_D5.**
4. Con Traccar: `docker compose -f docker-compose.yml -f traccar/docker-compose.traccar.yml up --build -d`, abrir `http://localhost:8082` y comprobar `docker compose ps` con el servicio `traccar` y los puertos 5055 y 5093. **S5_D6.**
5. Apagar: `docker compose down` (agregar `-v` solo si se quiere borrar los datos).

## Qué revisar si algo falla
- `api` se reinicia: ver `docker compose logs api`; casi siempre es un `.env` ausente o `TRACCAR_TOKEN` mal copiado en `traccar.xml`.
- El token de `traccar/traccar.xml` debe ser el mismo `TRACCAR_TOKEN` del `.env`.
- Nunca subir el `.env` ni el token real al repositorio.

## Notas del análisis estático
- Con el compose de Traccar los puertos publicados son 8000 (API), 5432 (base de datos), 8082 (panel de Traccar), 5055 (OsmAnd, el que usa el celular de la demo) y 5093 (protocolo `watch`, solo necesario si se compra una pulsera de ese tipo).
- La imagen de Traccar usa `latest`; conviene fijar una versión una vez probada.
