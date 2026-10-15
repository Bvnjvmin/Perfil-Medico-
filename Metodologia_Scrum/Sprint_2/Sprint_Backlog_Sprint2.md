# Sprint Backlog — Sprint 2 (S7–S8)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 20 de septiembre al 3 de octubre de 2026 (semanas 7 y 8 del Cronograma)
**Cierre formal y actualización final:** 12 de octubre de 2026 (estado verificado contra `main`, commit `1650323`)
**Objetivo del sprint:** cerrar los arrastres del Sprint 1 (API de HU 2 y validación de HU 3) e incorporar las dos historias nuevas del Product Backlog: registro de medicamentos y rutinas de cuidado (HU 4) y agenda diaria de actividades (HU 5).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregable comprometido:** API de perfil/alergias/contactos de emergencia funcional (HU 2), API de medicamentos/rutinas de cuidado funcional (HU 4), evidencia de validación de HU 3, y pantallas de agenda diaria en la app (HU 5).

## Resultado del sprint

**5 de 5 historias terminadas** (HU 2, HU 3, HU 4 y HU 5, más la HU 1 heredada del Sprint 1 sin cambios). Dos de ellas, **HU 3 y HU 5, se cerraron fuera del plazo del sprint**: el backend de HU 2 y HU 4 quedó en `main` el 30-09, pero el trabajo de la app y la evidencia de HU 3 y HU 5 se subieron el 10-10-2026, una semana después del cierre del 03-10.

**Limitación principal:** la confirmación de actividades de la agenda (HU 5) **se guarda solo en el celular**, no en el backend, porque las tablas `ACTIVIDAD` y `RUTINA_HORARIO` quedaron diferidas al Sprint 3 (decisión de alcance ratificada por el Product Owner el 01-10-2026, ver `Checklist_Aceptacion_PO_Sprint2.md`). Cumple los criterios de aceptación que este sprint escribió, pero **no cumple todavía la "confirmación de actividades de punta a punta (API, BD y UI conectadas)"** que pide el Cronograma para la semana 8. Esa parte pasa al Sprint 3.

## 1. Historias comprometidas

### HU 2 — Datos básicos de salud del titular (arrastre del Sprint 1, cierre de API)
- **Historia:** Como titular quiero registrar mis datos básicos de salud (RUT, grupo sanguíneo, alergias, contactos de emergencia) para tenerlos disponibles en una emergencia.
- **Responsables:** Benjamín Leiva (Backend) / Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - El titular autenticado puede crear, listar, consultar, actualizar y eliminar su perfil de salud.
  - El titular puede agregar, listar y eliminar alergias y contactos de emergencia de su propio perfil.
  - Un titular nunca puede ver ni modificar el perfil, alergias o contactos de otro titular (la API responde 404, no 403, para no revelar que el id pertenece a otra cuenta).
- **Estado al cierre:** ✅ **Terminada.** BD y migración desde el cierre del Sprint 1 (commit `6c01968`, Sergio); API completa en este sprint (esquemas Pydantic, dependencia `obtener_perfil_propio`, 11 endpoints y 10 pruebas automatizadas). El Product Owner la aceptó el 01-10-2026.
- **Evidencia:** `app/schemas/perfil.py`, `app/api/routes/perfil.py`, `app/tests/test_perfil.py` (10 pruebas, todas pasan).
- **Actualización 10-10-2026:** la app incorpora la pantalla "Mi perfil de salud" (crear y editar nombre, RUT y grupo sanguíneo). **Alergias y contactos de emergencia siguen disponibles solo desde la API**, sin pantalla en la app (ver sección 6).

### HU 3 — Pantallas de registro e inicio de sesión en la app (arrastre del Sprint 1, cierre de validación)
- **Historia:** Como usuario quiero una pantalla de registro/login simple en la app móvil para entrar a Perfil Médico+ desde mi celular.
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Se ejecutan las pruebas Flutter existentes (`usuario_test.dart`, `login_screen_test.dart`) con el SDK real y quedan registradas como evidencia.
  - Se documenta una prueba manual del flujo registro → login → Home contra el backend, con capturas de pantalla.
