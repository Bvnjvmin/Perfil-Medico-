# Sprint Backlog — Sprint 5 (S13–S14)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 2 al 14 de noviembre de 2026 (semanas 13 y 14 del Cronograma)
**Última actualización:** 13 de noviembre de 2026 (día 12 de 13) · **Estado del sprint:** en cierre; la base de datos, el backend y la app están integrados y probados en el emulador (evidencia en la sección 5); faltan la aceptación del Product Owner, la prueba con Traccar y la pulsera reales, la prueba de la IA con un proveedor real y la retrospectiva

**Objetivo del sprint:** que el titular y los cuidadores registren y vean los indicadores de salud y el historial de cumplimiento (HU 12 y 13), que el perfil dependiente pueda pedir ayuda con un botón (HU 14), que una pulsera GPS envíe su ubicación y sus alertas al sistema (HU 17 y 19) y que exista un asistente de IA de orientación general (HU 15).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregables del Cronograma:** Sprint Backlog 5 (semana 13); Demo interna y Retrospectiva del Sprint 5 (semana 14, cierre el sábado 14).

> Leyenda: ✅ terminado y verificado · 🟡 hecho en parte (se indica qué falta) · ⬜ pendiente · ❌ no cumplido. Una historia solo pasa a terminada cuando está integrada al repositorio, probada y documentada. Los criterios y decisiones son propuesta hasta confirmarlos en la reunión del equipo.

## 1. Historias comprometidas

### HU 12 — Registro de indicadores de salud
Como usuario quiero registrar indicadores (peso, presión, glucosa y frecuencia cardíaca) de un perfil y verlos en un gráfico de evolución.
- **Criterios de aceptación**
  - Se registra un valor por tipo; la presión lleva sistólica y diastólica. Un valor fuera de rango se rechaza.
  - Se ve el último valor de cada tipo y la evolución de los últimos 7, 30 o 90 días, con mínimo, máximo y promedio.
  - Solo ve y registra quien tiene permiso (`puede_ver_indicadores`; para registrar, además `puede_confirmar`). Una cuenta ajena recibe 404.

### HU 13 — Historial de cumplimiento
Como titular o cuidador quiero ver el % de cumplimiento de medicamentos, hidratación y alimentación de un perfil.
- **Criterios de aceptación**
  - Porcentaje general, por categoría y por día para un rango de hasta 92 días.
  - Las actividades omitidas y las pendientes de hoy que aún no llegan a su hora no cuentan.
- **Evidencia:** completa (secciones 5.2 y 5.3, pasos 2 a 7).

### HU 14 — Botón de asistencia
Como perfil dependiente quiero un botón «Necesito ayuda» que notifique a los cuidadores autorizados.
- **Criterios de aceptación**
  - Al pulsarlo (con confirmación) se crea un evento y se avisa al titular y a los cuidadores con alertas.
  - Pulsarlo varias veces seguidas no duplica el aviso.
  - El botón está en el modo simplificado.

### HU 15 — Asistente de IA (orientación general)
Como usuario quiero preguntarle a un asistente de IA sobre la información registrada en un perfil.
- **Criterios de aceptación**
  - La respuesta siempre muestra que es orientación general y que no reemplaza a un profesional.
  - Una pregunta de urgencia recibe un texto fijo con el 131 (SAMU) y el *4141, sin consultar al modelo.
  - No se envían al modelo el RUT, el correo ni los teléfonos. Máximo 30 consultas por usuario al día.

### HU 17 — Pulsera: ubicación y geocercas
Como titular o cuidador quiero ver la ubicación y recibir alertas de geocerca desde la pulsera, mediante un servidor Traccar propio.
- **Criterios de aceptación**
  - Se registra una pulsera con el identificador (IMEI) de Traccar y se ve su última ubicación y su batería.
  - Se crean zonas circulares; al salir de una se crea un evento.
  - Solo el titular registra pulseras y zonas.

### HU 18 — Pulsera: frecuencia cardíaca y presión referencial (Health Connect)
Como titular o cuidador quiero ver la frecuencia cardíaca y la presión referencial del perfil dependiente desde la pulsera conectada.
- **Estado:** no iniciada. El backend ya acepta indicadores con `fuente = pulsera`; falta que la app lea Health Connect y los envíe (ver decisiones).

### HU 19 — Pulsera: alertas de seguridad
Como cuidador quiero recibir una alerta si la pulsera detecta una caída, se presiona el botón SOS, la batería está baja o hay inactividad inusual.
- **Criterios de aceptación**
  - SOS, caída y batería baja crean un evento (la batería baja no se repite en 2 horas).
  - La inactividad (3 horas sin moverse más de 30 m, entre 08:00 y 22:00) crea un evento.
  - Cada evento llega al titular y a los cuidadores con alertas y se ve en la app.

## 2. Tareas por integrante

