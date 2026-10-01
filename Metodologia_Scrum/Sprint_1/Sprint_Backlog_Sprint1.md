# Sprint Backlog — Sprint 1 (S5–S6)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo:** 7 al 19 de septiembre de 2026 (semanas 5 y 6 del Cronograma)
**Objetivo del sprint:** dejar operativa la base técnica del sistema: autenticación de cuentas titulares, modelo de datos inicial y estructura base de la app móvil conectada al backend.
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregable comprometido en el Cronograma:** repositorio GitHub activo + README + esquema de BD + Sprint Backlog 1 + módulo de autenticación funcional.

## 1. Historias comprometidas

Historias tomadas del Product Backlog MVP (Cronograma, hoja "Product Backlog MVP") para el Sprint 1.

### HU 1 — Registro e inicio de sesión de la cuenta titular
- **Historia:** Como usuario quiero registrarme e iniciar sesión con una cuenta titular para acceder de forma segura a mi información de salud.
- **Responsable:** Benjamín Leiva (Backend) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Se puede registrar un usuario nuevo con nombre, correo y contraseña.
  - No se permite registrar dos usuarios con el mismo correo.
  - El login con credenciales correctas entrega un token JWT; con contraseña incorrecta se rechaza.
  - Existe un endpoint protegido (`/auth/me`) que responde solo con un token válido.
- **Estado al cierre:** ✅ **Terminada.**
- **Evidencia:** código en `Evidencias de sistema/Aplicacion/backend` (FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, Docker); 7 pruebas automatizadas que pasan (verificado el 24-09-2026: `7 passed`).

### HU 2 — Datos básicos de salud del titular
- **Historia:** Como titular quiero registrar mis datos básicos de salud (RUT, grupo sanguíneo, alergias, contactos de emergencia) para tenerlos disponibles en una emergencia.
- **Responsables:** Benjamín Leiva (Backend) / Sergio Ocares (BD) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Existe la tabla `perfiles` con RUT, grupo sanguíneo y fecha de nacimiento.
  - Existen las tablas `alergias` y `contactos_emergencia` asociadas al perfil.
  - El titular puede crear y consultar su perfil desde la API.
- **Estado al cierre:** 🟡 **Parcial.** El diseño de las tablas está hecho (ver modelo de datos), pero **no están implementadas** en el backend ni migradas: hoy solo existe la tabla `usuarios`.
- **Decisión:** pasa al Sprint 2 como arrastre (ver sección 4).
- **Actualización 30-09-2026:** Sergio cerró la parte de base de datos de este arrastre (commit `6c01968`): se crearon e migraron las tablas `perfil`, `alergia` y `contacto_emergencia`, y se eliminó la columna `rol` de `usuarios`. Ese commit dejó `app/schemas/usuario.py`, `app/api/routes/auth.py` y `app/tests/test_auth.py` todavía referenciando el campo/enum `rol` eliminado, lo que impedía levantar el backend (`ImportError`); se corrigió el mismo día (commits `fc0d184`, `232d2e7`, `8a01b23`) y las 7 pruebas de autenticación vuelven a pasar. Sigue faltando la parte de API de HU 2 (endpoints para que el titular cree y consulte su perfil, alergias y contactos de emergencia): eso se aborda en el Sprint 2 (ver `Metodologia_Scrum/Sprint_2/Sprint_Backlog_Sprint2.md`).

### HU 3 — Pantallas de registro e inicio de sesión en la app
- **Historia:** Como usuario quiero una pantalla de registro/login simple en la app móvil para entrar a Perfil Médico+ desde mi celular.
- **Responsable:** Matías Pizarro (App) · **Prioridad:** Alta
- **Criterios de aceptación:**
  - Pantallas de Login, Registro y Home (protegida por sesión).
  - El JWT se guarda de forma segura (no en texto plano).
  - La app consume `/auth/register`, `/auth/login` y `/auth/me` del backend.
- **Estado al cierre:** 🟡 **Entregada, con validación pendiente.** El código está en el repositorio (`app_movil/`) y se corrigieron errores de integración después de la primera subida, pero **falta evidencia documentada** de la prueba manual contra el backend y de la ejecución de las 2 pruebas Flutter con el SDK real.

## 2. Tareas técnicas del sprint