- **Estado al cierre:** ✅ **Terminada el 10-10-2026** (fuera del plazo del sprint, que cerró el 03-10).
- **Evidencia** (en `Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/app_movil/evidencias/`):
  - `evidencias flutter_test_HU3-HU5/evidencia_flutter_test_HU3.log`: 2 pruebas, `All tests passed!`.
  - `evidencias capturas_HU3/`: 8 capturas del flujo (login, validación del formulario vacío, registro, cuenta existente, notificación de cuenta creada, Home con la cuenta creada, error de contraseña incorrecta y cierre de sesión).
- **Notas:**
  - La prueba manual se hizo contra un backend **local** desde el emulador Android (la app apunta a `10.0.2.2:8000`, que es el computador anfitrión), no contra un backend desplegado, que es lo que dice literalmente el criterio.
  - El backend ya no expone el campo `rol` (se quitó de `usuarios`; ver sección 5), así que las pantallas y pruebas no lo usan.
  - En la numeración de las capturas falta la `HU3_03`, y la primera se llama `HU3_1_Registrando_cuenta`. Es solo un detalle de nombres.

### HU 4 — Medicamentos y rutinas de cuidado
- **Historia:** Como titular quiero registrar medicamentos y rutinas de cuidado (alimentación, hidratación, vitaminas) para mi propio perfil.
- **Responsables:** Benjamín Leiva (Backend) / Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Existen las tablas `medicamento` y `rutina_cuidado`, asociadas a un perfil mediante `perfil_id`.
  - El titular autenticado puede registrar, listar, actualizar y eliminar medicamentos y rutinas de cuidado de su propio perfil.
  - Un titular nunca puede ver ni modificar los medicamentos o rutinas del perfil de otro (respuesta 404).
- **Estado al cierre:** ✅ **Terminada** (backend el 30-09; pantallas en la app el 10-10). Modelo de datos, migración Alembic, esquemas Pydantic, 10 endpoints y 8 pruebas automatizadas. El Product Owner la aceptó el 01-10-2026, **con la simplificación de alcance ratificada**: se construyeron `Medicamento` y `RutinaCuidado` directos, sin `RUTINA_HORARIO` ni `ACTIVIDAD`.
- **Evidencia:** `app/models/medicamento.py`, `alembic/versions/a1b2c3d4e5f6_...py`, `app/schemas/medicamento.py`, `app/api/routes/medicamento.py`, `app/tests/test_medicamento.py` (8 pruebas, todas pasan). En la app: `screens/medicamentos_screen.dart` y `screens/rutinas_screen.dart`, con capturas `HU5_03` a `HU5_05`.
- **Actualización 10-10-2026:** las pantallas de la app permiten **registrar, listar y eliminar**. **No permiten editar**, aunque el endpoint `PUT` existe en el backend (ver sección 6).

### HU 5 — Agenda diaria de actividades
- **Historia:** Como usuario quiero ver mi agenda diaria de actividades y confirmar cada una.
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Alta (así figura en el Product Backlog; la versión anterior de este documento decía Media)
- **Criterios de aceptación:**
  - La app muestra una pantalla de agenda diaria que lista las actividades del perfil (medicamentos y rutinas de cuidado, consumidos desde los endpoints de HU 4).
  - El usuario puede marcar cada actividad como confirmada/realizada desde la pantalla.
