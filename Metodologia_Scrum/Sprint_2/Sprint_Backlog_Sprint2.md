# Sprint Backlog — Sprint 2 (S7–S8)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 20 de septiembre al 3 de octubre de 2026 (semanas 7 y 8 del Cronograma)
**Objetivo del sprint:** cerrar los arrastres del Sprint 1 (API de HU 2 y validación de HU 3) e incorporar las dos historias nuevas del Product Backlog: registro de medicamentos y rutinas de cuidado (HU 4) y agenda diaria de actividades (HU 5).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregable comprometido:** API de perfil/alergias/contactos de emergencia funcional (HU 2), API de medicamentos/rutinas de cuidado funcional (HU 4), evidencia de validación de HU 3, y pantallas de agenda diaria en la app (HU 5).

## 1. Historias comprometidas

### HU 2 — Datos básicos de salud del titular (arrastre del Sprint 1, cierre de API)
- **Historia:** Como titular quiero registrar mis datos básicos de salud (RUT, grupo sanguíneo, alergias, contactos de emergencia) para tenerlos disponibles en una emergencia.
- **Responsables:** Benjamín Leiva (Backend) / Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - El titular autenticado puede crear, listar, consultar, actualizar y eliminar su perfil de salud.
  - El titular puede agregar, listar y eliminar alergias y contactos de emergencia de su propio perfil.
  - Un titular nunca puede ver ni modificar el perfil, alergias o contactos de otro titular (la API responde 404, no 403, para no revelar que el id pertenece a otra cuenta).
- **Estado al cierre:** ✅ **Terminada.** BD y migración ya estaban hechas desde el cierre del Sprint 1 (commit `6c01968`, Sergio); este sprint se agregó la API completa (esquemas Pydantic, dependencia `obtener_perfil_propio`, 11 endpoints y 10 pruebas automatizadas).
- **Evidencia:** `app/schemas/perfil.py`, `app/api/routes/perfil.py`, `app/tests/test_perfil.py` (10 pruebas, todas pasan).

### HU 3 — Pantallas de registro e inicio de sesión en la app (arrastre del Sprint 1, cierre de validación)
- **Historia:** Como usuario quiero una pantalla de registro/login simple en la app móvil para entrar a Perfil Médico+ desde mi celular.
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Se ejecutan las pruebas Flutter existentes (`usuario_test.dart`, `login_screen_test.dart`) con el SDK real y quedan registradas como evidencia.
  - Se documenta una prueba manual del flujo registro → login → Home contra el backend desplegado, con capturas de pantalla.
- **Estado al cierre:** ⏭️ **Pendiente — a cargo de Matías.** No requiere cambios de backend; es evidencia y ejecución de lo ya construido en el Sprint 1.
- **Nota:** el backend ya no expone el campo `rol` (se eliminó en el cierre del Sprint 1), por lo que las pruebas y capturas deben reflejar las pantallas sin ese campo.

### HU 4 — Medicamentos y rutinas de cuidado
- **Historia:** Como titular quiero registrar medicamentos y rutinas de cuidado (alimentación, hidratación, vitaminas) para mi propio perfil.
- **Responsables:** Benjamín Leiva (Backend) / Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Existen las tablas `medicamento` y `rutina_cuidado`, asociadas a un perfil mediante `perfil_id`.
  - El titular autenticado puede registrar, listar, actualizar y eliminar medicamentos y rutinas de cuidado de su propio perfil.
  - Un titular nunca puede ver ni modificar los medicamentos o rutinas del perfil de otro (respuesta 404).
- **Estado al cierre:** ✅ **Terminada** (backend). Modelo de datos, migración Alembic, esquemas Pydantic, 10 endpoints y 8 pruebas automatizadas, todo construido y verificado este sprint.
- **Evidencia:** `app/models/medicamento.py`, `alembic/versions/a1b2c3d4e5f6_...py`, `app/schemas/medicamento.py`, `app/api/routes/medicamento.py`, `app/tests/test_medicamento.py` (8 pruebas, todas pasan).

