# Evidencia de pruebas del backend — Sprint 5 (HU 12 a 19)

**Rol:** Benjamín Leiva (Backend) · **Fecha de la prueba:** 10 de noviembre de 2026
**Entorno:** API (`uvicorn`) del código integrado en `main` (con `main.py` del commit `11bcf7c`) sobre PostgreSQL 16 creado desde cero con `alembic upgrade head` (cabeza `a5b6c7d8e9f0`). `TRACCAR_TOKEN` de prueba. Simulador `scripts/simular_pulsera.py`.
**Cómo repetirla:** `scripts/prueba_humo_sprint5.py` (ver su cabecera).

> Alcance: prueba por API, no por la app. No incluye Docker Compose (la prueba se hizo sin Docker), Traccar real, pulsera física ni proveedor de IA real. La aceptación del Product Owner es aparte (`Checklist_Aceptacion_PO_Sprint5.md`).

## Resultado: 29 de 29 verificaciones correctas

| # | HU | Verificación | Resultado |
|---|---|---|---|
| 1 | — | Vincular un cuidador con `puede_ver_indicadores` | 201 ✅ |
| 2 | 12 | Registrar peso, presión, glucosa y frecuencia cardíaca (4 pruebas) | 201 ✅ |
| 3 | 12 | Peso 700 kg rechazado; presión sin diastólica rechazada | 422 ✅ |
| 4 | 12 | Últimos valores y serie de peso de 30 días | 200 ✅ |
| 5 | 12 | Cuidador con permiso ve los indicadores | 200 ✅ |
| 6 | 12 | Cuidador sin `puede_ver_indicadores` | 403 ✅ |
| 7 | 13 | Cumplimiento de 7 días (perfil sin actividades: total 0, porcentaje vacío) | 200 ✅ |
| 8 | 14 | «Necesito ayuda»; repetirlo no duplica el evento | 201 / 200 ✅ |
| 9 | 19 | El cuidador ve el evento de asistencia | 200 ✅ |
| 10 | 17 | Registrar pulsera (titular); el cuidador no puede | 201 / 403 ✅ |
| 11 | 17 | Crear geocerca (200 m) | 201 ✅ |
| 12 | 17 | Traccar con token inválido | 401 ✅ |
| 13 | 17/19 | Simulador: posición, SOS, caída, batería al 9 % y recorrido de 600 m | 200 ✅ |
| 14 | 17 | Última ubicación de la pulsera | 200 ✅ |
| 15 | 19 | Eventos creados: `asistencia`, `bateria_baja`, `caida`, `geocerca_salida`, `sos` | ✅ |
| 16 | 19 | Marcar un evento como atendido | 200 ✅ |
| 17 | 15 | IA: pregunta normal (proveedor `simulado`) | 201 ✅ |
| 18 | 15 | IA: «Me duele el pecho» responde con reglas y el 131 (proveedor `reglas`) | 201 ✅ |

## Observaciones
- El tipo de indicador del pulso se llama `frecuencia_cardiaca` (no `pulso`); la app ya usa ese nombre.
- El cumplimiento solo se pudo comprobar con 0 actividades: el cálculo con datos reales está cubierto por las pruebas automáticas (210 pasan), no por esta prueba.
- Con proveedor `simulado` la IA no da respuestas útiles a preguntas normales; eso requiere el proveedor real.

## Pendiente
Docker Compose completo, Traccar con pulsera física, proveedor de IA real y push (FCM).
