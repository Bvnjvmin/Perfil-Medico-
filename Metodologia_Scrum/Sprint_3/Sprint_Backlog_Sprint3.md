# Sprint Backlog — Sprint 3 (S9–S10)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 5 al 17 de octubre de 2026 (semanas 9 y 10 del Cronograma)
**Última actualización:** 20 de octubre de 2026 (estado verificado contra `main`, commit `6a948d8`)
**Objetivo del sprint:** cerrar la confirmación de actividades de punta a punta (HU 5), validar los perfiles de dependientes (HU 6), permitir que un titular vincule cuidadores con permisos por perfil (HU 7) y entregar una versión inicial del panel de estado diario (HU 8).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregables del Cronograma:** Sprint Backlog 3 y Autoevaluación de avance de Fase 2 (semana 9); **Informe de Avance, evaluación sumativa del 20 %** (semana 10, cierre el sábado 17).

## Estado del sprint (13-10-2026)

**Base de datos terminada.** Las tablas `actividad` y `perfil_acceso`, el índice de titular único y el borrado en cascada ya están en `main` (commits `7e2ebdb`, `4f81fdd` y `b010924`), junto con `modelo_datos.md` y el diagrama ER actualizados (commit `8149142`). Esto desbloquea las rutas del backend y la conexión de la app. Las 25 pruebas del backend siguen pasando.

**Backend terminado (15-10).** Validación de perfiles dependientes, agenda diaria con confirmación guardada en el servidor, cuidadores con permisos por perfil y `GET /panel` están en `main` (commits `beedd83` a `7d30476`), con 119 pruebas automatizadas que pasan.

**App terminada (15 y 16-10).** Las pantallas "Mis perfiles", "Compartir perfil" y "Panel" (HU 6, HU 7 y HU 8) y la agenda conectada a la API (HU 5) están en `main` (commits `45308b6` a `5c6783a`); se eliminó `agenda_storage.dart`, que guardaba la agenda en el dispositivo. `flutter test` pasa 10 de 10 y `flutter analyze` no reporta errores (4 avisos informativos). Matías probó los flujos en el emulador con dos cuentas (titular y cuidador) y dejó 17 capturas.

**Pruebas del backend (17-10).** Las 119 pruebas fallaban a partir del 15-10 porque usaban fechas fijas y las actividades solo se generan desde la creación del medicamento. Se cambiaron a la fecha de hoy y vuelven a pasar las 119.

**Cierre (17 al 19-10).** Los textos de evidencia y la retrospectiva del Sprint 3 (Matías, 17-10), las autoevaluaciones 2.2 de Matías (17-10) y de Sergio (19-10) y el Informe de Avance (`Informe_Avance_2_4.docx`, 17-10) están en `main`.

**Pendiente:** el checklist de aceptación del Product Owner (`Checklist_Aceptacion_PO_Sprint3.md`), que Sergio sube antes de la evaluación del 21-10.

## 1. Historias comprometidas

### HU 6 — Perfiles de dependientes
- **Responsables:** Benjamín Leiva (Backend), Matías Pizarro (App), Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Un titular puede crear perfiles dependientes con `tipo = 'dependiente'` y `subtipo` válido (`adulto_mayor` o `nino`); un subtipo inválido se rechaza, y el titular no lleva subtipo.
  - Cada cuenta tiene un solo perfil titular; un segundo titular se rechaza.
  - Borrar un perfil con alergias, contactos, medicamentos, rutinas, actividades y vínculos deja todo limpio.
  - La app muestra la pantalla "Mis perfiles" y permite elegir el perfil activo.
- **Estado:** 🟡 **Lista, falta la aceptación del PO.** Base de datos lista (commits `4f81fdd` y `b010924`) y backend listo (validación de `tipo` y `subtipo`, un solo titular por cuenta y borrado ordenado, 15-10). Las pantallas "Mis perfiles" (con etiquetas "Tuyo" y "Compartido contigo"), el formulario de dependiente con subtipo y el selector de perfil activo están en `main` (Matías, 15-10); probado en el emulador (capturas `S3_01` a `S3_03`). Falta la aceptación del Product Owner.

### HU 5 — Agenda diaria de actividades (cierre)
- **Responsables:** Sergio Ocares (BD), Benjamín Leiva (Backend), Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Existe la tabla `actividad` y la confirmación se guarda en el backend, no en el dispositivo.
  - Al pedir la agenda de una fecha, el backend devuelve las actividades de cada medicamento o rutina activos, sin duplicarlas.
  - Se puede confirmar y desconfirmar una actividad, y el cambio se conserva al volver a consultar.
  - La agenda de la app consume la API en vez de `shared_preferences`.