### HU 5 — Agenda diaria de actividades
- **Historia:** Como usuario quiero ver mi agenda diaria de actividades y confirmar cada una.
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Media
- **Criterios de aceptación:**
  - La app muestra una pantalla de agenda diaria que lista las actividades del perfil (medicamentos y rutinas de cuidado, consumidos desde los endpoints de HU 4).
  - El usuario puede marcar cada actividad como confirmada/realizada desde la pantalla.
- **Estado al cierre:** ⏭️ **Pendiente — a cargo de Matías.** Depende de los endpoints de HU 4, que ya están disponibles en `main` (`GET /perfiles/{perfil_id}/medicamentos` y `GET /perfiles/{perfil_id}/rutinas`).

## 2. Tareas técnicas del sprint — quién sube qué

| Tarea | Historia | Responsable | Estado | Dónde subirlo |
|---|---|---|---|---|
| Esquemas Pydantic de Perfil/Alergia/ContactoEmergencia | HU 2 | Benjamín | ✅ Hecha (commit `fb20f39`) | Ya en `main` |
| Dependencia `obtener_perfil_propio` (acotar acceso al titular dueño del token) | HU 2 / HU 4 | Benjamín | ✅ Hecha (commit `9d2b425`) | Ya en `main` |
| Endpoints CRUD de Perfil/Alergia/ContactoEmergencia | HU 2 | Benjamín | ✅ Hecha (commit `3c11446`) | Ya en `main` |
| 10 pruebas automatizadas de HU 2 | HU 2 | Benjamín | ✅ Hecha (commit `0af466e`) | Ya en `main` |
| Modelos `Medicamento` y `RutinaCuidado` | HU 4 | Benjamín | ✅ Hecha (commit `63f9451`) | Ya en `main` |
| Migración Alembic de `medicamento` y `rutina_cuidado` | HU 4 | Benjamín | ✅ Hecha (commit `de402ba`) | Ya en `main` |
| Esquemas Pydantic de Medicamento/RutinaCuidado | HU 4 | Benjamín | ✅ Hecha (commit `5a73c38`) | Ya en `main` |
| Endpoints CRUD de Medicamento/RutinaCuidado | HU 4 | Benjamín | ✅ Hecha (commit `246aac5`) | Ya en `main` |
| 8 pruebas automatizadas de HU 4 | HU 4 | Benjamín | ✅ Hecha (commit `42b274b`) | Ya en `main` |
| Registrar routers de perfil y medicamento en `main.py` | HU 2 / HU 4 | Benjamín | ✅ Hecha (commit `09151d2`) | Ya en `main` |
| Ejecutar `flutter test` sobre `usuario_test.dart` y `login_screen_test.dart` | HU 3 | Matías | ⏭️ Pendiente | Matías sube la evidencia (capturas/log) a `Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/app_movil` desde su propia cuenta |
| Prueba manual registro → login → Home contra el backend, con capturas | HU 3 | Matías | ⏭️ Pendiente | Matías sube las capturas a la misma carpeta de evidencias |
| Pantalla de agenda diaria (lista medicamentos/rutinas del día) | HU 5 | Matías | ⏭️ Pendiente | Matías implementa y sube `app_movil/lib/screens/agenda_screen.dart` (y el servicio que consuma `/perfiles/{id}/medicamentos` y `/perfiles/{id}/rutinas`) desde su propia cuenta |
| Marcar actividad como confirmada en la agenda | HU 5 | Matías | ⏭️ Pendiente | Idem, mismo PR/commit de la pantalla de agenda |

