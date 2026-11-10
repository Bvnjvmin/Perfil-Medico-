# Contrato de API — Sprint 5

Complementa el contrato del Sprint 4. Todos los endpoints exigen `Authorization: Bearer <token>` salvo `/traccar/posiciones`, que usa la clave del servidor Traccar. La documentación interactiva está en `/docs`.

## Reglas de acceso (igual que en el Sprint 4)

- Un perfil ajeno responde **404**; un perfil visible pero sin el permiso necesario responde **403**.
- Nuevo permiso `puede_ver_indicadores` (columna que ya existía en `perfil_acceso`): controla indicadores, pulseras, ubicación y geocercas. El titular siempre lo tiene.
- Registrar o borrar indicadores exige además `puede_confirmar`. El rol `lectura` no puede registrar.
- `PATCH /perfiles/{id}/cuidadores/{vinculo}` y la creación aceptan ahora `puede_ver_indicadores` (booleano).

## Indicadores de salud (HU 12)

| Método y ruta | Descripción |
|---|---|
| `POST /perfiles/{id}/indicadores` | Registra una medición. 201. |
| `GET /perfiles/{id}/indicadores?tipo=&desde=&hasta=&limite=100` | Historial, del más reciente al más antiguo. |
| `GET /perfiles/{id}/indicadores/ultimos` | La última medición de cada tipo. |
| `GET /perfiles/{id}/indicadores/serie?tipo=peso&dias=30` | Serie lista para graficar con mínimo, máximo y promedio (`dias` de 1 a 365). |
| `DELETE /perfiles/{id}/indicadores/{indicador_id}` | Borra una medición. 204. |

Tipos: `peso` (kg), `presion` (mmHg), `glucosa` (mg/dL), `frecuencia_cardiaca` (lpm).

```json
{ "tipo": "presion", "valor": 128, "valor_secundario": 82, "nota": "después de caminar" }
```

- En la presión, `valor` es la sistólica y `valor_secundario` la diastólica (obligatoria y menor que la sistólica). En los demás tipos `valor_secundario` no se envía.
- `medido_en` es opcional (por defecto, ahora) y no puede estar en el futuro. `fuente` es `manual` o `pulsera`.
- Los rangos solo evitan errores de tipeo (peso 1–400, sistólica 30–300, glucosa 10–1000, pulso 20–300); no son diagnóstico. Fuera de rango responde **422**.

## Historial de cumplimiento (HU 13)

`GET /perfiles/{id}/cumplimiento?desde=2026-11-01&hasta=2026-11-07` (por defecto, los últimos 7 días hasta hoy; máximo 92 días). Si `desde` es posterior a `hasta` o el rango pasa de 92 días responde **400**.

Respuesta: `total`, `cumplidas`, `porcentaje` (nulo si no hubo actividades exigibles), `por_categoria` (medicamentos, hidratacion, alimentacion, otras) y `por_dia` para graficar.

- Cuentan: confirmadas, vencidas y pendientes de días pasados (o de hoy con la hora ya cumplida).
- No cuentan: omitidas y las pendientes de hoy sin hora o con la hora aún por llegar.

## Botón de asistencia y eventos (HU 14 y 19)

| Método y ruta | Descripción |
|---|---|
| `POST /perfiles/{id}/asistencia` | Botón «Necesito ayuda». Cuerpo opcional `{ "mensaje": "..." }` (máx. 200). 201 con el evento. |
| `GET /eventos?solo_pendientes=false&limite=50` | Eventos de los perfiles propios y de aquellos donde el usuario recibe alertas (pantalla Avisos). |
| `POST /eventos/{evento_id}/atendido` | Marca el evento como atendido (idempotente). |

`tipo`: `asistencia`, `sos`, `caida`, `bateria_baja`, `inactividad`, `geocerca_salida`. Un mismo aviso no se repite dentro de su ventana (10 min por defecto; 1 min el botón; 120 min batería; 180 min inactividad), de modo que pulsar varias veces no llena de avisos a los cuidadores. Si se repite dentro de la ventana, el botón responde **200** con el evento ya existente en vez de 201.

