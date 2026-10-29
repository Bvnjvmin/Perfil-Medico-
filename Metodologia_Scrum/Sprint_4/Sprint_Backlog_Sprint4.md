# Sprint Backlog — Sprint 4 (S11–S12)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 19 al 31 de octubre de 2026 (semanas 11 y 12 del Cronograma)
**Subido al repositorio:** 25 de octubre de 2026 (`31c3353`) · **Última actualización:** 29 de octubre de 2026 (día 11 de 13) · **Estado del sprint:** en curso; el backend está probado (148 pruebas) y la app se probó en el emulador el 25-10 (10 flujos, capturas `S4_01` a `S4_11`, ver `Evidencia_Sprint4.md`; 10 ✅; los flujos 5 y 9 se repitieron el 27 y el 28-10); faltan la aceptación del Product Owner, el push real (FCM) y la retrospectiva final

**Objetivo del sprint:** que el sistema genere solo las actividades de cada día (`RUTINA_HORARIO` y generación programada), avise al usuario antes de cada actividad (HU 9), escale el aviso a los cuidadores cuando una actividad importante no se confirma (HU 10) y que el perfil dependiente tenga una interfaz simplificada de un toque (HU 11).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregables del Cronograma:** Sprint Backlog 4 (semana 11); Demo interna y Retrospectiva del Sprint 4 (semana 12, cierre el sábado 31).

> Leyenda: ✅ terminado y verificado · 🟡 escrito, falta subirlo o verificarlo (se indica qué) · ⬜ pendiente. Una historia solo pasa a terminada cuando está integrada al repositorio, probada y documentada. Los criterios y decisiones son propuesta hasta confirmarlos en la reunión del equipo.

## 1. Historias comprometidas

### HU 9 — Notificaciones push de actividades pendientes
- **Responsables:** Benjamín Leiva (Backend), Matías Pizarro (App), Sergio Ocares (BD) · **Prioridad:** Media (en el Backlog), necesaria para HU 10
- **Criterios de aceptación (propuestos):**
  - El backend permite registrar el dispositivo del usuario (`POST /dispositivos`) para poder enviarle notificaciones.
  - El backend crea un recordatorio 10 minutos antes de la hora de cada actividad pendiente del día, para el titular y los vinculados con `recibe_alertas`.
  - Una actividad ya confirmada no genera recordatorio.
  - Los recordatorios se ven en la pantalla Avisos de la app; tocar uno abre la Agenda del perfil correspondiente.
  - **Alcance real:** el envío de la notificación push al celular (FCM) **no está implementado**; hoy el backend registra el envío en el log y el usuario ve el aviso dentro de la app. Falta decidir el proveedor y sus credenciales.
- **Estado:** 🟡 Backend probado (rutas, recordatorios y registro de dispositivo). En el emulador (25-10) el recordatorio aparece sin leer en Avisos y tocarlo marca el aviso como leído y abre la Agenda (capturas `S4_01` a `S4_03`). Falta el push real, registrar commits y la aceptación del PO.

### HU 10 — Alertas escalonadas
- **Responsables:** Benjamín Leiva (Backend), Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación (propuestos):**
  - Si una actividad sigue pendiente 30 minutos después de su hora, se crea una alerta de nivel 1 para el titular y los cuidadores con `recibe_alertas = true` y `nivel_escalamiento = 1`.
  - Si sigue sin confirmarse 60 minutos después de su hora, se crea una alerta de nivel 2 para los cuidadores con `nivel_escalamiento = 2`.
  - Confirmar la actividad detiene el escalamiento.
  - Cada alerta queda registrada con actividad, destinatario, nivel y fecha, y se puede consultar desde la API.
  - El sistema no asume una emergencia: el mensaje informa que la actividad no fue confirmada.
  - Al terminar el día, las actividades sin confirmar pasan a `vencida`.
- **Estado:** 🟡 Backend probado (escalamiento, destinatarios, no repetir avisos, `GET /alertas`). En el emulador (25-10) las alertas de nivel 1 llegan al cuidador y al titular con un mensaje que no asume una emergencia (`S4_04`); el nivel 2 llega al cuidador configurado en nivel 2 (`S4_04.5`); el titular y el cuidador en nivel 1 no reciben el nivel 2 (`S4_04.6`). "Confirmar detiene el escalamiento" está probado en el backend (`test_confirmar_detiene_el_escalamiento`) y también en la app (28-10, con plazos de prueba de 1 y 5 minutos): las dos actividades reciben el nivel 1 y solo la no confirmada recibe el nivel 2 (`S4_05.3` a `S4_05.5`). Falta la cuenta ajena y la aceptación del PO.

