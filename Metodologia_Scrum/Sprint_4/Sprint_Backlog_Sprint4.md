# Sprint Backlog — Sprint 4 (S11–S12)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 19 al 31 de octubre de 2026 (semanas 11 y 12 del Cronograma)
**Publicado:** 21 de octubre de 2026 · **Última actualización:** 25 de octubre de 2026 · **Estado del sprint:** en curso; el backend está probado (148 pruebas) y la app se probó en el emulador el 25-10 (10 flujos, capturas `S4_01` a `S4_10`, ver `Evidencia_Sprint4.md`); faltan registrar los commits, la aceptación del Product Owner, el push real (FCM), un par de mejoras y la retrospectiva
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
- **Estado:** 🟡 Backend probado (escalamiento, destinatarios, no repetir avisos, `GET /alertas`). En el emulador (25-10) las alertas de nivel 1 llegan al cuidador y al titular con un mensaje que no asume una emergencia (`S4_04`); el nivel 2 llega al cuidador configurado en nivel 2 (`S4_04.5`); falta la cuenta ajena y la aceptación del PO.

### HU 11 — Interfaz simplificada para el perfil dependiente
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación (propuestos):**
  - Existe un modo simplificado con botones grandes y texto grande que muestra solo las actividades de hoy del perfil.
  - Confirmar una actividad toma un solo toque, sin menús intermedios.
  - El modo simplificado no permite editar ni borrar datos.
  - Se puede entrar y salir del modo desde la cuenta del titular (la salida pide confirmación).
- **Estado:** 🟡 Probado en el emulador (25-10): solo actividades de hoy, botones grandes, confirmación en un toque guardada en el servidor y sin opciones de editar o borrar (capturas `S4_06` a `S4_08`). Falta la captura de la salida con confirmación y la aceptación del PO.

### Habilitadores técnicos (del Cronograma, semana 11)
`RUTINA_HORARIO` y generación programada de actividades: son la base de HU 9 y HU 10, porque las notificaciones y las alertas necesitan saber de antemano qué actividad toca y a qué hora. **Estado:** 🟡 tabla, rutas de horarios y tarea programada listas y probadas (backend y PostgreSQL); falta subirlas.

### Extras (Deseable)
Editar medicamentos y rutinas desde la app, y pantallas de alergias y contactos. Son lo primero que se recorta.

## 2. Tareas técnicas del sprint