- **Estado:** 🟡 **Lista, falta la aceptación del PO.** Tabla `actividad` (commit `7e2ebdb`), endpoints (15-10) y agenda de la app conectada a la API (Matías, 15-10); la confirmación se conserva al cerrar sesión y volver a entrar (capturas `S3_04`).

### HU 7 — Permisos y cuidadores
- **Responsables:** Sergio Ocares (BD), Benjamín Leiva (Backend), Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Existe la tabla `perfil_acceso`, con un solo vínculo por persona y perfil.
  - El titular puede vincular a un cuidador por correo (solo si ya tiene cuenta; si no, recibe un error claro), cambiar sus permisos y revocarlos.
  - Se respeta la matriz de acceso: un cuidador ve el perfil y confirma solo si tiene `puede_confirmar` (si no, 403); no puede editar ni borrar el perfil; una cuenta ajena recibe 404.
  - La app respeta los permisos de cada perfil.
- **Estado:** 🟡 **Lista, falta la aceptación del PO.** Tabla `perfil_acceso` lista (commit `b010924`) y rutas de cuidadores con dependencia de permisos listas (15-10). La app (15-10) muestra el formulario para compartir, bloquea la edición y la confirmación según el rol, y muestra el mensaje del backend si el correo no existe (capturas `S3_06`). Falta la aceptación del Product Owner.

### HU 8 — Panel de estado diario (versión inicial)
- **Responsables:** Benjamín Leiva (Backend), Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - `GET /panel?fecha=` devuelve, por cada perfil al que el usuario tiene acceso, el total de actividades, las confirmadas y las pendientes.
  - La pantalla "Panel" muestra ese avance por perfil, propio y compartido.
- **Estado:** 🟡 **Lista, falta la aceptación del PO.** `GET /panel?fecha=` en el backend (15-10) y pantalla "Panel" en la app (Matías, 15-10), con una tarjeta de avance por perfil (captura `S3_05`). Limitación conocida: la app hace una llamada por perfil en vez de usar `GET /panel`.

### Extras (Deseable)
Editar medicamentos y rutinas desde la app, pantallas de alergias y contactos, pantalla para compartir un perfil, `RUTINA_HORARIO` y datos de prueba. Son lo primero que se recorta.

## 2. Tareas técnicas del sprint