### HU 11 — Interfaz simplificada para el perfil dependiente
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación (propuestos):**
  - Existe un modo simplificado con botones grandes y texto grande que muestra solo las actividades de hoy del perfil.
  - Confirmar una actividad toma un solo toque, sin menús intermedios.
  - El modo simplificado no permite editar ni borrar datos.
  - Se puede entrar y salir del modo desde la cuenta del titular (la salida pide confirmación).
- **Estado:** 🟡 Probado en el emulador (25-10): solo actividades de hoy, botones grandes, confirmación en un toque guardada en el servidor y sin opciones de editar o borrar (capturas `S4_06` a `S4_08`). La salida pide confirmación (`S4_06.1`). Falta la aceptación del PO.

### Habilitadores técnicos (del Cronograma, semana 11)
`RUTINA_HORARIO` y generación programada de actividades: son la base de HU 9 y HU 10, porque las notificaciones y las alertas necesitan saber de antemano qué actividad toca y a qué hora. **Estado:** 🟡 tabla, rutas de horarios y tarea programada listas, probadas (backend y PostgreSQL) y subidas el 22-10 (sección 7).

### Extras (Deseable)
Editar medicamentos y rutinas desde la app, y pantallas de alergias y contactos. Son lo primero que se recorta.

## 2. Tareas técnicas del sprint

| Tarea | Historia | Responsable | Estado | Dónde |
|---|---|---|---|---|
| Contrato de API del sprint (rutas, cuerpos y errores) acordado con la app **antes** de implementar | HU 9 / HU 10 | Benjamín | 🟡 Redactado con las rutas reales (`Contrato_API_Sprint4.md`); Matías lo revisó el 27-10 (sección 9 del contrato, aprobado con observaciones); falta el visto bueno de Sergio | `backend/` |
| Migración y modelo de `RUTINA_HORARIO` | Habilitador | Sergio | ✅ Listo, probado en PostgreSQL y subido el 22-10 (`4539965`, `4542b76`) | `alembic/versions/`, `models/` |
| Migraciones de `alerta` y de dispositivos para notificaciones; `hora` y estados `omitida` y `vencida` de `actividad` | HU 9 / HU 10 | Sergio | ✅ Listas, probadas en PostgreSQL y subidas el 22-10 (`4539965`, `4542b76`) | `alembic/versions/` |
| `modelo_datos.md` y diagrama ER al día | Habilitador | Sergio | ✅ Actualizados (decisiones del Sprint 4, diagrama y PNG) y subidos el 22-10 (`8cc29c2`, `ca2f230`) | `Base de datos/` |
| Rutas para crear y listar los horarios de un medicamento o rutina | Habilitador | Benjamín | ✅ Listas, 10 pruebas, subidas el 22-10 (`3546342`, `fd5bec6`) | `backend/app/api/routes/` |
| Tarea programada que genera las actividades con 24 a 48 h de anticipación | Habilitador | Benjamín | ✅ Lista (ciclo dentro del backend, hoy y 2 días adelante), subida el 22-10 (`09e90e6`, `9c51bcf`, `34b907b`) | `backend/app/services/` |
| Registro del dispositivo y envío de notificaciones | HU 9 | Benjamín | 🟡 Registro y avisos listos y subidos el 22-10 (`3546342`); el envío real por FCM no está hecho (notificador de log) | `backend/` |
| Motor de alertas escalonadas y consulta de alertas | HU 10 | Benjamín | ✅ Listo (19 pruebas de avisos), subido el 22-10 (`09e90e6`) | `backend/` |
| Pruebas del backend de cada ruta nueva (sin fechas fijas) | HU 9 / HU 10 | Benjamín | ✅ 29 pruebas nuevas; suite completa 148 de 148, subidas el 22-10 (`e1144e6`) | `backend/app/tests/` |
| Recepción de notificaciones y registro del dispositivo en la app | HU 9 | Matías | ⬜ Pendiente: la app consulta los avisos (`GET /alertas`) pero no recibe push ni registra el dispositivo hasta elegir FCM | `app_movil/lib/` |
| Modo simplificado del dependiente | HU 11 | Matías | 🟡 Probado en el emulador el 25-10 (`S4_06` a `S4_08`, incluida la salida con confirmación `S4_06.1`); falta aceptación del PO | `app_movil/lib/screens/` |
| Mostrar alertas recibidas en la app | HU 10 | Matías | 🟡 Pantalla Avisos probada en el emulador el 25-10 (`S4_02` a `S4_05`); niveles 1 y 2 evidenciados (`S4_04`); "confirmar detiene" evidenciado el 28-10 (`S4_05.3` a `S4_05.5`) | `app_movil/lib/` |
| Acciones de la retrospectiva del Sprint 3: "Mi perfil de salud" para cuidadores, Panel con `GET /panel?fecha=`, timeouts y los 4 avisos de `flutter analyze` | Mejora | Matías | ✅ Panel con `GET /panel` (`S4_09.2`), timeouts y mensaje de error de conexión (`S4_10`), `flutter analyze` sin avisos (`analyze.log`) y "Mi perfil de salud" del cuidador corregido el 27-10 en `home_screen.dart` (`S4_09.3`); `flutter analyze` y `flutter test` repetidos el 28-10 con ese cambio y en verde | `app_movil/lib/` |
| Pruebas de la app (`flutter test`, `flutter analyze`) y evidencia del sprint | HU 9 / HU 10 / HU 11 | Matías | 🟡 Evidencia manual lista (`Evidencia_Sprint4.md`, 10 de 10 flujos ✅); `flutter analyze` sin avisos; `flutter test` 14 de 14 pruebas en verde (7 de modelos, 1 de login, 2 de agenda y 4 de avisos; `test.log` y `S4_11`); el hash del código probado quedó en la evidencia (backend `ec20c37`, app `12fb551`). Repetidos el 28-10 tras el cambio de `home_screen.dart`: `flutter analyze` sin avisos y `flutter test` 14 de 14 | `app_movil/evidencias/evidencias Sprint 4/` |
| Checklist de aceptación del Product Owner, dentro del sprint | HU 9 / HU 10 / HU 11 | Sergio | ⬜ Pendiente: plantilla sin ejecutar (17 criterios, tres cuentas); fecha objetivo antes del 31-10 | `Base de datos/Checklist_Aceptacion_PO_Sprint4.md` |
| Retrospectiva del Sprint 4, el último día | — | Matías | 🟡 Borrador al 29-10 en `Retrospectiva_Sprint4.md`; se cierra el 31-10 con el resultado real | `Metodologia_Scrum/Sprint_4/` |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 9 | ✅ (sección 7) | 🟡 backend y emulador sí; push real pendiente | 🟡 | ⬜ |
| HU 10 | ✅ (sección 7) | 🟡 backend y emulador (niveles 1 y 2); falta la cuenta ajena | 🟡 | ⬜ |
| HU 11 | ✅ (sección 7) | 🟡 emulador sí | 🟡 | ⬜ |