| Tarea | Historia | Responsable | Estado | Dónde |
|---|---|---|---|---|
| Contrato de API del sprint (rutas, cuerpos y errores) acordado con la app **antes** de implementar | HU 9 / HU 10 | Benjamín | 🟡 Redactado con las rutas reales (`Contrato_API_Sprint4.md`); falta que Matías lo revise | `backend/` |
| Migración y modelo de `RUTINA_HORARIO` | Habilitador | Sergio | 🟡 Listo y probado en PostgreSQL; falta subir | `alembic/versions/`, `models/` |
| Migraciones de `alerta` y de dispositivos para notificaciones; `hora` y estados `omitida` y `vencida` de `actividad` | HU 9 / HU 10 | Sergio | 🟡 Listas y probadas en PostgreSQL; falta subir | `alembic/versions/` |
| `modelo_datos.md` y diagrama ER al día | Habilitador | Sergio | 🟡 Actualizados (decisiones del Sprint 4, diagrama y PNG); falta subir | `Base de datos/` |
| Rutas para crear y listar los horarios de un medicamento o rutina | Habilitador | Benjamín | 🟡 Listas, 10 pruebas; falta subir | `backend/app/api/routes/` |
| Tarea programada que genera las actividades con 24 a 48 h de anticipación | Habilitador | Benjamín | 🟡 Lista (ciclo dentro del backend, hoy y 2 días adelante); falta subir | `backend/app/services/` |
| Registro del dispositivo y envío de notificaciones | HU 9 | Benjamín | 🟡 Registro y avisos listos; el envío real por FCM no está hecho (notificador de log) | `backend/` |
| Motor de alertas escalonadas y consulta de alertas | HU 10 | Benjamín | 🟡 Listo (19 pruebas de avisos); falta subir | `backend/` |
| Pruebas del backend de cada ruta nueva (sin fechas fijas) | HU 9 / HU 10 | Benjamín | ✅ 29 pruebas nuevas; suite completa 148 de 148 (21-10) | `backend/app/tests/` |
| Recepción de notificaciones y registro del dispositivo en la app | HU 9 | Matías | ⬜ Pendiente: la app consulta los avisos (`GET /alertas`) pero no recibe push ni registra el dispositivo hasta elegir FCM | `app_movil/lib/` |
| Modo simplificado del dependiente | HU 11 | Matías | 🟡 Probado en el emulador el 25-10 (`S4_06` a `S4_08`); falta aceptación del PO | `app_movil/lib/screens/` |
| Mostrar alertas recibidas en la app | HU 10 | Matías | 🟡 Pantalla Avisos probada en el emulador el 25-10 (`S4_02` a `S4_05`); niveles 1 y 2 evidenciados (`S4_04`) | `app_movil/lib/` |
| Acciones de la retrospectiva del Sprint 3: "Mi perfil de salud" para cuidadores, Panel con `GET /panel?fecha=`, timeouts y los 4 avisos de `flutter analyze` | Mejora | Matías | 🟡 Panel con `GET /panel` ✅ (`S4_09.2`), timeouts y mensaje de error de conexión ✅ (`S4_10`), `flutter analyze` sin avisos ✅ (`analyze.log`); "Mi perfil de salud" para cuidadores ❌ sigue mostrando el titular ajeno (`S4_09.3`) | `app_movil/lib/` |
| Pruebas de la app (`flutter test`, `flutter analyze`) y evidencia del sprint | HU 9 / HU 10 / HU 11 | Matías | 🟡 Evidencia manual lista (`Evidencia_Sprint4.md`, 8 de 10 flujos ✅ y 2 en parte); `flutter analyze` sin avisos; `flutter test` 14 de 14 pruebas en verde (7 de modelos, 1 de login, 2 de agenda y 4 de avisos; `test.log` y `S4_11`) | `app_movil/evidencias/evidencias Sprint 4/` |
| Checklist de aceptación del Product Owner, dentro del sprint | HU 9 / HU 10 / HU 11 | Sergio | ⬜ Pendiente | `Base de datos/Checklist_Aceptacion_PO_Sprint4.md` |
| Retrospectiva del Sprint 4, el último día | — | Matías | ⬜ Pendiente (plantilla en `Retrospectiva_Sprint4.md`) | `Metodologia_Scrum/Sprint_4/` |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 9 | ⬜ (falta registrar commits) | 🟡 backend y emulador sí; push real pendiente | 🟡 | ⬜ |
| HU 10 | ⬜ (falta registrar commits) | 🟡 backend y emulador (niveles 1 y 2); falta la cuenta ajena | 🟡 | ⬜ |
| HU 11 | ⬜ (falta registrar commits) | 🟡 emulador sí | 🟡 | ⬜ |

## 4. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| Suites del backend existentes (119 pruebas) | Automática (backend) | ✅ pasan, dentro de las 148 |
| Pruebas nuevas de horarios, generación de actividades, notificaciones y alertas | Automática (backend) | ✅ 29 pruebas (`test_horario.py` 10 y `test_avisos.py` 19); total 148 de 148 en 199 s |
| `alembic upgrade head` desde base vacía y `downgrade` / `upgrade` de cada migración nueva | Manual (PostgreSQL) | ✅ probado en PostgreSQL 16 local (relleno de datos, ciclo `downgrade`/`upgrade`, única duplicada y cascada); repetir en Docker antes de cerrar |
| Checklist de aceptación del Product Owner con tres cuentas | Manual (Product Owner) | ⬜ |
| Flujo equivalente desde la app (notificación, alerta y modo simplificado) | Manual (emulador, Matías) | 🟡 25-10: 8 de 10 flujos ✅, 2 en parte (confirmar detiene la alerta; "Mi perfil de salud" del cuidador); capturas `S4_01` a `S4_10` |
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

## 6. Trabajo que pasa al Sprint 5

Se completa al cierre del sprint. Previsto: indicadores de salud, % de cumplimiento, pulsera con Traccar y Health Connect, botón de asistencia y orientación general de IA. Lo que no alcance del Sprint 4 entra aquí o se recorta.

## 7. Seguimiento de commits del sprint

Se completa durante el sprint, con la fecha y el commit de cada avance. Acuerdo del Sprint 3: subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint (miércoles 28-10).
