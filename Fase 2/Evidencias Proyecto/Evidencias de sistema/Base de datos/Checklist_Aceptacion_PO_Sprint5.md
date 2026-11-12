# Checklist de aceptación — Product Owner (Sprint 5)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de cerrar las HU 12, 13, 14, 15, 17, 18 y 19, el Product Owner valida que lo construido cumple los criterios de aceptación. Quien prueba no escribió el código y usa tres cuentas (titular, cuidador autorizado y persona ajena).

> Ejecución del 10 y el 12-nov-2026: las filas 2 a 10 se probaron en Swagger (✅); las filas 12 a 23, 25 y 27 a 31 se verificaron en un entorno de prueba (copia local del backend con base nueva y el simulador de la pulsera) y se marcan «✅ entorno de prueba» hasta repetirlas en el Docker del proyecto; las filas 1 y 11 están probadas en parte; las filas 24 y 26 siguen en ⏳. Marca ✅ o ❌ al probar y anota lo observado. **Alcance real:** el aviso llega a la pantalla Avisos; el push con FCM no está implementado. La pulsera real y el servidor Traccar se prueban aparte (ver `Aplicacion/backend/traccar/README.md`); mientras tanto se usa el simulador `backend/scripts/simular_pulsera.py`.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend` (las migraciones corren solas).
2. Abre `http://localhost:8000/docs` y registra tres usuarios: **titular**, **cuidador** y **ajena**. Vincula al cuidador con `POST /perfiles/{id}/cuidadores` (con `puede_ver_indicadores` y `puede_confirmar` en verdadero, salvo donde se indique).
3. Para la pulsera: define `TRACCAR_TOKEN` en `.env` y usa el simulador con `--token` y `--id` (ver su encabezado).
4. Los endpoints están en `Contrato_API_Sprint5.md`.

## Habilitadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 1 | Las migraciones nuevas se aplican en una base vacía y `alembic check` no detecta diferencias | `docker compose up --build`; luego `docker compose exec api alembic current` debe mostrar `a5b6c7d8e9f0` | ✅ parcial | En una base vacía las migraciones se aplicaron hasta `a5b6c7d8e9f0` (cabeza única) y `alembic check` respondió «No new upgrade operations detected». Falta guardar la captura de `alembic current` en el Docker del proyecto. |
| 2 | El permiso `puede_ver_indicadores` se puede dar y quitar | `PATCH /perfiles/{id}/cuidadores/{vinculo}` | ✅ | Probado en Swagger (10-nov): `puede_ver_indicadores` pasó de `false` a `true` y de `true` a `false` sin errores y se dejó en `true`; el vínculo conservó el nivel 2. Nota: la ruta real es `PUT /perfiles/{id}/cuidadores/{acceso_id}`; el contrato dice `PATCH`, pero ese método no existe en la API. |

## HU 12 — Registro de indicadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 3 | El titular registra peso, presión, glucosa y pulso | `POST /perfiles/{id}/indicadores` por cada tipo → 201 | ✅ | Probado en Swagger (10-nov): `POST /perfiles/{id}/indicadores` con peso (62.5), presión (128/82), glucosa (105) y pulso (74) → 201 en los cuatro; la unidad se asigna sola (kg, mmHg, mg/dL, lpm). |
| 4 | La presión exige diastólica menor que la sistólica; un valor absurdo se rechaza | Presión sin diastólica y peso 700 → 422 | ✅ | Probado en Swagger (10-nov): presión sin diastólica y peso 700 fueron rechazados con error de validación («La presión necesita sistólica y diastólica» y «El valor de peso debe estar entre 1 y 400»). |
| 5 | El historial y el último valor de cada tipo se consultan | `GET .../indicadores` y `.../ultimos` | ✅ | Probado en Swagger (10-nov): `GET .../indicadores` devolvió las cuatro mediciones, de la más reciente a la más antigua, y `GET .../ultimos` devolvió la última de cada tipo. |
| 6 | Un cuidador sin `puede_ver_indicadores` recibe 403; con el permiso ve los datos; una cuenta ajena recibe 404 | Probar con las tres cuentas | ✅ | Probado con las tres cuentas (10-nov): cuidador sin `puede_ver_indicadores` → 403; con el permiso → 200 con las mediciones; cuenta ajena → 404 («perfil no encontrado»). |
| 7 | El rol de solo lectura no puede registrar | Cuidador con `puede_confirmar` falso → 403 | ✅ | Probado (10-nov): con el cuidador en `puede_confirmar` falso (y `puede_ver_indicadores` verdadero), `POST .../indicadores` respondió 403. |

## HU 12 — Evolución de indicadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 8 | La serie entrega puntos ordenados, mínimo, máximo y promedio | `GET .../indicadores/serie?tipo=peso&dias=30` | ✅ | Probado en Swagger (10-nov): con tres pesos (62.5, 64 y 61.5), la serie de 30 días devolvió los puntos del más antiguo al más nuevo, con mínimo 61.5, máximo 64 y promedio de unos 62.67. |
| 9 | Sin mediciones en el rango, la serie viene vacía sin error | Rango sin datos | ✅ | Probado en Swagger (10-nov): tras borrar la única medición de glucosa, `GET .../serie?tipo=glucosa&dias=30` respondió sin error con `puntos` vacío y mínimo, máximo y promedio nulos. |