Quién puede pulsar: el titular y los cuidadores con `puede_confirmar`. Los avisos llegan al titular y a los cuidadores vinculados, por el notificador configurado (por ahora solo log; el push con FCM sigue pendiente).

## Pulsera, ubicación y geocercas (HU 17)

> Registrar, editar o borrar pulseras y crear, editar o borrar geocercas es solo del **titular**. Leer pulseras, ubicación y geocercas exige `puede_ver_indicadores`.

| Método y ruta | Descripción |
|---|---|
| `POST /perfiles/{id}/pulseras` | Registra una pulsera: `{ "identificador": "356938035643809", "nombre": "Pulsera de la abuela", "modelo": "..." }`. El identificador es el `uniqueId` de Traccar (normalmente el IMEI) y debe ser único. |
| `GET /perfiles/{id}/pulseras` | Lista. |
| `PATCH /perfiles/{id}/pulseras/{pulsera_id}` | Cambia nombre, modelo o `activa`. |
| `DELETE /perfiles/{id}/pulseras/{pulsera_id}` | Elimina la pulsera y sus posiciones. 204. |
| `GET /perfiles/{id}/ubicacion` | Última posición conocida, pulsera (batería, última conexión) y nombres de las geocercas donde está. |
| `GET /perfiles/{id}/ubicacion/historial?limite=200` | Últimas posiciones. |
| `POST/GET/PATCH/DELETE /perfiles/{id}/geocercas` | Zonas circulares: `{ "nombre": "Casa", "latitud": -33.45, "longitud": -70.66, "radio_m": 150 }`. Radio de 20 a 50 000 m; máximo 20 por perfil. |

## Recepción desde Traccar (uso interno)

`POST` o `GET /traccar/posiciones?token=<TRACCAR_TOKEN>` (también acepta el encabezado `X-Traccar-Token`). Sin `TRACCAR_TOKEN` configurado responde 503; token incorrecto, 401; pulsera no registrada, 404; datos incompletos, 422.

La app móvil **no** llama a este endpoint. Detecta SOS, caída, batería baja, salida de geocerca e inactividad.

## Asistente de IA (HU 15)

| Método y ruta | Descripción |
|---|---|
| `POST /perfiles/{id}/ia/consultas` | `{ "pregunta": "¿Puedo tomar el paracetamol con el desayuno?" }`. 201 con `respuesta`, `proveedor` y `aviso`. |
| `GET /perfiles/{id}/ia/consultas` | Historial de consultas del usuario sobre ese perfil. |

- Es orientación general, no un diagnóstico. **Mostrar siempre el campo `aviso`** bajo la respuesta.
- Si la pregunta suena a urgencia, la respuesta es fija e indica llamar al 131 (SAMU) o *4141, y no se envía al modelo.
- Máximo 30 consultas por usuario al día (**429**). Si el proveedor falla responde **503** y no se guarda nada.

## Para Matías (Flutter)

1. **Avisos / Eventos**: `GET /eventos` al abrir la pantalla; botón «Marcar atendido» → `POST /eventos/{id}/atendido`. El color o ícono puede depender de `tipo`.
2. **Botón «Necesito ayuda»** en la pantalla del titular → `POST /perfiles/{id}/asistencia`; confirmar con un mensaje del tipo «Avisamos a tus cuidadores».
3. **Indicadores**: formulario de registro por tipo (la presión pide dos campos), lista de últimos valores y gráfico con `/serie`.
4. **Cumplimiento**: gráfico de barras con `por_dia` y tarjetas con `por_categoria`.
5. **Pulsera**: pantalla de registro (identificador), mapa con `/ubicacion`, y administración de geocercas. Sin pulsera, `pulsera` y `posicion` vienen nulos: mostrar un estado vacío.
6. **Asistente de IA**: campo de pregunta, respuesta y el `aviso` siempre visible; manejar 429 y 503 con mensajes claros.
7. Ocultar indicadores, pulsera y ubicación a quien no tenga `puede_ver_indicadores` (el servidor responde 403).
