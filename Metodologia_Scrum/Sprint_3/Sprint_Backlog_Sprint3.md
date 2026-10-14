# Sprint Backlog — Sprint 3 (S9–S10)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 5 al 17 de octubre de 2026 (semanas 9 y 10 del Cronograma)
**Última actualización:** 13 de octubre de 2026 (estado verificado contra `main`, commit `8149142`)
**Objetivo del sprint:** cerrar la confirmación de actividades de punta a punta (HU 5), validar los perfiles de dependientes (HU 6), permitir que un titular vincule cuidadores con permisos por perfil (HU 7) y entregar una versión inicial del panel de estado diario (HU 8).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregables del Cronograma:** Sprint Backlog 3 y Autoevaluación de avance de Fase 2 (semana 9); **Informe de Avance, evaluación sumativa del 20 %** (semana 10, cierre el sábado 17).

## Estado del sprint (13-10-2026)

**Base de datos terminada.** Las tablas `actividad` y `perfil_acceso`, el índice de titular único y el borrado en cascada ya están en `main` (commits `7e2ebdb`, `4f81fdd` y `b010924`), junto con `modelo_datos.md` y el diagrama ER actualizados (commit `8149142`). Esto desbloquea las rutas del backend y la conexión de la app. Las 25 pruebas del backend siguen pasando.

**Pendiente:** validaciones y rutas del backend (HU 6, HU 5, HU 7, HU 8), pantallas de la app, checklist de aceptación del Product Owner y documentos del sprint. Esta sección se actualiza a medida que avanza el sprint.

## 1. Historias comprometidas

### HU 6 — Perfiles de dependientes
- **Responsables:** Benjamín Leiva (Backend), Matías Pizarro (App), Sergio Ocares (BD) · **Prioridad:** Imprescindible
- **Criterios de aceptación:**
  - Un titular puede crear perfiles dependientes con `tipo = 'dependiente'` y `subtipo` válido (`adulto_mayor` o `nino`); un subtipo inválido se rechaza, y el titular no lleva subtipo.
  - Cada cuenta tiene un solo perfil titular; un segundo titular se rechaza.
  - Borrar un perfil con alergias, contactos, medicamentos, rutinas, actividades y vínculos deja todo limpio.
  - La app muestra la pantalla "Mis perfiles" y permite elegir el perfil activo.
- **Estado:** 🟡 **En curso.** Base de datos lista (índice de titular único y cascadas, commits `4f81fdd` y `b010924`). Faltan validaciones y arreglo del borrado en el backend, y las pantallas de la app.

### HU 5 — Agenda diaria de actividades (cierre)
- **Responsables:** Sergio Ocares (BD), Benjamín Leiva (Backend), Matías Pizarro (App) · **Prioridad:** Imprescindible
- **Criterios de aceptación:**
  - Existe la tabla `actividad` y la confirmación se guarda en el backend, no en el dispositivo.
  - Al pedir la agenda de una fecha, el backend devuelve las actividades de cada medicamento o rutina activos, sin duplicarlas.
  - Se puede confirmar y desconfirmar una actividad, y el cambio se conserva al volver a consultar.
  - La agenda de la app consume la API en vez de `shared_preferences`.
- **Estado:** 🟡 **En curso.** Tabla `actividad` lista (commit `7e2ebdb`). Faltan los endpoints de actividades y conectar la agenda de la app.

### HU 7 — Permisos y cuidadores
- **Responsables:** Sergio Ocares (BD), Benjamín Leiva (Backend), Matías Pizarro (App) · **Prioridad:** Importante
- **Criterios de aceptación:**
  - Existe la tabla `perfil_acceso`, con un solo vínculo por persona y perfil.
  - El titular puede vincular a un cuidador por correo (solo si ya tiene cuenta; si no, recibe un error claro), cambiar sus permisos y revocarlos.
  - Se respeta la matriz de acceso: un cuidador ve el perfil y confirma solo si tiene `puede_confirmar` (si no, 403); no puede editar ni borrar el perfil; una cuenta ajena recibe 404.
  - La app respeta los permisos de cada perfil.
- **Estado:** 🟡 **En curso.** Tabla `perfil_acceso` lista (commit `b010924`). Faltan las rutas de cuidadores, la dependencia de permisos y la app.

### HU 8 — Panel de estado diario (versión inicial)
- **Responsables:** Benjamín Leiva (Backend), Matías Pizarro (App) · **Prioridad:** Importante
- **Criterios de aceptación:**
  - `GET /panel?fecha=` devuelve, por cada perfil al que el usuario tiene acceso, el total de actividades, las confirmadas y las pendientes.
  - La pantalla "Panel" muestra ese avance por perfil, propio y compartido.
- **Estado:** ⬜ **No iniciada.** Depende de `actividad` y `perfil_acceso` (ya disponibles). Se entrega en su versión mínima si el tiempo no alcanza.

### Extras (Deseable)
Editar medicamentos y rutinas desde la app, pantallas de alergias y contactos, pantalla para compartir un perfil, `RUTINA_HORARIO` y datos de prueba. Son lo primero que se recorta.

## 2. Tareas técnicas del sprint

