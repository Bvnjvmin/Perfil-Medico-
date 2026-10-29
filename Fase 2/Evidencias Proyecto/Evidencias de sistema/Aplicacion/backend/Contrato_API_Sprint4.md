# Contrato de API — Sprint 4

**Autor:** Benjamín Leiva (Backend) · **Estado:** rutas implementadas y probadas en el backend (21-10). Matías debe revisarlo contra la app; cualquier cambio se acuerda antes de tocar las rutas. La referencia exacta siempre es `/docs` de FastAPI.

## Convenciones

- Todas las rutas exigen JWT, como las actuales.
- Matriz de acceso de siempre: titular todo; cuidador solo lo que su vínculo permite; cuenta sin vínculo recibe 404.
- La fecha la envía la app como `?fecha=AAAA-MM-DD`.
- Los errores devuelven `detail` en español, para mostrarlo tal cual.
- Las horas son `HH:MM` o `HH:MM:SS`. El backend interpreta los horarios en la zona `America/Santiago` (`ZONA_HORARIA`).

## 1. Horarios de medicamentos y rutinas (habilitador)

| Método y ruta | Quién | Cuerpo | Respuesta |
|---|---|---|---|
| `POST /medicamentos/{id}/horarios` | titular o cuidador con `puede_editar_rutinas` | `{ "hora": "08:00" }` | 201 con `{ id, hora, medicamento_id, rutina_id }`; 409 «Ya existe un horario a esa hora»; 403 sin permiso; 404 sin vínculo |
| `GET /medicamentos/{id}/horarios` | quien ve el perfil | | 200, lista ordenada por hora |
| `POST /rutinas/{id}/horarios` | igual | `{ "hora": "08:00" }` | igual que el de medicamentos |
| `GET /rutinas/{id}/horarios` | quien ve el perfil | | 200, lista ordenada por hora |
| `DELETE /horarios/{horario_id}` | igual que el `POST` | | 204; 404 «Horario no encontrado» |

Si un medicamento o rutina no tiene horarios, la actividad usa su `hora_inicio` / `hora` de siempre, así que lo anterior sigue funcionando.

## 2. Generación de actividades

- Sin ruta pública. Un ciclo dentro del backend (`TAREAS_PROGRAMADAS=true`, cada `TAREAS_INTERVALO_SEGUNDOS` = 60 s) crea las actividades de hoy y de los próximos `GENERAR_DIAS_ADELANTE` = 2 días, una por horario, sin duplicar. Borra las pendientes de horarios que ya no existen.
- `GET /perfiles/{id}/actividades?fecha=` sigue completando las que falten, y ahora devuelve una actividad por cada horario del día. `hora` viene siempre informada.
- El `estado` puede ser `pendiente`, `confirmada` o `vencida` (pendiente cuando terminó el día). `omitida` existe en el modelo pero ninguna ruta la usa todavía. La app debe tolerar estados desconocidos.

## 3. Dispositivos y notificaciones (HU 9)

| Método y ruta | Quién | Cuerpo | Respuesta |
|---|---|---|---|
| `POST /dispositivos` | usuario autenticado | `{ "token": "...", "plataforma": "android" }` (`android` o `ios`) | 201 con `{ id, plataforma, creado_en }`; 200 si el token ya era suyo; si era de otra cuenta, se reasigna a esta |
| `DELETE /dispositivos/{token}` | el dueño | | 204; 404 si no es suyo |

**Qué se envía hoy:** nada llega al celular. `NOTIFICADOR="log"` escribe cada envío en el log del backend. El push real (FCM) requiere elegir proveedor y credenciales; cuando exista, el contenido será el mismo aviso de la sección 4.

## 4. Avisos: recordatorios y alertas (HU 9 y HU 10)

| Método y ruta | Quién | Cuerpo | Respuesta |
|---|---|---|---|
| `GET /alertas?solo_no_leidas=false&limite=50` | usuario autenticado | | 200, avisos propios, los más nuevos primero: `{ id, perfil_id, actividad_id, tipo, nivel, mensaje, creada_en, leida_en }` |
| `POST /alertas/{id}/leida` | el destinatario | | 200 con el aviso; 404 si no es suyo |

