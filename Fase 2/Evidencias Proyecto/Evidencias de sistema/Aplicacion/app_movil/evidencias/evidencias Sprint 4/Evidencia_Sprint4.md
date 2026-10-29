# Evidencia de Pruebas — Sprint 4 (HU 9, HU 10 y HU 11)

**Rol:** Matías Pizarro (App Móvil y Scrum Master)
**Periodo:** 19 al 31 de octubre de 2026 · **Pruebas del** 25 de octubre de 2026 (los flujos 5 y 9 se repitieron el 27 y el 28-10) · **Última actualización:** 28 de octubre de 2026
**Entorno:** emulador Android (app Flutter en modo debug) conectado al backend local con Docker Compose (servicios `api-1` y `db-1`, PostgreSQL 16); commit del backend: *(pegar el hash con `git rev-parse --short HEAD` antes de entregar)*
**Cuentas usadas:** una cuenta titular y una cuenta cuidador. Perfiles de prueba: *Marty Gallina Mcfly* (titular) y *Dr. Emmett Brown* (dependiente, adulto mayor).

> Las capturas de este sprint están en esta misma carpeta, con el nombre `S4_NN_...png`. Cada una lleva abajo una frase que dice qué criterio respalda. Las rutas del backend (horarios, dispositivos, vínculos de cuidador) se probaron desde `/docs` de FastAPI; el resto, desde la app en el emulador. Los números de criterio son los de `Checklist_Aceptacion_PO_Sprint4.md`.

## 1. Validación automatizada

| Comando | Resultado | Evidencia |
| :--- | :--- | :--- |
| `flutter analyze` | No issues found (sin avisos ni errores), corrido el 28-10 con el cambio de `home_screen.dart` incluido (6,8 s) | `app_movil/analyze.log` |
| `flutter test` | 14 de 14 pruebas pasan, corrida del 28-10 (7 de modelos, 1 de login, 2 de agenda y 4 de avisos) | `app_movil/test.log` y `S4_11_flutter_test_por_archivo.png` |
| `pytest` (backend) | 148 pruebas pasan en 199 s (119 anteriores + 29 nuevas: 10 de horarios y 19 de avisos) | `backend/pytest.log` |

Pruebas nuevas de la app en este sprint: `test/services/avisos_test.dart` (modelo `Alerta`, estado `vencida`, `AvancePerfil.desdePanel`) y `test/services/agenda_test.dart`.

Pruebas del backend que respaldan criterios que la app no puede mostrar por sí sola: `test_confirmar_detiene_el_escalamiento` (criterio 11), `test_la_alerta_escala_al_nivel_2_solo_para_quien_corresponde` (criterio 10), `test_quien_pierde_el_acceso_deja_de_ver_los_avisos` y `test_cada_alerta_queda_registrada_y_se_puede_consultar` (criterio 12) y `test_una_actividad_confirmada_no_genera_recordatorio` (criterio 7), todas en `test_avisos.py`.

Nota: `analyze.log` y `test.log` se repitieron el 28-10 tras el cambio de `home_screen.dart` del 27-10 (paso 9). La captura `S4_11` es del 25-10; el resultado (14 de 14) es el mismo. El nombre de una prueba con tilde puede verse con caracteres cambiados en `test.log` por la codificación de la consola de PowerShell.

Límite conocido: la app no recibe notificaciones push ni registra el dispositivo (falta elegir FCM); los avisos se ven en la pantalla Avisos.

## 2. Flujos funcionales en el emulador

Leyenda: ✅ cumplido · 🟡 cumplido en parte · ❌ no cumplido (mejora pendiente).