| Tarea | Historia | Responsable | Estado | Dónde |
|---|---|---|---|---|
| Tablas `indicador_salud`, `pulsera`, `posicion`, `geocerca`, `evento_seguridad` y `consulta_ia`; 4 migraciones | HU 12 / 14 / 15 / 17 / 19 | Sergio | ✅ Subidas el 06-11 (`3b3483c`, `ff2aa1c`), probadas en PostgreSQL 16 y en Docker (`alembic current` y `alembic check`: `S5_00.1`, `S5_00.4`) | `backend/alembic/versions/`, `models/` |
| `modelo_datos.md` y diagrama ER al día | Habilitador | Sergio | ✅ Subidos el 06-11 (`3131080`, `0412152`) | `Base de datos/` |
| Servidor Traccar (compose, `traccar.xml`, guía) | HU 17 / 19 | Sergio | 🟡 Archivos subidos el 06-11 (`9c93e43`, `4fd14bb`); sin levantar ni capturar un envío real | `backend/traccar/` |
| Pulsera de muestra comprada y configurada | HU 17 / 19 | Sergio | ⬜ Pendiente (la demo usa el simulador) | — |
| Contexto de la IA y casos de prueba | HU 15 | Sergio | 🟡 Documentos subidos el 06-11 (`65d9ec5`); casos sin ejecutar | `Base de datos/` |
| Checklist de aceptación del Product Owner del Sprint 5 | HU 12 a 19 | Sergio | 🟡 Plantilla subida el 06-11 (`3131080`); sin ejecutar con las tres cuentas | `Base de datos/Checklist_Aceptacion_PO_Sprint5.md` |
| Permiso `puede_ver_indicadores` y configuración nueva | HU 12 / 17 | Benjamín | ✅ Subido el 05-11 (`d77e9c1`, `6bb5659`, `b0f9742`) | `backend/app/` |
| Indicadores, cumplimiento, asistencia, pulsera, geocercas, Traccar e IA (servicios y rutas) | HU 12 a 19 | Benjamín | ✅ Subidos el 05-11 (`2228cb2`, `cd64277`) y conectados en `main.py` el 07-11 (`11bcf7c`) | `backend/app/` |
| Pruebas del backend | HU 12 a 19 | Benjamín | ✅ 62 pruebas nuevas; suite completa 210 de 210 (`21d86b8`) | `backend/app/tests/` |
| Contrato de API y simulador de pulsera | HU 12 a 19 | Benjamín | ✅ Subidos el 05-11 (`de429a1`, `88db528`) | `backend/` |
| Prueba con Docker (`docker compose up --build`, `alembic current`, `alembic check`) | Habilitador | Benjamín | ✅ Verificado en Docker Compose (`api` y `db`) | — |
| Push real con FCM (arrastre del Sprint 4) | HU 9 | Benjamín / Matías | 🟡 Backend en `main` (apagado por defecto, 6 pruebas); la app queda sin push real, propuesta de dejarlo como límite conocido (decisión 1) | `backend/app/services/notificador.py`, `backend/docs/Notas_FCM_Sprint5.md` |
| Pantalla de eventos de seguridad | HU 14 / 19 | Matías | ✅ Integrada y probada en el emulador (alerta recibida y atendida) | `app_movil/lib/screens/` |
| Botón «Necesito ayuda» en el modo simplificado | HU 14 | Matías | ✅ Integrado y probado en el emulador (con confirmación) | `app_movil/lib/widgets/` |
| Pantalla de cumplimiento con gráfico | HU 13 | Matías | ✅ Integrada y probada en el emulador (7, 14 y 30 días) | `app_movil/lib/screens/` |
| Pantalla de indicadores con registro y gráfico | HU 12 | Matías | ✅ Integrada y probada en el emulador | `app_movil/lib/screens/` |
| Pantalla de pulsera, ubicación y zonas | HU 17 / 19 | Matías | ✅ Integrada y probada en el emulador | `app_movil/lib/screens/` |
| Pantalla del asistente de IA | HU 15 | Matías | ✅ Integrada y probada en el emulador (modo simulado) | `app_movil/lib/screens/` |
| Lectura de Health Connect (frecuencia cardíaca y presión) | HU 18 | Matías | ⬜ Sin iniciar; depende de la decisión 3 | — |
| `flutter analyze` y `flutter test` con las pantallas nuevas | HU 12 a 19 | Matías | ✅ Sin avisos; pruebas en verde (`analyze.log`, `test.log`) | `app_movil/` |
| Evidencia del sprint (capturas `S5_xx`) | HU 12 a 19 | Matías | 🟡 Completa para HU 12, 13, 14, 15, 17 y 19; faltan algunos criterios (sección 5.5) | `app_movil/evidencias/` |
| Retrospectiva del Sprint 5, el último día | — | Matías | ⬜ Pendiente | `Metodologia_Scrum/Sprint_5/` |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 12 | 🟡 BD y backend sí; app lista, falta confirmar sus commits | 🟡 backend y emulador sí; falta el PO | ✅ contrato y evidencia | 🟡 |
| HU 13 | 🟡 BD y backend sí; app lista, falta confirmar sus commits | 🟡 backend y emulador sí (rangos, omitidas, pendientes y límite de 92 días); falta el PO | ✅ contrato y evidencia | 🟡 |
| HU 14 | 🟡 backend sí; app lista, falta confirmar sus commits | 🟡 backend y emulador sí; falta el PO | ✅ contrato y evidencia | 🟡 |
| HU 15 | 🟡 backend sí; app lista, falta confirmar sus commits | 🟡 backend y emulador en modo simulado; falta un proveedor real y el PO | ✅ `Contexto_IA_Sprint5.md` y evidencia | 🟡 |
| HU 17 | 🟡 backend y Traccar sí; app lista, falta confirmar sus commits | 🟡 backend y emulador con el simulador; falta Traccar y pulsera reales | ✅ `traccar/README.md` y evidencia | 🟡 |
| HU 18 | ⬜ | ⬜ | ⬜ | ⬜ |
| HU 19 | 🟡 backend sí; app lista, falta confirmar sus commits | 🟡 backend y emulador con el simulador; falta la pulsera real | ✅ contrato y evidencia | 🟡 |

