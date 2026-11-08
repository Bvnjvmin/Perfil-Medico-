# Requisitos no funcionales — Perfil Médico+

**Equipo 7 · Capstone_005D · Ingeniería Informática, Sede Plaza Oeste**
**Responsable del documento:** Sergio Ocares (Product Owner)
**Estado al 5 de noviembre de 2026** (Sprints 1 a 4 terminados; el Sprint 4 sigue en validación del Product Owner).

Los requisitos funcionales dicen **qué hace** el sistema (las historias de usuario del Product Backlog). Los no funcionales dicen **qué tan bien** lo hace: qué tan seguro, rápido, confiable, usable y fácil de mantener es. Este documento recoge los requisitos del proyecto y declara, uno por uno y con su evidencia, cuáles se cumplen hoy. Lo que no se ha construido o medido figura como **pendiente**.

## Resumen

| Estado | Cantidad |
|---|---|
| ✅ Cumplido | 20 |
| 🟡 Parcial | 5 |
| ⏳ Pendiente | 9 |
| **Total** | **34** |

**Lo más importante que falta** antes de pensar en un despliegue real: HTTPS, restringir CORS, limitar los intentos de inicio de sesión, medir tiempos de respuesta y analizar el cumplimiento de la ley de protección de datos personales. Son temas de seguridad y de operación, no de funcionalidad, y se abordan al desplegar el sistema (Sprint 6 y Fase 3).

**Cómo leer las tablas:** *Cumplido* significa que existe en el código y hay evidencia en el repositorio. *Parcial* significa que existe pero con una limitación que se indica. *Pendiente* significa que no está implementado o no se ha medido.

## Seguridad

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-01 | Las contraseñas nunca se guardan en texto plano: se almacena solo un hash bcrypt, y la API nunca devuelve la contraseña. | ✅ Cumplido | `core/security.py`; el esquema `UsuarioOut` no incluye `hashed_password`. |
| RNF-02 | La contraseña debe tener entre 8 y 72 caracteres. | ✅ Cumplido | `schemas/usuario.py` (`UsuarioCreate`). Revisado en el código; no tiene una prueba automática propia. |
| RNF-03 | La sesión se maneja con tokens JWT firmados que vencen a las 24 horas. | ✅ Cumplido | `core/config.py` (`ACCESS_TOKEN_EXPIRE_MINUTES`); `core/security.py`; `test_auth.py` cubre el login con token, el token inválido y el acceso sin token. El vencimiento no tiene prueba propia. |
| RNF-04 | Cada perfil solo es visible para su titular y los cuidadores vinculados. Una cuenta sin vínculo recibe 404 (no se revela que el perfil existe) y una con vínculo pero sin el permiso pedido recibe 403. | ✅ Cumplido | `api/deps.py`; checklists de aceptación del PO (Sprint 3: 17 de 17; Sprint 4: criterio 12). |
| RNF-05 | Los permisos del cuidador son configurables por perfil (confirmar, editar rutinas, ver indicadores, recibir alertas) y se pueden revocar con efecto inmediato. | ✅ Cumplido | Tabla `perfil_acceso`; `routes/cuidador.py`; checklist Sprint 3 (HU 7). |
| RNF-06 | El token de sesión se guarda en la app con almacenamiento seguro del sistema. | ✅ Cumplido | `app_movil/lib/services/token_storage.dart` (`flutter_secure_storage`). |
| RNF-07 | Los secretos y las claves están fuera del código, en variables de entorno, y el archivo `.env` no se sube a GitHub. | 🟡 Parcial | `.env.example` y `core/config.py`. Queda por cambiar la `SECRET_KEY` de ejemplo por una generada al azar antes de cualquier despliegue real. |
| RNF-08 | Toda entrada se valida en la API (tipos, largos máximos y mínimos, formato de correo). | ✅ Cumplido | Esquemas Pydantic en `app/schemas/`. |
| RNF-09 | La comunicación entre la app y la API va cifrada (HTTPS). | ⏳ Pendiente | Hoy corre en HTTP local (`localhost:8000`). Se resuelve al desplegar, con un proxy con certificado. |
| RNF-10 | La API solo acepta peticiones desde orígenes autorizados (CORS restringido). | ⏳ Pendiente | `main.py` tiene `allow_origins=["*"]`, válido para desarrollo pero no para producción. |
| RNF-11 | Se limita el número de intentos de inicio de sesión para frenar ataques de fuerza bruta. | ⏳ Pendiente | No está implementado. |

## Privacidad y datos de salud

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-12 | Los avisos y alertas informan que una actividad no fue confirmada, pero no afirman que exista una emergencia ni entregan diagnósticos. | ✅ Cumplido | `services/alertas.py` (`_mensaje`); criterio 13 del checklist Sprint 4. |
| RNF-13 | Al invitar a un cuidador, la API no debe revelar si un correo está registrado. | 🟡 Parcial | Hoy responde 404 si el correo no existe, lo que sí lo revela; está documentado como decisión aceptada para el MVP en `routes/cuidador.py`. |
| RNF-14 | El tratamiento de datos de salud cumple la normativa chilena de protección de datos personales (Ley N° 19.628 y su actualización, Ley N° 21.719): consentimiento informado, finalidad y política de privacidad. | ⏳ Pendiente | Pendiente de análisis. Conviene confirmar con el docente qué alcance se exige a un MVP académico. |
| RNF-15 | Las respuestas del módulo de IA se presentan como orientación general, no como diagnóstico médico. | ⏳ Pendiente | El módulo de IA se construye en los Sprints 5 y 6. |

