# Sprint Backlog — Sprint 6 (S15)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo planificado:** 16 al 21 de noviembre de 2026 (semana 15 del Cronograma) · ⬜ confirmar si el equipo extiende el cierre hasta el jueves 26-11 por el push con FCM
**Última actualización:** 25 de noviembre de 2026 · **Estado del sprint:** BORRADOR. Armado desde el repositorio (`main`), el informe 2.6, `Verificacion_cifras_informe26.md` y el paquete FCM del 23-11. Lo marcado con ⬜ lo confirma quien hizo ese trabajo.

**Objetivo del sprint:** cerrar el proyecto para la entrega final: pruebas integrales con el backend en Docker, documentación (manual técnico, README, Docker), informe final y demo; y, si el tiempo lo permite, el push real con FCM (HU 9) y las historias del incremento (HU 20, 21 y 22).
**Product Owner:** Sergio Ocares · **Scrum Master:** Matías Pizarro
**Entregables del Cronograma:** Sprint Backlog 6 (semana 15); Informe Final 2.6 + manual técnico + README + aplicación funcional con backend en Docker; Retrospectiva del Sprint 6 (último día del sprint).

> Leyenda: ✅ terminado y verificado · 🟡 hecho en parte (se indica qué falta) · ⬜ pendiente · ❌ no cumplido. Una historia solo pasa a terminada cuando está integrada al repositorio, probada y documentada. Los criterios y decisiones son propuesta hasta confirmarlos en la reunión del equipo.

## 1. Historias y trabajo comprometido

### HU 16 — Seguridad y despliegue
Como equipo queremos el sistema dockerizado, con control de accesos por rol y datos simulados en pruebas.
- **Criterios de aceptación**
  - `docker compose up --build` levanta `db` y `api`; `alembic current` y `alembic check` sin diferencias.
  - `pytest` completo pasa dentro del contenedor y la prueba de humo (29 comprobaciones) se repite en Docker.
  - El control de acceso por rol (titular, cuidador con permisos, cuenta ajena) está cubierto por pruebas y por el checklist del Product Owner.
  - Los datos de prueba son simulados (sin datos reales de personas).
- **Estado al 25-11:** 🟡 migraciones verificadas en Docker (`S5_00.1`, `S5_00.4`); falta la prueba completa (compose ps, health, pytest en contenedor, humo) y capturar D1 a D5. Ver `backend/docs/Guia_Docker_Compose_Sprint5.md`.

### HU 9 (cierre) — Push real con FCM
Como cuidador quiero recibir el aviso como notificación en el celular, aunque la app esté cerrada.
- **Criterios de aceptación**
  - La app registra el token del celular al iniciar sesión y lo da de baja al cerrar sesión.
  - Con la app cerrada llega la notificación; con la app abierta se ve el aviso en pantalla.
  - Probado en un celular real, **por una persona que no escribió el código**.
- **Estado al 25-11:** 🟡 código escrito (paquete `FCM_para_Matias`, parches `fcm_app.patch` y `fcm_backend.patch`); **sin compilar ni probar con Firebase real**. **Plazo duro: jueves 26-11.** Si no funciona en un celular real ese día, se descarta y se declara el límite (plan B en la guía del paquete).

### HU 20 — Registro manual de glucosa
Como cuidador quiero ingresar manualmente la lectura de un glucómetro certificado y verla en el historial del perfil.
- **Lo que ya existe:** desde el Sprint 5 el backend y la app registran `glucosa` como tipo de indicador (mg/dL, rango 10 a 1000) con gráfico de evolución (HU 12).
- **Estado al 25-11:** ⬜ **decisión pendiente del Product Owner:** (a) declarar la HU 20 cubierta por la HU 12 y agregar solo la evidencia con una lectura de glucosa; o (b) dejarla como proyección. No se construyó nada nuevo para esta historia.

