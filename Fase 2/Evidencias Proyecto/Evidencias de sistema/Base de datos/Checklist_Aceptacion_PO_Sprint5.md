# Checklist de aceptación — Product Owner (Sprint 5)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de cerrar las HU 12, 13, 14, 15, 17, 18 y 19, el Product Owner valida que lo construido cumple los criterios de aceptación. Quien prueba no escribió el código y usa tres cuentas (titular, cuidador autorizado y persona ajena).

> Plantilla sin ejecutar: todas las filas están en ⏳. Marca ✅ o ❌ al probar y anota lo observado. **Alcance real:** el aviso llega a la pantalla Avisos; el push con FCM no está implementado. La pulsera real y el servidor Traccar se prueban aparte (ver `Aplicacion/backend/traccar/README.md`); mientras tanto se usa el simulador `backend/scripts/simular_pulsera.py`.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend` (las migraciones corren solas).
2. Abre `http://localhost:8000/docs` y registra tres usuarios: **titular**, **cuidador** y **ajena**. Vincula al cuidador con `POST /perfiles/{id}/cuidadores` (con `puede_ver_indicadores` y `puede_confirmar` en verdadero, salvo donde se indique).
3. Para la pulsera: define `TRACCAR_TOKEN` en `.env` y usa el simulador con `--token` y `--id` (ver su encabezado).
4. Los endpoints están en `Contrato_API_Sprint5.md`.

## Habilitadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 1 | Las migraciones nuevas se aplican en una base vacía y `alembic check` no detecta diferencias | `docker compose up --build`; luego `docker compose exec api alembic current` debe mostrar `a5b6c7d8e9f0` | ⏳ | |
| 2 | El permiso `puede_ver_indicadores` se puede dar y quitar | `PATCH /perfiles/{id}/cuidadores/{vinculo}` | ⏳ | |

## HU 12 — Registro de indicadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 3 | El titular registra peso, presión, glucosa y pulso | `POST /perfiles/{id}/indicadores` por cada tipo → 201 | ⏳ | |
| 4 | La presión exige diastólica menor que la sistólica; un valor absurdo se rechaza | Presión sin diastólica y peso 700 → 422 | ⏳ | |
| 5 | El historial y el último valor de cada tipo se consultan | `GET .../indicadores` y `.../ultimos` | ⏳ | |
| 6 | Un cuidador sin `puede_ver_indicadores` recibe 403; con el permiso ve los datos; una cuenta ajena recibe 404 | Probar con las tres cuentas | ⏳ | |
| 7 | El rol de solo lectura no puede registrar | Cuidador con `puede_confirmar` falso → 403 | ⏳ | |

## HU 12 — Evolución de indicadores

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 8 | La serie entrega puntos ordenados, mínimo, máximo y promedio | `GET .../indicadores/serie?tipo=peso&dias=30` | ⏳ | |
| 9 | Sin mediciones en el rango, la serie viene vacía sin error | Rango sin datos | ⏳ | |

## HU 13 — Historial de cumplimiento

| # | Criterio | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 10 | El porcentaje general, por categoría y por día coincide con la agenda | Confirmar algunas actividades y comparar con `GET .../cumplimiento` | ⏳ | |
| 11 | Las omitidas no cuentan; las pendientes futuras de hoy no cuentan | Omitir una actividad y revisar el total | ⏳ | |
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

Resultado general: ⏳ &nbsp; Fecha: ____ &nbsp; Observaciones: ____
