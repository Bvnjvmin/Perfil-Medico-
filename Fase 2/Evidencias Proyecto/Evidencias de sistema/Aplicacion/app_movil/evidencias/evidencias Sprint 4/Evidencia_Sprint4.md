# Evidencia de Pruebas — Sprint 4 (HU 9, HU 10 y HU 11)

**Rol:** Matías Pizarro (App Móvil y Scrum Master)
**Periodo:** 19 al 31 de octubre de 2026 · **Pruebas del** 25 de octubre de 2026
**Entorno:** emulador Android (app Flutter en modo debug) conectado al backend local con Docker Compose (servicios `api-1` y `db-1`, PostgreSQL 16); commit del backend: *(pegar el hash)*
**Cuentas usadas:** una cuenta titular y una cuenta cuidador. Perfiles de prueba: *Marty Gallina Mcfly* (titular) y *Dr. Emmett Brown* (dependiente, adulto mayor).

> Las capturas de este sprint están en esta misma carpeta, con el nombre `S4_NN_...png`. Cada una lleva abajo una frase que dice qué criterio respalda. Las rutas del backend (horarios, avisos) se probaron desde `/docs` de FastAPI; el resto, desde la app en el emulador.

## 1. Validación automatizada

| Comando | Resultado | Evidencia |
| :--- | :--- | :--- |
| `flutter analyze` | No issues found (sin avisos ni errores), corrido el 25-10 con el código del Sprint 4 (26,7 s) | `app_movil/analyze.log` |
| `flutter test` | 14 de 14 pruebas pasan, corrida del 25-10 (7 de modelos, 1 de login, 2 de agenda y 4 de avisos) | `app_movil/test.log` y `S4_11_flutter_test_por_archivo.png` |
| `pytest` (backend) | 148 pruebas pasan en 199 s (119 anteriores + 29 nuevas) | `backend/pytest.log` |

Pruebas nuevas de la app en este sprint: `test/services/avisos_test.dart` (modelo `Alerta`, estado `vencida`, `AvancePerfil.desdePanel`) y `test/services/agenda_test.dart`.

Límite conocido: la app no recibe notificaciones push ni registra el dispositivo (falta elegir FCM); los avisos se ven en la pantalla Avisos.

## 2. Flujos funcionales en el emulador

Leyenda: ✅ cumplido · 🟡 cumplido en parte · ❌ no cumplido (mejora pendiente).

| Paso | Historia | Qué se hizo en la App | Resultado esperado | Capturas | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | HU 9 | Se creó un horario a las 14:57 para un medicamento (`POST /medicamentos/{id}/horarios`, desde `/docs`). | La agenda muestra la actividad a esa hora. | `S4_01.1`, `S4_01.2` | ✅ |
| 2 | HU 9 | Se registró un dispositivo (`POST /dispositivos`, desde `/docs`), se esperó el recordatorio y se abrió Avisos (campana del Home). | El backend envía el aviso al notificador y aparece el recordatorio sin leer. | `S4_02`, `S4_02.1`, `S4_02.2` | ✅ |
| 3 | HU 9 | Se tocó el aviso. | Se marca leído y abre la Agenda del perfil. | `S4_03.1`, `S4_03.2` | ✅ |
| 4 | HU 10 | Se dejaron actividades sin confirmar y se entró con la cuenta del cuidador y con la del titular; después se configuró al cuidador con `nivel_escalamiento = 2` y se volvió a abrir Avisos. | Ambos ven la alerta de nivel 1; el cuidador en nivel 2 recibe además la de nivel 2. | `S4_04.1`, `S4_04.2`, `S4_04.5` | ✅ |
| 5 | HU 10 | Se confirmó una actividad y otra quedó pendiente. | La alerta deja de escalar para la confirmada. | `S4_05.1`, `S4_05.1.1`, `S4_05.2` | 🟡 |
| 6 | HU 11 | Se entró al modo simplificado de un dependiente. | Solo actividades de hoy, botones grandes. | `S4_06` | ✅ |
| 7 | HU 11 | Se confirmó una actividad con un toque. | El estado se guarda en el servidor. | `S4_07.1`, `S4_07.2` | ✅ |
| 8 | HU 11 | Se buscó editar o borrar desde el modo simplificado; también se abrió un perfil de solo lectura. | No hay opción de editar ni borrar. | `S4_08.1`, `S4_08.3` | ✅ |
| 9 | Mejora | Panel con `GET /panel?fecha=` (una sola llamada); "Mi perfil de salud" con cuenta de cuidador. | Datos correctos y sin mostrar el titular ajeno. | `S4_09.1`, `S4_09.2`, `S4_09.3` | 🟡 |
| 10 | Mejora | Se cortó el backend y se abrió la agenda. | Mensaje claro de conexión, sin quedarse cargando. | `S4_10` | ✅ |

