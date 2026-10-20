# Checklist de aceptación — Product Owner (Sprint 3)

**Rol:** Sergio Ocares, Product Owner
**Qué es esto:** antes de dar por cerradas las HU 5, 6, 7 y 8, el Product Owner valida que lo construido cumple los criterios de aceptación del Sprint Backlog 3. No basta con que las pruebas automatizadas pasen: alguien que no escribió el código lo prueba desde afuera, con tres cuentas (titular, cuidador autorizado y persona ajena). Esto completa la Definition of Done del equipo ("integrada al repositorio + probada + documentada") desde el ángulo del PO.

## Cómo probar

1. Levanta el backend: `docker compose up --build` desde `Aplicacion/backend` (o `uvicorn app.main:app --reload` si ya tienes el entorno local armado).
2. Abre `http://localhost:8000/docs`: ahí están todos los endpoints con un botón para probarlos sin necesitar la app ni Postman.
3. Registra tres usuarios (`POST /auth/register`): **titular**, **cuidador** y **ajena**. Autentícate con cada uno (`POST /auth/login`, botón "Authorize") según la fila que pruebes.
4. Para los criterios de la app, usa el emulador con dos cuentas (titular y cuidador).
5. Marca cada fila (✅ / ❌) a medida que la pruebas.

## HU 6 — Perfiles de dependientes

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 1 | El titular crea un perfil dependiente con `tipo = 'dependiente'` y `subtipo` válido (`adulto_mayor` o `nino`) | `POST /perfiles` con cada subtipo → 201 | ✅ | 201 con `adulto_mayor` y con `nino`. |
| 2 | Un subtipo inválido se rechaza y el perfil titular no lleva subtipo | `POST /perfiles` con `subtipo = 'otro'` → error; titular con subtipo → error | ✅ | Subtipo `otro`, titular con subtipo y dependiente sin subtipo → 422 en los tres casos. |
| 3 | Cada cuenta tiene un solo perfil titular | Crear un segundo `tipo = 'titular'` con la misma cuenta → rechazado | ✅ | Segundo titular → 409; en la BD queda 1 solo titular por cuenta. |
| 4 | Borrar un perfil con alergias, contactos, medicamentos, rutinas, actividades y vínculos deja todo limpio | `DELETE /perfiles/{id}` y luego consultar cada recurso → 404 / vacío | ✅ | DELETE → 204. Filas de alergia, contacto, medicamento, rutina, actividad y vínculo: 1/1/1/1/2/1 antes y 0 después. Todas las consultas posteriores → 404. |
| 5 | La app muestra "Mis perfiles" y permite elegir el perfil activo | Emulador: capturas `S3_01` a `S3_03` | ✅ |  probar en el emulador (capturas S3_01 a S3_03). |

## HU 5 — Agenda diaria de actividades (cierre)

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 6 | La confirmación se guarda en el backend (tabla `actividad`), no en el dispositivo | Confirmar una actividad, cerrar sesión, volver a entrar y consultar | ✅ | Confirmar → 200; tras volver a iniciar sesión sigue `confirmada`, y la fila está en la tabla `actividad`. |
| 7 | La agenda de una fecha devuelve las actividades de cada medicamento o rutina activos, sin duplicarlas | `GET` de la agenda con `?fecha=AAAA-MM-DD`, dos veces seguidas → mismo resultado | ✅ | Dos consultas seguidas devuelven los mismos ids; 1 actividad por medicamento y 1 por rutina; 2 filas en la BD, sin duplicados. |
| 8 | Se puede confirmar y desconfirmar, y el cambio se conserva | Confirmar, desconfirmar y volver a consultar | ✅ | Desconfirmar → `pendiente`; volver a confirmar → `confirmada`; el cambio se conserva al consultar. |
| 9 | La agenda de la app consume la API (no `shared_preferences`) | Emulador: capturas `S3_04` | ✅ | probar en el emulador (capturas S3_04). |

## HU 7 — Permisos y cuidadores

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 10 | Existe un solo vínculo por persona y perfil | Vincular dos veces al mismo cuidador al mismo perfil → rechazado | ✅ | Primer vínculo → 201; segundo igual → 409; 1 sola fila en `perfil_acceso`. |
| 11 | El titular vincula a un cuidador por correo; si el correo no tiene cuenta, recibe un error claro | Vincular con el correo de **cuidador** → 201; con un correo inexistente → error con mensaje | ✅ | Correo del cuidador → 201; correo inexistente → 404 con mensaje «No existe una cuenta con ese correo». |
| 12 | El titular cambia los permisos y revoca el vínculo | `PUT` y `DELETE` sobre el vínculo; el cuidador pierde el acceso | ✅ | PUT permisos → 200 (confirmar=false, editar_rutinas=true); DELETE → 204; después el cuidador recibe 404 en perfil y agenda. |
| 13 | Matriz de acceso: el cuidador ve el perfil; confirma solo con `puede_confirmar` (si no, 403); no edita ni borra el perfil; la cuenta **ajena** recibe 404 | Probar cada caso con las tres cuentas | ✅ | Cuidador: ve perfil 200, confirma 200 con permiso y 403 sin él, edita 403, borra 403. Ajena: 404 en perfil, agenda, confirmar, editar, borrar y listar cuidadores. |
| 14 | La app respeta los permisos de cada perfil | Emulador con la cuenta cuidador: capturas `S3_06` | ✅ | probar en el emulador (capturas S3_06). |

## HU 8 — Panel de estado diario (versión inicial)

| # | Criterio de aceptación | Cómo probarlo | ✅ / ❌ | Notas |
|---|---|---|---|---|
| 15 | `GET /panel?fecha=` devuelve, por perfil con acceso, el total de actividades, las confirmadas y las pendientes | Consultar con la cuenta titular y comparar con la agenda | ✅ | Panel del titular: el perfil de prueba muestra total 2, confirmadas 1, pendientes 1, igual que su agenda. |
| 16 | El panel no incluye perfiles de cuentas sin vínculo | Consultar con la cuenta **ajena** → lista vacía | ✅ | Panel de la cuenta ajena → 200 con lista vacía. |
| 17 | La pantalla "Panel" muestra el avance por perfil, propio y compartido | Emulador: captura `S3_05` | ✅ | probar en el emulador (capturas S3_05). |

## Registro de ejecución (filas probadas contra la API)

- Fecha de la prueba: 20 de octubre de 2026.
- Entorno: backend del repositorio (último commit `d327b27`) con migraciones de Alembic aplicadas sobre PostgreSQL 16, tres cuentas nuevas (titular, cuidador, ajena) y `uvicorn` local.
- Filas 1–4, 6–8, 10–13 y 15–16: ejecutadas con asistencia de IA mediante un script que llama a la API y consulta la base de datos. Resultado: 13 de 13 ✅.
- Filas 5, 9, 14 y 17 dependen de la app y no se pueden probar por API: se completan en el emulador.

## Limitación conocida de la HU 8

La app hace una llamada por perfil en vez de usar `GET /panel` (ver Sprint Backlog 3).

- [x] **Acepto** la limitación para esta versión inicial del panel.
- [ ] **No acepto** — especificar qué falta:
  - _____________________________________________

## Veredicto final

- [x] **HU 5: Aceptada**
- [x] **HU 6: Aceptada**
- [x] **HU 7: Aceptada**
- [x] **HU 8: Aceptada** (versión inicial)

**Product Owner:** Sergio Ocares
**Fecha:** 20 de octubre de 2026

