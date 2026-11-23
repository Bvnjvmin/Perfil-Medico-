# Evidencia de la prueba con Docker Compose — Sprint 5

**Responsable:** Benjamín Leiva (backend) · **Fecha de la prueba:** __/11/2026 (completar)
**Entorno:** Docker __ (completar con `docker --version`) en __ (sistema operativo). Servicios `db` (PostgreSQL 16) y `api` (FastAPI).
**Código probado:** commit `____` (completar con `git rev-parse --short HEAD`).
**Cómo se ejecutó:** `bash prueba_docker_sprint5.sh` desde `Aplicacion/backend`.

> Alcance: prueba de que el backend levanta completo con Docker Compose, aplica las migraciones y pasa sus pruebas. No incluye Traccar con pulsera física, proveedor de IA real ni push FCM.

## Resultados

| Paso | Qué se probó | Resultado esperado | Resultado real (✅ / ❌ y lo observado) | Captura |
|---|---|---|---|---|
| D1 | Servicios arriba | `db` healthy y `api` en ejecución | (completar) | `S5_D1_docker_compose_ps.png` |
| D2 | Migraciones | `a5b6c7d8e9f0 (head)`; `alembic check` sin diferencias | (completar) | `S5_D2_alembic_current_check.png` |
| D3 | API y documentación | `/health` responde y `/docs` lista las rutas | (completar) | `S5_D3_health_y_docs.png` |
| D4 | Pruebas automáticas en el contenedor | 216 pasan | (completar: número real) | `S5_D4_pytest_en_contenedor.png` |
| D5 | Prueba de humo | 29 de 29 | (completar) | `S5_D5_prueba_humo.png` |
| D6 | Traccar (opcional) | Servicio `traccar` arriba | (completar o «no se probó») | `S5_D6_traccar_ps.png` |

## Observaciones

(Completar: problemas encontrados, cómo se resolvieron, qué quedó sin probar.)

## Límites que se mantienen

- Traccar con una pulsera real sigue sin probarse; la demo usa el simulador.
- La IA corre en modo simulado.
- El push FCM está en el backend, apagado y sin verificar con Firebase real.
