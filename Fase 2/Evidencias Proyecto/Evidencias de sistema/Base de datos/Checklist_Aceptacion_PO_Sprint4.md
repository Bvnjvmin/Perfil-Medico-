# Checklist de aceptación — Product Owner (Sprint 4)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de dar por cerradas las HU 9, 10 y 11, el Product Owner valida que lo construido cumple los criterios de aceptación del Sprint Backlog 4. Alguien que no escribió el código lo prueba desde afuera, con tres cuentas (titular, cuidador autorizado y persona ajena). Completa la Definition of Done del equipo ("integrada al repositorio + probada + documentada") desde el ángulo del PO.

> Plantilla sin ejecutar: los ✅ / ❌ y las notas se llenan al probar. Los criterios coinciden con el Sprint Backlog 4 y con el comportamiento real del backend; se ajustan si el equipo cambia algo en la reunión. **Alcance real de HU 9:** el aviso llega a la app (pantalla Avisos); el push al celular con FCM no está implementado, así que los criterios 6 y 8 se prueban con la pantalla Avisos y quedan anotados como parciales hasta que se elija el proveedor.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend`.
2. Abre `http://localhost:8000/docs`.
3. Registra tres usuarios (`POST /auth/register`): **titular**, **cuidador** y **ajena**, y autentícate con cada uno según la fila.
4. Para los criterios de la app, usa el emulador con dos cuentas (titular y cuidador).
5. Marca cada fila (✅ / ❌) a medida que la pruebas. Para probar los plazos sin esperar una hora, usa un horario cercano a la hora actual (zona America/Santiago) y, si hace falta, baja los plazos con las variables `RECORDATORIO_MINUTOS_ANTES`, `ALERTA_PLAZO_1_MINUTOS` y `ALERTA_PLAZO_2_MINUTOS` en `docker-compose.yml` (valores propuestos: 10, 30 y 60). Las alertas se consultan con `GET /alertas`. Cuidadores: `recibe_alertas` y `nivel_escalamiento` se fijan al vincularlos (`POST /perfiles/{id}/cuidadores`). El ciclo corre cada 60 s.

## Habilitadores — Horarios y generación de actividades

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 1 | Un medicamento o rutina puede tener varias horas por día | `POST /medicamentos/{id}/horarios` dos o más veces y `GET` | | |
| 2 | Una hora repetida o un horario sin origen se rechaza | Repetir la hora → 409; usar un medicamento ajeno → 404 | | |
| 3 | Las actividades del día se generan solas, una por horario, sin duplicarse | Esperar la tarea programada o dispararla; consultar la agenda dos veces | | |
| 4 | Borrar el medicamento o la rutina borra sus horarios y actividades | `DELETE` y consultar | | |

## HU 9 — Notificaciones push

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 5 | El backend registra el dispositivo del usuario | `POST /dispositivos` con un token de prueba → 201; repetirlo → 200 sin duplicar. (La app aún no lo llama: falta FCM.) | | |
| 6 | Se crea un recordatorio antes de la hora de una actividad pendiente | Crear un horario cercano, esperar el ciclo y consultar `GET /alertas` (tipo `recordatorio`) y la pantalla Avisos | | |
| 7 | Una actividad confirmada no genera recordatorio | Confirmar antes del recordatorio y consultar `GET /alertas` | | |
| 8 | Tocar un aviso abre la Agenda del perfil | Emulador, pantalla Avisos | | |

## HU 10 — Alertas escalonadas

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 9 | Pasado el primer plazo sin confirmar, se alerta al titular y a los cuidadores con `recibe_alertas` y nivel 1 | Dejar una actividad sin confirmar; consultar las alertas de cada cuenta | | |
| 10 | Pasado el segundo plazo, se crea la alerta de nivel 2 para los cuidadores con `nivel_escalamiento = 2` | Seguir sin confirmar; un cuidador con nivel 2 la recibe | | |
| 11 | Confirmar la actividad detiene el escalamiento | Confirmar y esperar el siguiente plazo | | |
| 12 | Cada alerta queda registrada y se puede consultar; la cuenta **ajena** no ve ninguna | `GET` de alertas con las tres cuentas | | |
| 13 | El mensaje informa que la actividad no fue confirmada, sin asumir una emergencia | Leer el texto de la alerta | | |

## HU 11 — Interfaz simplificada del dependiente

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 14 | El modo simplificado muestra solo las actividades de hoy, con botones y texto grandes | Emulador | | |
| 15 | Confirmar una actividad toma un solo toque | Emulador | | |
| 16 | El modo simplificado no permite editar ni borrar datos | Emulador | | |
| 17 | Se entra y se sale del modo desde la cuenta del titular | Emulador | | |

## Registro de ejecución

- Fecha de la prueba: *(...)*
- Entorno: *(commit, PostgreSQL, cuentas usadas)*
- Resultado: *(n)* de 17 ✅
- Qué se probó por API y qué en el emulador: *(...)*

## Limitaciones conocidas

*(se completan al probar)*