| Tarea | Historia | Responsable | Estado | Dónde |
|---|---|---|---|---|
| Modelo y migración de `ACTIVIDAD` (dos llaves opcionales, restricciones e índice por perfil y fecha) | HU 5 | Sergio | ✅ Hecha el 13-10 (commit `7e2ebdb`) | `backend/app/models/actividad.py`, `alembic/versions/b3c4d5e6f7a8_...py` |
| Índice único del perfil titular por cuenta | HU 6 | Sergio | ✅ Hecha el 13-10 (commit `4f81fdd`) | `alembic/versions/c4d5e6f7a8b9_...py` |
| Modelo y migración de `PERFIL_ACCESO` y borrado en cascada de las tablas de perfil | HU 7 / HU 6 | Sergio | ✅ Hecha el 13-10 (commit `b010924`) | `alembic/versions/d5e6f7a8b9c0_...py`, `e6f7a8b9c0d1_...py` |
| `modelo_datos.md` y diagrama ER al día | HU 6 / HU 7 | Sergio | ✅ Hecha el 13-10 (commit `8149142`) | `Base de datos/` |
| Validaciones de `tipo` y `subtipo`, y arreglo del borrado de perfiles | HU 6 | Benjamín | ✅ Hecha el 15-10 (commit `534d656`) | `backend/` |
| Rutas de actividades (listar agenda, confirmar, desconfirmar) | HU 5 | Benjamín | ✅ Hecha el 15-10 (commits `0bf2126` y `5edcc9d`) | `backend/` |
| Dependencia de permisos y rutas de cuidadores | HU 7 | Benjamín | ✅ Hecha el 15-10 (commits `beedd83` y `534d656`) | `backend/` |
| `GET /panel` y pruebas de la matriz de permisos | HU 8 / HU 7 | Benjamín | ✅ Hecha el 15-10 (commits `5edcc9d` y `7d30476`) | `backend/` |
| Modelo `Perfil` con tipo y subtipo; pantalla "Mis perfiles" y selector de perfil activo | HU 6 | Matías | ✅ Hecha el 15-10 (commits `45308b6`, `66f29a4` y `c5ac914`) | `app_movil/lib/` |
| Agenda conectada a la API | HU 5 | Matías | ✅ Hecha el 15-10 (commits `a5be8cb` y `cbdff7f`) | `app_movil/lib/` |
| Permisos respetados en la app | HU 7 | Matías | ✅ Hecha el 15-10 (commits `a69c7f2`, `a43d4aa` y `a5be8cb`) | `app_movil/lib/` |
| Pantalla "Panel" | HU 8 | Matías | ✅ Hecha el 15-10 (commit `45308b6`) | `app_movil/lib/` |
| Pruebas de la app (`flutter test`, 10 de 10) y logs del sprint | HU 5 / HU 6 / HU 7 / HU 8 | Matías | ✅ Hecha el 15 y 16-10 (commits `71571ae`, `85114c8`, `1a1c0d9` y `5c6783a`) | `app_movil/test/`, `evidencias/` |
| Pruebas del backend con fecha dinámica (119 pasan) | HU 5 | Benjamín | ✅ Hecha el 17-10 | `backend/app/tests/` |
| Checklist de aceptación del Product Owner | HU 5 / HU 6 / HU 7 / HU 8 | Sergio | ⬜ Pendiente: Sergio lo sube antes del 21-10 | `Base de datos/Checklist_Aceptacion_PO_Sprint3.md` |
| Retrospectiva del Sprint 2 | — | Matías | ✅ Redactada el 15-10 a partir del repositorio (commit `656cf4b`); se confirma en la reunión del equipo | `Metodologia_Scrum/Sprint_2/` |
| Diario de Reflexión 2.1 | — | Sergio | ✅ Hecha el 07-10 (commit `9bc9097`) | `Fase 2/Evidencias Individuales/` |
| Autoevaluación de avance 2.2 | — | Benjamín | ✅ Hecha el 15-10 (commit `dd5dd13`) | `Fase 2/Evidencias Individuales/` |
| Autoevaluación de avance 2.2 | — | Sergio / Matías | ✅ Hecha el 17-10 (Matías) y el 19-10 (Sergio) | `Fase 2/Evidencias Individuales/` |
| Sección de base de datos y ensamble del Informe de Avance | — | Sergio | ✅ Hecha el 17-10 | `Fase 2/Evidencias Grupales/Informe_Avance_2_4.docx` |
| Textos de evidencia y retrospectiva del Sprint 3, y secciones del Informe | — | Matías / Benjamín | ✅ Hecha el 17-10 | `app_movil/evidencias/`, `Metodologia_Scrum/Sprint_3/`, Informe de Avance |
| `RUTINA_HORARIO` y datos de prueba | HU 4 | Sergio / Matías | ⬜ Deseable, solo si sobra tiempo | — |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 6 | ✅ Base de datos, backend y app | ✅ 119 pruebas del backend, 10 de la app y emulador | ✅ `modelo_datos.md` y `Evidencia_Sprint3.md` | Falta el checklist del PO |
| HU 5 (cierre) | ✅ Tabla, backend y app | ✅ 119 pruebas del backend, 10 de la app y emulador | ✅ `modelo_datos.md` y `Evidencia_Sprint3.md` | Falta el checklist del PO |
| HU 7 | ✅ Tabla, backend y app | ✅ 119 pruebas del backend, 10 de la app y emulador (dos cuentas) | ✅ `modelo_datos.md` y `Evidencia_Sprint3.md` | Falta el checklist del PO |
| HU 8 | ✅ Backend y app | ✅ 119 pruebas del backend, 10 de la app y emulador | ✅ `Evidencia_Sprint3.md` | Falta el checklist del PO |

Las migraciones de este sprint se probaron desde una base vacía, hacia arriba y hacia abajo, y borrar un perfil con datos asociados deja todas las tablas limpias.

## 4. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| Suites del backend existentes (HU 1, HU 2 y HU 4) | Automática (backend) | ✅ 25 pruebas pasan (13-10, con los cambios de base de datos) |
| `alembic upgrade head` desde base vacía y `downgrade` / `upgrade` de cada migración nueva | Manual (PostgreSQL en Docker) | ✅ Sin errores (13-10) |
| Un segundo perfil titular de la misma cuenta se rechaza | Manual (PostgreSQL) | ✅ Rechazado por `uq_perfil_un_titular_por_cuenta` (13-10) |
| Actividad con las dos llaves vacías, con las dos llenas o duplicada el mismo día | Automática | ✅ Pasan (15-10) |
| Borrar un perfil con datos asociados | Manual (PostgreSQL) | ✅ Todo queda limpio (13-10) |
| Matriz de permisos (titular, cuidador, lectura y cuenta ajena) | Automática (backend) | ✅ Pasan (15-10, 119 pruebas en total; el 17-10 se cambiaron las fechas fijas por la fecha de hoy y vuelven a pasar las 119) |
| Checklist de aceptación del Product Owner con tres cuentas (dueño, cuidador y ajena) | Manual (Product Owner) | ⬜ Pendiente: Sergio lo sube antes del 21-10 |
| Flujo equivalente desde la app (perfiles, agenda, panel y permisos de cuidador, con dos cuentas) | Manual (emulador, Matías) | ✅ 15 y 16-10, 17 capturas en `app_movil/evidencias/evidencias Sprint 3/` |
| `flutter test` y `flutter analyze` | Automática (app) | ✅ 10 de 10 pasan; sin errores y 4 avisos informativos (16-10) |