## 4. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| Suites del backend existentes (119 pruebas) | Automática (backend) | ✅ pasan, dentro de las 148 |
| Pruebas nuevas de horarios, generación de actividades, notificaciones y alertas | Automática (backend) | ✅ 29 pruebas (`test_horario.py` 10 y `test_avisos.py` 19); total 148 de 148 en 199 s |
| `alembic upgrade head` desde base vacía y `downgrade` / `upgrade` de cada migración nueva | Manual (PostgreSQL) | ✅ probado en PostgreSQL 16 local (relleno de datos, ciclo `downgrade`/`upgrade`, única duplicada y cascada); repetir en Docker antes de cerrar |
| Checklist de aceptación del Product Owner con tres cuentas | Manual (Product Owner) | ⬜ |
| Flujo equivalente desde la app (notificación, alerta y modo simplificado) | Manual (emulador, Matías) | ✅ 25, 27 y 28-10: 10 de 10 flujos ✅ ("confirmar detiene" cerrado el 28-10 con plazos de prueba, `S4_05.3` a `S4_05.5`); capturas `S4_01` a `S4_10`, más `S4_11` (`flutter test`) |
| `flutter test` y `flutter analyze` | Automática (app) | ✅ `flutter analyze`: sin avisos (`analyze.log`); `flutter test`: 14 de 14 pasan (`test.log` y `S4_11`) |

Comando de las pruebas del backend: `pytest app/tests/ -v`.

## 5. Decisiones por tomar en la reunión del equipo

Lo siguiente ya está implementado como propuesta; si el equipo decide otra cosa, se ajusta.

1. **Proveedor de notificaciones push.** Sigue abierta: hay que elegir el servicio (la opción natural es Firebase Cloud Messaging) y guardar sus credenciales fuera del repositorio. Mientras tanto el backend usa un notificador de log (`NOTIFICADOR="log"`).
2. **Cómo se programa la tarea que genera actividades.** Implementado: un ciclo dentro del proceso de FastAPI cada 60 s (`TAREAS_PROGRAMADAS=true` en Docker Compose). Limitación: si se levantan varias réplicas del backend, el ciclo correría en cada una (los avisos no se duplican por la restricción única, pero conviene un solo proceso).
3. **Plazos de las alertas.** Propuesta implementada y configurable: recordatorio 10 min antes, alerta 1 a los 30 min, alerta 2 a los 60 min.
4. **Qué actividades cuentan como "importantes"** para escalar. Hoy escalan todas (medicamentos y rutinas); falta decidir si solo los medicamentos.
5. **Cómo entra el dependiente al modo simplificado.** Hoy un dependiente es un perfil de la cuenta del titular, no una cuenta propia; se implementó como un modo dentro de la misma sesión, desde el Home.
6. **Solo Sergio crea migraciones de Alembic** en este sprint, como en el Sprint 3, para mantener una única cabeza (ahora `c0d1e2f3a4b5`, con las cuatro migraciones nuevas de Sergio).
7. **Hora que muestra la pantalla Avisos.** En las capturas del 25-10 la fecha bajo cada aviso aparecía en UTC (una alerta de una actividad de las 16:30 salía como 20:00); en las del 28-10 (`S4_05.3` a `S4_05.5`) aparece en hora de Chile. Confirmar que hubo un cambio en la app y, si es así, cerrar esta decisión.
8. **Panel «de dependientes» y el titular.** El Panel lista también al titular (`S4_09.1`); decidir si se oculta o se renombra el título.
9. **Qué significa "escalar".** Hoy el nivel 2 va solo a los cuidadores con `nivel_escalamiento = 2` y no al titular ni a los de nivel 1; si nadie está en nivel 2, no llega a nadie, y el nivel 3 (aceptado por el esquema) no existe. Decidir si el titular y los cuidadores de nivel 1 también deben recibir el nivel 2, y si se implementa o se limita a 1 y 2.