| Tarea | Historia | Responsable | Estado |
|---|---|---|---|
| Repositorio GitHub, estructura de carpetas y README | — | Benjamín | ✅ Hecha |
| Docker y docker-compose (API + PostgreSQL) | HU 1 | Benjamín | ✅ Hecha |
| Modelo `Usuario`, migración Alembic inicial | HU 1 | Benjamín | ✅ Hecha |
| Endpoints de registro, login y `/auth/me` con JWT | HU 1 | Benjamín | ✅ Hecha |
| 7 pruebas automatizadas del módulo de autenticación | HU 1 | Benjamín | ✅ Hecha (7 pasan) |
| Diagrama entidad-relación y justificación de diseño (`modelo_datos.md`) | HU 2 | Sergio | ✅ Hecha |
| Implementar `perfiles`, `alergias`, `contactos_emergencia` + migración | HU 2 | Sergio / Benjamín | ✅ BD hecha (30-09-2026, commit `6c01968`) · ⏭️ API pasa a Sprint 2 |
| Exportar el diagrama ER como imagen (`modelo_datos_perfilmedico.png`) | HU 2 | Sergio | ⏭️ Pasa a Sprint 2 |
| Estructura base Flutter (`models`, `services`, `screens`) | HU 3 | Matías | ✅ Hecha |
| Pantallas Login, Registro y Home + almacenamiento seguro del JWT | HU 3 | Matías | ✅ Hecha |
| 2 pruebas Flutter (modelo `Usuario` y validación del formulario de login) | HU 3 | Matías | 🟡 Escritas, sin ejecutar con SDK |
| Prueba manual app ↔ backend con capturas | HU 3 | Matías | ⏭️ Pasa a Sprint 2 |

## 3. Definition of Done — estado por historia

Definición del equipo (Metodología del 1.5): *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 1 | ✅ | ✅ (7 pruebas automatizadas) | ✅ (README y README del backend) | **Sí** |
| HU 2 | 🟡 (BD y migración sí, desde el 30-09-2026; falta la API) | ❌ (sin endpoints que probar todavía) | 🟡 (`modelo_datos.md`) | No |
| HU 3 | ✅ | 🟡 (sin evidencia) | ✅ (README de `app_movil`) | No, hasta cerrar la prueba |

## 4. Trabajo que pasa al Sprint 2

1. ~~**HU 2 completa:** tablas `perfiles`, `alergias` y `contactos_emergencia`, con migración y endpoints.~~ **Actualizado 30-09-2026:** tablas y migración ✅ hechas (commit `6c01968`, Sergio). Quedan los **endpoints** (crear/consultar perfil, alergias y contactos de emergencia) — trabajo del Sprint 2.
2. ~~**Eliminar la columna `rol` de `usuarios`** (migración nueva).~~ ✅ **Hecho el 30-09-2026** (commit `6c01968`), junto con la corrección de `schemas/usuario.py`, `api/routes/auth.py` y `tests/test_auth.py`, que todavía referenciaban el campo/enum `rol` eliminado (commits `fc0d184`, `232d2e7`, `8a01b23`).
3. **Cerrar la validación de HU 3:** ejecutar `flutter test` y una prueba manual app ↔ backend, con capturas guardadas como evidencia.
4. **Diagramas:** exportar el ER como imagen a `Diagramas/`.
5. **Repositorio:** añadir `.env.example` y `.gitignore` (ver revisión de estructura).

## 5. Plan de pruebas y evidencia del sprint

| Prueba | Tipo | Resultado |
|---|---|---|
| `test_registrar_usuario_nuevo` | Automática (backend) | ✅ Pasa |
| `test_no_permite_correo_duplicado` | Automática (backend) | ✅ Pasa |
| `test_login_exitoso_devuelve_token` | Automática (backend) | ✅ Pasa |
| `test_login_con_contrasena_incorrecta_falla` | Automática (backend) | ✅ Pasa |
| `test_me_devuelve_usuario_del_token` | Automática (backend) | ✅ Pasa |
| `test_me_sin_token_rechaza_acceso` | Automática (backend) | ✅ Pasa |
| `test_me_con_token_invalido_rechaza_acceso` | Automática (backend) | ✅ Pasa |
| `usuario_test.dart`, `login_screen_test.dart` | Automática (Flutter) | ⏳ Sin ejecutar |
| Flujo registro → login → Home en la app contra el backend | Manual | ⏳ Sin evidencia documentada |

Comando de las pruebas del backend: `pytest app/tests/ -v` (usan SQLite en memoria; no requieren Docker). Verificado nuevamente el 30-09-2026 tras el cierre de HU 2 (BD): `7 passed`.

## 6. Seguimiento de commits del sprint

- 16-09: estructura de Fase 2 y backend (Benjamín).
- 17-09: modelo de datos (Sergio).
- 19–20-09: estructura base y archivos Android de la app, y correcciones de integración (Matías).
- 30-09: tablas `perfil`/`alergia`/`contacto_emergencia` + eliminación de `rol` (Sergio, commit `6c01968`); corrección de `schemas`/`rutas`/`tests` que quedaron referenciando `rol` (Benjamín, commits `fc0d184`, `232d2e7`, `8a01b23`).