| Tarea | Historia | Responsable | Estado | Dónde |
|---|---|---|---|---|
| Modelo y migración de `ACTIVIDAD` (dos llaves opcionales, restricciones e índice por perfil y fecha) | HU 5 | Sergio | ✅ Hecha el 13-10 (commit `7e2ebdb`) | `backend/app/models/actividad.py`, `alembic/versions/b3c4d5e6f7a8_...py` |
| Índice único del perfil titular por cuenta | HU 6 | Sergio | ✅ Hecha el 13-10 (commit `4f81fdd`) | `alembic/versions/c4d5e6f7a8b9_...py` |
| Modelo y migración de `PERFIL_ACCESO` y borrado en cascada de las tablas de perfil | HU 7 / HU 6 | Sergio | ✅ Hecha el 13-10 (commit `b010924`) | `alembic/versions/d5e6f7a8b9c0_...py`, `e6f7a8b9c0d1_...py` |
| `modelo_datos.md` y diagrama ER al día | HU 6 / HU 7 | Sergio | ✅ Hecha el 13-10 (commit `8149142`) | `Base de datos/` |
| Validaciones de `tipo` y `subtipo`, y arreglo del borrado de perfiles | HU 6 | Benjamín | ⬜ Pendiente | `backend/` |
| Rutas de actividades (listar agenda, confirmar, desconfirmar) | HU 5 | Benjamín | ⬜ Pendiente | `backend/` |
| Dependencia de permisos y rutas de cuidadores | HU 7 | Benjamín | ⬜ Pendiente | `backend/` |
| `GET /panel` y pruebas de la matriz de permisos | HU 8 / HU 7 | Benjamín | ⬜ Pendiente | `backend/` |
| Modelo `Perfil` con tipo y subtipo; pantalla "Mis perfiles" y selector de perfil activo | HU 6 | Matías | ⬜ Pendiente | `app_movil/lib/` |
| Agenda conectada a la API | HU 5 | Matías | ⬜ Pendiente | `app_movil/lib/` |
| Permisos respetados en la app | HU 7 | Matías | ⬜ Pendiente | `app_movil/lib/` |
| Pantalla "Panel" | HU 8 | Matías | ⬜ Pendiente | `app_movil/lib/` |
| Checklist de aceptación del Product Owner | HU 5 / HU 6 / HU 7 / HU 8 | Sergio | ⬜ Pendiente (jueves 15, con la API de Benjamín) | `Base de datos/Checklist_Aceptacion_PO_Sprint3.md` |
| Retrospectiva del Sprint 2 | — | Matías | ⬜ Pendiente (después de la reunión del equipo) | `Metodologia_Scrum/Sprint_2/` |
| Diario de Reflexión 2.1 | — | Sergio | ✅ Hecha el 07-10 (commit `9bc9097`) | `Fase 2/Evidencias Individuales/` |
| Autoevaluación de avance 2.2 | — | Sergio | ⬜ Pendiente | `Fase 2/Evidencias Individuales/` |
| Sección de base de datos y ensamble del Informe de Avance | — | Sergio | ⬜ Pendiente (viernes 16 y sábado 17) | Informe de Avance |
| Textos de evidencia del Sprint 2 y del Sprint 3, y secciones del Informe | — | Matías / Benjamín | ⬜ Pendiente | `app_movil/evidencias/`, Informe de Avance |
| `RUTINA_HORARIO` y datos de prueba | HU 4 | Sergio / Matías | ⬜ Deseable, solo si sobra tiempo | — |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 6 | 🟡 Solo la base de datos | ⬜ | 🟡 `modelo_datos.md` al día | No |
| HU 5 (cierre) | 🟡 Solo la tabla | ⬜ | 🟡 `modelo_datos.md` al día | No |
| HU 7 | 🟡 Solo la tabla | ⬜ | 🟡 `modelo_datos.md` al día | No |
| HU 8 | ⬜ | ⬜ | ⬜ | No |

Las migraciones de este sprint se probaron desde una base vacía, hacia arriba y hacia abajo, y borrar un perfil con datos asociados deja todas las tablas limpias.

## 4. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| Suites del backend existentes (HU 1, HU 2 y HU 4) | Automática (backend) | ✅ 25 pruebas pasan (13-10, con los cambios de base de datos) |
| `alembic upgrade head` desde base vacía y `downgrade` / `upgrade` de cada migración nueva | Manual (PostgreSQL en Docker) | ✅ Sin errores (13-10) |
| Un segundo perfil titular de la misma cuenta se rechaza | Manual (PostgreSQL) | ✅ Rechazado por `uq_perfil_un_titular_por_cuenta` (13-10) |
| Actividad con las dos llaves vacías, con las dos llenas o duplicada el mismo día | Automática | ⬜ Pendiente con las rutas de actividades |
| Borrar un perfil con datos asociados | Manual (PostgreSQL) | ✅ Todo queda limpio (13-10) |
| Matriz de permisos (titular, cuidador, lectura y cuenta ajena) | Automática (backend) | ⬜ Pendiente |
| Checklist de aceptación del Product Owner con tres cuentas (dueño, cuidador y ajena) | Manual (Product Owner) | ⬜ Pendiente (jueves 15) |
| Flujo equivalente desde la app | Manual (emulador) | ⬜ Pendiente |

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
2. **Alertas escalonadas** (HU 10) y **% de cumplimiento** (HU 13), que dependen de `ACTIVIDAD` y de `nivel_escalamiento` de `PERFIL_ACCESO`.
3. **Lo que no alcance del Sprint 3:** extras Deseables, edición de medicamentos y rutinas desde la app, y pantallas de alergias y contactos.
4. **Ideas pendientes de decisión:** recuperar contraseña y cambiar correo (requieren infraestructura de correo), invitación de cuidadores por enlace o código, y creación automática del perfil titular al registrarse.

## 7. Seguimiento de commits del sprint

- 13-10: tabla `actividad`, índice de titular único, tabla `perfil_acceso` y borrado en cascada (Sergio, commits `7e2ebdb`, `4f81fdd`, `b010924`).
- 13-10: `modelo_datos.md` y diagrama ER actualizados al Sprint 3 (Sergio, commit `8149142`).
