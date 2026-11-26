# Evidencia de la prueba con Docker Compose — Sprint 5

**Responsable:** Benjamín Leiva (backend) · **Fecha de la prueba:** 23 de noviembre de 2026 (12:34, hora de Chile)
**Entorno:** Docker 29.8.0 (build 88096ef) en Windows, ejecutado con Git Bash. Servicios `db` (PostgreSQL 16, imagen `postgres:16-alpine`) y `api` (FastAPI); Traccar en un archivo aparte.
**Código probado:** copia local de la carpeta `backend` sin repositorio git (el script mostró «Commit del repositorio: sin git»). *(Completar con el commit si se repite la prueba desde el clon: `git rev-parse --short HEAD`.)*
**Cómo se ejecutó:** `bash prueba_docker_sprint5.sh` desde `Aplicacion/backend`.

> Alcance: prueba de que el backend levanta completo con Docker Compose, aplica las migraciones y pasa sus pruebas. No incluye Traccar con pulsera física, proveedor de IA real ni push FCM.

> **Estado de este documento:** D0 a D3 y D5 salen de las capturas de la corrida del 23-nov. **D4 tuvo un fallo en esa corrida** (se explica abajo) y debe repetirse con el parche antes de darlo por aprobado. D6 está a medio documentar: falta la captura del panel de Traccar. Las filas marcadas con ⬜ hay que completarlas con la corrida nueva; no se deben rellenar con valores que no se hayan visto.

## Resultados

| Paso | Qué se probó | Resultado esperado | Resultado real (✅ / ❌ y lo observado) | Captura |
|---|---|---|---|---|
| D0 | Construir y levantar | La imagen se construye y los contenedores arrancan | ✅ `docker compose up --build -d`: imagen `backend-api` construida; contenedores `backend-db-1` (healthy) y `backend-api-1` iniciados | (captura de la construcción) |
| D1 | Servicios arriba | `db` healthy y `api` en ejecución | ✅ `backend-db-1` «Up … (healthy)» y `backend-api-1` «Up»; puertos 8000 (API) y 5432 (base) publicados | `S5_D1_docker_compose_ps.png` |
| D2 | Migraciones | `a5b6c7d8e9f0 (head)`; `alembic check` sin diferencias | ✅ `alembic current` → `a5b6c7d8e9f0 (head)`; `alembic check` → «No new upgrade operations detected» | `S5_D2_alembic_current_check.png` |
| D3 | API y documentación | `/health` responde y `/docs` lista las rutas | ✅ `/health` → HTTP 200 `{"status":"ok","service":"Perfil Médico+ API"}`; el `openapi.json` tiene **43 rutas y 65 operaciones HTTP**. ⬜ Falta la captura de `http://localhost:8000/docs` en el navegador | `S5_D3_health_y_docs.png` |
| D4 | Pruebas automáticas en el contenedor | 216 pasan (226 con el parche de seguridad) | ❌ **En la corrida del 23-nov: 215 pasaron y 1 falló** (`test_traccar_apagado_sin_token_configurado`), en 227,89 s (3 min 47 s). ⬜ Repetir con `fix_D4_test_traccar.patch` (o con el parche único) y anotar aquí el número real | `S5_D4_pytest_en_contenedor.png` |
| D5 | Prueba de humo | 29 de 29 | ✅ «RESULTADO: 29/29 OK» contra la API en el puerto 8000 | `S5_D5_prueba_humo.png` |
| D6 | Traccar (opcional) | Servicio `traccar` arriba | 🟡 Con `docker compose -f docker-compose.yml -f traccar/docker-compose.traccar.yml up --build -d` quedaron arriba `backend-api-1`, `backend-db-1` y `backend-traccar-1` (imagen `traccar/traccar:latest`, puertos 5055, 5093 y 8082). ⬜ Falta abrir el panel en `http://localhost:8082` y capturarlo | `S5_D6_traccar_ps.png` |

## Observaciones

- **El fallo de D4 no es un error de la aplicación.** El script agrega `TRACCAR_TOKEN` al `.env` para que la prueba de humo (D5) pueda usar Traccar. Dentro del contenedor, ese token queda activo y el test `test_traccar_apagado_sin_token_configurado` parte de la base de que está vacío, así que recibe 401 en vez de 503. Los otros 215 tests, incluidos los demás de Traccar (que activan el token por sí mismos), pasaron.
- **Corrección:** el test ahora fuerza el token vacío con `monkeypatch`. Con `TRACCAR_TOKEN` puesto en el entorno, el archivo `test_pulsera.py` pasa completo (21 de 21); sin la corrección, ese test falla. Cambio de una línea en `app/tests/test_pulsera.py` (`fix_D4_test_traccar.patch`).
- **Puerto de la base de datos:** en la corrida del 23-nov, `docker compose ps` muestra PostgreSQL publicado en `0.0.0.0:5432`, es decir, visible desde la red local. El parche de seguridad lo deja solo en `127.0.0.1:5432` (brecha 2 de `Seguridad_de_datos_evaluacion_y_plan.md`). Si se repite la prueba con el parche, la captura D1 mostrará `127.0.0.1:5432->5432`.
- **Orden de las cifras:** 216 pruebas es el total del repositorio actual; con el parche de seguridad son 226 (216 + 10 nuevas).
- ⬜ *(Completar si hubo otros problemas al repetir la prueba, cómo se resolvieron y qué quedó sin probar.)*

## Límites que se mantienen

- Traccar con una pulsera real sigue sin probarse; la demo usa el simulador.
- La IA corre en modo simulado en la demo; la prueba con el modelo real (Claude Haiku 5.5, de Anthropic) se documenta aparte con `scripts/prueba_haiku_real.py`.
- El push FCM está en el backend, apagado y sin verificar con Firebase real.
- Docker no se probó en un servidor ni con HTTPS: la prueba fue local.