- **Estado al cierre:** ✅ **Terminada el 10-10-2026** según los criterios de este sprint (fuera del plazo del sprint, que cerró el 03-10), **con la limitación descrita en "Resultado del sprint"**: la confirmación se guarda en el dispositivo.
- **Cómo funciona hoy:** `agenda_screen.dart` consume `GET /perfiles/{id}/medicamentos` y `GET /perfiles/{id}/rutinas`, une ambos en una lista ordenada por hora (las actividades sin hora van al final) y omite las inactivas. Cada actividad se marca con una casilla y el avance se muestra como "X de Y confirmadas". Las confirmaciones se guardan con `shared_preferences`, separadas por perfil y por día (`agenda_storage.dart`).
- **Consecuencias de guardar la confirmación en el celular:** se pierde si se desinstala la app o se cambia de dispositivo, y otra persona (un cuidador) no puede verla. Por eso HU 8, HU 10 y HU 13 necesitan la tabla `ACTIVIDAD` en el backend.
- **Evidencia:** `evidencias flutter_test_HU3-HU5/evidencia_flutter_test_HU5.log` (6 pruebas, `All tests passed!`) y `evidencias capturas_HU5/` (8 capturas: crear perfil de salud, cuenta con perfil, registro de medicamento, rutinas de cuidado, agenda inicial del día, agenda con actividades confirmadas y agenda con las confirmaciones conservadas al reabrir).

## 2. Tareas técnicas del sprint — estado final

| Tarea | Historia | Responsable | Estado | Dónde quedó |
|---|---|---|---|---|
| Esquemas Pydantic de Perfil/Alergia/ContactoEmergencia | HU 2 | Benjamín | ✅ Hecha (commit `fb20f39`) | `main` |
| Dependencia `obtener_perfil_propio` (acotar acceso al titular dueño del token) | HU 2 / HU 4 | Benjamín | ✅ Hecha (commit `9d2b425`) | `main` |
| Endpoints CRUD de Perfil/Alergia/ContactoEmergencia | HU 2 | Benjamín | ✅ Hecha (commit `3c11446`) | `main` |
| 10 pruebas automatizadas de HU 2 | HU 2 | Benjamín | ✅ Hecha (commit `0af466e`) | `main` |
| Modelos `Medicamento` y `RutinaCuidado` | HU 4 | Benjamín | ✅ Hecha (commit `63f9451`) | `main` |
| Migración Alembic de `medicamento` y `rutina_cuidado` | HU 4 | Benjamín | ✅ Hecha (commit `de402ba`) | `main` |
| Esquemas Pydantic de Medicamento/RutinaCuidado | HU 4 | Benjamín | ✅ Hecha (commit `5a73c38`) | `main` |
| Endpoints CRUD de Medicamento/RutinaCuidado | HU 4 | Benjamín | ✅ Hecha (commit `246aac5`) | `main` |
| 8 pruebas automatizadas de HU 4 | HU 4 | Benjamín | ✅ Hecha (commit `42b274b`) | `main` |
| Registrar routers de perfil y medicamento en `main.py` | HU 2 / HU 4 | Benjamín | ✅ Hecha (commit `09151d2`) | `main` |
| Ejecutar `flutter test` sobre `usuario_test.dart` y `login_screen_test.dart` | HU 3 | Matías | ✅ Hecha el 10-10 (commit `ee1d986`) | `app_movil/evidencias/` |
| Prueba manual registro → login → Home contra el backend, con capturas | HU 3 | Matías | ✅ Hecha el 10-10 (commit `ee1d986`) | `app_movil/evidencias/` |
| Modelos Dart (`Perfil`, `Medicamento`, `RutinaCuidado`, `ActividadAgenda`) y formato de hora | HU 4 / HU 5 | Matías | ✅ Hecha el 10-10 (commits `7ae1d6c`, `d9330ed`) | `app_movil/lib/` |
| Métodos de la API en `api_service.dart` (perfiles, medicamentos, rutinas) | HU 4 / HU 5 | Matías | ✅ Hecha el 10-10 (commit `854f877`) | `app_movil/lib/services/` |
| Pantallas de perfil, medicamentos, rutinas y agenda; Home con accesos | HU 4 / HU 5 | Matías | ✅ Hecha el 10-10 (commits `b30b31f`, `f5cbd7e`) | `app_movil/lib/screens/` |
| Marcar actividad como confirmada en la agenda (guardado local) | HU 5 | Matías | ✅ Hecha el 10-10 (commit `48c4c2b`), **solo en el dispositivo** | `app_movil/lib/services/agenda_storage.dart` |
| Pruebas Flutter de modelos y agenda (6 pruebas) | HU 4 / HU 5 | Matías | ✅ Hecha el 10-10 (commits `9bbc9ff`, `cc673a0`) | `app_movil/test/` |
| Permiso de internet y ajustes de Android para que la app llame al backend | HU 3 / HU 5 | Matías | ✅ Hecha el 10-10 (commits `3d6984d`, `a602045`, `c6b240a`) | `app_movil/android/` |
| Quitar el campo `rol` de `usuarios` en modelo, esquema, ruta de registro y migración | HU 1 / HU 2 | Matías | ✅ Hecha el 08-10 (commits `6cce62e`, `d202e1f`, `fc120f1`, `959da63`, `61ab8bd`, `53e58af`) | `backend/` |
| Duración del aviso "Cuenta creada" (8 s, con botón para cerrarlo) | HU 3 | Benjamín / Matías | ✅ Hecha (commits `4a87923` y `be8313b`, este último corrige un error de sintaxis del primero) | `app_movil/lib/screens/register_screen.dart` |
| Exportar el diagrama ER como imagen (arrastre del Sprint 1) | — | Sergio | ✅ Hecha el 01-10 (commit `64e8e35`) | `Base de datos/Diagramas/` |
| Actualizar `modelo_datos.md` con el estado real de HU 2/HU 4 y la decisión de alcance simplificado | HU 2 / HU 4 | Sergio | ✅ Hecha el 01-10 (commits `98f2f13`, `54ace69`) | `Base de datos/modelo_datos.md` |
| Checklist de aceptación del Product Owner (valida HU 2 y HU 4 contra sus criterios de aceptación) | HU 2 / HU 4 | Sergio | ✅ Hecha el 01-10 (commit `3cd0ee8`) | `Base de datos/Checklist_Aceptacion_PO_Sprint2.md` |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 2 | ✅ | ✅ (10 pruebas automatizadas y checklist del PO) | ✅ (este documento + `modelo_datos.md`) | **Sí** |
| HU 3 | ✅ | ✅ (2 pruebas Flutter y prueba manual con 8 capturas) | ✅ (este documento + capturas y log en `evidencias/`) | **Sí** (cerrada el 10-10, fuera de plazo) |
| HU 4 | ✅ | ✅ (8 pruebas automatizadas, 4 pruebas Flutter de modelos y checklist del PO) | ✅ (este documento + `modelo_datos.md`) | **Sí**, con alcance simplificado |
| HU 5 | ✅ | ✅ (2 pruebas Flutter de agenda y prueba manual con 8 capturas) | ✅ (este documento + capturas y log en `evidencias/`) | **Sí** según los criterios de este sprint (cerrada el 10-10, fuera de plazo); confirmación solo local |

