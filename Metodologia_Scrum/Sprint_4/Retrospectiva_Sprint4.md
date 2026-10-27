# Retrospectiva — Sprint 4 (S11–S12)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo del sprint:** 19 al 31 de octubre de 2026
**Fecha de redacción:** *(31 de octubre de 2026, último día del sprint)* · **Borrador con el estado al 27 de octubre de 2026**
**Scrum Master:** Matías Pizarro
**Participantes:** Matías Pizarro (App móvil y Scrum Master), Benjamín Leiva (Backend), Sergio Ocares (Base de datos, IA y Product Owner)

> Borrador armado a partir del repositorio y de la evidencia del 25-10. Lo que depende de lo que pase hasta el 31-10 (aceptación del Product Owner, commits, pendientes) está marcado con ⬜ o con *(...)* y se completa el último día; las conclusiones se confirman en la reunión del equipo.

## Resultado del sprint

Historias comprometidas: 3 (HU 9, HU 10 y HU 11) más los habilitadores `RUTINA_HORARIO` y generación programada · Terminadas según la Definition of Done del equipo (integrada + probada + documentada): *(n)* de 3 al 31-10 · Aceptadas por el Product Owner: *(n)* de 17 criterios (`Checklist_Aceptacion_PO_Sprint4.md`, sin ejecutar al 27-10). Detalle en `Sprint_Backlog_Sprint4.md`.

Estado al 27-10: las tres historias están construidas y probadas en backend y emulador, pero ninguna se da por terminada hasta registrar los commits y pasar la aceptación del PO. **HU 9 queda parcial por diseño:** el aviso llega a la pantalla Avisos, pero el push al celular (FCM) no está implementado.

- **Base de datos:** tablas `rutina_horario`, `alerta` y `dispositivo_push`, columna `hora` y estados `omitida` y `vencida` en `actividad`; cuatro migraciones nuevas con cabeza única `c0d1e2f3a4b5`, probadas en PostgreSQL 16 (relleno de datos, `downgrade`/`upgrade` y cascada); `modelo_datos.md` y diagrama al día. *(fecha de subida: ...)*
- **Backend:** rutas de horarios, tarea programada que genera actividades (hoy y 2 días adelante), recordatorio 10 min antes, alertas de nivel 1 (30 min) y 2 (60 min), `GET /alertas`, `POST /alertas/{id}/leida` y `POST /dispositivos`; 148 de 148 pruebas pasan (29 nuevas). *(fecha de subida: ...)*
- **App:** pantalla Avisos con recordatorios y alertas, modo simplificado del dependiente, Panel con `GET /panel`, timeouts y mensaje de error de conexión; `flutter analyze` sin avisos y `flutter test` 14 de 14 (25-10); prueba manual con 10 flujos (8 ✅, 2 en parte) y 31 capturas `S4_*`. Evidencia en `Evidencia_Sprint4.md`.

## ¿Qué funcionó bien este sprint?

- **El contrato de API se escribió con las rutas reales** (`Contrato_API_Sprint4.md`), así que la app pudo consumir horarios, avisos y alertas sin los desajustes de nombres del Sprint 3.
- **La lógica de avisos quedó cubierta por pruebas automáticas** (19 de avisos y 10 de horarios): plazos, destinatarios, no repetir avisos, confirmar detiene el escalamiento, pérdida de acceso y fallo del notificador. Los criterios que la app no puede mostrar por sí sola tienen respaldo en el backend.
- **Los cambios de base de datos se probaron contra PostgreSQL**, no solo contra SQLite, y se mantuvo una sola persona creando migraciones (cabeza única).
- **La evidencia mejoró:** cada captura lleva una frase con el criterio que respalda, y se distinguió con honestidad lo que quedó en parte (`🟡`) y lo que no se resolvió (`❌`).
- **Se cerraron tres acciones de la retrospectiva anterior:** Panel con una sola llamada (`GET /panel`), timeouts con mensaje de error de red (`S4_10`) y `flutter analyze` sin avisos.
- **El sistema no asume una emergencia:** el texto de las alertas informa que la actividad no fue confirmada (`S4_04`).

## ¿Qué no funcionó o nos costó más de lo esperado?

