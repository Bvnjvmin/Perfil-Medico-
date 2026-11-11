# Retrospectiva — Sprint 4 (S11–S12)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo del sprint:** 19 al 31 de octubre de 2026
**Fecha de redacción:** 11 de noviembre de 2026 (versión final) · **Estado al** 8 de noviembre de 2026 (aceptación del Product Owner), con el código y la evidencia del repositorio revisados el 10-11
**Scrum Master:** Matías Pizarro
**Participantes:** Matías Pizarro (App móvil y Scrum Master), Benjamín Leiva (Backend), Sergio Ocares (Base de datos, IA y Product Owner)

> Versión final armada a partir del repositorio, de la evidencia del sprint y del checklist del Product Owner del 8-11. Reemplaza al borrador del 29-10. Las conclusiones y las acciones se confirman en la reunión del equipo.

## Resultado del sprint

Historias comprometidas: 3 (HU 9, HU 10 y HU 11) más los habilitadores `RUTINA_HORARIO` y generación programada · Terminadas según la Definition of Done del equipo (integrada + probada + documentada): 2 de 3 (HU 10 y HU 11) · Aceptadas por el Product Owner: 17 de 17 criterios al 8-11 (`Checklist_Aceptacion_PO_Sprint4.md`, ejecutado después del cierre del sprint: al 31-10 ninguna historia estaba aceptada todavía). Detalle en `Sprint_Backlog_Sprint4.md`.

**Estado final:** las tres historias quedaron construidas, probadas en backend y emulador e integradas al repositorio (commits en la sección 7 del Sprint Backlog). **HU 10 y HU 11 están terminadas:** pasaron la aceptación del Product Owner el 8-11 (criterios 9 a 13 y 14 a 17) y tienen evidencia completa. **HU 9 queda parcial por diseño:** el recordatorio se crea, llega a la pantalla Avisos y abre la Agenda (criterios 5 a 8 aceptados, el 6 y el 8 como parciales), pero el push al celular (FCM) no está implementado y la app no registra el dispositivo; ese trabajo pasa al Sprint 5. Los habilitadores (`RUTINA_HORARIO` y generación programada) están terminados y aceptados (criterios 1 a 4; el 2, en parte).

- **Base de datos:** tablas `rutina_horario`, `alerta` y `dispositivo_push`, columna `hora` y estados `omitida` y `vencida` en `actividad`; cuatro migraciones nuevas con cabeza única `c0d1e2f3a4b5`, probadas en PostgreSQL 16 (relleno de datos, `downgrade`/`upgrade` y cascada); `modelo_datos.md` y diagrama al día. Subido el 22-10 (`4539965`, `4542b76`, `8cc29c2`, `ca2f230`).
- **Backend:** rutas de horarios, tarea programada que genera actividades (hoy y 2 días adelante), recordatorio 10 min antes, alertas de nivel 1 (30 min) y 2 (60 min), `GET /alertas`, `POST /alertas/{id}/leida` y `POST /dispositivos`; 148 de 148 pruebas pasan (29 nuevas). Subido el 22-10 (`3546342` a `f7f22d0`, ver sección 7 del Sprint Backlog).
- **App:** pantalla Avisos con recordatorios y alertas, modo simplificado del dependiente, Panel con `GET /panel`, timeouts y mensaje de error de conexión; `flutter analyze` sin avisos y `flutter test` 14 de 14 (28-10); prueba manual con 10 flujos (10 ✅) y 34 capturas `S4_*`. Evidencia en `Evidencia_Sprint4.md`.

## ¿Qué funcionó bien este sprint?

