# Perfil Médico+

Propuesta de Proyecto APT · Capstone_005D (Grupo 7) · Ingeniería Informática · Sede Plaza Oeste

## Estado del proyecto

**Fase actual: Fase 2 — Desarrollo del Proyecto APT** (Asignatura CAPSTONE, PTY4614)

**Fase 1 — Definición (completa):**
- [x] Definición del proyecto y alcance del MVP
- [x] Documento de Inicio de Proyecto / Guía Sumativa Fase 1
- [x] Product Backlog y cronograma de actividades del equipo
- [x] Exposición grupal sumativa (Semana 4)

**Fase 2 — Desarrollo (por sprint):**
- [x] Sprint 1 (S5-S6) — Autenticación, modelo de datos, estructura base de la app
  - Backend (FastAPI + PostgreSQL) con registro, login (JWT) y endpoint protegido
  - Migraciones con Alembic, Docker + docker-compose, 7 pruebas automatizadas
  - Cierre con arrastre menor a Sprint 2 (parte de datos básicos de salud y validación de la app) — ver [`Metodologia_Scrum/Sprint_1`](<./Metodologia_Scrum/Sprint_1>)
- [x] Sprint 2 (S7-S8) — Perfil de salud, medicamentos, rutinas de cuidado y agenda diaria *(cerrado: 5 de 5 historias)*
  - Backend: perfil de salud con alergias y contactos de emergencia, medicamentos y rutinas (25 pruebas automatizadas); entregado el 30-09
  - App: pantallas de registro e inicio de sesión, perfil, medicamentos, rutinas y agenda diaria, con 8 pruebas de Flutter y capturas de la prueba manual
  - La app de la HU 3 y la HU 5 se cerró el 10-10, una semana después del cierre del sprint (03-10); la confirmación de actividades quedó guardada solo en el celular y se completa en el Sprint 3 — ver [`Metodologia_Scrum/Sprint_2`](<./Metodologia_Scrum/Sprint_2>)
- [ ] Sprint 3 (S9-S10) — Perfiles dependientes, cuidadores con permisos y panel diario · Informe de Avance (cierre el 17-10) *(en curso)*
  - Base de datos terminada (13-10): tablas `actividad` y `perfil_acceso`, índice de un solo titular por cuenta y borrado en cascada
  - Backend terminado (15-10): perfiles dependientes validados (HU 6), agenda diaria con confirmación guardada en el servidor (HU 5), cuidadores con permisos por perfil (HU 7) y `GET /panel` (HU 8); 119 pruebas automatizadas
  - Pendiente: pantallas de la app para las HU 6, 7 y 8, checklist de aceptación del Product Owner, retrospectiva del Sprint 2 e Informe de Avance — ver [`Metodologia_Scrum/Sprint_3`](<./Metodologia_Scrum/Sprint_3>)
- [ ] Sprint 4 (S11-S12) — Recordatorios y alertas escalonadas
- [ ] Sprint 5 (S13-S14) — Indicadores de salud, módulo de IA, pulsera inteligente (Traccar + Health Connect)
- [ ] Sprint 6 (S15) — Glucosa manual, recordatorios extendidos, farmacias vía IA, pruebas, Informe Final (Semana 15)

**Fase 3 — Presentación y defensa final (Semanas 16-18)**

## Documentación

**Fase 1** — en [`Fase 1`](./Fase%201):

- [Guía Sumativa Fase 1 (grupal)](<./Fase 1/Evidencias Grupales/1.5_GuiaEstudiante_Fase1_DefinicionProyectoAPT_PerfilMedico.docx>)
- [Formativa Fase 1 — Informe Técnico (grupal)](<./Fase 1/Evidencias Grupales/1.4_APT122_FormativaFase1.docx>)
- [Cronograma de actividades y Product Backlog](<./Fase 1/Evidencias Grupales/Cronograma_Actividades_Equipo_PerfilMedico.xlsx>)
- [Autoevaluaciones y Diario de Reflexión (individuales)](<./Fase 1/Evidencias Individuales>)