| Paso | Historia | Qué se hizo en la App | Resultado esperado | Capturas | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | HU 9 | Se creó un horario a las 14:57 para un medicamento (`POST /medicamentos/{id}/horarios`, desde `/docs`). | La agenda muestra la actividad a esa hora. | `S4_01.1`, `S4_01.2` | ✅ |
| 2 | HU 9 | Se creó un medicamento con hora de inicio 20:15 y se registró un dispositivo (`POST /dispositivos`, desde `/docs`); se esperó el recordatorio y se abrió Avisos (campana del Home). | El backend envía el aviso al notificador y aparece el recordatorio sin leer. | `S4_02.0` (dos capturas), `S4_02`, `S4_02.1`, `S4_02.2` | ✅ |
| 3 | HU 9 | Se tocó el aviso. | Se marca leído y abre la Agenda del perfil. | `S4_03.1`, `S4_03.2` | ✅ |
| 4 | HU 10 | Se dejaron actividades sin confirmar y se entró con la cuenta del cuidador y con la del titular; con `PUT /perfiles/{id}/cuidadores/{vínculo}` se probó al cuidador con `nivel_escalamiento = 1` y luego con `2`, y se volvió a abrir Avisos. | El titular y el cuidador en nivel 1 ven la alerta de nivel 1; al pasar el segundo plazo, la de nivel 2 llega solo al cuidador configurado en nivel 2 (que no recibe la de nivel 1). El titular nunca recibe la de nivel 2. | `S4_04.1`, `S4_04.2`, `S4_04.3` (dos), `S4_04.4`, `S4_04.5`, `S4_04.6` (dos) | ✅ |
| 5 | HU 10 | En el perfil de Dr. Emmett Brown se crearon dos medicamentos con la misma hora (03:42) y plazos de alerta de prueba de 1 y 5 minutos. Con la cuenta titular se confirmó «Prueba confirmada» después de la alerta de nivel 1 y «Prueba pendiente» se dejó sin confirmar. | Ambas reciben el nivel 1; solo la no confirmada recibe el nivel 2 (en la cuenta de Sergio, cuidador en nivel 2). | `S4_05.3`, `S4_05.4`, `S4_05.5` (antecedentes del 25-10: `S4_05.1`, `S4_05.2.1`, `S4_05.2`) | ✅ |
| 6 | HU 11 | Se entró al modo simplificado de un dependiente y se tocó el icono de salir. | Solo actividades de hoy, botones grandes; la salida pide confirmación. | `S4_06`, `S4_06.1` | ✅ |
| 7 | HU 11 | Se confirmó una actividad con un toque. | El estado se guarda en el servidor. | `S4_07.1`, `S4_07.2` | ✅ |
| 8 | HU 11 | Se buscó editar o borrar desde el modo simplificado; también se abrió un perfil de solo lectura. | No hay opción de editar ni borrar. | `S4_08.1`, `S4_08.3` | ✅ |
| 9 | Mejora | Panel con `GET /panel?fecha=` (una sola llamada); "Mi perfil de salud" con cuenta de cuidador. | Datos correctos y sin mostrar el titular ajeno. | `S4_09.1`, `S4_09.2`, `S4_09.3` | ✅ |
| 10 | Mejora | Se cortó el backend y se abrió la agenda. | Mensaje claro de conexión, sin quedarse cargando. | `S4_10` | ✅ |

**Resultado:** 10 de 10 flujos ✅. El paso 5 pasó a ✅ el 28-10 al repetirse con plazos de prueba (`S4_05.3` a `S4_05.5`), el paso 9 el 27-10 al corregirse «Mi perfil de salud» del cuidador (`S4_09.3`) y el paso 6 al agregarse la captura del diálogo de salida (`S4_06.1`).

## 3. Qué respalda cada captura