- **El contrato de API se escribió con las rutas reales** (`Contrato_API_Sprint4.md`), así que la app pudo consumir horarios, avisos y alertas sin los desajustes de nombres del Sprint 3.
- **La lógica de avisos quedó cubierta por pruebas automáticas** (19 de avisos y 10 de horarios): plazos, destinatarios, no repetir avisos, confirmar detiene el escalamiento, pérdida de acceso y fallo del notificador. Los criterios que la app no puede mostrar por sí sola tienen respaldo en el backend.
- **Los cambios de base de datos se probaron contra PostgreSQL**, no solo contra SQLite, y se mantuvo una sola persona creando migraciones (cabeza única).
- **La evidencia mejoró:** cada captura lleva una frase con el criterio que respalda, y se distinguió con honestidad lo que quedó en parte (`🟡`) y lo que no se resolvió (`❌`).
- **Se cerraron cuatro acciones de la retrospectiva anterior:** Panel con una sola llamada (`GET /panel`), timeouts con mensaje de error de red (`S4_10`), `flutter analyze` sin avisos y «Mi perfil de salud» del cuidador (corregido el 27-10: ya no muestra el perfil titular de otra persona, `S4_09.3`).
- **El sistema no asume una emergencia:** el texto de las alertas informa que la actividad no fue confirmada (`S4_04`).
- **La aceptación del Product Owner se hizo desde afuera y con honestidad sobre sus límites:** tres cuentas (titular, cuidador y ajena) por API en Swagger, con los criterios 2, 6 y 8 anotados como parciales y los intentos no válidos de los criterios 7 y 11 registrados en vez de borrados (`Checklist_Aceptacion_PO_Sprint4.md`).

## ¿Qué no funcionó o nos costó más de lo esperado?

- **El push real quedó sin hacer.** La decisión del proveedor (FCM) y sus credenciales se siguió posponiendo; la app ni siquiera registra el dispositivo. Al 10-11 el repositorio ya trae un `NotificadorFCM` en el backend (apagado por defecto y probado solo con respuestas simuladas, sin proyecto de Firebase ni app que envíe el token; ver `docs/Notas_FCM_Sprint5.md`); eso es trabajo del Sprint 5 y no cambia el estado de HU 9 en este sprint. *Aprendizaje:* decidir los servicios externos en la planificación del sprint, no durante la implementación.
- **El Sprint Backlog 4 llegó al repositorio el 25-10** (`31c3353`), seis días después de empezar el sprint, a pesar de la acción acordada de publicarlo el primer día.
- **La evidencia necesitó una revisión de consistencia:** varios nombres de captura citados en `Evidencia_Sprint4.md` no existían en la carpeta y otras capturas no estaban referenciadas (`S4_06.1`, `S4_04.6`, `S4_05.2`). Al cierre se repitió la comprobación (10-11): las 34 capturas `S4_*` de la carpeta están citadas en `Evidencia_Sprint4.md` y todos los nombres citados existen. *Aprendizaje:* verificar la lista de archivos contra el texto antes de cerrar.
- **"Confirmar detiene el escalamiento" tardó en cerrarse en la app:** las capturas del 25-10 se tomaron antes del plazo del nivel 2 y una del 27-10 se descartó por no coincidir con la salida de la app. Se cerró el 28-10 con plazos de prueba de 1 y 5 minutos (`S4_05.3` a `S4_05.5`). *Aprendizaje:* preparar desde el inicio una forma de probar con plazos cortos los flujos que dependen de esperas largas.
- **El escalamiento no escala para todos:** el nivel 2 solo llega a los cuidadores configurados en nivel 2; el titular y los de nivel 1 solo ven el nivel 1, aunque pase el tiempo. Cumple el criterio escrito y el Product Owner lo aceptó el 8-11 (criterio 10), pero la observación 3 del contrato (a quién llega el nivel 2) sigue abierta (decisión 9 del backlog). Al 10-11 el backend ya tiene la opción `ALERTA_NIVEL_2_INCLUYE_TITULAR` (apagada por defecto, con prueba en `test_nivel2_titular.py`); el nivel 3 sigue sin implementarse. Pasa al Sprint 5.
- **Un detalle de experiencia quedó sin cerrar:** el Panel de dependientes sigue listando al titular (`S4_09.1`; decisión 8, pasa al Sprint 5). La otra duda, la hora de los avisos, quedó resuelta: no es un defecto de la app ni del backend. La hora que muestra la pantalla Avisos depende de la zona horaria del dispositivo: la app convierte `creada_en` (que el backend envía en UTC) con `.toLocal()` en `alertas_screen.dart`. En las pruebas y capturas el emulador de Android Studio quedó configurado en la zona de Santiago de Chile, por eso se ven en hora de Chile.
- **La configuración nueva no estaba en `.env.example` durante el desarrollo:** variables como `TAREAS_PROGRAMADAS`, `ZONA_HORARIA`, los plazos de alerta y `NOTIFICADOR` solo se veían en `docker-compose.yml` y `config.py`. Al 10-11 ya figuran en `.env.example` con su explicación; no se revisó en el historial de git cuándo se agregaron.
- **Los commits llegaron concentrados.** El backend y la base de datos se subieron el 22-10 (Benjamín y Sergio) y casi toda la app el 25-10 (Matías); hubo commits en cinco días distintos del sprint (22, 25, 27, 28 y 29-10). El acuerdo se cumplió a nivel de equipo, pero no por persona. *Aprendizaje:* subir avances parciales durante la semana, no al final.
- **El checklist del Product Owner se cerró tarde.** La plantilla seguía sin ejecutar al 31-10 y se completó en varias sesiones (22 y 23-10, 2-11 y 8-11). Los criterios 7 y 11 (una actividad confirmada no genera recordatorio y confirmar detiene el escalamiento) no se pudieron probar el 2-11: los plazos cortos no se aplicaron y las confirmaciones llegaron después de cada plazo. Se probaron el 8-11 con plazos de 2, 3 y 6 minutos y, para el criterio 11, con el plazo del nivel 2 subido a 15 minutos para dejar margen entre el nivel 1 y el nivel 2. *Aprendizaje:* dejar documentada una configuración de prueba con plazos cortos (los plazos se bajan con las variables de `.env.example`; el `docker-compose.prueba.yml` fue solo un archivo temporal para tomar las capturas) y probar esos flujos con margen suficiente entre cada plazo.
- **La retrospectiva final se cerró tarde.** Estaba prevista para el último día del sprint (31-10) y el borrador quedó en el estado del 29-10; la versión final se cerró el 11-11, once días después, cuando ya estaba hecha la aceptación del Product Owner (8-11). *Aprendizaje:* dejar agendado el cierre del Sprint Backlog y de la retrospectiva para el último día del sprint, con el resultado real, y no esperar a que termine la aceptación del Product Owner para cerrarlos (se puede anotar «aceptación pendiente»).