## 4. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| Suite de perfil, alergias y contactos de emergencia (HU 2, 10 pruebas) | Automática (backend) | ✅ Pasan |
| Suite de medicamentos y rutinas de cuidado (HU 4, 8 pruebas) | Automática (backend) | ✅ Pasan |
| Suite de autenticación (HU 1, heredada, 7 pruebas) | Automática (backend) | ✅ Pasan |
| `usuario_test.dart`, `login_screen_test.dart` (2 pruebas) | Automática (Flutter) | ✅ Pasan (log del 10-10) |
| `cuidado_test.dart` (4 pruebas) y `agenda_test.dart` (2 pruebas) | Automática (Flutter) | ✅ Pasan (log del 10-10) |
| Flujo registro → login → Home contra el backend | Manual | ✅ 8 capturas, contra el backend local |
| Agenda diaria: crear perfil, registrar medicamentos y rutinas, listar y confirmar actividades, y reabrir la app | Manual | ✅ 8 capturas |
| Checklist de aceptación PO: criterios de HU 2 y HU 4 contra la API en vivo | Manual (Product Owner) | ✅ Aceptadas el 01-10-2026 |

Comando de las pruebas del backend: `pytest app/tests/ -v` (usan SQLite en memoria; no requieren Docker). **Verificado el 12-10-2026 contra `main` (commit `1650323`): 25 passed.** Las pruebas Flutter se ejecutaron en el computador de Matías; los logs están en `app_movil/evidencias/evidencias flutter_test_HU3-HU5/`.

