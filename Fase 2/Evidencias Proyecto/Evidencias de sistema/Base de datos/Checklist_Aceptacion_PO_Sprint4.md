# Checklist de aceptación — Product Owner (Sprint 4)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de dar por cerradas las HU 9, 10 y 11, el Product Owner valida que lo construido cumple los criterios de aceptación del Sprint Backlog 4. Alguien que no escribió el código lo prueba desde afuera, con tres cuentas (titular, cuidador autorizado y persona ajena). Completa la Definition of Done del equipo ("integrada al repositorio + probada + documentada") desde el ángulo del PO.

> Ejecución parcial: los ✅ son pruebas hechas por el Product Owner; ⏳ significa que aún no se probó. Los criterios coinciden con el Sprint Backlog 4 y con el comportamiento real del backend; se ajustan si el equipo cambia algo en la reunión. **Alcance real de HU 9:** el aviso llega a la app (pantalla Avisos); el push al celular con FCM no está implementado, así que los criterios 6 y 8 se prueban con la pantalla Avisos y quedan anotados como parciales hasta que se elija el proveedor.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend`.
2. Abre `http://localhost:8000/docs`.
3. Registra tres usuarios (`POST /auth/register`): **titular**, **cuidador** y **ajena**, y autentícate con cada uno según la fila.
4. Para los criterios de la app, usa el emulador con dos cuentas (titular y cuidador).
5. Marca cada fila (✅ / ❌) a medida que la pruebas. Para probar los plazos sin esperar una hora, usa un horario cercano a la hora actual (zona America/Santiago) y, si hace falta, baja los plazos con las variables `RECORDATORIO_MINUTOS_ANTES`, `ALERTA_PLAZO_1_MINUTOS` y `ALERTA_PLAZO_2_MINUTOS` en `docker-compose.yml` (valores propuestos: 10, 30 y 60). Las alertas se consultan con `GET /alertas`. Cuidadores: `recibe_alertas` y `nivel_escalamiento` se fijan al vincularlos (`POST /perfiles/{id}/cuidadores`). El ciclo corre cada 60 s.

## Habilitadores — Horarios y generación de actividades

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 1 | Un medicamento o rutina puede tener varias horas por día | `POST /medicamentos/{id}/horarios` dos o más veces y `GET` | ✅ | Probado en Swagger: dos `POST` de horarios → 201 y 201; el `GET` devolvió 200 con 2 horarios. |
| 2 | Una hora repetida o un horario sin origen se rechaza | Repetir la hora → 409; usar un medicamento ajeno → 404 | ✅ parcial | Probado en Swagger: hora repetida → 409. (El caso de medicamento ajeno → 404 no se probó en Swagger.) |
| 3 | Las actividades del día se generan solas, una por horario, sin duplicarse | Esperar la tarea programada o dispararla; consultar la agenda dos veces | ✅ | Probado en Swagger: `GET /perfiles/{id}/actividades` dos veces seguidas → 200, siempre 2 actividades (19:30 y 23:00) con los mismos ids, en estado `pendiente`. |
| 4 | Borrar el medicamento o la rutina borra sus horarios y actividades | `DELETE` y consultar | ✅ | Probado en Swagger (2-nov): con la cuenta del cuidador, `DELETE /medicamentos/{id}` → 403 (sin permiso de edición). Con el titular → 204; luego `GET /medicamentos/{id}/horarios` → 404 y la agenda del día ya no mostró ninguna actividad del medicamento borrado. |

## HU 9 — Notificaciones push

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 5 | El backend registra el dispositivo del usuario | `POST /dispositivos` con un token de prueba → 201; repetirlo → 200 sin duplicar. (La app aún no lo llama: falta FCM.) | ✅ | Probado en Swagger: `POST /dispositivos` → 201 la primera vez y 200 la segunda, sin duplicar. |
| 6 | Se crea un recordatorio antes de la hora de una actividad pendiente | Crear un horario cercano, esperar el ciclo y consultar `GET /alertas` (tipo `recordatorio`) y la pantalla Avisos | ✅ | Probado con `GET /alertas`: apareció un recordatorio (`tipo` recordatorio, `nivel` 0) para la actividad de las 19:30. Parcial: no se probó en la pantalla Avisos de la app y el push real no está implementado. |
| 7 | Una actividad confirmada no genera recordatorio | Confirmar antes del recordatorio y consultar `GET /alertas` | ✅ | Probado en Swagger (8-nov): la actividad de las 18:14 se confirmó a las 18:08, antes de que le tocara el recordatorio (18:12), y no apareció ningún recordatorio ni alerta para ella en `GET /alertas`. Control: la actividad de las 18:15, sin confirmar, sí tuvo su recordatorio a las 18:13. (Intentos anteriores, 2-nov y 8-nov, no fueron válidos: la confirmación llegó después del recordatorio.) |
| 8 | Tocar un aviso abre la Agenda del perfil | Emulador, pantalla Avisos | ⏳ | Pendiente: se prueba en el emulador con la app. |

