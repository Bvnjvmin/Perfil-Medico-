# Checklist de aceptación — Product Owner (Sprint 5)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de cerrar las HU 12, 13, 14, 15, 17, 18 y 19, el Product Owner valida que lo construido cumple los criterios de aceptación. Quien prueba no escribió el código y usa tres cuentas (titular, cuidador autorizado y persona ajena).

> Ejecución parcial (10-nov-2026): las filas 2 a 10 están probadas (✅), la 11 está probada en parte y el resto sigue en ⏳. Marca ✅ o ❌ al probar y anota lo observado. **Alcance real:** el aviso llega a la pantalla Avisos; el push con FCM no está implementado. La pulsera real y el servidor Traccar se prueban aparte (ver `Aplicacion/backend/traccar/README.md`); mientras tanto se usa el simulador `backend/scripts/simular_pulsera.py`.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend` (las migraciones corren solas).
2. Abre `http://localhost:8000/docs` y registra tres usuarios: **titular**, **cuidador** y **ajena**. Vincula al cuidador con `POST /perfiles/{id}/cuidadores` (con `puede_ver_indicadores` y `puede_confirmar` en verdadero, salvo donde se indique).
3. Para la pulsera: define `TRACCAR_TOKEN` en `.env` y usa el simulador con `--token` y `--id` (ver su encabezado).
4. Los endpoints están en `Contrato_API_Sprint5.md`.

## Habilitadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 1 | Las migraciones nuevas se aplican en una base vacía y `alembic check` no detecta diferencias | `docker compose up --build`; luego `docker compose exec api alembic current` debe mostrar `a5b6c7d8e9f0` | ⏳ | Las migraciones se aplicaron (los endpoints de indicadores funcionan en Docker). Falta guardar la captura de `alembic current` (debe mostrar `a5b6c7d8e9f0`) y de `alembic check`. |
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
| 12 | Un rango mayor a 92 días se rechaza | `desde` hace 100 días → 400 | ⏳ | |

## HU 14 — Botón de asistencia

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 13 | Al pulsar el botón se crea un evento y se avisa a titular y cuidadores | `POST .../asistencia`; revisar `GET /eventos` y los avisos de cada cuenta | ⏳ | |
| 14 | Pulsarlo varias veces seguidas no duplica el aviso | Dos `POST` en menos de un minuto → 201 y luego 200 con el mismo evento | ⏳ | |
| 15 | El cuidador puede marcar el evento como atendido | `POST /eventos/{id}/atendido` | ⏳ | |

## HU 17 — Pulsera y geocercas

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 16 | Se registra una pulsera y no se puede repetir el identificador | `POST .../pulseras` dos veces | ⏳ | |
| 17 | La última ubicación y la batería se ven en `GET .../ubicacion` | Simulador: `posicion --bateria 80` | ⏳ | |
| 18 | Se crea una geocerca y se indica en cuáles está la persona | `POST .../geocercas` y luego `posicion` en su centro | ⏳ | |
| 19 | Al salir de la geocerca se crea un evento de salida | Simulador: `recorrido --metros 400` | ⏳ | |
| 20 | Una lectura con token incorrecto se rechaza | Simulador con `--token` erróneo → 401 | ⏳ | |

## HU 19 — Alertas de la pulsera

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 21 | El botón SOS crea un evento `sos` | Simulador: `sos` | ⏳ | |
| 22 | La caída crea un evento `caida` | Simulador: `caida` | ⏳ | |
| 23 | La batería baja crea un evento, sin repetirlo en 2 horas | Simulador: `bateria` dos veces | ⏳ | |
| 24 | La inactividad (3 h sin moverse, entre 08:00 y 22:00) crea un evento | Se cubre con pruebas automáticas; con la pulsera real, observar una tarde | ⏳ | |
| 25 | Cada evento llega a titular y cuidadores con alertas | `GET /eventos` con cada cuenta | ⏳ | |
| 26 | Con la pulsera y Traccar reales, las alertas llegan igual | Ver `traccar/README.md` | ⏳ | Depende de comprar y configurar la pulsera |

## HU 15 — Asistente de IA

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 27 | Responde con el aviso de que no reemplaza a un profesional | `POST .../ia/consultas` | ⏳ | |
| 28 | Una pregunta de urgencia responde 131 y *4141 | Caso 6 de `casos_prueba_ia.md` | ⏳ | |
| 29 | No se entregan RUT, correo ni teléfonos | Casos 8 y 9 | ⏳ | |
| 30 | Después de 30 consultas en el día responde 429 | Caso 12 | ⏳ | |
| 31 | Una cuenta ajena recibe 404 | Caso 13 | ⏳ | |

## Cierre

Resultado general: parcial, 9 de 31 criterios ✅ (filas 2 a 10) y 1 ✅ parcial (fila 11). Pendientes: la fila 1 (falta la captura de `alembic current` y `alembic check`) y las filas 12 a 31. &nbsp; Fecha: 10-11-2026 &nbsp; Observaciones: la ruta real para cambiar los permisos del cuidador es `PUT`, no `PATCH` como dice el contrato; la API no tiene ruta para marcar una actividad como omitida, por lo que esa prueba se hizo en la base de datos; el simulador de la pulsera y los casos de IA aún no se ejecutaron.