## 5. Decisiones tomadas durante el sprint

1. **Alcance simplificado de HU 4:** `Medicamento` y `RutinaCuidado` directos; `RUTINA_HORARIO` y `ACTIVIDAD` pasan al Sprint 3. Ratificada por el Product Owner (01-10-2026).
2. **Confirmación local provisoria en HU 5:** como consecuencia de la decisión anterior, la agenda guarda las confirmaciones en el dispositivo hasta que exista el endpoint de confirmar.
3. **El campo `rol` sale de `usuarios`:** el 08-10 se quitó del modelo, del esquema y de la ruta de registro (y de la migración `39dd888f4030`, que ahora hace `drop_column`). Ser titular o cuidador no es un atributo de la persona sino del vínculo con un perfil, que se modelará en `PERFIL_ACCESO` (Sprint 3). Esto deja el código alineado con `modelo_datos.md`.

## 6. Trabajo que pasa al Sprint 3

1. **Confirmación persistida de punta a punta (HU 5):** tablas `ACTIVIDAD` y, si alcanza el tiempo, `RUTINA_HORARIO`; endpoints para listar las actividades del día y confirmarlas; y que la agenda de la app deje de usar `shared_preferences`.
2. **Edición de medicamentos y rutinas desde la app:** el endpoint `PUT` ya existe; faltan las pantallas.
3. **Pantallas de alergias y contactos de emergencia** (parte de HU 2 que solo existe en la API).
4. **Retrospectiva del Sprint 2:** ✅ redactada el 15-10 (`Metodologia_Scrum/Sprint_2/Retrospectiva_Sprint2.md`, a partir del repositorio; se confirma en la reunión del equipo). La demo interna sigue pendiente.
5. **Textos de la evidencia:** las capturas y los logs están subidos, pero no un texto corto que explique cada captura y a qué criterio corresponde.
6. **Diario de Reflexión 2.1 de Sergio:** ✅ resuelto. El archivo subido el 07-10 está completo y distinto de la plantilla vacía.
7. **Sprint Backlog 3:** ✅ subido el 13-10 (`Metodologia_Scrum/Sprint_3/Sprint_Backlog_Sprint3.md`).

## 7. Seguimiento de commits del sprint

- 30-09: esquemas, dependencia de autorización, endpoints y pruebas de HU 2 (Benjamín, commits `fb20f39`, `9d2b425`, `3c11446`, `0af466e`).
- 30-09: modelo, migración, esquemas, endpoints y pruebas de HU 4 (Benjamín, commits `63f9451`, `de402ba`, `5a73c38`, `246aac5`, `42b274b`).
- 30-09: registro de los nuevos routers en `main.py` (Benjamín, commit `09151d2`).
- 01-10: diagrama ER, `modelo_datos.md` actualizado y checklist de aceptación del PO (Sergio, commits `64e8e35`, `98f2f13`, `54ace69`, `3cd0ee8`).
- 02-10: correcciones del campo `rol` en backend y de `pubspec.yaml` (Matías, commits `4262e13`, `c9b3abb`, `e083ce5`, `3f779e4`, `9140dda`).
- 07-10: duración del aviso de cuenta creada (Benjamín, commit `4a87923`).
- 08-10: eliminación del campo `rol` y corrección del aviso de cuenta creada (Matías, commits `6cce62e` a `be8313b`).
- 10-10: pantallas, modelos, servicio, pruebas, ajustes de Android y evidencias de HU 3 y HU 5 (Matías, commits `d4401c8` a `ee1d986`); Diario de Reflexión 2.1 de Matías (commit `1650323`).