`tipo` es `recordatorio` (nivel 0) o `alerta` (nivel 1 o 2).

### Reglas (parámetros en `app/core/config.py`)

| Aviso | Cuándo | Quién lo recibe |
|---|---|---|
| Recordatorio, nivel 0 | desde 10 min antes de la hora (`RECORDATORIO_MINUTOS_ANTES`) | titular y vinculados con `recibe_alertas` |
| Alerta, nivel 1 | 30 min después de la hora sin confirmar (`ALERTA_PLAZO_1_MINUTOS`) | titular y vinculados con `recibe_alertas` y `nivel_escalamiento = 1` |
| Alerta, nivel 2 | 60 min después de la hora sin confirmar (`ALERTA_PLAZO_2_MINUTOS`) | vinculados con `recibe_alertas` y `nivel_escalamiento = 2` |

- Confirmar la actividad detiene el escalamiento.
- Un aviso no se repite: hay una restricción única por actividad, destinatario, tipo y nivel.
- Al terminar el día, las pendientes pasan a `vencida`.
- El mensaje informa que la actividad no fue confirmada; no afirma una emergencia. Ejemplo: «La actividad «Losartán» de Rosa (programada a las 08:00) aún no fue confirmada.»

## 5. Cambios a rutas existentes

- Cuidadores (`POST` y `PUT /perfiles/{id}/cuidadores`): aceptan y devuelven `recibe_alertas` (bool) y `nivel_escalamiento` (1 a 3).
- `GET /panel?fecha=`: sin cambios en la respuesta; la app ya lo usa en lugar de una llamada por perfil.
- Al borrar un medicamento, una rutina o un perfil se borran también sus horarios y avisos.

## 6. Pruebas que acompañan

`app/tests/test_horario.py` (10) y `app/tests/test_avisos.py` (19): matriz de permisos y escalamiento, sin fechas fijas; el motor recibe la hora actual como parámetro (`procesar_avisos(db, ahora)`) y el notificador se reemplaza por uno falso. Suite completa: **148 de 148** (119 anteriores + 29 nuevas).

## 7. Pendiente y preguntas abiertas

1. Proveedor de push (FCM) y dónde viven sus credenciales. Sin eso no hay notificación en el celular.
2. ¿Escalan todas las actividades o solo los medicamentos? Hoy escalan todas.
3. Plazos definitivos (10 / 30 / 60 minutos son una propuesta).
4. Si el backend corre con varias réplicas, el ciclo correría en cada una.

## 8. Avance

| Tarea | Estado | Fecha | Commit |
|---|---|---|---|
| Contrato revisado con Matías y Sergio | 🟡 Matías revisó contra la app el 27-10 (sección 9); falta el visto bueno de Sergio | 27-10 | |
| Rutas de horarios | 🟡 listas, falta subir | 21-10 | |
| Tarea programada de actividades | 🟡 lista, falta subir | 21-10 | |
| Dispositivos y avisos | 🟡 listos, falta subir (sin push real) | 21-10 | |
| Motor de alertas | 🟡 listo, falta subir | 21-10 | |
| Pruebas sin fechas fijas | ✅ 148 de 148 | 21-10 | |

## 9. Revisión de la app (Matías Pizarro, 27-10-2026)

**Alcance:** se comparó este contrato con las rutas del backend (`app/api/routes/`) y con las llamadas de la app (`lib/services/api_service.dart`, `lib/models/`). Además, la app se probó contra el backend en el emulador el 25-10 (`Evidencia_Sprint4.md`, capturas `S4_*`). No se encontraron diferencias entre el contrato y el backend.

### 9.1 Rutas que la app usa hoy