- **El push real quedó sin hacer.** La decisión del proveedor (FCM) y sus credenciales se siguió posponiendo; la app ni siquiera registra el dispositivo. *Aprendizaje:* decidir los servicios externos en la planificación del sprint, no durante la implementación.
- **"Mi perfil de salud" para cuentas de cuidador sigue mal** (`S4_09.3`): es una acción del Sprint 3 que se arrastró sin resolverse.
- **El Sprint Backlog 4 se publicó el 21-10**, dos días después de empezar el sprint, a pesar de la acción acordada.
- **La evidencia necesitó una revisión de consistencia:** varios nombres de captura citados en `Evidencia_Sprint4.md` no existían en la carpeta y otras capturas no estaban referenciadas (`S4_06.1`, `S4_04.6`, `S4_05.2`). *Aprendizaje:* verificar la lista de archivos contra el texto antes de cerrar.
- **"Confirmar detiene el escalamiento" quedó solo en parte en la app:** las capturas se tomaron antes del plazo del nivel 2 y no prueban la ausencia de una alerta nueva (lo cubre una prueba del backend).
- **Detalles de experiencia sin cerrar:** la fecha de los avisos parece mostrarse en UTC y el Panel de dependientes lista al titular.
- **La configuración nueva no está en `.env.example`:** variables como `TAREAS_PROGRAMADAS`, `ZONA_HORARIA`, los plazos de alerta y `NOTIFICADOR` solo se ven en `docker-compose.yml` y `config.py`.
- *(Completar el 31-10: cierre del checklist del PO, distribución de los commits en el sprint y lo que no alcanzó.)*

## Seguimiento de las acciones de la retrospectiva del Sprint 3

| Acción acordada | Estado |
|---|---|
| Mantener `flutter analyze` y `flutter test` en verde antes de cada commit a `main` | ✅ al 25-10: `flutter analyze` sin avisos y `flutter test` 14 de 14 (`analyze.log`, `test.log`, `S4_11`); repetir antes del último commit |
| Que las pruebas del backend no usen fechas fijas | ✅ Las 29 pruebas nuevas usan fechas relativas; 148 de 148 pasan (`pytest.log`) |
| Subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint | ⬜ Verificar con `git log` en la revisión del miércoles 28-10 |
| Publicar el Sprint Backlog 4 el primer día del sprint | ❌ Se publicó el 21-10 (el sprint empezó el 19-10) |
| Revisar cada integración app-backend contra `/docs` de FastAPI | 🟡 El contrato se redactó con las rutas reales y la app se probó contra el backend; falta la revisión escrita de Matías al contrato |
| Corregir "Mi perfil de salud" para cuentas de cuidador | ❌ Sin resolver al 27-10: la cuenta cuidador sigue viendo el perfil titular de otra persona (`S4_09.3`) |
| Pasar el Panel a `GET /panel?fecha=`; agregar timeouts y manejo de errores de red | ✅ Panel con `GET /panel` (`S4_09.2`) y mensaje de error de conexión (`S4_10`) |
| Cambiar `value` por `initialValue` en los 4 avisos de `flutter analyze` | ✅ `analyze.log` sin avisos |
| Cerrar el checklist del Product Owner dentro del sprint, no después | ⬜ En curso: plantilla sin ejecutar al 27-10; objetivo antes del 31-10 |

## ¿Qué vamos a cambiar o probar distinto en el próximo sprint?

Propuesta para confirmar en la reunión del equipo.

| Acción | Responsable | Cuándo |
|---|---|---|
| Decidir los servicios externos (FCM, proveedor de IA, Traccar) y sus credenciales en la planificación, no durante el desarrollo | Todos / Scrum Master | Planificación del Sprint 5 |
| Resolver "Mi perfil de salud" del cuidador como primera tarea de la app, antes de historias nuevas | Matías | Primera semana del Sprint 5 |
| Publicar el Sprint Backlog 5 el primer día del sprint | Scrum Master | 2-11 *(confirmar fecha de inicio)* |
| Ejecutar el checklist del Product Owner a mitad de sprint (con las partes ya terminadas) y completarlo al cierre | Sergio | Mitad y cierre del sprint |
| Antes de cerrar la evidencia, verificar que cada captura citada exista en la carpeta y pegar el hash del commit | Matías | Último día de cada sprint |
| Agregar las variables nuevas de configuración a `.env.example` | Benjamín | Antes del cierre del Sprint 4 |
| Mostrar la fecha de los avisos en hora de Chile | Matías | Sprint 5 |
| Subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint | Todos / Scrum Master | Todo el Sprint 5 |