## HU 10 — Alertas escalonadas

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 9 | Pasado el primer plazo sin confirmar, se alerta al titular y a los cuidadores con `recibe_alertas` y nivel 1 | Dejar una actividad sin confirmar; consultar las alertas de cada cuenta | ✅ | Probado: pasados 30 min de las 19:30, el titular recibió una alerta de nivel 1. El cuidador (vinculado con nivel 2) no la recibió y solo tenía el recordatorio. |
| 10 | Pasado el segundo plazo, se crea la alerta de nivel 2 para los cuidadores con `nivel_escalamiento = 2` | Seguir sin confirmar; un cuidador con nivel 2 la recibe | ✅ | Probado con datos reales (2-nov): el cuidador con nivel 2 recibió una alerta de nivel 2 de «Losartán» (19:30) y ninguna de nivel 1; la lista del titular tenía alertas de nivel 1 y ninguna de nivel 2. Nota: esa alerta se creó al reiniciar el servidor, cuando la actividad ya llevaba más de 60 min sin confirmar (plazos por defecto). |
| 11 | Confirmar la actividad detiene el escalamiento | Confirmar y esperar el siguiente plazo | ✅ | Probado en Swagger (8-nov): la actividad de las 18:15 recibió la alerta de nivel 1 a las 18:18 y se confirmó a las 18:19. Pasado el plazo del nivel 2 (18:30), el cuidador no recibió ninguna alerta de nivel 2 para esa actividad. Para esta prueba el plazo del nivel 2 se subió a 15 min, para tener margen entre el nivel 1 y el nivel 2. (Un intento previo del mismo día no fue válido: se confirmó 9 segundos después de que saliera el nivel 2.) |
| 12 | Cada alerta queda registrada y se puede consultar; la cuenta **ajena** no ve ninguna | `GET` de alertas con las tres cuentas | ✅ | Probado: la cuenta ajena hizo `GET /alertas` → 200 con lista vacía `[]`. El titular y el cuidador vieron solo sus propios avisos. |
| 13 | El mensaje informa que la actividad no fue confirmada, sin asumir una emergencia | Leer el texto de la alerta | ✅ | Mensaje de la alerta: «La actividad «Losartán» de Abuela Rosa (programada a las 19:30) aún no fue confirmada.» No menciona una emergencia. |

## HU 11 — Interfaz simplificada del dependiente

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 14 | El modo simplificado muestra solo las actividades de hoy, con botones y texto grandes | Emulador | ⏳ | Pendiente: se prueba en el emulador con la app. |
| 15 | Confirmar una actividad toma un solo toque | Emulador | ⏳ | Pendiente: se prueba en el emulador con la app. |
| 16 | El modo simplificado no permite editar ni borrar datos | Emulador | ⏳ | Pendiente: se prueba en el emulador con la app. |
| 17 | Se entra y se sale del modo desde la cuenta del titular | Emulador | ⏳ | Pendiente: se prueba en el emulador con la app. |

## Registro de ejecución

- Fecha de la prueba: 22 y 23 de octubre y 2 y 8 de noviembre de 2026.
- Entorno: backend del repositorio en Docker Compose (commit `ca2f230`), PostgreSQL, Swagger en `http://localhost:8000/docs`. Tres cuentas: titular, cuidador (vinculado con `recibe_alertas` y nivel 2) y ajena. Perfil de prueba: dependiente «Abuela Rosa» con el medicamento Losartán a las 19:30 y a las 23:00 (más horarios temporales creados para las pruebas del 8-nov).
- Resultado: 12 de 17 ✅ (criterios 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12 y 13; el 2 y el 6 con parte sin probar, como indican sus notas). Quedan pendientes los criterios 8, 14, 15, 16 y 17 (emulador).
- Qué se probó por API y qué en el emulador: todo lo marcado ✅ se probó por API en Swagger. Nada se probó aún en el emulador.

## Limitaciones conocidas

- El push real al celular (FCM) no está implementado: los avisos se consultan con `GET /alertas` y en la pantalla Avisos, por eso el criterio 6 queda como parcial.
- El 8-nov los plazos cortos sí se aplicaron (recordatorio a 2 min, nivel 1 a 3 min y nivel 2 a 6 min; 15 min para el nivel 2 en la prueba del criterio 11). Los plazos propuestos originalmente (10, 30 y 60 minutos) no se usaron en esas pruebas.
- Los criterios pendientes se actualizarán en este mismo archivo cuando se prueben.
