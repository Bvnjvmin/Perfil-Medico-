# Checklist de aceptación — Product Owner (Sprint 2)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de dar por cerradas HU 2 y HU 4, el Product Owner valida que lo construido cumple los criterios de aceptación — no basta con que las pruebas automatizadas pasen, alguien del equipo que no escribió el código tiene que probarlo desde afuera. Esto completa la Definition of Done del equipo ("integrada al repositorio + probada + documentada") desde el ángulo de PO, que hasta ahora nadie había cubierto.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend` (o `uvicorn app.main:app --reload` si ya tienes el entorno local armado).
2. Abre `http://localhost:8000/docs` — ahí están todos los endpoints con un botón para probarlos directamente, sin necesitar la app ni Postman.
3. Crea un usuario de prueba (`POST /auth/register`) y autentícate (`POST /auth/login`, el botón "Authorize" arriba a la derecha acepta el token).
4. Ve marcando cada fila de abajo a medida que la pruebas.

## HU 2 — Datos básicos de salud del titular

| Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|
| El titular puede crear su perfil de salud | `POST /perfiles` con tus datos | ✅ | Validado correctamente |
| El titular puede listar sus perfiles | `GET /perfiles` | ✅ | |
| El titular puede actualizar su perfil | `PUT /perfiles/{id}` cambiando algún campo | ✅ | |
| El titular puede eliminar su perfil | `DELETE /perfiles/{id}` | ✅ | |
| El titular puede agregar y listar alergias | `POST` y `GET /perfiles/{id}/alergias` | ✅ | |
| El titular puede agregar y listar contactos de emergencia | `POST` y `GET /perfiles/{id}/contactos-emergencia` | ✅ | |
| Un titular NO puede ver el perfil de otro (prueba con un segundo usuario registrado) | Autentícate con el segundo usuario y prueba `GET /perfiles/{id-del-primero}` → debe dar 404, no 403 | ✅ | |

## HU 4 — Medicamentos y rutinas de cuidado

| Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|
| El titular puede registrar un medicamento en su perfil | `POST /perfiles/{id}/medicamentos` | ✅ | |
| El titular puede listar, actualizar y eliminar sus medicamentos | `GET` / `PUT` / `DELETE /medicamentos/{id}` | ✅ | |
| El titular puede registrar, listar, actualizar y eliminar rutinas de cuidado | mismos verbos en `/perfiles/{id}/rutinas` y `/rutinas/{id}` | ✅ | |
| Un titular NO puede ver los medicamentos/rutinas de otro | repite la prueba cruzada de HU 2 con `/medicamentos/{id}` | ✅ | |

## Ratificación de la decisión de alcance de HU 4

En `Base de datos/modelo_datos.md` (sección "Decisión de alcance — Sprint 2") quedó documentado que el equipo simplificó el alcance de HU 4: se construyeron `Medicamento` y `RutinaCuidado`, pero **no** `RUTINA_HORARIO` ni `ACTIVIDAD` (quedan para el Sprint 3). Esto significa que, por ahora, una rutina con varias tomas al día se registra como una sola fila, y "confirmar" una actividad no se guarda en el backend (ver también el pendiente de Matías en HU 5).

Como Product Owner, decide y dejar registrado aquí:

- [x] **Acepto** la simplificación tal como quedó documentada, y los campos de horario múltiple / confirmación persistida quedan priorizados para el Sprint 3.
- [ ] **No acepto** — especificar qué falta antes de cerrar HU 4:
  - _____________________________________________

## Veredicto final

- [x] **HU 2: Aceptada** — cumple los criterios de aceptación del Sprint Backlog.
- [x] **HU 4: Aceptada** — cumple los criterios de aceptación del Sprint Backlog (con la simplificación de alcance ratificada arriba).

**Product Owner:** Sergio Ocares
**Fecha:** 01 de octubre de 2026

---

*Una vez completado, sube este archivo junto con el `modelo_datos.md` actualizado y el diagrama exportado, en un commit del tipo:*