## 4. Plan de pruebas del sprint

| Prueba | Tipo | Estado |
|---|---|---|
| Suites del backend existentes (148 pruebas) | Automática (backend) | ✅ pasan, dentro de las 210 |
| Pruebas nuevas de indicadores, cumplimiento, asistencia, pulsera, IA y nivel 2 | Automática (backend) | ✅ 62 pruebas; total 210 de 210 en unos 250 s |
| `alembic upgrade head` desde base vacía, `alembic check` y `downgrade` / `upgrade` de cada migración nueva | Manual (PostgreSQL) | ✅ probado en PostgreSQL 16 (cabeza `a5b6c7d8e9f0`) y repetido en Docker (`S5_00.1`, `S5_00.4`) |
| Alertas de la pulsera con el simulador (`simular_pulsera.py`) | Manual (API) | ✅ SOS, caída, batería baja y salida de zona crearon sus eventos |
| Servidor Traccar con un envío real a la API | Manual (Sergio) | ⬜ |
| Checklist de aceptación del Product Owner con tres cuentas | Manual (Product Owner) | ⬜ |
| Flujos de las pantallas nuevas en el emulador | Manual (emulador, Matías) | ✅ HU 12, 13, 14, 15, 17 y 19 (sección 5.2) |
| `flutter test` y `flutter analyze` | Automática (app) | ✅ |

Comando de las pruebas del backend: `pytest app/tests/ -v` (en Docker: `docker compose exec api python -m pytest`).

## 5. Evidencia de pruebas del sprint

**Rol:** Matías Pizarro (App Móvil y Backend Developer)
**Entorno:** emulador Android (app Flutter en modo debug) conectado al backend local con Docker Compose (servicios `api` y `db`, PostgreSQL 16). Las rutas del backend (cumplimiento, asistencia, pulseras, geocercas y eventos) se probaron en `/docs` de FastAPI; el resto, desde la app en el emulador.
**Perfil de prueba principal:** Dr. Emmett Brown (`1127a031-1d1a-4f8a-9408-2ddb9fe44288`).
**Pulsera simulada y geocerca:** dispositivo `PULSERA-EMMETT-01` (`id: 9e755d13-2862-4759-9353-34d43992e075`) y zona segura «Casa Dr. Brown» (`id: 25c34130-1b41-45d6-ac0d-03b12bd862ef`, radio de 200 m en `-33.4489, -70.6693`).

> Las capturas están en `app_movil/evidencias/evidencias Sprint 5/`, con el prefijo `S5_NN_...png`. En las capturas de Swagger el token del `curl` está difuminado.

### 5.1 Validación automatizada

| Comando | Resultado | Evidencia |
| :--- | :--- | :--- |
| `flutter analyze` | No issues found. | `app_movil/analyze.log`, `S5_00.2_flutter_analyze_and_test.png` |
| `flutter test` | Pruebas de modelos, widgets y servicios de agenda y alertas en verde. | `app_movil/test.log` |
| `pytest` (backend) | Pruebas de cumplimiento, asistencia, eventos y tramas de pulsera (Traccar) en verde. | `backend/pytest.log`, `S5_00.3_pytest_backend_210.png` |
| `alembic current` y `alembic check` en Docker | Cabeza `a5b6c7d8e9f0`; «No new upgrade operations detected». | `S5_00.1_alembic_current_docker.png`, `S5_00.4_alembic_check.png` |

### 5.2 Flujos funcionales

Leyenda: ✅ cumplido · 🟡 cumplido en parte · ❌ no cumplido.