| Ruta | Dónde se usa | Resultado |
|---|---|---|
| `GET /perfiles/{id}/actividades?fecha=` | Agenda y modo simplificado | ✅ Coincide con el contrato (sección 2) |
| `POST /actividades/{id}/confirmar` y `/desconfirmar` | Agenda y modo simplificado | ✅ Sin cambios |
| `GET /panel?fecha=` | Panel de dependientes | ✅ Coincide (sección 5) |
| `GET /alertas?solo_no_leidas=` | Pantalla Avisos y campana del Home | ✅ Coincide (sección 4) |
| `POST /alertas/{id}/leida` | Al tocar un aviso | ✅ Coincide (sección 4) |

### 9.2 Rutas del contrato que la app todavía no usa

| Ruta o campo | Estado en la app | Cómo se probó |
|---|---|---|
| `POST /dispositivos` y `DELETE /dispositivos/{token}` | No se llaman: la app no registra el dispositivo (falta definir FCM) | `/docs`, `S4_02.0` |
| `POST/GET /medicamentos/{id}/horarios`, `POST/GET /rutinas/{id}/horarios`, `DELETE /horarios/{id}` | Sin pantalla; la app muestra los horarios como actividades de la agenda | `/docs`, `S4_01.1` |
| `recibe_alertas` y `nivel_escalamiento` en `POST` y `PUT /perfiles/{id}/cuidadores` | La app no los envía al compartir un perfil: el cuidador queda con `recibe_alertas = true` y `nivel_escalamiento = 1`. No hay forma de configurar el nivel 2 desde la app | `/docs`, `S4_04.3` y `S4_04.4` |

### 9.3 Cumplimiento de lo que el contrato pide a la app

- **Estados desconocidos:** la app guarda `estado` como texto y solo distingue `confirmada` y `vencida`; cualquier otro valor (por ejemplo `omitida`) se trata como no confirmada y no rompe. ✅
- **Campos de un aviso:** el modelo `Alerta` lee los 8 campos de `AlertaOut` (`id`, `perfil_id`, `actividad_id`, `tipo`, `nivel`, `mensaje`, `creada_en`, `leida_en`) y tolera valores ausentes. ✅
- **Errores:** la app muestra el `detail` en español tal cual y un mensaje de conexión cuando no hay respuesta (`S4_10`). ✅
- **Fecha:** se envía como `?fecha=AAAA-MM-DD`. ✅

### 9.4 Observaciones

1. **Ruta de cuidadores:** la sección 5 menciona `PUT /perfiles/{id}/cuidadores`; en el backend lleva el id del vínculo (`PUT /perfiles/{id}/cuidadores/{acceso_id}`, usado en `S4_04.4`). Conviene corregir el texto del contrato.
2. **Fecha de los avisos:** `creada_en` llega sin conversión. En las capturas del 25-10 la pantalla Avisos la mostraba en UTC (una alerta de una actividad de las 16:30 aparecía como 20:00); en las del 28-10 (`S4_05.3` a `S4_05.5`) aparece en hora de Chile. Falta confirmar si hubo un cambio y si la conversión la hace la app o el backend.
3. **A quién llega el nivel 2:** hoy solo a los vinculados con `nivel_escalamiento = 2`; el titular y los vinculados en nivel 1 no lo reciben aunque pase el tiempo. Falta que el Product Owner confirme si eso es lo esperado (decisión 9 del Sprint Backlog). Además, el esquema acepta `nivel_escalamiento = 3`, pero el motor solo crea los niveles 0, 1 y 2.
4. **Dependencia de la configuración:** los avisos solo se generan con `TAREAS_PROGRAMADAS=true`; conviene dejar esa variable (y las demás del Sprint 4) en `.env.example`.

### 9.5 Resultado

**Aprobado con observaciones** para el alcance del Sprint 4: las rutas que la app usa coinciden con el contrato. Las observaciones 1 a 3 se resuelven antes de cerrar el sprint o pasan al Sprint 5. Falta el visto bueno de Sergio (Product Owner), en especial sobre la observación 3.

| Revisó | Fecha | Visto bueno |
|---|---|---|
| Matías Pizarro (App móvil) | 27-10-2026 | ✅ |
| Sergio Ocares (Product Owner) | | ⬜ |