**Fase 2** — en [`Fase 2`](<./Fase 2>):

- [Documentos de evaluación grupales (2.3, 2.4, 2.6)](<./Fase 2/Evidencias Grupales>) — el 2.3 es la pauta de referencia del docente y se sube tal cual, sin rellenar. Las planillas de evaluación de avance/final no se suben al repositorio (uso interno del docente, confirmado con él).
- [Diario de Reflexión y Autoevaluación individuales (2.1, 2.2)](<./Fase 2/Evidencias Individuales>) — un archivo por integrante, con el patrón `Apellido_Nombre_2.X_...docx` (mismo criterio que en Fase 1).
- [Metodología Scrum — Sprint Backlog, actas y retrospectivas](<./Metodologia_Scrum>)
- [Código del backend](<./Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend>) (autenticación, perfil de salud, medicamentos y rutinas, agenda diaria, perfiles dependientes, cuidadores y panel)
- [Código de la app móvil](<./Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/app_movil>) (registro e inicio de sesión, perfil, medicamentos, rutinas y agenda diaria; las pantallas de perfiles dependientes, cuidadores y panel están pendientes)
- [Modelo de datos (diagrama ER)](<./Fase 2/Evidencias Proyecto/Evidencias de sistema/Base de datos/modelo_datos.md>) y checklist de aceptación del Product Owner

## Descripción

**Perfil Médico+** es una aplicación móvil pensada para centralizar la gestión de la salud personal y familiar: horas médicas, medicamentos, tratamientos, controles, alimentación e hidratación.

Está dirigida principalmente a **adultos mayores no autovalentes** y **niños** — los dos perfiles dependientes que atiende el proyecto —, además de los adultos responsables que los cuidan. Su diferenciador es el modelo de **cuenta titular con perfiles dependientes**: un usuario puede vincular y hacer seguimiento de personas a su cargo desde una sola cuenta, con permisos configurables sobre qué información puede ver cada cuidador.

El sistema funciona bajo un flujo de seguimiento continuo:

```
Planificar → Recordar → Confirmar → Monitorear → Alertar → Acompañar
```

Cuando una actividad de cuidado (medicamento, comida, hidratación, etc.) no se confirma dentro del plazo esperado, el sistema escala el aviso hasta notificar al cuidador autorizado, sin asumir automáticamente una emergencia.

### Tres interfaces distintas según quién la usa

- **App del titular/cuidador** — estructura completa: gestión de perfiles, alertas, historial, configuración.
- **Vista de la app para el perfil dependiente** — simplificada: botones grandes, solo acciones de confirmación.
- **Pulsera inteligente** — su propia interfaz física, mínima: botón SOS + pantalla de estado, independiente de la app.

## Diferenciadores (roadmap Fase 2)

Para distinguirse de otras apps de recordatorio de medicamentos, Perfil Médico+ se integra con una **pulsera inteligente ya disponible en el mercado** (sin fabricar hardware propio):