| Paso | Historia | Qué se hizo | Resultado esperado | Capturas | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | HU 12 | Se probaron en Swagger y en la app el permiso de indicadores, el listado de últimos valores, la validación de valores fuera de rango, el gráfico de 7, 30 y 90 días y el acceso de un cuidador con y sin permiso y de una cuenta ajena. | Se registra un valor por tipo (la presión con sistólica y diastólica) y un valor fuera de rango se rechaza; se ve el último valor y la evolución; solo ve y registra quien tiene permiso y una cuenta ajena recibe 404. | `S5_01.1_...` a `S5_01.5c2_...` (detalle en 5.3) | ✅ |
| 2 | HU 13 | Se abrió la agenda de hoy (13/11, 13:21). | La agenda muestra 3 de 13 actividades confirmadas. | `S5_02.1a_agenda_confirmadas.png` | ✅ |
| 3 | HU 13 | Se abrió el cumplimiento de 7, 14 y 30 días en la app. | Porcentaje general, gráfico «Por día» y barras «Por categoría» por rango; no cuentan las pendientes de hoy que aún no llegan a su hora. | `S5_02.1b_cumplimiento_7_dias.png`, `S5_02.1b_cumplimiento_14_dias.png`, `S5_02.1b_cumplimiento_30_dias.png` | ✅ |
| 4 | HU 13 | Se consultó `GET /perfiles/{id}/cumplimiento` en Swagger para 7 días y para hoy. | 200 con totales, cumplidas, porcentajes y desglose por categoría y por día; coinciden con la app y con la agenda. | `S5_02_1c1_swagger_7_dias_totales_y_categorias.png`, `S5_02_1c2_swagger_7_dias_por_dia.png`, `S5_02_1d_swagger_cumplimiento_hoy.png` | ✅ |
| 5 | HU 13 | Se comparó la agenda de hoy (15:56) con el cumplimiento de hoy en Swagger (15:57). | La agenda tiene 13 actividades y el cumplimiento cuenta 10: las 3 que aún no llegan a su hora o no tienen hora no cuentan. | `S5_02_2a_agenda_hoy_pendientes_futuras.png`, `S5_02_2b_swagger_hoy_excluye_futuras.png`, `S5_02_2b2_swagger_hoy_por_dia.png` | ✅ |
| 6 | HU 13 | Se consultó el 09/11, se marcó una actividad como `omitida` en la base de datos y se consultó de nuevo. | El total baja de 13 a 12 y la categoría hidratación queda en 0 con porcentaje `null`: las omitidas no cuentan. | `S5_02_2c_swagger_antes_de_omitir.png`, `S5_02_2d_bd_actividad_omitida.png`, `S5_02_2e_swagger_despues_de_omitir.png`, `S5_02_2e2_swagger_despues_de_omitir_por_dia.png` | ✅ |
| 7 | HU 13 | Se probó el límite del rango en Swagger con `hasta=2026-11-13`. | 101 días → 400; 92 días → 200; 93 días → 400 («El rango máximo es de 92 días»); `desde` posterior a `hasta` → 400. | `S5_02_3a_rango_101_dias_400.png`, `S5_02_3b_rango_92_dias_200.png`, `S5_02_3c_rango_93_dias_400.png`, `S5_02_3d_desde_posterior_a_hasta_400.png` | ✅ |
| 8 | HU 14 | Se entró al modo simplificado del Dr. Emmett Brown y se presionó el botón rojo **«SOS Necesito ayuda»**. | Aparece el diálogo de confirmación antes de enviar el aviso. | `S5_03.1a_modo_simplificado_boton_ayuda.png`, `S5_03.1b_modal_confirmar_pedir_ayuda.png` | ✅ |
| 9 | HU 14 | Se confirmó la asistencia en el diálogo (evento de las 17:52) y se envió además un `POST /perfiles/{id}/asistencia` directo desde Swagger (evento de las 18:00). | Aparece el aviso «Listo, avisamos a tus cuidadores» y el evento queda guardado (`201`, `origen: app`, sin atender). | `S5_03.1c_snackbar_aviso_enviado.png`, `S5_03.1f_swagger_post_asistencia.png` | ✅ |
| 10 | HU 14 / 19 | Se abrió **«Eventos de seguridad»** con la cuenta del cuidador. | Se ve la alerta pendiente con el botón **«Atender»**. | `S5_03.1d_eventos_seguridad_alerta_recibida.png`, `S5_03.1g_swagger_get_eventos_pendientes.png` | ✅ |
| 11 | HU 14 / 19 | Se marcó el evento como atendido y se verificó en Swagger. | El evento pasa a atendido (`✓`) y el backend guarda `atendido_en` y `atendido_por_id`. | `S5_03.1e_eventos_seguridad_alerta_atendida.png`, `S5_03.1h_swagger_get_eventos_atendidos.png` | ✅ |
| 12 | HU 17 | Se registró una pulsera (`POST /perfiles/{id}/pulseras`) y una geocerca circular (`POST /perfiles/{id}/geocercas`) en Swagger. | Ambas se guardan vinculadas al perfil con código 201. | `S5_04.1a_swagger_post_registrar_pulsera.png`, `S5_04.1b_swagger_post_crear_geocerca.png` | ✅ |
| 13 | HU 17 | Se abrió el estado de la pulsera y las zonas en la app. | Se ven la batería, la última conexión, las coordenadas y las geocercas activas. | `S5_04.1c_app_pulsera_y_geocercas.png` | ✅ |
| 14 | HU 19 | Se ejecutó `scripts/simular_pulsera.py` con posición, SOS, caída, batería baja (9 %) y recorrido fuera de la geocerca. | El backend acepta las tramas con el token (`TRACCAR_TOKEN`) y crea las alertas automáticas. | `S5_05.1a_consola_simulador_alarmas.png` | ✅ |
| 15 | HU 19 | Se abrió la bandeja de eventos y se consultó el endpoint de eventos en Swagger. | Las 4 alertas de la pulsera (SOS, caída, batería baja y salida de zona) aparecen centralizadas. | `S5_05.1b_app_eventos_pulsera.png`, `S5_05.1c_swagger_get_eventos_pulsera.png` | ✅ |
| 16 | HU 15 | Se abrió el **Asistente de IA** del Dr. Emmett Brown y se hizo una pregunta normal («¿Qué medicamentos toma hoy?»). | La respuesta se basa en los datos del perfil y siempre muestra el aviso de orientación general: no reemplaza a un profesional de la salud. | `S5_05.1d_consola_posiciones_sin_movimiento.png` | Consola con 6 lecturas de posición en el mismo punto, todas `-> 200`. | HU 19: lecturas sin movimiento que originan el evento de inactividad. |
| `S5_05.1e_swagger_evento_inactividad.png` | `GET /eventos?solo_pendientes=true` con un evento `tipo: inactividad`, `origen: sistema`, sin atender, junto a los eventos de la pulsera. | HU 19: la inactividad crea un evento. |
| `S5_05.1f_app_evento_inactividad.png` | Bandeja «Eventos de seguridad» con «Sin movimiento · Dr. Emmett Brown» y el botón «Atender» (22:14). | HU 19: el evento se ve en la app. |
| `S5_06.1a_app_ia_orientacion_general.png` | ✅ |
| 17 | HU 15 | Se preguntó «Le duele el pecho y le cuesta respirar» desde la app y desde Swagger (`POST /perfiles/{id}/ia/consultas`). | Se devuelve el texto fijo de urgencia con el 131 (SAMU) y el *4141, sin consultar al modelo (`"proveedor": "reglas"`). | `S5_06.1b_app_ia_urgencia_131.png`, `S5_06.1c_swagger_ia_urgencia_proveedor_reglas.png` | ✅ |
| 18 | HU 15 | Se consultó la tabla `consulta_ia` en PostgreSQL. | La pregunta de urgencia queda con `contexto_resumen` «ninguno (respuesta fija de urgencia)» y la normal, con solo nombre de pila, edad, alergias, medicamentos activos, cumplimiento de 7 días e indicadores; no hay RUT, correo ni teléfonos. | `S5_06.1d_bd_contexto_resumen_sin_datos_personales.png` | ✅ |
| 19 | HU 19 | Para probar la inactividad, la ventana se redujo de 180 a 5 minutos en el `.env` (`INACTIVIDAD_MINUTOS=5`; `INACTIVIDAD_HASTA_HORA=24` porque la prueba fue después de las 22:00) y se enviaron 6 lecturas de posición en el mismo lugar, una por minuto. | A los pocos minutos la tarea programada crea un evento `inactividad` (`origen: sistema`) que llega a la bandeja del cuidador. | `S5_05.1d_consola_posiciones_sin_movimiento.png`, `S5_05.1e_swagger_evento_inactividad.png`, `S5_05.1f_app_evento_inactividad.png` | ✅ |

