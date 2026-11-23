# Guía de capturas de Docker — Sprint 5

Base: `Aplicacion/backend/docs/Guia_Docker_Compose_Sprint5.md`. Esta guía agrega el nombre de cada captura y qué debe verse. Carpeta sugerida para subirlas: `Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend/evidencias/` (donde ya está `S5_alembic_docker.png`).

| Captura | Comando (lo ejecuta el script) | Qué debe verse | Resultado esperado |
|---|---|---|---|
| `S5_D1_docker_compose_ps.png` | `docker compose ps` | Servicios `db` y `api` | `db` con estado *healthy* y `api` en ejecución (*Up*) |
| `S5_D2_alembic_current_check.png` | `alembic current` y `alembic check` | La cabeza de migraciones | `a5b6c7d8e9f0 (head)` y «No new upgrade operations detected» |
| `S5_D3_health_y_docs.png` | `curl /health` y `http://localhost:8000/docs` | Respuesta del health y la lista de rutas en Swagger | Rutas de indicadores, cumplimiento, asistencia, pulsera, Traccar e IA |
| `S5_D4_pytest_en_contenedor.png` | `python -m pytest -q` dentro de `api` | La línea final de pytest | **216 passed** (verificado: 216 pruebas recolectadas desde el código; el `pytest.log` del repositorio dice 210 porque es anterior a las 6 de FCM) |
| `S5_D5_prueba_humo.png` | `prueba_humo_sprint5.py` (copia con puerto 8000) | La lista OK y el total | 29 de 29 (según la evidencia del 10-nov; pasa de nuevo si todo está bien) |
| `S5_D6_traccar_ps.png` (opcional) | `docker compose -f ... -f traccar/... ps` | Servicio `traccar` y puertos 5055 y 5093 | Solo si quieres declarar que Traccar levanta. Un envío real desde una pulsera sigue sin probarse. |

## Reglas de honestidad para la evidencia

- Si un paso falla, se captura el error y se anota en el documento. Un paso fallido bien explicado vale más que uno ausente.
- Si D4 da un número distinto de 216 (por ejemplo 210), se escribe el número real y se corrige la cifra del informe 2.6 y de la diapositiva 10 y 12.
- La prueba de humo puede dar 29 de 29 solo con una base vacía o recién migrada; si falla por usuarios ya existentes, se baja con `docker compose down -v` (esto **borra los datos** de la base de prueba) y se repite.
- No mostrar el valor de `TRACCAR_TOKEN` en las capturas.