### HU 21 — Recordatorios extendidos (indicaciones post-consulta y citas)
- **Estado al 25-11:** ⬜ **no iniciada.** No hay tablas, rutas ni pantallas en el repositorio. Queda como proyección salvo decisión contraria del equipo (el informe 2.6 dice que los objetivos 9 a 11 solo se abordan si el tiempo lo permite).

### HU 22 — Farmacias cercanas vía IA
- **Estado al 25-11:** ⬜ **no iniciada.** El asistente de IA hoy responde que no puede ayudar con farmacias o precios (`app/services/ia.py`). Queda como proyección salvo decisión contraria del equipo.

### Trabajo de cierre (no son historias)
- Manual técnico (borrador en `Documentos/Manual_Tecnico_BORRADOR.md`), README y guía de Docker.
- Informe Final 2.6 y correcciones de `Verificacion_cifras_informe26.md`.
- Firma del checklist del Product Owner del Sprint 5 (veredicto y fecha).
- Ensayo de la presentación y demo (viernes 4-12).

## 2. Tareas por integrante

| Tarea | Historia | Responsable | Estado | Dónde |
|---|---|---|---|---|
| Aplicar `fcm_app.patch`, correr `flutter pub add firebase_core firebase_messaging`, `flutter analyze` y `flutter run` | HU 9 | Matías | ⬜ | `app_movil/` (rama `fcm`) |
| Crear el proyecto de Firebase y bajar `google-services.json` | HU 9 | Matías | ⬜ | `app_movil/android/app/` (no se sube) |
| Aplicar `fcm_backend.patch`, activar `NOTIFICADOR=fcm`, levantar con `docker-compose.fcm.yml` | HU 9 | Benjamín | ⬜ | `backend/` |
| Prueba de extremo a extremo con celular real y capturas | HU 9 | Matías / Benjamín (+ una persona que no escribió el código) | ⬜ | `app_movil/evidencias/evidencias Sprint 6/` |
| Prueba completa con Docker (D1 a D5) | HU 16 | Benjamín | ⬜ | `backend/docs/` |
| Decidir HU 20, 21 y 22 (hacer / cubrir / proyección) | HU 20–22 | Sergio (Product Owner) | ⬜ | Sección 6 |
| Firmar el checklist del Sprint 5 y repetir en Docker las filas verificadas en entorno de prueba | Habilitador | Sergio / Benjamín | ⬜ | `Base de datos/` |
| Manual técnico final | HU 16 | Sergio / Benjamín | 🟡 borrador del 22-11 | `Documentos/` |
| Corregir el informe 2.6 y la presentación según `Verificacion_cifras_informe26.md` | Habilitador | Benjamín / Matías | ⬜ | `Fase 2/Evidencias Grupales/` |
| Evidencia del sprint (capturas `S6_xx`) | HU 9 / 16 | Matías | ⬜ | `app_movil/evidencias/evidencias Sprint 6/` |
| Anotar los hashes de commits de la app (Sprints 5 y 6) en la sección 8 | Habilitador | Matías | ⬜ | Este archivo y `Sprint_5/` |
| Retrospectiva del Sprint 6, el último día | — | Matías | ⬜ | `Metodologia_Scrum/Sprint_6/` |
| Mantener una sola cabeza de migraciones (`a5b6c7d8e9f0`; si no se agregan tablas, no cambia) | Habilitador | Sergio | ⬜ | `backend/alembic/` |

## 3. Definition of Done — estado por historia

Definición del equipo: *integrada al repositorio + probada + documentada.*

| Historia | Integrada al repo | Probada | Documentada | ¿Terminada? |
|---|---|---|---|---|
| HU 9 (push real) | ⬜ rama `fcm` sin unir a `main` | ⬜ sin compilar ni probar con celular real | 🟡 guía y notas FCM | ⬜ |
| HU 16 | 🟡 | 🟡 migraciones en Docker; falta la prueba completa | 🟡 manual técnico en borrador | 🟡 |
| HU 20 | 🟡 cubierta por HU 12 (decisión pendiente) | ⬜ falta evidencia con glucosa | ⬜ | ⬜ |
| HU 21 | ⬜ | ⬜ | ⬜ | ⬜ |
| HU 22 | ⬜ | ⬜ | ⬜ | ⬜ |

