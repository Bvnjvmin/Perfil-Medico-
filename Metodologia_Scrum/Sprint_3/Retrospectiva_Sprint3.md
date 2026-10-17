# Retrospectiva — Sprint 3 (S9–S10)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo del sprint:** 5 al 17 de octubre de 2026
**Fecha de redacción:** 17 de octubre de 2026 (último día del sprint)
**Scrum Master:** Matías Pizarro
**Participantes:** Matías Pizarro (App móvil y Scrum Master), Benjamín Leiva (Backend), Sergio Ocares (Base de datos, IA y Product Owner)

## Resultado del sprint

Historias comprometidas: 4 (HU 5 en su cierre, HU 6, HU 7 y HU 8) · Terminadas en base de datos, backend y app: 4 · Pendiente: la aceptación del Product Owner (`Checklist_Aceptacion_PO_Sprint3.md`). Detalle en `Sprint_Backlog_Sprint3.md`.

- **Base de datos (13-10):** tablas `actividad` y `perfil_acceso`, índice de titular único, borrado en cascada y `modelo_datos.md` al día.
- **Backend (15-10):** perfiles dependientes validados, agenda con confirmación guardada en el servidor, cuidadores con permisos por perfil y `GET /panel`; 119 pruebas pasan.
- **App (15 y 16-10):** perfiles dependientes, compartir perfil con permisos, Panel de dependientes y agenda conectada a la API; `flutter test` 10 de 10, sin errores en `flutter analyze` (4 avisos *info*), y prueba manual con dos cuentas (17 capturas). Evidencia en `Evidencia_Sprint3.md`.

## ¿Qué funcionó bien este sprint?

- **Contratos definidos antes de programar:** acordar el formato JSON entre app y backend evitó los bloqueos del Sprint 2; la app avanzó en paralelo con el backend.
- **Se cerró la confirmación de actividades de punta a punta (HU 5):** la agenda de la app usa la API y la confirmación se conserva al cerrar sesión, con lo que se quitó el almacenamiento local (`agenda_storage.dart`) que ocultaba errores.
- **Pruebas automatizadas y prueba manual con dos cuentas:** las pruebas detectaron inconsistencias entre app y servidor, y el flujo de cuidador (HU 7) se validó con una cuenta titular y una invitada.
- **Se respetó la división por módulos:** Sergio dejó la base de datos lista el 13-10, antes que el backend y la app, lo que desbloqueó las rutas y las pantallas.
- **La evidencia del sprint se generó con logs y capturas nuevos**, no con los de sprints anteriores.

## ¿Qué no funcionó o nos costó más de lo esperado?

- **Desalineación entre app y backend:** nombres de campo y rutas distintos (`rol` vs `rol_vinculo`, `/contactos` vs `/contactos-emergencia`, `nombre` vs `sustancia`); los respaldos en memoria ocultaron varios errores. *Aprendizaje:* contrastar cada llamada con `/docs` de FastAPI antes de dar una historia por terminada.
- **Mensajes de error que engañan:** un 404 se mostró como "función no disponible" cuando el correo no estaba registrado. *Aprendizaje:* mostrar siempre el `detail` del backend.
- **Formato de datos:** el subtipo de dependiente se enviaba como "Adulto mayor" y el backend exige `adulto_mayor` o `nino`. *Aprendizaje:* probar cada formulario contra el backend real, no solo con pruebas de modelo.
- **Pruebas del backend con fecha fija:** desde el 16-10 fallaban 12 pruebas y otras 54 daban error (`pytest`: 53 pasadas de 119), porque las pruebas usaban `2026-10-14` y la agenda solo genera actividades desde el día anterior a la creación del medicamento. Se corrigió el 17-10 con la fecha de hoy (119 pasan). *Aprendizaje:* las pruebas no deben depender de la fecha del calendario.
- **La subida volvió a concentrarse:** el 15-10 se registraron 36 de los 49 commits del 13 al 16-10. Es la misma observación de los Sprints 1 y 2.
- **El Sprint Backlog 3 se publicó el 13-10** (día 9 de 13), no el primer día.
- **Cierre ajustado:** la aceptación del Product Owner, la autoevaluación 2.2 y las partes del Informe de Avance quedaron para el último día.
- **Tiempo ajustado para la app:** programar varias historias, validar en emulador y ser Scrum Master en dos semanas obligó a priorizar; las mejoras visuales quedaron como opcionales.

## Seguimiento de las acciones de la retrospectiva del Sprint 2

| Acción acordada | Estado |
|---|---|
| Subir al repositorio al menos dos veces por semana, con commits pequeños | ❌ No se cumplió: ráfaga del 15-10 |
| Ejecutar `flutter analyze` y `pytest` (o `flutter test`) antes de cada commit | 🟡 Parcial: la app cierra sin errores de análisis y con 10 de 10 pruebas; el backend falló por fechas fijas y se corrigió el 17-10 |
| Contrato de API antes de construir cada historia | ✅ Cumplida |
| Probar los cambios de base de datos también contra PostgreSQL | ✅ Cumplida (migraciones y borrado de perfiles) |
| Un solo integrante crea las migraciones de Alembic | ✅ Cumplida (Sergio; cabeza única `e6f7a8b9c0d1`) |
| Subir avances parciales de la app en cuanto funcionen | 🟡 Parcial: la app se subió el 15 y el 16-10, casi toda el 15-10 |
| Redactar la retrospectiva el último día del sprint | ✅ Cumplida (17-10) |
| Texto corto que explique cada captura y su criterio | ✅ Cumplida en `Evidencia_Sprint3.md` |

## ¿Qué vamos a cambiar o probar distinto en el próximo sprint?

| Acción | Responsable | Cuándo |
|---|---|---|
| Mantener `flutter analyze` y `flutter test` en verde antes de cada commit a `main` | Matías | Permanente |
| Que las pruebas del backend no usen fechas fijas | Benjamín | Ya aplicado (17-10); revisar en cada prueba nueva |
| Subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint | Todos / Scrum Master | Todo el Sprint 4 |
| Publicar el Sprint Backlog 4 el primer día del sprint | Scrum Master | 19-10 |
| Revisar cada integración app-backend contra `/docs` de FastAPI | Matías y Benjamín | Cada historia |
| Corregir "Mi perfil de salud" para cuentas de cuidador (no mostrar el titular ajeno) | Matías | Sprint 4 |
| Pasar el Panel a `GET /panel?fecha=`; agregar timeouts y manejo de errores de red | Matías | Sprint 4 |
| Cambiar `value` por `initialValue` en los 4 avisos de `flutter analyze` | Matías | Sprint 4 |
| Cerrar el checklist del Product Owner dentro del sprint, no después | Sergio | Cada sprint |
