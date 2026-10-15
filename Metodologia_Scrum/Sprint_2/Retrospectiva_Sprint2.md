# Retrospectiva — Sprint 2 (S7–S8)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo del sprint:** 20 de septiembre al 3 de octubre de 2026
**Participantes:** Benjamín Leiva, Sergio Ocares, Matías Pizarro
**Fecha de redacción:** 15 de octubre de 2026 (después del cierre del sprint). Este texto se armó a partir de lo que consta en el repositorio y en `Sprint_Backlog_Sprint2.md`; las acciones de mejora se confirman o se ajustan en la reunión del equipo.

## Resultado del sprint

Historias comprometidas: 4 (HU 2, HU 3, HU 4 y HU 5; la HU 1 venía heredada del Sprint 1) · Terminadas: 4 · Fuera de plazo: 2 (HU 3 y HU 5, cerradas el 10-10 en vez del 03-10). Detalle en `Sprint_Backlog_Sprint2.md`.

Limitación principal: la confirmación de actividades de la HU 5 se guarda solo en el celular, porque `ACTIVIDAD` y `RUTINA_HORARIO` se difirieron al Sprint 3 (decisión ratificada por el Product Owner el 01-10).

## ¿Qué funcionó bien este sprint?

- **El backend de HU 2 y HU 4 se cerró con pruebas:** perfil de salud, alergias, contactos, medicamentos y rutinas, con 25 pruebas automatizadas que pasan (10 de HU 2, 8 de HU 4 y 7 de autenticación).
- **El Product Owner validó las historias contra la API en vivo** con un checklist de aceptación (01-10), y la simplificación de alcance de HU 4 quedó ratificada por escrito en lugar de entregarse a medias.
- **Se cumplió la acción de cerrar HU 2** (perfiles, alergias y contactos con migración), que era el arrastre principal del Sprint 1.
- **La app pasó de la teoría a la evidencia:** `flutter test` se ejecutó con el SDK real (8 pruebas en total), y hay una prueba manual con 16 capturas del flujo contra el backend local (8 de HU 3 y 8 de HU 5).
- **El diseño y el código se realinearon:** el campo `rol` salió de `usuarios` el 30-09, con las referencias del backend y de la app corregidas ese mismo día, y el modelo de datos, el backend y la app quedaron coherentes. Ser titular o cuidador pasó a ser un vínculo con el perfil.
- **El modelo de datos y el diagrama ER se mantuvieron al día** (`modelo_datos.md` y la imagen del diagrama).
- **Se rebalanceó la carga a mitad del sprint:** se agregaron al Sprint Backlog tareas reales de Sergio (modelo de datos y validación como Product Owner) el 30-09.

## ¿Qué no funcionó o nos costó más de lo esperado?

- **El trabajo de la app llegó una semana tarde.** HU 3 y HU 5 se cerraron el 10-10, siete días después del cierre del sprint, y los commits de la app se concentraron en una sola tarde (10-10, 14 commits).
- **La subida volvió a concentrarse en pocos días.** El 30-09 se registraron 53 commits del repositorio, y no hubo commits entre el 03 y el 06-10. Es la misma observación del Sprint 1, que no se corrigió.
- **El Sprint Backlog y esta retrospectiva se escribieron después del cierre.** Debían escribirse el primer y el último día del sprint; el Backlog quedó listo el 30-09 (día 11) y la retrospectiva recién ahora.
- **La confirmación de actividades quedó solo en el dispositivo.** Se pierde al desinstalar la app y un cuidador no puede verla; por eso HU 8, HU 10 y HU 13 dependen de `ACTIVIDAD`.
- **Un error de sintaxis llegó al repositorio sin pasar por el análisis estático** (aviso de "Cuenta creada", 07-10) y se corrigió al día siguiente.
- **La limpieza de `rol` necesitó varias pasadas:** después de la corrección del 30-09, la migración y el modelo del backend se ajustaron de nuevo el 02-10 y el 08-10.
- **Cierre incompleto de la evidencia:** las capturas y los logs están subidos, pero no un texto corto que explique cada captura y a qué criterio corresponde. La retrospectiva y la demo interna tampoco existían al cierre.
- **Quedaron fuera de la app** la edición de medicamentos y rutinas (el endpoint `PUT` existe), y las pantallas de alergias y contactos de emergencia.

## Seguimiento de las acciones de la retrospectiva del Sprint 1

| Acción acordada | Estado |
|---|---|
| Subir avances al menos 2 veces por semana, en commits pequeños | ❌ No se cumplió: ráfagas el 30-09 y el 10-10 |
| Escribir el Sprint Backlog el primer día y la retrospectiva el último | ❌ No se cumplió: ambos se escribieron después |
| Cerrar HU 2 (`perfiles`, `alergias`, `contactos_emergencia`) | ✅ Cumplida el 30-09 |
| Actualizar backend, modelo de datos y app al eliminar `rol` | ✅ Cumplida el 30-09, con ajustes posteriores el 02-10 y el 08-10 |
| Ejecutar `flutter test` y una prueba manual con capturas | ✅ Cumplida el 10-10, con retraso |
| Agregar `.gitignore` y `.env.example` | ✅ Cumplida |
| Trabajar desde un clon local con git | A confirmar con el equipo |
| Mantener las tareas en el tablero de GitHub Projects | A confirmar con el equipo |

## ¿Qué vamos a cambiar o probar distinto en el próximo sprint?

| Acción | Responsable | Cuándo |
|---|---|---|
| Subir al repositorio al menos dos veces por semana, con commits pequeños; revisar el historial a mitad de sprint | Todos / Scrum Master | Todo el Sprint 3 |
| Ejecutar `flutter analyze` y `pytest` (o `flutter test`) antes de cada commit | Todos | Desde el Sprint 3 |
| Escribir un contrato de API antes de construir cada historia, para que la app avance en paralelo con el backend | Benjamín / Matías | Inicio de cada historia |
| Probar los cambios de base de datos también contra PostgreSQL, no solo con SQLite | Sergio / Benjamín | Cada migración |
| Un solo integrante crea las migraciones de Alembic por sprint, para mantener una única cabeza | Sergio | Sprint 3 |
| Subir avances parciales de la app en cuanto funcionen, sin esperar al cierre del backend | Matías | Todo el Sprint 3 |
| Redactar la retrospectiva del Sprint 3 el último día del sprint | Scrum Master | 17-10 |
| Agregar a la evidencia un texto corto que explique cada captura y su criterio | Matías / Benjamín | Cierre del Sprint 3 |