## 6. Trabajo que pasa al Sprint 5

Se confirma al cierre del sprint. Lo previsto del Product Backlog: indicadores de salud, % de cumplimiento (HU 13), pulsera con Traccar y Health Connect, botón de asistencia y orientación general de IA.

Pendientes del Sprint 4 que hoy (29-10) pasarían al Sprint 5 si no se cierran antes del 31-10:

1. **Push real con FCM (HU 9):** elegir proveedor, guardar las credenciales fuera del repositorio, registrar el dispositivo desde la app y reemplazar el notificador de log (`NOTIFICADOR`).
2. **Panel:** decidir si el titular aparece en el «Panel de dependientes» (`S4_09.1`).
3. **Hora local en Avisos** (decisión 7), si no se confirma que ya está corregida.
4. **Qué actividades escalan** (decisión 4) **y a quién escala el nivel 2** (decisión 9): hoy escalan todas y el nivel 2 no llega al titular.
5. **Extras Deseables:** editar medicamentos y rutinas desde la app, y pantallas de alergias y contactos (se recortan primero).

## 7. Seguimiento de commits del sprint

Acuerdo del Sprint 3: subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint.

**Estado al 29-10:** historial verificado con `git log --since=2026-10-19`. Los commits del 19 y 20-10 son del cierre del Sprint 3 y no se cuentan aquí.

| Fecha | Qué se subió | Quién | Commits |
|---|---|---|---|
| 22-10 | Rutas de horarios, dispositivos y alertas; esquemas; configuración de plazos; routers y ciclo programado en `main.py`; generación programada y avisos escalonados | Benjamín | `3546342`, `fd5bec6`, `9c51bcf`, `34b907b`, `09e90e6` |
| 22-10 | 29 pruebas nuevas; Docker Compose, dependencias, `pytest.log` y `Contrato_API_Sprint4.md` | Benjamín | `e1144e6`, `f7f22d0` |
| 22-10 | Tablas `rutina_horario`, `alerta` y `dispositivo_push` | Sergio | `4539965`, `4542b76` |
| 22-10 | `modelo_datos.md` y diagrama ER | Sergio | `8cc29c2`, `ca2f230` |
| 25-10 | App: Avisos, modo simplificado, Panel, perfil, modelos, `api_service`, `hora.dart`, `avisos_test`; `analyze.log` y `test.log` | Matías | `e31e387`, `3216eb2`, `0b093ba`, `be93915`, `76ce2ff`, `8c4c01b`, `c8f5e24`, `2f25077`, `e5fc6e8`, `6bd2103`, `50575cf`, `0b45bda`, `ac84891`, `8a9b38a`, `8df975e` |
| 25-10 | Ajuste de una línea en `backend/app/main.py` | Matías | `ec20c37` |
| 25-10 | Evidencia, Sprint Backlog y retrospectiva (primera versión) | Matías | `ebc4d2a`, `26a340b`, `31c3353`, `c112ee8`, `7f8dbb2` |
| 27-10 | «Mi perfil de salud» del cuidador (`home_screen.dart`) y su captura; revisión del contrato; evidencia, retrospectiva y README | Matías | `12fb551`, `fd5de7b`, `ba1797c`, `88769ff`, `6f6b534`, `fb3d807`, `745a578`, `c47e142` |
| 28-10 | Capturas del paso 5 (`S4_05.3` a `S4_05.5`) y evidencia | Matías | `7eb7c18`, `583de93` |
| 29-10 | Cierre: evidencia de los flujos 5 y 9, backlog, retrospectiva, README y contrato (PR #1) | Matías | `570d030`, `af9530a` |
| — | Checklist de aceptación del Product Owner ejecutado | Sergio | ⬜ sin commits |