## HU 13 — Historial de cumplimiento

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 10 | El porcentaje general, por categoría y por día coincide con la agenda | Confirmar algunas actividades y comparar con `GET .../cumplimiento` | ✅ | Probado en Swagger (10-nov): la agenda del 8-nov tenía 14 actividades con 6 confirmadas; `GET .../cumplimiento?desde=2026-11-08&hasta=2026-11-08` devolvió total 14, cumplidas 6 y 42.9 %, todo en medicamentos y con una sola entrada en `por_dia`. |
| 11 | Las omitidas no cuentan; las pendientes futuras de hoy no cuentan | Omitir una actividad y revisar el total | ✅ parcial | Parte de las omitidas probada (10-nov): se marcó una actividad como omitida directamente en la base de datos (la API no tiene una ruta para eso) y el total del 8-nov bajó de 14 a 13 y el porcentaje subió a 46.2; después se restauró. Pendiente probar en Swagger que las pendientes futuras de hoy no cuentan. |
| 12 | Un rango mayor a 92 días se rechaza | `desde` hace 100 días → 400 | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): un rango de 101 días respondió 400 («El rango máximo es de 92 días»). |

## HU 14 — Botón de asistencia

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 13 | Al pulsar el botón se crea un evento y se avisa a titular y cuidadores | `POST .../asistencia`; revisar `GET /eventos` y los avisos de cada cuenta | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): `POST .../asistencia` → 201; el evento lo vieron el titular y el cuidador, y la cuenta ajena no vio ninguno. |
| 14 | Pulsarlo varias veces seguidas no duplica el aviso | Dos `POST` en menos de un minuto → 201 y luego 200 con el mismo evento | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): dos `POST` seguidos → 201 y luego 200 con el mismo evento. |
| 15 | El cuidador puede marcar el evento como atendido | `POST /eventos/{id}/atendido` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): el cuidador marcó el evento como atendido → 200. |

## HU 17 — Pulsera y geocercas

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 16 | Se registra una pulsera y no se puede repetir el identificador | `POST .../pulseras` dos veces | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): el primer registro → 201 y repetir el identificador → 409. |
| 17 | La última ubicación y la batería se ven en `GET .../ubicacion` | Simulador: `posicion --bateria 80` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): tras enviar una posición con el simulador, `GET .../ubicacion` → 200 con la posición, la hora de la última conexión y el porcentaje de batería. |
| 18 | Se crea una geocerca y se indica en cuáles está la persona | `POST .../geocercas` y luego `posicion` en su centro | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): `POST .../geocercas` → 201 y, con la posición en su centro, `GET .../ubicacion` indica que la persona está dentro de «Casa». |
| 19 | Al salir de la geocerca se crea un evento de salida | Simulador: `recorrido --metros 400` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): el simulador con `recorrido --metros 400` creó un evento `geocerca_salida`. |
| 20 | Una lectura con token incorrecto se rechaza | Simulador con `--token` erróneo → 401 | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): una lectura con token incorrecto → 401 («Token de Traccar inválido»). |

## HU 19 — Alertas de la pulsera

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 21 | El botón SOS crea un evento `sos` | Simulador: `sos` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): el simulador con `sos` creó un evento `sos`. |
| 22 | La caída crea un evento `caida` | Simulador: `caida` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): el simulador con `caida` creó un evento `caida`. |
| 23 | La batería baja crea un evento, sin repetirlo en 2 horas | Simulador: `bateria` dos veces | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): dos lecturas de batería baja seguidas (9 % y 8 %) crearon un solo evento. |
| 24 | La inactividad (3 h sin moverse, entre 08:00 y 22:00) crea un evento | Se cubre con pruebas automáticas; con la pulsera real, observar una tarde | ⏳ | No probado: se cubre con pruebas automáticas; con la pulsera real, observar una tarde. |
| 25 | Cada evento llega a titular y cuidadores con alertas | `GET /eventos` con cada cuenta | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): el titular y el cuidador vieron los mismos eventos; la cuenta ajena no vio ninguno. |
| 26 | Con la pulsera y Traccar reales, las alertas llegan igual | Ver `traccar/README.md` | ⏳ | Depende de comprar y configurar la pulsera. |

## HU 15 — Asistente de IA

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 27 | Responde con el aviso de que no reemplaza a un profesional | `POST .../ia/consultas` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): `POST .../ia/consultas` → 201 con el aviso de que no reemplaza a un profesional (IA en modo simulado). |
| 28 | Una pregunta de urgencia responde 131 y *4141 | Caso 6 de `casos_prueba_ia.md` | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): la pregunta de urgencia respondió la respuesta fija con 131 y *4141, con proveedor `reglas` (sin consultar al modelo). |
| 29 | No se entregan RUT, correo ni teléfonos | Casos 8 y 9 | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): con un perfil que sí tiene RUT y un contacto con teléfono, las preguntas por el RUT, el teléfono y el correo no los entregaron: el contexto de la IA solo incluye el primer nombre del perfil. |
| 30 | Después de 30 consultas en el día responde 429 | Caso 12 | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): tras 30 consultas en el día, la consulta 31 respondió 429. |
| 31 | Una cuenta ajena recibe 404 | Caso 13 | ✅ entorno de prueba | Verificado en un entorno de prueba (12-nov): una cuenta ajena al perfil recibió 404. |

## Cierre

Resultado general: 9 criterios ✅ en Swagger (filas 2 a 10), 18 ✅ en entorno de prueba (filas 12 a 23, 25 y 27 a 31) y 2 ✅ parciales (filas 1 y 11); pendientes las filas 24 y 26. &nbsp; Fecha: 12-11-2026 &nbsp; Observaciones: la ruta real para cambiar los permisos del cuidador es `PUT`, no `PATCH` como dice el contrato; la API no tiene ruta para marcar una actividad como omitida, por lo que esa prueba se hizo en la base de datos; la IA se probó solo en modo simulado; la inactividad (fila 24) y la pulsera con Traccar reales (fila 26) no se probaron.