| Captura | Qué muestra | Criterio que respalda |
| :--- | :--- | :--- |
| `S4_01.1_crear_horario_swagger.png` | `POST /medicamentos/{id}/horarios` con `{"hora": "14:57"}` y respuesta 201 con el horario creado. | Habilitador: un medicamento tiene horarios propios (criterio 1). |
| `S4_01.2_agenda_actividad_con_horario.png` | Agenda de hoy con «Omeprazol» a las 14:55 y a las 14:57 como actividades separadas. | Habilitador: una actividad por horario (criterio 3). |
| `S4_02.0_registra_un_medicamento_dispositivo_swagger.png` | `POST /perfiles/{id}/medicamentos` con «Paracetamol», 500 mg y `hora_inicio` 20:15, respuesta 201. | Preparación de HU 9: medicamento al que le llegará el recordatorio de las 20:15. |
| `S4_02.0_registrar_dispositivo_swagger.png` | `POST /dispositivos` en `/docs` para registrar el dispositivo de prueba. | HU 9: registro del dispositivo (criterio 5). |
| `S4_02_avisos_recordatorio_sin_leer.png` | Pantalla Avisos con recordatorios y alertas sin leer (punto verde, texto en negrita). | HU 9: el recordatorio llega a la app (criterio 6). |
| `S4_02.1_log_backend_notificador.png` | Log del backend: `perfil_medico.notificador: Aviso para 1 dispositivo(s): Recordatorio: «Paracetamol» de Dr. Emmett Brown es a las 20:15` con el tipo `recordatorio`, el perfil y la actividad. Los caracteres raros son de la consola de PowerShell. | HU 9: el backend crea el recordatorio y lo entrega al notificador de log del dispositivo registrado (criterios 5 y 6). No es un push real al celular. |
| `S4_02.2_log_backend_llamadas_alertas.png` | Terminal del backend con `GET /alertas` y `POST /alertas/{id}/leida` respondiendo 200. | HU 9: la app consulta los avisos y los marca como leídos. |
| `S4_03.1_agenda_abierta_desde_aviso.png` | Agenda de hoy abierta al tocar un aviso. | HU 9: tocar un aviso abre la Agenda del perfil (criterio 8). |
| `S4_03.2_aviso_marcado_leido.png` | La misma lista de Avisos, ahora sin punto verde ni negrita. | HU 9: el aviso queda marcado como leído. |
| `S4_04.1_avisos_alerta_nivel1_cuidador.png` | Avisos del cuidador con «La actividad … aún no fue confirmada» y etiqueta «Alerta de nivel 1». | HU 10: alerta de nivel 1 al cuidador (criterio 9); el texto no asume una emergencia (criterio 13). |
| `S4_04.2_avisos_alerta_titular.png` | Avisos del titular con las mismas alertas de nivel 1. | HU 10: la alerta también llega al titular (criterio 9). |
| `S4_04.3_avisos_alerta_nivel1_paracetamol.png` | Avisos con la alerta de nivel 1 de «Paracetamol» (programada a las 20:15). | HU 10: alerta de nivel 1 tras el primer plazo (criterio 9). |
| `S4_04.3_cuidador_nivel_escalamiento_1_swagger.png` | Vínculo del cuidador en `/docs` con `nivel_escalamiento = 1`. | HU 10: configuración del cuidador en nivel 1 (criterio 10, parte previa). |
| `S4_04.4_cuidador_nivel_escalamiento_2_swagger.png` | `PUT /perfiles/{id}/cuidadores/{vínculo}` con `recibe_alertas: true` y `nivel_escalamiento: 2`, respuesta 200. El vínculo es de solo lectura (`rol_vinculo: lectura`, `puede_confirmar: false`). | HU 10: se configura al cuidador en nivel 2 (criterio 10, parte previa). |
| `S4_04.5_avisos_alerta_nivel2_cuidador.png` | Avisos del cuidador con «La actividad «Omeprazol» de Dr. Emmett Brown (programada a las 14:57) aún no fue confirmada. Sigue sin confirmarse.» y la etiqueta «Alerta de nivel 2». | HU 10: alerta de nivel 2 para el cuidador con `nivel_escalamiento = 2` (criterio 10); el texto no asume una emergencia (criterio 13). |
| `S4_04.6_avisos_alerta_nivel1_actividad.png` | Avisos con alertas de nivel 1 de actividades sin confirmar. | HU 10: complemento del criterio 9. |
| `S4_04.6_avisos_titular_sin_alerta_nivel2.png` | Avisos del titular con recordatorios y alertas de nivel 1 («Hora de descanso», «Cena liviana», «Paracetamol»), sin ninguna de nivel 2. | HU 10: el nivel 2 no llega al titular ni a quien está en nivel 1 (criterio 10). |
| `S4_05.1_avisos_solo_alerta_de_la_pendiente.png` | Avisos (5:09) con tres avisos sin leer: la alerta y el recordatorio de «Tiempo libre» y la alerta de «Omeprazol». | HU 10: punto de partida del paso 5. |
| `S4_05.2.1_agenda_una_confirmada_una_pendiente.png` | Agenda (5:12) con «Tiempo libre» confirmada y «Cena», «Hora de descanso» y otras aún pendientes. | HU 10: una actividad confirmada y otras pendientes (criterio 11). |
| `S4_05.2_pantalla_avisos_campana_una_confirmada_una_pendiente.png` | Avisos (5:13) ya leídos; la alerta de «Tiempo libre» es anterior a la confirmación. | HU 10: parcial. La captura se tomó antes del plazo del nivel 2 (17:30), así que no prueba por sí sola que el escalamiento se detenga; ver nota en la sección 4. |
| `S4_05.3_avisos_titular_nivel1_ambas_pendientes.png` | Avisos de la cuenta titular (28-10, 03:43): alerta de nivel 1 de «Prueba pendiente» y de «Prueba confirmada» (ambas programadas a las 03:42), creadas a las 03:43, más sus recordatorios de las 03:40. La pantalla no muestra el nombre de la cuenta; se identifica porque incluye alertas de nivel 1 de Dr. Emmett Brown. | HU 10 (criterio 11): punto de partida, las dos actividades siguen sin confirmar y escalan al nivel 1. |
| `S4_05.4_agenda_una_confirmada_una_pendiente.png` | Agenda de hoy, 28/10/2026 (03:43): «Prueba confirmada» marcada y «Prueba pendiente» sin marcar; «1 de 14 actividades confirmadas». | HU 10 (criterio 11): una actividad confirmada y otra pendiente, con la hora a la vista. |
| `S4_05.5_avisos_cuidador_nivel2_solo_pendiente.png` | Avisos de la cuenta de Sergio (28-10, 03:47): alerta de **nivel 2** solo de «Prueba pendiente» («Sigue sin confirmarse»), creada a las 03:47, 5 minutos después de la hora programada. De «Prueba confirmada» solo está el recordatorio. Sin alertas de nivel 1 de Dr. Emmett Brown, porque Sergio está en nivel 2 en ese perfil. | HU 10 (criterios 10 y 11): el nivel 2 llega al cuidador en nivel 2 solo para la actividad no confirmada; confirmar detuvo el escalamiento. |
| `S4_06_modo_simplificado_dependiente.png` | Modo simplificado de «Dr. Emmett Brown»: «Hoy, 25/10/2026», «9 de 12 hechas» y botones «Hecho» grandes. | HU 11: solo actividades de hoy, botones y texto grandes (criterio 14). |
| `S4_06.1_salir_del_modo_simplificado_dependiente.png` | Diálogo «¿Salir del modo simplificado? Se vuelve al menú completo.» con los botones «Quedarme» y «Salir». | HU 11: la salida del modo pide confirmación (criterio 17). |
| `S4_07.1_modo_simplificado_actividad_confirmada.png` | Tarjetas que pasan a «Hecha» en verde tras un toque. | HU 11: confirmar toma un solo toque (criterio 15). |
| `S4_07.2_agenda_refleja_confirmacion.png` | Agenda de hoy con «10 de 12 actividades confirmadas» (antes eran 9 de 12). | HU 11: la confirmación se guarda en el servidor y la agenda la refleja. |
| `S4_08.1_modo_simplificado_sin_edicion.png` | Modo simplificado solo con el botón «Hecho»; sin editar ni borrar. | HU 11: no permite editar ni borrar (criterio 16). |
| `S4_08.3_modo_simplificado_solo_lectura.png` | Aviso «Este perfil es de solo lectura: no se pueden confirmar actividades»; sin botón «Hecho». | HU 11 + HU 7: un perfil compartido solo para lectura no confirma. |
| `S4_09.1_panel_titular(Mejora pendiente).png` | «Panel de dependientes» con el avance por perfil; el titular aparece en la lista con la etiqueta «Titular». | Mejora: el Panel usa `GET /panel`. Pendiente decidir si el titular debe aparecer en un panel «de dependientes». |
| `S4_09.2_log_backend_get_panel.png` | Log del backend con `GET /panel?fecha=2026-10-25` respondiendo 200. | Mejora: una sola llamada para todo el panel. |
| `S4_09.3_mi_perfil_salud_cuidador.png` | Home de la cuenta cuidador (Sergio, 27-10, 10:28) con el perfil activo «Marty Gallina Mcfly (Titular)»; «Mi perfil de salud» dice «Aún no lo completas» en vez de mostrar el perfil del titular. | Mejora: «Mi perfil de salud» ya no cae en el perfil titular de otra persona (cambio en `home_screen.dart`, 27-10). |
| `S4_10_error_conexion_sin_backend.png` | Agenda con el mensaje «No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.» | Mejora: error de red claro, sin quedarse cargando. |
| `S4_11_flutter_test_por_archivo.png` | Terminal con `flutter test` corrido por archivo: `avisos_test.dart` (+4), `agenda_test.dart` (+2) y `login_screen_test.dart` (+1), todas «All tests passed!». | Pruebas de la app del Sprint 4 en verde (HU 9 y HU 10: modelo `Alerta`, agenda). |