## Rendimiento

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-16 | La app no queda bloqueada si el servidor no responde: corta la espera a los 15 segundos y muestra un mensaje de error de conexión. | ✅ Cumplido | `app_movil/lib/services/api_service.dart`; captura `S4_10` de la evidencia del Sprint 4. |
| RNF-17 | La tarea programada revisa las actividades cada 60 segundos sin duplicar avisos aunque corra muchas veces. | ✅ Cumplido | `services/alertas.py`; restricción única `uq_alerta_actividad_usuario_nivel`; `test_avisos.py`. |
| RNF-18 | Las operaciones comunes de la API responden en menos de 1 segundo. | ⏳ Pendiente | Meta propuesta, aún sin medir. Hoy solo hay pruebas funcionales, no de tiempos. |
| RNF-19 | El sistema soporta usuarios concurrentes sin degradarse. | ⏳ Pendiente | Sin pruebas de carga. |

## Confiabilidad e integridad de datos

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-20 | La base de datos hace cumplir la integridad: llaves foráneas, restricciones únicas y de valores válidos, y borrado en cascada. | ✅ Cumplido | Modelos y migraciones; migraciones del Sprint 4 probadas en PostgreSQL 16 (subida, bajada y subida de cada una). |
| RNF-21 | Los cambios al esquema están versionados con Alembic, con una única cabeza en la cadena de migraciones, y se pueden revertir. | ✅ Cumplido | `backend/alembic/versions/`; el README indica que una sola persona crea las migraciones de cada sprint. |
| RNF-22 | Las horas de las actividades se interpretan en la zona horaria de Chile (America/Santiago). | 🟡 Parcial | `ZONA_HORARIA` en `core/config.py`. Falta decidir y confirmar cómo se muestra la hora local en la pantalla Avisos (decisión 7 del Sprint 4). |
| RNF-23 | Los avisos llegan al celular aunque la app esté cerrada (notificaciones push). | ⏳ Pendiente | FCM no está implementado: los avisos se ven en la pantalla Avisos y se escriben en el log (`NOTIFICADOR=log`). |

## Usabilidad

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-24 | El perfil dependiente dispone de un modo simplificado: solo las actividades de hoy, botones y texto grandes, confirmación con un toque y sin posibilidad de editar ni borrar. | ✅ Cumplido | HU 11; capturas `S4_06` a `S4_08.3` de la evidencia del Sprint 4. Falta que el PO lo valide en el emulador. |
| RNF-25 | Los mensajes de la app y de la API están en español y son claros. | ✅ Cumplido | Mensajes de error y de avisos del backend; pantallas de la app. |
| RNF-26 | La app cumple criterios de accesibilidad (contraste, tamaño de fuente configurable, lector de pantalla). | ⏳ Pendiente | No evaluado. Solo el modo simplificado está pensado con botones y texto grandes. |

## Mantenibilidad y calidad

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-27 | El código backend se cubre con pruebas automatizadas que corren sin Docker ni PostgreSQL. | ✅ Cumplido | 148 pruebas con `pytest` (SQLite en memoria). |
| RNF-28 | La app móvil tiene pruebas automatizadas y análisis estático sin avisos. | ✅ Cumplido | 14 pruebas de Flutter y `flutter analyze` sin avisos (README, Sprint 4). |
| RNF-29 | La API está documentada y se puede probar sin escribir código. | ✅ Cumplido | Swagger en `/docs` y `backend/Contrato_API_Sprint4.md`. |
| RNF-30 | El backend se organiza en capas separadas (rutas, esquemas, modelos y servicios). | ✅ Cumplido | Estructura de `backend/app/`. |
| RNF-31 | La configuración se cambia con variables de entorno, sin tocar el código. | ✅ Cumplido | `.env.example` y `core/config.py` (plazos de alerta, zona horaria, notificador). |

## Portabilidad y despliegue

| ID | Requisito | Estado | Evidencia o comentario |
|---|---|---|---|
| RNF-32 | El sistema (API y base de datos) se levanta con un solo comando. | ✅ Cumplido | `docker compose up --build`; instrucciones en el README. |
| RNF-33 | El build de Docker funciona en cualquier red. | 🟡 Parcial | El `Dockerfile` instala paquetes del sistema con `apt` y falla en redes que bloquean el repositorio de Debian (se vio en un computador de la sede). Como el proyecto usa `psycopg2-binary`, ese paso no es necesario. |
| RNF-34 | La app móvil funciona en Android e iOS. | 🟡 Parcial | Se probó en el emulador de Android (apunta al backend en `10.0.2.2:8000`). iOS no se ha probado. |

## Cómo se verifican

- **Pruebas automatizadas:** 148 pruebas del backend (`pytest app/tests/ -v`) y 14 de la app (`flutter test`).
- **Checklists de aceptación del Product Owner:** `Base de datos/Checklist_Aceptacion_PO_Sprint2.md`, `..._Sprint3.md` y `..._Sprint4.md`, probados con tres cuentas (titular, cuidador y persona ajena).
- **Evidencia del Sprint 4:** `app_movil/evidencias/evidencias Sprint 4/Evidencia_Sprint4.md`, con capturas de la app y de Swagger.

## Próximos pasos

1. Medir los tiempos de respuesta de los endpoints principales y fijar la meta definitiva del RNF-18.
2. Preparar el despliegue con HTTPS, `SECRET_KEY` propia y CORS restringido (RNF-07, 09 y 10).
3. Agregar un límite de intentos de inicio de sesión (RNF-11).
4. Quitar del `Dockerfile` la instalación con `apt`, que no es necesaria (RNF-33).
5. Definir con el equipo el proveedor de notificaciones push (RNF-23).
6. Revisar con el docente el alcance de la normativa de protección de datos para este proyecto (RNF-14).
