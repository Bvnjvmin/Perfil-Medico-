# Perfil Médico+

Propuesta de Proyecto APT · Capstone_005D (Grupo 7) · Ingeniería Informática · Sede Plaza Oeste

## Descripción

**Perfil Médico+** es una plataforma (app móvil + web) pensada para centralizar la gestión de la salud personal y familiar: horas médicas, medicamentos, tratamientos, controles, alimentación e hidratación.

Está dirigida principalmente a adultos mayores, personas con enfermedades crónicas, niños y personas que requieren apoyo permanente, además de los familiares y cuidadores que los acompañan. Su diferenciador es el modelo de **cuenta titular con perfiles dependientes**: un usuario puede vincular y hacer seguimiento de personas a su cargo (por ejemplo, un padre adulto mayor o un hijo) desde una sola cuenta, con permisos configurables sobre qué información puede ver cada cuidador.

El sistema funciona bajo un flujo de seguimiento continuo:

```
Planificar → Recordar → Confirmar → Monitorear → Alertar → Acompañar
```

Cuando una actividad de cuidado (medicamento, comida, hidratación, etc.) no se confirma dentro del plazo esperado, el sistema escala el aviso hasta notificar al cuidador autorizado, sin asumir automáticamente una emergencia.

## Tecnologías utilizadas

| Capa | Tecnología | Motivo |
|---|---|---|
| App móvil | **Flutter** (Dart) | Un solo código para iOS y Android, clave con un equipo chico; ecosistema maduro para formularios, notificaciones y navegación. |
| Backend | **FastAPI** (Python) | Levantar endpoints rápido, validación automática de datos y documentación Swagger generada sola. |
| Base de datos | **PostgreSQL** | Relacional; se ajusta a los datos interrelacionados del paciente (horas, medicamentos, exámenes) y al modelo de cuenta titular + perfiles dependientes. |
| Autenticación | **JWT** | Distingue entre usuario titular y perfiles dependientes, y controla accesos sobre datos médicos sensibles. |
| Módulo de IA | API de modelo de lenguaje (LLM) | Consultas básicas de síntomas, sin entrenar un modelo propio, para enfocar el esfuerzo del semestre en la gestión médica/familiar. |
| Diseño UI/UX | **Figma** | Definir pantallas y flujos antes de programar, evitando rehacer trabajo. |

## Instrucciones para ejecutar el proyecto localmente

> Instrucciones base; ajustar cuando el repo tenga la estructura final de carpetas (`/backend`, `/app`, etc.) y su `docker-compose.yml`.

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # completar variables (DB, JWT_SECRET, LLM_API_KEY, etc.)
uvicorn app.main:app --reload
```

La documentación interactiva de la API queda disponible en `http://localhost:8000/docs`.

### Base de datos (PostgreSQL)

```bash
docker compose up -d db
alembic upgrade head             # o el método de migraciones que se defina
```

### App móvil (Flutter)

```bash
cd app
flutter pub get
flutter run
```

### Variables de entorno mínimas

```
DATABASE_URL=postgresql://usuario:password@localhost:5432/perfilmedicoplus
JWT_SECRET=
LLM_API_KEY=
```

## Integrantes del equipo

| Integrante | Rol | Contacto |
|---|---|---|
| Benjamín Leiva | *Backend Developer* | b.leiva@duocuc.cl |
| Sergio Ocares | *Product Owner* | se.ocares@duouc.cl |
| Matías Pizarro | *Frontend Developer* | mr.pizarro@duocuc.cl |

## Metodología de trabajo

El equipo trabaja con **Scrum**: sprints cortos, Product Backlog priorizado con historias de usuario, Sprint Backlog por sprint, revisión y retrospectiva al cierre de cada sprint. La evidencia de avance (Product Vision, Backlog, Sprint Backlog, Definition of Done y retrospectivas) queda documentada en el repositorio conforme a lo exigido por el Instructivo CAPSTONE.

## Arquitectura de la solución

Arquitectura de alto nivel orientada a servicios:

- **App móvil (Flutter):** interfaz para paciente, adulto mayor (modo simplificado) y cuidador. Consume la API vía HTTPS.
- **API (FastAPI):** expone endpoints REST para perfiles, rutinas, actividades, confirmaciones, alertas y el módulo de IA. Maneja autenticación/autorización con JWT y control de acceso basado en roles (titular / dependiente / cuidador).
- **Base de datos (PostgreSQL):** modelo relacional que conecta cuentas, perfiles dependientes, actividades de cuidado y su estado de cumplimiento.
- **Servicio de IA:** integración externa vía API de LLM para consultas básicas de síntomas, desacoplada del núcleo del sistema.
- **Sistema de notificaciones/alertas:** genera recordatorios y escala a alertas al cuidador cuando una actividad no se confirma en el tiempo esperado.

```
[App Flutter] ──HTTPS──> [API FastAPI] ──> [PostgreSQL]
                              │
                              ├──> [API LLM externa]  (consultas de síntomas)
                              └──> [Servicio de notificaciones/alertas]
```

*(Diagrama de arquitectura detallado y diagramas UML se agregarán en la documentación de diseño del proyecto, conforme al Instructivo CAPSTONE.)*