**Resultado:** todos los pasos listados quedaron en ✅.

### 5.3 Qué respalda cada captura

| Captura | Qué muestra | Criterio / historia que respalda |
| :--- | :--- | :--- |
| `S5_00.1_alembic_current_docker.png` | `alembic current` dentro de Docker. | Habilitador: migraciones del Sprint 5 aplicadas. |
| `S5_00.4_alembic_check.png` | `alembic check` sin operaciones pendientes. | Habilitador: el modelo coincide con la base de datos. |
| `S5_01.1_permiso_indicadores_swagger.png` | Swagger con el permiso `puede_ver_indicadores`. | HU 12: permiso para ver indicadores. |
| `S5_01.2b_lista_ultimos_valores.png` | Lista con el último valor de cada tipo de indicador. | HU 12: último valor por tipo. |
| `S5_01.3a_peso_700_rechazado_app.png` | La app rechaza un peso de 700. | HU 12: un valor fuera de rango se rechaza. |
| `S5_01.3b_presion_sin_diastolica_422.png` | Presión sin diastólica: respuesta 422. | HU 12: la presión lleva sistólica y diastólica. |
| `S5_01.4a_grafico_peso_30_dias.png` | Gráfico de peso a 30 días. | HU 12: evolución a 30 días. |
| `S5_01.4b_grafico_peso_90_dias.png` | Gráfico de peso a 90 días. | HU 12: evolución a 90 días. |
| `S5_01.4c_grafico_peso_7_dias.png` | Gráfico de peso a 7 días. | HU 12: evolución a 7 días. |
| `S5_01.4d2_serie_vacia_sin_error.png` | Serie sin datos, sin error. | HU 12: rango sin valores. |
| `S5_01.5a_cuidador_sin_permiso_indicadores.png` | Cuidador sin permiso de indicadores. | HU 12: solo ve quien tiene permiso. |
| `S5_01.5b_cuenta_ajena_404.png` | Cuenta ajena: 404. | HU 12: una cuenta ajena recibe 404. |
| `S5_01.5c1_cuidador_ve_indicadores.png` | Cuidador con permiso ve los indicadores. | HU 12: acceso de lectura con permiso. |
| `S5_01.5c1_cuidador_ve_indicadores_sin_boton_registrar.png` | Cuidador con permiso de lectura: no aparece el botón de registrar. | HU 12: registrar exige además `puede_confirmar`. |
| `S5_01.5c2_cuidador_lectura_registrar_403.png` | Cuidador de solo lectura intenta registrar: 403. | HU 12: registrar exige además `puede_confirmar`. |
| `S5_02.1a_agenda_confirmadas.png` | Agenda de hoy a las 13:21 con 3 de 13 confirmadas. | HU 13: base del cálculo de cumplimiento. |
| `S5_02.1b_cumplimiento_7_dias.png` | Cumplimiento a 7 días a las 13:23: 9 % (3 de 33). | HU 13: porcentaje general, por día y por categoría. |
| `S5_02.1b_cumplimiento_14_dias.png` | Cumplimiento a 14 días: igual al de 7 días, porque no hay actividades entre el 30/10 y el 07/11. | HU 13: rango de 14 días. |
| `S5_02.1b_cumplimiento_30_dias.png` | Cumplimiento a 30 días: 14 % (13 de 94), con el 25/10 en 77 %. | HU 13: rango de 30 días. |
| `S5_02_1c1_swagger_7_dias_totales_y_categorias.png` | Swagger 07/11 a 13/11 a las 15:28: total 36, 3 cumplidas, 8,3 %, con las categorías. | HU 13: totales y porcentaje por categoría. |
| `S5_02_1c2_swagger_7_dias_por_dia.png` | Misma respuesta con `por_dia`: 08/11 (13, 0), 09/11 (13, 0) y 13/11 (10, 3, 30 %). | HU 13: serie por día; coincide con el gráfico «Por día» de la app. |
| `S5_02_1d_swagger_cumplimiento_hoy.png` | Swagger de hoy con 8 exigibles (entre las 13:30 y las 14:55): 3 cumplidas, 37,5 %. | HU 13: rango de un solo día. |
| `S5_02_2a_agenda_hoy_pendientes_futuras.png` | Agenda a las 15:56 con scroll: se ven las 3 que aún no cuentan (Paracetamol 20:15, Cena 20:30 y Caminata sin hora). | HU 13: pendientes de hoy que no llegan a su hora. |
| `S5_02_2b_swagger_hoy_excluye_futuras.png` | Swagger de hoy a las 15:57: total 10, 3 cumplidas, 30 %, con las categorías. | HU 13: las pendientes futuras no suman al total. |
| `S5_02_2b2_swagger_hoy_por_dia.png` | `por_dia` de la misma respuesta: 13/11 con 10 y 3. | HU 13: serie del día. |
| `S5_02_2c_swagger_antes_de_omitir.png` | Swagger del 09/11 antes de omitir: total 13, hidratación 1. | HU 13: estado inicial para la prueba de omitidas. |
| `S5_02_2d_bd_actividad_omitida.png` | `UPDATE` en PostgreSQL: la actividad de las 07:30 del 09/11 queda en `omitida` (`UPDATE 1`). | HU 13: preparación de la prueba de omitidas. |
| `S5_02_2e_swagger_despues_de_omitir.png` | Mismo GET: total 12; hidratación en 0 con porcentaje `null`. | HU 13: las omitidas no cuentan. |
| `S5_02_2e2_swagger_despues_de_omitir_por_dia.png` | `por_dia` del 09/11 con total 12. | HU 13: las omitidas no cuentan en la serie por día. |
| `S5_02_3a_rango_101_dias_400.png` | `desde=2026-08-05`: 400, «El rango máximo es de 92 días». | HU 13: rango mayor al máximo. |
| `S5_02_3b_rango_92_dias_200.png` | `desde=2026-08-14` (92 días): 200. | HU 13: borde permitido. |
| `S5_02_3c_rango_93_dias_400.png` | `desde=2026-08-13` (93 días): 400. | HU 13: primer día rechazado. |
| `S5_02_3d_desde_posterior_a_hasta_400.png` | `desde=2026-11-13` y `hasta=2026-11-01`: 400, «'desde' no puede ser posterior a 'hasta'». | HU 13: validación del orden de las fechas. |
| `S5_03.1a_modo_simplificado_boton_ayuda.png` | Modo simplificado con el botón rojo **«SOS Necesito ayuda»**. | HU 14: el botón está en el modo simplificado. |
| `S5_03.1b_modal_confirmar_pedir_ayuda.png` | Diálogo de confirmación. | HU 14: evita activaciones accidentales. |
| `S5_03.1c_snackbar_aviso_enviado.png` | Aviso visual de que la alerta fue enviada. | HU 14: respuesta inmediata al perfil dependiente. |
| `S5_03.1d_eventos_seguridad_alerta_recibida.png` | Bandeja del cuidador con la alerta pendiente y el botón «Atender». | HU 14 / 19: el cuidador recibe el evento. |
| `S5_03.1e_eventos_seguridad_alerta_atendida.png` | Bandeja con el evento atendido (`✓`). | HU 14 / 19: cierre del evento. |
| `S5_03.1f_swagger_post_asistencia.png` | `POST /perfiles/{id}/asistencia` directo desde Swagger: `201 Created`, `tipo: asistencia`, `origen: app`, `atendido_en: null` (evento de las 18:00). | HU 14: el evento queda guardado. |
| `S5_03.1g_swagger_get_eventos_pendientes.png` | `GET /eventos?solo_pendientes=true` con el evento de las 18:00 aún sin atender. | HU 14 / 19: consulta de pendientes. |
| `S5_03.1h_swagger_get_eventos_atendidos.png` | `GET /eventos?solo_pendientes=false` con los dos eventos de asistencia ya atendidos (`atendido_en` y `atendido_por_id`). | HU 14 / 19: trazabilidad de la atención. |
| `S5_04.1a_swagger_post_registrar_pulsera.png` | Registro de `PULSERA-EMMETT-01` (`201`). | HU 17: pulsera registrada con su identificador. |
| `S5_04.1b_swagger_post_crear_geocerca.png` | Zona «Casa Dr. Brown» de 200 m (`201`). | HU 17: zona circular. |
| `S5_04.1c_app_pulsera_y_geocercas.png` | App con batería, última conexión, coordenadas y zonas. | HU 17: última ubicación y batería. |
| `S5_05.1a_consola_simulador_alarmas.png` | `simular_pulsera.py`: SOS, caída, batería al 9 % y un recorrido de 1000 m en 5 pasos; todos responden `200`. La salida de zona se dispara en el paso 2/5 (400 m, fuera de los 200 m de la zona). | HU 19: envío de tramas y alertas. |
| `S5_05.1b_app_eventos_pulsera.png` | Bandeja con 4 alertas: salida de zona, batería baja, caída y SOS. | HU 19: los eventos se ven en la app. |
| `S5_05.1c_swagger_get_eventos_pulsera.png` | `GET /eventos?solo_pendientes=true` con eventos `"origen": "pulsera"` (batería baja, caída y SOS en pantalla). | HU 19: los eventos quedan guardados en el backend. |
| `S5_06.1a_app_ia_orientacion_general.png` | Asistente: pregunta «¿Qué medicamentos toma hoy?» y respuesta con los datos del perfil, marcada «[Modo simulado]», más el aviso de orientación general. | HU 15: la respuesta siempre muestra que es orientación general. |
| `S5_06.1b_app_ia_urgencia_131.png` | Asistente: pregunta de urgencia y texto fijo con el 131 (SAMU) y el *4141, con el aviso. | HU 15: urgencia con texto fijo. |
| `S5_06.1c_swagger_ia_urgencia_proveedor_reglas.png` | `POST /perfiles/{id}/ia/consultas`: `201`, `"proveedor": "reglas"`, texto fijo de urgencia. | HU 15: la urgencia no consulta al modelo. |
| `S5_06.1d_bd_contexto_resumen_sin_datos_personales.png` | `consulta_ia`: dos consultas de urgencia con «ninguno (respuesta fija de urgencia)» y una normal con el resumen de contexto (nombre de pila, edad, alergias, medicamentos activos, cumplimiento 7 días, últimos indicadores). | HU 15: no se envían RUT, correo ni teléfonos al modelo. |