## Seguimiento de las acciones de la retrospectiva del Sprint 3

| Acción acordada | Estado |
|---|---|
| Mantener `flutter analyze` y `flutter test` en verde antes de cada commit a `main` | ✅ `flutter analyze` sin avisos y `flutter test` 14 de 14 (`analyze.log`, `test.log`, `S4_11`); repetidos el 28-10, después del último cambio de código de la app (27-10) |
| Que las pruebas del backend no usen fechas fijas | ✅ Las 29 pruebas nuevas usan fechas relativas; 148 de 148 pasan (`pytest.log`) |
| Subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint | 🟡 Verificado con `git log` el 29-10: hubo commits en cinco días distintos (22, 25, 27, 28 y 29-10), pero por persona el código se subió casi todo en un solo día (Benjamín y Sergio el 22-10; la app de Matías el 25-10) |
| Publicar el Sprint Backlog 4 el primer día del sprint | ❌ Se subió al repositorio el 25-10 (`31c3353`); el sprint empezó el 19-10 |
| Revisar cada integración app-backend contra `/docs` de FastAPI | 🟡 Verificado el 27-10 contra el código: todas las rutas del contrato existen en el backend y las 5 que usa la app (`GET /perfiles/{id}/actividades`, `POST /actividades/{id}/confirmar` y `/desconfirmar`, `GET /panel`, `GET /alertas`, `POST /alertas/{id}/leida`) coinciden. La app aún no consume `/dispositivos`, los horarios ni los campos `recibe_alertas` y `nivel_escalamiento`. La revisión escrita de Matías está en la sección 9 del contrato (27-10); Sergio dio su visto bueno el 8-11 con las observaciones 2 y 3 abiertas: la 2 (hora de los avisos) quedó resuelta el 10-11 y la 3 (a quién llega el nivel 2) pasa al Sprint 5 |
| Corregir "Mi perfil de salud" para cuentas de cuidador | ✅ Corregido el 27-10 en `home_screen.dart`: la cuenta cuidador sin perfil propio ve «Aún no lo completas» (`S4_09.3`); `flutter analyze` y `flutter test` repetidos el 28-10 y en verde |
| Pasar el Panel a `GET /panel?fecha=`; agregar timeouts y manejo de errores de red | ✅ Panel con `GET /panel` (`S4_09.2`) y mensaje de error de conexión (`S4_10`) |
| Cambiar `value` por `initialValue` en los 4 avisos de `flutter analyze` | ✅ `analyze.log` sin avisos |
| Cerrar el checklist del Product Owner dentro del sprint, no después | ❌ No se cumplió: el checklist se cerró el 8-11, ocho días después del cierre del sprint (17 de 17) |