## 4. Plan de pruebas del sprint

| # | Prueba | Cómo | Resultado |
|---|---|---|---|
| P1 | `pytest app/tests` en el contenedor | `docker compose exec api pytest` | ⬜ (216 de 216 verificadas el 22-11 fuera de Docker) |
| P2 | `alembic current` y `alembic check` | Docker | ✅ hecho en el Sprint 5; repetir si hay cambios |
| P3 | Prueba de humo (29 comprobaciones) | `scripts/prueba_humo_sprint5.py` en Docker | ⬜ |
| P4 | `flutter analyze` y `flutter test` con el código de FCM | Emulador | ⬜ |
| P5 | App compila sin `google-services.json` y el push queda desactivado | `flutter run` | ⬜ |
| P6 | Push con la app cerrada, con la app abierta y tras cerrar sesión | Celular real | ⬜ |
| P7 | Lectura de glucosa registrada y vista en el gráfico (si se cubre la HU 20) | Emulador | ⬜ |

## 5. Evidencia de pruebas del sprint

Pendiente. Se completa en `app_movil/evidencias/evidencias Sprint 6/Evidencia_Sprint6.md` (plantilla incluida) con capturas `S6_xx`. Cada captura debe indicar el criterio que respalda.

### Criterios sin captura todavía
| Historia | Criterio | Estado |
|---|---|---|
| HU 9 | Push con la app cerrada en un celular real | Pendiente (plazo 26-11) |
| HU 16 | Prueba completa con Docker (D1 a D5) | Pendiente |
| HU 15 / 17 / 19 | Proveedor de IA real, Traccar y pulsera reales | Límites conocidos; no se prueban en este sprint |

## 6. Decisiones del sprint

Propuesta para confirmar en la reunión del equipo.

1. **Push real con FCM.** El 23-11 el Product Owner lo había dejado como límite conocido; el paquete FCM abre una última oportunidad con plazo duro el 26-11. ⬜ confirmar que el equipo intenta hacerlo en una rama aparte y que **no se une a `main` sin haber probado que la app compila**. Si falla, se usa el texto de límite conocido de `Notas_FCM_Sprint5.md`.
2. **HU 20 (glucosa).** ⬜ Product Owner: cubierta por la HU 12 o proyección.
3. **HU 21 y 22.** ⬜ Product Owner: proyección (propuesta), con el mismo tratamiento que la HU 18.
4. **HU 18 (Health Connect).** Sigue como proyección (decisión del 23-11).
5. **Congelamiento.** Desde el 2-12 solo se corrigen textos (acuerdo del paquete FCM).
6. **Claves de Firebase.** `google-services.json` y la clave de la cuenta de servicio **nunca** se suben; el `.gitignore` se actualiza antes del primer `git add`.

## 7. Trabajo que pasa a la proyección

Según lo que se decida en la sección 6: HU 18, HU 21 y HU 22 (y la HU 20 si no se cubre con la HU 12); push real con FCM si no se verifica; prueba con Traccar y pulsera reales; prueba de la IA con un proveedor real.

## 8. Seguimiento de commits del sprint

Acuerdo del Sprint 3: subir al repositorio al menos dos veces por semana.

| Fecha | Qué se subió | Quién | Commits |
|---|---|---|---|
| ⬜ | Sprint Backlog 6 | Matías | ⬜ |
| ⬜ | Rama `fcm` (app) | Matías | ⬜ |
| ⬜ | Rama `fcm` (backend) | Benjamín | ⬜ |
| ⬜ | Evidencia del Sprint 6 | Matías | ⬜ |
| ⬜ | Retrospectiva del Sprint 6 | Matías | ⬜ |
