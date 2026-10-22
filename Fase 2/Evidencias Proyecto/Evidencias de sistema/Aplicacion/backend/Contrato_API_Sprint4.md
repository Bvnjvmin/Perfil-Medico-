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
| Contrato revisado con Matías y Sergio | ⬜ | | |
| Rutas de horarios | 🟡 listas, falta subir | 21-10 | |
| Tarea programada de actividades | 🟡 lista, falta subir | 21-10 | |
| Dispositivos y avisos | 🟡 listos, falta subir (sin push real) | 21-10 | |
| Motor de alertas | 🟡 listo, falta subir | 21-10 | |
| Pruebas sin fechas fijas | ✅ 148 de 148 | 21-10 | |