## 4. Notas y limitaciones

- **Qué rutas usa la app y cuáles no (revisado en `api_service.dart`):** la app llama a `GET /perfiles/{id}/actividades`, `POST /actividades/{id}/confirmar` y `/desconfirmar`, `GET /panel`, `GET /alertas` y `POST /alertas/{id}/leida`, todas iguales a las del backend y del contrato. No llama a `/dispositivos`, a las rutas de horarios ni envía `recibe_alertas` ni `nivel_escalamiento` al compartir un perfil (`POST /perfiles/{id}/cuidadores`). Por eso horarios, dispositivo y nivel de escalamiento se configuraron desde `/docs` (`S4_01.1`, `S4_02.0`, `S4_04.4`), y un cuidador creado desde la app queda con `recibe_alertas = true` y `nivel_escalamiento = 1`.
- **Push real (FCM) no implementado.** HU 9 se prueba con la pantalla Avisos y queda parcial hasta elegir proveedor. La app tampoco registra el dispositivo: `POST /dispositivos` se probó desde `/docs` y el backend entregó el aviso al notificador de log (`S4_02.1`).
- **Rol de lectura y alertas:** la cuenta de nivel 2 usada en las pruebas (Sergio) tiene rol de solo lectura. El rol no impide recibir alertas (solo cuentan `recibe_alertas` y `nivel_escalamiento`), pero esa cuenta no puede confirmar actividades; las confirmaciones de las pruebas se hacen con la cuenta titular.
- **Cómo escala (según el código y `test_la_alerta_escala_al_nivel_2_solo_para_quien_corresponde`):** cada nivel va a un grupo distinto. El nivel 1 llega al titular y a los cuidadores en nivel 1; el nivel 2, solo a los cuidadores con `recibe_alertas` y `nivel_escalamiento = 2` (`S4_04.5`), que no reciben el nivel 1. El titular y los cuidadores en nivel 1 nunca ven un nivel 2 por mucho que pase el tiempo (`S4_04.6_avisos_titular_sin_alerta_nivel2`), y si nadie está en nivel 2, esa alerta no llega a nadie. El nivel 3 aceptado por el esquema (`nivel_escalamiento` hasta 3) no está implementado. La cuenta ajena (que no ve avisos) queda para el checklist del Product Owner (criterio 12).
- **Confirmar detiene el escalamiento (paso 5, cerrado el 28-10).** Las capturas del 25-10 se tomaron antes del plazo del nivel 2. Se repitió con los plazos reducidos solo para la prueba (`ALERTA_PLAZO_1_MINUTOS=1` y `ALERTA_PLAZO_2_MINUTOS=5` con `docker-compose.prueba.yml`; por defecto son 30 y 60 minutos): a las 03:43 las dos actividades de las 03:42 recibieron el nivel 1 (`S4_05.3`), se confirmó una (`S4_05.4`) y a las 03:47 solo la no confirmada recibió el nivel 2 (`S4_05.5`). Lo respalda además `test_confirmar_detiene_el_escalamiento`. Según las capturas, el nivel de escalamiento de Sergio es por perfil (se guarda en cada vínculo): en el perfil de Marty recibe el nivel 1 y en el de Dr. Emmett Brown, el nivel 2.
- **"Mi perfil de salud" para cuidadores: corregido el 27-10.** El getter que elegía el perfil caía en el perfil titular de otra persona compartido con la cuenta; ahora solo usa el perfil propio, y una cuenta cuidador sin perfil propio ve «Aún no lo completas» (`S4_09.3`). `flutter analyze` y `flutter test` se repitieron el 28-10 con el cambio y pasan.
- **Panel:** el Panel ya usa `GET /panel`, pero lista al titular bajo el título «Panel de dependientes» (`S4_09.1`).
- **Salida del modo simplificado:** el icono de salir se ve en `S4_06` y el diálogo de confirmación en `S4_06.1`; el criterio 17 queda evidenciado.
- Las capturas de HU 10 muestran mensajes que informan que la actividad no fue confirmada; en ningún caso el sistema afirma una emergencia.
- **Hora de los avisos (por confirmar).** En las capturas del 25-10 la fecha bajo cada aviso aparecía en UTC (p. ej. «Alerta de nivel 1 · 25/10 20:00» para una actividad de las 16:30). En las del 28-10 (`S4_05.3` a `S4_05.5`) aparece en hora de Chile (alerta de las 03:42 → 03:43), con el reloj del emulador en GMT-03:00 y coincidiendo con el del PC. Confirmar si hubo un cambio en la app; si no, es una mejora pendiente.