- **Ubicación y salud:** GPS con geocercas (alerta si el niño no llega al colegio o el adulto mayor sale de una zona segura) vía un servidor propio [Traccar](https://www.traccar.org/) (plataforma de rastreo GPS gratuita y de código abierto, auto-hospedada) — así el dato de ubicación llega directo a nuestra base de datos, sin depender de la app cerrada del fabricante de la pulsera. Además, frecuencia cardíaca vía [Health Connect](https://developer.android.com/health-and-fitness/guides/health-connect) (API gratuita y oficial de Android), y presión arterial referencial (no reemplaza un tensiómetro médico).
- **Seguridad:** detección automática de caídas, botón SOS físico, alerta de batería baja del dispositivo, y detección de inactividad inusual — funciones que ya traen de fábrica los relojes GPS para niños/adultos mayores.

> Para comprar el modelo correcto: la pulsera debe usar un protocolo compatible con Traccar (ej. GT06, TK102/103, Coban) — se verifica con el proveedor antes de comprar el lote, probando 1-2 unidades de muestra.

Además, se suman tres funcionalidades 100% de software:

- **Registro manual de glucosa:** el cuidador ingresa la lectura de un glucómetro certificado. No se mide de forma automática por seguridad — la [FDA advirtió en 2024](https://www.fda.gov/medical-devices/safety-communications/no-utilice-relojes-inteligentes-ni-anillos-inteligentes-para-medir-los-niveles-de-glucosa-en-sangre) que ningún smartwatch o anillo inteligente está aprobado para medir glucosa sin pinchazo.
- **Recordatorios extendidos:** indicaciones posteriores a una consulta médica y citas médicas pendientes, con recordatorio diario.
- **Farmacias cercanas vía IA:** consulta sobre disponibilidad y precio de un medicamento, comparando por cercanía y precio — inspirado en herramientas públicas reales como [TuFarmacia.gob.cl](https://tufarmacia.minsal.cl/) (MINSAL) y comparadores como [BuscaFarma](https://buscafarma.cl/).

Todo lo anterior se plantea como **incremento sobre el MVP base**, a priorizar en Fase 2 según el avance del equipo (ver Sprints 5-6 más abajo) — el MVP (autenticación, rutinas, recordatorios, permisos) es lo que se entrega sí o sí.

## Modelo de negocio (proyección a futuro)

| Plan | Precio | Incluye |
|---|---|---|
| **Gratis** | $0 | 1 perfil, recordatorios básicos, confirmación manual, historial de 7 días |
| **Perfil Médico+ Premium** | $3.490 CLP/mes o $29.990 CLP/año (**primer** perfil dependiente) | Pulsera inteligente conectada, alertas escalonadas al cuidador, historial completo + reportes para el médico, módulo de IA (orientación + farmacias) |

Cada perfil dependiente adicional que la misma cuenta agregue (manteniendo el primero activo) tiene un **5% de descuento** sobre el valor de ese perfil extra (ej. segundo perfil: ~$3.315 CLP/mes) — premiando a quien cuida de más de una persona, sin encarecer el plan base. El precio se fijó buscando ser accesible para una familia chilena, y a la vez permitir alcanzar rentabilidad en un plazo razonable dado el bajo costo operativo (APIs externas gratuitas como Health Connect y Traccar). El plan pagado se activa naturalmente en el momento de mayor necesidad percibida: cuando el usuario quiere agregar a un familiar a su cargo.

## Tecnologías utilizadas

| Capa | Tecnología | Motivo |
|---|---|---|
| App móvil | **Flutter** (Dart) | Un solo código para iOS y Android, clave con un equipo chico. |
| Backend | **FastAPI** (Python) | Endpoints rápidos, validación automática de datos y documentación Swagger generada sola. |
| Base de datos | **PostgreSQL** | Relacional; se ajusta a los datos interrelacionados del perfil dependiente y al modelo de cuenta titular + perfiles dependientes. |
| Autenticación | **JWT** | Distingue entre usuario titular y perfiles dependientes, y controla accesos sobre datos médicos sensibles. |
| Migraciones | **Alembic** | Versiona los cambios al esquema de base de datos junto con el código. |
| Módulo de IA | API de modelo de lenguaje (LLM) | Consultas básicas de síntomas y farmacias, sin entrenar un modelo propio. |
| Wearables (salud) | **Health Connect** | API gratuita y oficial de Android para leer datos de la pulsera inteligente (frecuencia cardíaca, presión referencial). |
| Wearables (ubicación) | **Traccar** | Servidor propio (Docker) que recibe el GPS directo de la pulsera, sin depender de la app cerrada del fabricante. |
| Diseño UI/UX | **Figma** | Definir pantallas y flujos antes de programar. |
| Contenedores | **Docker** | Empaquetar backend, base de datos y Traccar para un despliegue reproducible, sin costos de licencia. |
| Generación de reportes | **PDF (backend)** | Exporta el historial de cumplimiento y signos vitales para llevar a la consulta médica. |

## Instrucciones para ejecutar el proyecto localmente

### Backend (FastAPI) — Sprints 1 a 3 (autenticación, salud, cuidado, perfiles dependientes, cuidadores y panel)

Código en [`Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend`](<./Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend>).

**Con Docker (recomendado):**

```bash
cd "Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend"
cp .env.example .env
docker compose up --build
```

La API queda en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

**Sin Docker:**

```bash
cd "Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend"
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

**Pruebas** (119 pruebas; no requieren Docker ni PostgreSQL, usan SQLite en memoria):

```bash
pytest app/tests/ -v
```

SQLite no valida llaves foráneas, así que los cambios de base de datos se prueban además contra PostgreSQL. Solo una persona crea migraciones de Alembic por sprint, para mantener una única cabeza en la cadena.

### App móvil (Flutter) — Sprint 2: registro, perfil, medicamentos, rutinas y agenda

```bash
cd "Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/app_movil"
flutter pub get
flutter run
flutter test
```

En el emulador de Android la app apunta al backend local en `10.0.2.2:8000`.

## Integrantes del equipo

| Integrante | Rol | Módulo | Contacto |
|---|---|---|---|
| Benjamín Leiva | *Backend Developer* | API, autenticación, orquestación de IA | b.leiva@duocuc.cl |
| Sergio Ocares | *Product Owner* | Base de datos, indicadores, integración de IA | se.ocares@duocuc.cl |
| Matías Pizarro | *App Developer (Flutter)* | Interfaz móvil, experiencia de usuario | mr.pizarro@duocuc.cl |

## Metodología de trabajo

El equipo trabaja con **Scrum**: sprints quincenales, Product Backlog priorizado con historias de usuario, Sprint Backlog por sprint, revisión y retrospectiva al cierre de cada sprint. La evidencia de avance (Sprint Backlog, actas de seguimiento y retrospectivas) queda documentada en [`Metodologia_Scrum`](<./Metodologia_Scrum>), conforme a lo exigido por el Instructivo CAPSTONE. El Product Backlog completo y el Cronograma del equipo viven en [`Cronograma_Actividades_Equipo_PerfilMedico.xlsx`](<./Fase 1/Evidencias Grupales/Cronograma_Actividades_Equipo_PerfilMedico.xlsx>).

## Arquitectura de la solución

Arquitectura de alto nivel orientada a servicios:

- **App móvil (Flutter):** interfaz para el titular, el perfil dependiente (modo simplificado) y el cuidador. Consume la API vía HTTPS.
- **API (FastAPI):** expone endpoints REST para cuentas, perfiles, rutinas, actividades, confirmaciones, alertas y el módulo de IA. Maneja autenticación/autorización con JWT.
- **Base de datos (PostgreSQL):** modelo relacional que conecta cuentas, perfiles dependientes, actividades de cuidado y su estado de cumplimiento. Versionada con Alembic.
- **Servidor Traccar:** recibe la señal GPS de la pulsera inteligente directo, sin pasar por el fabricante; el backend consulta su API REST.
- **Servicio de IA:** integración externa vía API de LLM para consultas de síntomas y farmacias cercanas, desacoplada del núcleo del sistema.
- **Sistema de notificaciones/alertas:** genera recordatorios y escala a alertas al cuidador cuando una actividad no se confirma en el tiempo esperado.

```
[App Flutter] ──HTTPS──> [API FastAPI] ──> [PostgreSQL]
                              │
                              ├──> [Servidor Traccar] ──> [Pulsera GPS]
                              ├──> [API LLM externa]  (síntomas / farmacias)
                              └──> [Servicio de notificaciones/alertas]
```

*(Diagrama de arquitectura detallado y diagramas UML se agregan en [`Metodologia_Scrum`](<./Metodologia_Scrum>), conforme al Instructivo CAPSTONE.)*