### 5.4 Notas técnicas

- **Cifras de hoy (HU 13).** El total del día crece cuando pasa la hora de cada actividad, por eso las capturas de hoy muestran cifras distintas que no se contradicen. El 13/11: a las 13:23 había 7 actividades exigibles (3 de 7, 43 %, en la app); al pasar las 13:30 eran 8 (3 de 8, 37,5 %, `1d`); desde las 14:57 son 10 (3 de 10, 30 %, `1c` y `2b`). De las 13 actividades de la agenda, las 3 restantes (Paracetamol 20:15, Cena 20:30 y Caminata sin hora) no cuentan hasta que llegue su hora o termine el día. Por eso el 7 días de la app (13:23) marca 33 actividades y el de Swagger (15:28), 36: la diferencia son Almuerzo (13:30) y los dos Omeprazol (14:55 y 14:57).
- **Inactividad (HU 19).** El criterio real es 3 horas sin moverse más de 30 m, entre 08:00 y 22:00. Para la prueba se redujo la ventana a 5 minutos con variables del `.env` y después se restauró el valor por defecto. Por eso el mensaje del evento dice «0.0833333 horas» (5 minutos); con la configuración normal dice «3 horas». Cada lectura responde `eventos: 0` porque el evento lo crea la tarea programada, que corre cada minuto, y no la recepción de la lectura.
- **Asistente de IA (HU 15).** Las capturas se hicieron con `IA_PROVEEDOR=simulado`: la respuesta lo indica con «[Modo simulado: esta respuesta no la generó una IA real.]». Una pregunta de urgencia no llama al modelo ni al simulador (`proveedor: reglas`). En el contexto, el nombre de pila se toma de la primera palabra del nombre del perfil, por eso aparece «Dr.».
- **Actividades omitidas (HU 13).** La API no tiene una ruta para omitir actividades; `omitida` es un estado válido del modelo, reservado. Para la prueba se cambió el estado con un `UPDATE` directo en PostgreSQL y después se restauró el estado original.
- **Integración con Traccar y simulador.** Se configuró `TRACCAR_TOKEN` en el `.env` del backend, de modo que el script `scripts/simular_pulsera.py` envía tramas autenticadas sin un servidor Traccar de producción. La demo usa el simulador y debe decirse así.
- **Trazabilidad de eventos.** Los eventos creados por el botón del perfil dependiente y por la pulsera quedan en una misma tabla de eventos de seguridad, y el cuidador los gestiona con el flujo pendiente / atendido.
- **Seguridad en los endpoints.** El registro de pulseras, la creación de geocercas y la consulta de eventos validan el token JWT y el rol del usuario.