**Resultado:** 8 de 10 flujos ✅, 2 en parte (pasos 5 y 9).

## 3. Qué respalda cada captura

| Captura | Qué muestra | Criterio que respalda |
| :--- | :--- | :--- |
| `S4_01.1_crear_horario_swagger.png` | `POST /medicamentos/{id}/horarios` con `{"hora": "14:57"}` y respuesta 201 con el horario creado. | Habilitador: un medicamento tiene horarios propios (Checklist PO, criterio 1). |
| `S4_01.2_agenda_actividad_con_horario.png` | Agenda de hoy con «Omeprazol» a las 14:55 y a las 14:57 como actividades separadas. | Habilitador: una actividad por horario (criterio 3). |
| `S4_02_avisos_recordatorio_sin_leer.png` | Pantalla Avisos con recordatorios y alertas sin leer (punto verde, texto en negrita). | HU 9: el recordatorio llega a la app (criterio 6). |
| `S4_02.1_log_backend_notificador.png` | Log del backend: `perfil_medico.notificador: Aviso para 1 dispositivo(s): Recordatorio: «Paracetamol» de Dr. Emmett Brown es a las 20:15` con el tipo `recordatorio`, el perfil y la actividad. Los caracteres raros son de la consola de PowerShell. | HU 9: el backend crea el recordatorio y lo entrega al notificador de log del dispositivo registrado (criterios 5 y 6). No es un push real al celular. |
| `S4_02.2_log_backend_llamadas_alertas.png` | Terminal del backend con `GET /alertas` y `POST /alertas/{id}/leida` respondiendo 200. | HU 9: la app consulta los avisos y los marca como leídos. |
| `S4_03.1_agenda_abierta_desde_aviso.png` | Agenda de hoy abierta al tocar un aviso. | HU 9: tocar un aviso abre la Agenda del perfil (criterio 8). |
| `S4_03.2_aviso_marcado_leido.png` | La misma lista de Avisos, ahora sin punto verde ni negrita. | HU 9: el aviso queda marcado como leído. |
| `S4_04.1_avisos_alerta_nivel1_cuidador.png` | Avisos del cuidador con «La actividad … aún no fue confirmada» y etiqueta «Alerta de nivel 1». | HU 10: alerta de nivel 1 al cuidador (criterio 9); el texto no asume una emergencia (criterio 13). |
| `S4_04.2_avisos_alerta_titular.png` | Avisos del titular con las mismas alertas de nivel 1. | HU 10: la alerta también llega al titular (criterio 9). |
| `S4_04.5_avisos_alerta_nivel2_cuidador.png` | Avisos del cuidador con «La actividad «Omeprazol» de Dr. Emmett Brown (programada a las 14:57) aún no fue confirmada. Sigue sin confirmarse.» y la etiqueta «Alerta de nivel 2». | HU 10: alerta de nivel 2 para el cuidador con `nivel_escalamiento = 2` (criterio 10); el texto no asume una emergencia (criterio 13). |
| `S4_05.1_agenda_una_confirmada_una_pendiente.png` | Pantalla Avisos con las alertas del perfil. | HU 10: contexto para el paso 5. |
| `S4_05.1.1_agenda_una_confirmada_una_pendiente.png` | Agenda con «Tiempo libre» confirmada y otras actividades pendientes. | HU 10: una actividad confirmada y otra pendiente (criterio 11). |
| `S4_05.2_avisos_solo_alerta_de_la_pendiente.png` | Avisos tras confirmar. La alerta de «Tiempo libre» es anterior a la confirmación. | HU 10: parcial; falta una captura que muestre que no se crea alerta nueva para la confirmada. |
| `S4_06_modo_simplificado_dependiente.png` | Modo simplificado de «Dr. Emmett Brown»: «Hoy, 25/10/2026», «9 de 12 hechas» y botones «Hecho» grandes. | HU 11: solo actividades de hoy, botones y texto grandes (criterio 14). |
| `S4_07.1_modo_simplificado_actividad_confirmada.png` | Tarjetas que pasan a «Hecha» en verde tras un toque. | HU 11: confirmar toma un solo toque (criterio 15). |
| `S4_07.2_agenda_refleja_confirmacion.png` | Agenda de hoy con «10 de 12 actividades confirmadas» (antes eran 9 de 12). | HU 11: la confirmación se guarda en el servidor y la agenda la refleja. |
| `S4_08.1_modo_simplificado_sin_edicion.png` | Modo simplificado solo con el botón «Hecho»; sin editar ni borrar. | HU 11: no permite editar ni borrar (criterio 16). |
| `S4_08.3_modo_simplificado_solo_lectura.png` | Aviso «Este perfil es de solo lectura: no se pueden confirmar actividades»; sin botón «Hecho». | HU 11 + HU 7: un perfil compartido solo para lectura no confirma. |
| `S4_09.1_panel_titular(Mejora pendiente).png` | «Panel de dependientes» con el avance por perfil; el titular aparece en la lista con la etiqueta «Titular». | Mejora: el Panel usa `GET /panel`. Pendiente decidir si el titular debe aparecer en un panel «de dependientes». |
| `S4_09.2_log_backend_get_panel.png` | Log del backend con `GET /panel?fecha=2026-10-25` respondiendo 200. | Mejora: una sola llamada para todo el panel. |
| `S4_09.3_mi_perfil_salud_cuidador(Mejora pendiente).png` | Home de la cuenta cuidador con el perfil activo «Marty Gallina Mcfly (Titular)» y «Mi perfil de salud» apuntando a ese perfil. | ❌ Mejora no resuelta: la cuenta cuidador ve el perfil titular de otra persona en «Mi perfil de salud». |
| `S4_10_error_conexion_sin_backend.png` | Agenda con el mensaje «No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.» | Mejora: error de red claro, sin quedarse cargando. |
| `S4_11_flutter_test_por_archivo.png` | Terminal con `flutter test` corrido por archivo: `avisos_test.dart` (+4), `agenda_test.dart` (+2) y `login_screen_test.dart` (+1), todas «All tests passed!». | Pruebas de la app del Sprint 4 en verde (HU 9 y HU 10: modelo `Alerta`, agenda). |

## 4. Notas y limitaciones

- **Push real (FCM) no implementado.** HU 9 se prueba con la pantalla Avisos y queda parcial hasta elegir proveedor. La app tampoco registra el dispositivo: `POST /dispositivos` se probó desde `/docs` y el backend entregó el aviso al notificador de log (`S4_02.1`).
- **Nivel 2:** solo llega a los cuidadores con `recibe_alertas` y `nivel_escalamiento = 2` (`S4_04.5`); un cuidador en nivel 1 recibe el nivel 1 pero no el 2. La cuenta ajena (que no ve avisos) queda para el checklist del Product Owner (criterio 12).
- **"Mi perfil de salud" para cuidadores sigue sin corregirse** (`S4_09.3`). Es la acción de la retrospectiva del Sprint 3 que no se cerró.
- **Panel:** el Panel ya usa `GET /panel`, pero lista al titular bajo el título «Panel de dependientes» (`S4_09.1`).
- **Salida del modo simplificado:** el icono de salir se ve en `S4_06`, pero no hay captura del diálogo de confirmación (criterio 17).
- Las capturas de HU 10 muestran mensajes que informan que la actividad no fue confirmada; en ningún caso el sistema afirma una emergencia.