## ¿Qué vamos a cambiar o probar distinto en el próximo sprint?

Propuesta para confirmar en la reunión del equipo. La última columna dice cómo estaba cada acción al 11-11; las que son de proceso del Sprint 5 se evalúan en su retrospectiva.

| Acción | Responsable | Cuándo | Estado al 11-11 |
|---|---|---|---|
| Decidir los servicios externos (FCM, proveedor de IA, Traccar) y sus credenciales en la planificación, no durante el desarrollo | Todos / Scrum Master | Planificación del Sprint 5 | 🟡 Traccar y la IA ya tienen configuración en el repositorio; FCM sigue sin proyecto de Firebase ni credenciales (`Notas_FCM_Sprint5.md`) |
| Publicar el Sprint Backlog 5 el primer día del sprint | Scrum Master | 2-11 (inicio planificado del Sprint 5) | Se evalúa en la retrospectiva del Sprint 5 |
| Ejecutar el checklist del Product Owner a mitad de sprint (con las partes ya terminadas) y completarlo al cierre | Sergio | Mitad y cierre del sprint | Se evalúa en la retrospectiva del Sprint 5 |
| Antes de cerrar la evidencia, verificar que cada captura citada exista en la carpeta y pegar el hash del commit | Matías | Último día de cada sprint | ✅ Hecho para el Sprint 4: 34 de 34 capturas existen y están citadas; hashes del código probado en la evidencia (`ec20c37` y `12fb551`) |
| Agregar las variables nuevas de configuración a `.env.example` | Benjamín | Antes del cierre del Sprint 4 | ✅ Hecho (verificado el 10-11) |
| Dejar documentada una forma de probar las alertas con plazos cortos | Benjamín / Matías | Sprint 5 | ✅ Cubierta: `.env.example` explica cómo bajar `ALERTA_PLAZO_1_MINUTOS` y `ALERTA_PLAZO_2_MINUTOS`; el `docker-compose.prueba.yml` fue un archivo temporal solo para las capturas del 28-10 y no se sube |
| Mostrar la fecha de los avisos en hora de Chile | Matías | Sprint 5 | ✅ Ya resuelta: la app muestra la hora de la zona horaria del dispositivo (`.toLocal()`); el emulador de las pruebas estaba en Santiago de Chile; no queda trabajo |
| Subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint | Todos / Scrum Master | Todo el Sprint 5 | Se evalúa en la retrospectiva del Sprint 5 |
| Cerrar el Sprint Backlog y la retrospectiva el último día del sprint, con el resultado real (se puede anotar «aceptación pendiente») | Scrum Master | Último día de cada sprint | Se evalúa en la retrospectiva del Sprint 5 |

## Qué pasa al Sprint 5

Los pendientes del Sprint 4 que pasan al Sprint 5 están en la sección 6 de `Sprint_Backlog_Sprint4.md`: push real con FCM (HU 9), Panel con el titular, a quién llega el nivel 2 y qué actividades escalan, y los extras Deseables.