### 5.5 Criterios sin captura todavía

| Historia | Criterio | Estado |
|---|---|---|
| HU 14 | Pulsar el botón varias veces seguidas no duplica el aviso. | Sin captura; cubierto por pruebas del backend. |
| HU 15 | Límite de 30 consultas por usuario al día. | Sin captura; cubierto por pruebas del backend. Tampoco se probó con un proveedor de IA real (la demo es en modo simulado). |
| HU 17 | Solo el titular registra pulseras y zonas. | Sin captura con una cuenta que no sea titular. |
| HU 17 / 19 | Servidor Traccar y pulsera reales. | Pendiente; la demo usa el simulador. |
| HU 12 a 19 | Checklist de aceptación del Product Owner con tres cuentas. | Pendiente de ejecutar. |

## 6. Decisiones por tomar en la reunión del equipo

Lo siguiente ya está implementado como propuesta; si el equipo decide otra cosa, se ajusta.

1. **Push real con FCM (arrastre del Sprint 4).** Propuesta: no hacerlo en la app este sprint y dejarlo como límite conocido, porque quedan 2 días de sprint y después viene la entrega final. Hacerlo implica crear el proyecto de Firebase, agregar `google-services.json`, instalar `firebase_messaging` y probar en un celular real, lo que puede romper la compilación justo antes de la demo. La demo queda cubierta: el backend genera los avisos y la app los muestra al abrir Avisos. El lado del backend ya está en `main` (apagado por defecto, con 6 pruebas), así que si se quiere después solo faltaría la parte de la app (se vería después del sábado 14). Cómo se documenta: el texto de límite conocido en el README y en el contrato (`backend/docs/Notas_FCM_Sprint5.md`), en el informe 2.6 (límites y proyecciones) y en este backlog, donde la HU 9 queda parcial sin push real, igual que en el Sprint 4.
2. **Proveedor de la IA.** Hoy responde en modo simulado (sin red ni clave). Decidir si se prueba con la API real de un modelo de lenguaje para la demo; la clave va en el `.env` local y nunca en el repositorio.
3. **Health Connect (HU 18).** Requiere que la app lea los datos en un dispositivo con Health Connect y los envíe como indicadores con `fuente = pulsera`. Decidir si se hace en este sprint o pasa al Sprint 6.
4. **Pulsera real o simulador en la demo.** Sin pulsera, la demo usa `simular_pulsera.py` y debe decirse así (la evidencia de esta versión se hizo con el simulador).
5. **Quién recibe el nivel 2 de las alertas** (decisión 9 del Sprint 4). Para cambiarlo basta `ALERTA_NIVEL_2_INCLUYE_TITULAR=true`.
6. **Solo Sergio crea migraciones de Alembic** en este sprint, para mantener una única cabeza (`a5b6c7d8e9f0`).