**Por qué se separa así:** todo el trabajo de backend (HU 2 y HU 4) ya quedó commiteado en `main` bajo la cuenta de Benjamín, porque es la parte que correspondía desarrollar esta sesión. El trabajo de HU 3 (validación) y HU 5 (pantallas nuevas en la app) es responsabilidad de Matías según el Product Backlog, así que se deja pendiente y debe subirse desde su propia cuenta para que la evaluación individual del curso refleje correctamente el aporte de cada integrante.

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 2 | ✅ | ✅ (10 pruebas automatizadas) | ✅ (este documento + README del backend) | **Sí** |
| HU 4 | ✅ | ✅ (8 pruebas automatizadas) | ✅ (este documento + README del backend) | **Sí** |
| HU 3 | ✅ (pantallas ya existían desde el Sprint 1) | 🟡 (pruebas escritas, ejecución pendiente) | 🟡 (falta evidencia de Matías) | No, hasta que Matías suba la evidencia |
| HU 5 | ❌ (pantalla aún no existe) | ❌ | ❌ | No |

## 4. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| `test_crear_perfil` | Automática (backend) | ✅ Pasa |
| `test_crear_perfil_sin_token_rechaza_acceso` | Automática (backend) | ✅ Pasa |
| `test_listar_perfiles_devuelve_solo_los_propios` | Automática (backend) | ✅ Pasa |
| `test_obtener_perfil_de_otro_titular_devuelve_404` | Automática (backend) | ✅ Pasa |
| `test_actualizar_perfil_propio` | Automática (backend) | ✅ Pasa |
| `test_eliminar_perfil_propio` | Automática (backend) | ✅ Pasa |
| `test_agregar_y_listar_alergias` | Automática (backend) | ✅ Pasa |
| `test_agregar_alergia_a_perfil_ajeno_devuelve_404` | Automática (backend) | ✅ Pasa |
| `test_agregar_y_listar_contactos_emergencia` | Automática (backend) | ✅ Pasa |
| `test_eliminar_contacto_emergencia` | Automática (backend) | ✅ Pasa |
| `test_registrar_y_listar_medicamento` | Automática (backend) | ✅ Pasa |
| `test_actualizar_medicamento_propio` | Automática (backend) | ✅ Pasa |
| `test_eliminar_medicamento_propio` | Automática (backend) | ✅ Pasa |
| `test_medicamento_de_perfil_ajeno_devuelve_404` | Automática (backend) | ✅ Pasa |
| `test_registrar_y_listar_rutina_cuidado` | Automática (backend) | ✅ Pasa |
| `test_actualizar_rutina_cuidado_propia` | Automática (backend) | ✅ Pasa |
| `test_eliminar_rutina_cuidado_propia` | Automática (backend) | ✅ Pasa |
| `test_rutina_de_perfil_ajeno_devuelve_404` | Automática (backend) | ✅ Pasa |
| Suite completa de autenticación (HU 1, heredada) | Automática (backend) | ✅ Pasa (7 pruebas) |
| `usuario_test.dart`, `login_screen_test.dart` | Automática (Flutter) | ⏳ Pendiente (Matías) |
| Flujo registro → login → Home contra el backend | Manual | ⏳ Pendiente (Matías) |
| Agenda diaria: listar y confirmar actividades | Manual | ⏳ Pendiente (Matías, tras construir HU 5) |

Comando de las pruebas del backend: `pytest app/tests/ -v` (usan SQLite en memoria; no requieren Docker). Verificado el 30-09-2026 contra el repositorio en GitHub tras los commits de este sprint: **25 passed**.

## 5. Seguimiento de commits del sprint

- 30-09: esquemas, dependencia de autorización, endpoints y pruebas de HU 2 (Benjamín, commits `fb20f39`, `9d2b425`, `3c11446`, `0af466e`).
- 30-09: modelo, migración, esquemas, endpoints y pruebas de HU 4 (Benjamín, commits `63f9451`, `de402ba`, `5a73c38`, `246aac5`, `42b274b`).
- 30-09: registro de los nuevos routers en `main.py` (Benjamín, commit `09151d2`).
- Pendiente: commits de Matías para el cierre de HU 3 y el desarrollo de HU 5.