Comando de las pruebas del backend: `pytest app/tests/ -v`. Las pruebas usan SQLite en memoria, que no valida llaves foráneas, por lo que los cambios de base de datos se prueban además contra PostgreSQL.

## 5. Decisiones del sprint

Criterios propuestos el 12-10-2026; se confirman o se ajustan en la reunión del equipo.

1. **El campo `rol` no vuelve a `usuarios`:** ser cuidador es un vínculo con un perfil y vive en `PERFIL_ACCESO`. El titular no tiene fila en esa tabla; su acceso sale de `perfil.cuenta_titular_id`.
2. **Tipos de perfil:** `tipo` es `titular` o `dependiente`; `subtipo` es obligatorio solo para dependientes y debe venir vacío en el titular. Cada cuenta tiene un solo titular.
3. **`ACTIVIDAD` apunta al origen con dos llaves opcionales** (`medicamento_id` o `rutina_id`, exactamente una), con borrado en cascada, en vez de una referencia genérica de tipo e id.
4. **Las actividades de un día se generan al consultar la agenda**, sin job programado; el job se necesitará en el Sprint 4 para las notificaciones.
5. **La fecha la envía la app** (`?fecha=AAAA-MM-DD`), porque el servidor puede estar en otra zona horaria que Chile.
6. **Vincular a un cuidador por correo** solo funciona con cuentas existentes. Esto revela si un correo está registrado; para el MVP se acepta y queda anotado.
7. **Solo Sergio crea migraciones de Alembic** en este sprint, para que la cadena tenga una única cabeza (hoy `e6f7a8b9c0d1`).

## 6. Trabajo que pasa al Sprint 4

Se completa al cierre del sprint. Lo previsto hasta ahora:

1. **`RUTINA_HORARIO`** y el job programado que genera las actividades con anticipación, necesario para las notificaciones.
2. **Alertas escalonadas** (HU 10), que dependen de `ACTIVIDAD` y de `nivel_escalamiento` de `PERFIL_ACCESO`. El **% de cumplimiento** (HU 13) sigue planificado para el Sprint 5, junto con los indicadores de salud.
3. **Lo que no alcance del Sprint 3:** extras Deseables, edición de medicamentos y rutinas desde la app, y pantallas de alergias y contactos.
4. **Ideas pendientes de decisión:** recuperar contraseña y cambiar correo (requieren infraestructura de correo), invitación de cuidadores por enlace o código, y creación automática del perfil titular al registrarse.

## 7. Seguimiento de commits del sprint

- 13-10: tabla `actividad`, índice de titular único, tabla `perfil_acceso` y borrado en cascada (Sergio, commits `7e2ebdb`, `4f81fdd`, `b010924`).
- 13-10: `modelo_datos.md` y diagrama ER actualizados al Sprint 3 (Sergio, commit `8149142`).
- 15-10: permisos por vínculo, validación de perfiles dependientes, agenda diaria, cuidadores, panel y pruebas del backend (Benjamín, commits `beedd83` a `7d30476`); autoevaluación 2.2 de Benjamín (commit `dd5dd13`); retrospectiva del Sprint 2 (commit `656cf4b`).
- 15 y 16-10: pantallas de perfiles, panel y compartir, agenda conectada a la API, pruebas de la app, logs y capturas del Sprint 3 (Matías, commits `45308b6` a `5c6783a`).
- 17-10: pruebas del backend con fecha dinámica y `pytest.log` nuevo (Benjamín); este Sprint Backlog actualizado.
- 17-10: evidencia y retrospectiva del Sprint 3 corregidas, autoevaluación 2.2 de Matías y capturas renombradas (Matías, commits `0f457a8` a `e5feecc`); Informe de Avance subido (Sergio).
- 19-10: autoevaluación 2.2 de Sergio.
- 20-10: estados de este Sprint Backlog y de los README al día.