## 7. Trabajo que pasa al Sprint 6

Se confirma al cierre del sprint. Lo previsto del Product Backlog: registro manual de glucosa, recordatorios extendidos, farmacias cercanas vía IA, pruebas integrales, documentación (manual técnico y Docker) e informe final. Si no se cierran en este sprint, pasan también la HU 18, la prueba con Traccar y pulsera reales y la prueba de la IA con un proveedor real. El push real con FCM en la app (HU 9, parcial) queda como límite conocido y proyección, salvo que el equipo decida lo contrario.

## 8. Seguimiento de commits del sprint

Acuerdo del Sprint 3: subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint.

**Estado al 07-11:** historial verificado con `git log --since=2026-11-02`. Los commits de la app y de la evidencia se anotan al subirlos.

| Fecha | Qué se subió | Quién | Commits |
|---|---|---|---|
| 05-11 | Configuración, permiso `puede_ver_indicadores`, esquemas, servicios y rutas del Sprint 5 | Benjamín | `d77e9c1`, `6bb5659`, `b0f9742`, `2228cb2`, `cd64277` |
| 05-11 | 62 pruebas nuevas, contrato de API, variables nuevas, `pytest.log` y simulador de pulsera | Benjamín | `21d86b8`, `de429a1`, `88db528` |
| 06-11 | Modelos y migraciones de las tablas del Sprint 5 | Sergio | `3b3483c`, `ff2aa1c` |
| 06-11 | `modelo_datos.md`, diagrama ER y checklist del Product Owner | Sergio | `3131080`, `0412152`, `6a71ed7` |
| 06-11 | Servidor Traccar, contexto de IA y casos de prueba | Sergio | `9c93e43`, `4fd14bb`, `65d9ec5` |
| 07-11 | Conexión de los routers del Sprint 5 en `main.py` | Benjamín | `11bcf7c` |
| — | Pantallas de la app del Sprint 5 y su evidencia (`S5_xx`) | Matías | ⬜ completar con los hashes al subirlos |
| — | Checklist de aceptación del Product Owner ejecutado | Sergio | ⬜ sin commits |
