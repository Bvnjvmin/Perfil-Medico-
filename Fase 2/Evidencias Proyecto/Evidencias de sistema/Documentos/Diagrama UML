# Diagramas UML — Perfil Médico+

**Equipo 7 · Capstone_005D · Ingeniería Informática, Sede Plaza Oeste**
**Estado del sistema documentado:** Sprints 1 a 4 (backend FastAPI + PostgreSQL y app Flutter), al 5 de noviembre de 2026.

Los diagramas están escritos en [Mermaid](https://mermaid.js.org/), así que GitHub los dibuja directamente al abrir este archivo. Se hicieron a partir del código real del repositorio (rutas, modelos y servicios del backend), no de una idea general del sistema. Lo que todavía no está construido (pulsera, módulo de IA, push real con FCM) aparece marcado como **futuro**.

## Contenido

1. [Diagrama de casos de uso](#1-diagrama-de-casos-de-uso)
2. [Diagrama de componentes (arquitectura)](#2-diagrama-de-componentes-arquitectura)
3. [Diagrama de clases del dominio](#3-diagrama-de-clases-del-dominio)
4. [Diagramas de secuencia](#4-diagramas-de-secuencia)
   - 4.1 Registro e inicio de sesión
   - 4.2 Invitar a un cuidador (HU 7)
   - 4.3 Confirmar una actividad (HU 5)
   - 4.4 Recordatorios y alertas escalonadas (HU 9 y 10)
5. [Diagrama de estados de una actividad](#5-diagrama-de-estados-de-una-actividad)

---

## 1. Diagrama de casos de uso

Muestra quién usa el sistema y qué puede hacer. El **Sistema** es un actor porque la tarea programada del backend actúa sola, sin que nadie la active (corre cada 60 segundos).

```mermaid
flowchart LR
    T["Titular"]:::actor
    C["Cuidador autorizado"]:::actor
    D["Dependiente<br/>(modo simplificado)"]:::actor
    S["Sistema<br/>(tarea programada)"]:::actor

    subgraph SIS["Perfil Médico+"]
        direction TB
        U1(["Registrarse e iniciar sesión (HU 1)"])
        U2(["Gestionar perfil de salud:<br/>alergias y contactos (HU 2)"])
        U3(["Gestionar medicamentos y rutinas (HU 4)"])
        U4(["Definir horarios de un<br/>medicamento o rutina"])
        U5(["Ver agenda diaria (HU 5)"])
        U6(["Confirmar o desconfirmar<br/>una actividad (HU 5)"])
        U7(["Crear perfil dependiente (HU 6)"])
        U8(["Invitar, editar y revocar<br/>cuidadores (HU 7)"])
        U9(["Ver panel de dependientes (HU 8)"])
        U10(["Ver avisos: recordatorios<br/>y alertas (HU 9 y 10)"])
        U11(["Registrar dispositivo<br/>para notificaciones (HU 9)"])
        U12(["Usar modo simplificado (HU 11)"])
        U13(["Generar actividades del día"])
        U14(["Enviar recordatorio"])
        U15(["Escalar alerta de nivel 1 y 2"])
        U16(["Marcar actividad como vencida"])
    end

    T --- U1
    T --- U2
    T --- U3
    T --- U4
    T --- U5
    T --- U6
    T --- U7
    T --- U8
    T --- U9
    T --- U10
    T --- U11
    T --- U12

    C --- U1
    C --- U5
    C --- U6
    C --- U9
    C --- U10
    C --- U11

    D --- U12
    D --- U6

    S --- U13
    S --- U14
    S --- U15
    S --- U16

    U15 -. "«extend»<br/>si sigue pendiente" .-> U14
    U12 -. "«include»" .-> U5

    classDef actor fill:#fff7e0,stroke:#b8860b,stroke-width:2px;
```

**Notas**
- El cuidador solo puede hacer lo que el titular le permita en cada perfil (`puede_confirmar`, `puede_editar_rutinas`, `puede_ver_indicadores`, `recibe_alertas`). Una persona sin vínculo recibe error 404 y no ve nada.
- El dependiente confirma sus actividades desde la cuenta del titular, en modo simplificado, sin poder editar ni borrar datos.
- **Futuro (Sprints 5 y 6):** indicadores de salud e historial de cumplimiento (HU 12 y 13), botón de asistencia y módulo de IA (HU 14 y 15), pulsera con Traccar y Health Connect (HU 17 a 19), registro manual de glucosa (HU 20), recordatorios extendidos (HU 21) y farmacias cercanas con IA (HU 22).

---

## 2. Diagrama de componentes (arquitectura)

Muestra las piezas que se construyeron y cómo se comunican. Las líneas punteadas son partes planificadas que aún no existen.

```mermaid
flowchart TB
    subgraph MOVIL["App móvil (Flutter)"]
        direction TB
        P1["Pantallas: login, perfil, medicamentos,<br/>rutinas, agenda, compartir perfil, panel"]
        P2["Pantalla Avisos y modo simplificado"]
        P3["ApiService<br/>(timeout de 15 s)"]
        P4["TokenStorage<br/>(flutter_secure_storage)"]
        P1 --> P3
        P2 --> P3
        P3 --> P4
    end

    subgraph API["Backend (FastAPI) — contenedor Docker"]
        direction TB
        R["Rutas (routers):<br/>auth, perfil, medicamento, horario, actividad,<br/>cuidador, panel, aviso"]
        SEG["Seguridad:<br/>JWT + bcrypt + permisos por perfil"]
        SV["Servicios:<br/>actividades, alertas, notificador, tiempo"]
        TP["Tarea programada<br/>(cada 60 s)"]
        R --> SEG
        R --> SV
        TP --> SV
    end

    DB[("PostgreSQL 16<br/>migraciones con Alembic")]
    LOG["Registro (log) de avisos"]

    P3 -- "HTTP / JSON + JWT" --> R
    SV --> DB
    SEG --> DB
    SV --> LOG

    FCM["Servicio push (FCM)<br/>FUTURO"]:::futuro
    TRC["Servidor Traccar + pulsera<br/>FUTURO"]:::futuro
    LLM["API de IA (LLM)<br/>FUTURO"]:::futuro
    SV -.-> FCM
    SV -.-> TRC
    SV -.-> LLM

    classDef futuro fill:#eeeeee,stroke:#999999,stroke-dasharray: 5 5,color:#555555;
```

**Notas**
- Hoy los avisos se guardan en la base de datos, se muestran en la pantalla Avisos y se escriben en el log (`NOTIFICADOR=log`). El push real al celular queda pendiente de elegir el proveedor.
- Docker Compose levanta la API y PostgreSQL con un solo comando; al arrancar aplica las migraciones y activa la tarea programada.

---

## 3. Diagrama de clases del dominio

Representa las tablas del modelo de datos como clases, con sus relaciones y multiplicidades. Es el mismo modelo que el diagrama ER de `Base de datos/Diagramas`, visto en notación UML.

```mermaid
classDiagram
    direction LR

    class Usuario {
        +str id
        +str nombre
        +str email
        +str hashed_password
        +datetime creado_en
    }
    class Perfil {
        +UUID id
        +str cuenta_titular_id
        +str tipo
        +str nombre
        +str rut
        +str grupo_sanguineo
        +date fecha_nacimiento
        +str subtipo
        +bool activo
        +datetime creado_en
    }
    class PerfilAcceso {
        +UUID id
        +str usuario_id
        +UUID perfil_id
        +str rol_vinculo
        +bool puede_confirmar
        +bool puede_editar_rutinas
        +bool puede_ver_indicadores
        +bool recibe_alertas
        +int nivel_escalamiento
    }
    class Alergia {
        +UUID id
        +str sustancia
        +str severidad
    }
    class ContactoEmergencia {
        +UUID id
        +str nombre
        +str telefono
        +str relacion
        +int prioridad
    }
    class Medicamento {
        +UUID id
        +str nombre
        +str dosis
        +str frecuencia
        +time hora_inicio
        +bool activo
        +datetime creado_en
    }
    class RutinaCuidado {
        +UUID id
        +str tipo
        +str descripcion
        +str frecuencia
        +time hora
        +bool activo
        +datetime creado_en
    }
    class RutinaHorario {
        +UUID id
        +time hora
    }
    class Actividad {
        +UUID id
        +date fecha
        +time hora
        +str estado
        +datetime confirmada_en
        +str confirmada_por_id
    }
    class Alerta {
        +UUID id
        +str tipo
        +int nivel
        +str mensaje
        +datetime creada_en
        +datetime leida_en
    }
    class DispositivoPush {
        +UUID id
        +str token
        +str plataforma
        +datetime creado_en
    }

    Usuario "1" --> "0..*" Perfil : administra como titular
    Usuario "1" --> "0..*" PerfilAcceso : tiene acceso a
    Perfil "1" --> "0..*" PerfilAcceso : tiene cuidadores
    Perfil "1" *-- "0..*" Alergia : registra
    Perfil "1" *-- "0..*" ContactoEmergencia : registra
    Perfil "1" *-- "0..*" Medicamento : tiene
    Perfil "1" *-- "0..*" RutinaCuidado : tiene
    Perfil "1" *-- "0..*" Actividad : tiene
    Medicamento "1" *-- "0..*" RutinaHorario : se toma a las
    RutinaCuidado "1" *-- "0..*" RutinaHorario : se hace a las
    Medicamento "0..1" --> "0..*" Actividad : genera
    RutinaCuidado "0..1" --> "0..*" Actividad : genera
    Usuario "0..1" --> "0..*" Actividad : confirma
    Actividad "1" *-- "0..*" Alerta : origina avisos
    Usuario "1" --> "0..*" Alerta : recibe
    Usuario "1" *-- "0..*" DispositivoPush : registra
```

**Reglas que la base de datos hace cumplir** (no solo el código):
- Una `Actividad` apunta a un medicamento **o** a una rutina, nunca a ambos ni a ninguno (restricción `ck_actividad_un_solo_origen`). Lo mismo vale para `RutinaHorario`.
- `estado` solo admite `pendiente`, `confirmada`, `vencida` u `omitida`.
- Una cuenta no puede tener dos perfiles `titular` (índice único).
- Una `Alerta` no se repite para la misma actividad, usuario, tipo y nivel, de modo que la tarea programada puede correr cada minuto sin duplicar avisos.
- Al borrar un perfil, medicamento, rutina o usuario, sus datos dependientes se borran en cascada.

---

## 4. Diagramas de secuencia

### 4.1 Registro e inicio de sesión

```mermaid
sequenceDiagram
    actor U as Usuario
    participant A as App Flutter
    participant API as API FastAPI
    participant DB as PostgreSQL

    U->>A: Ingresa nombre, correo y contraseña
    A->>API: POST /auth/register
    API->>API: Valida datos (correo válido, contraseña de 8 a 72 caracteres)
    API->>API: Calcula el hash bcrypt de la contraseña
    API->>DB: Guarda el usuario con hashed_password
    API-->>A: 201 Usuario (sin contraseña)

    U->>A: Ingresa correo y contraseña
    A->>API: POST /auth/login
    API->>DB: Busca el usuario por correo
    API->>API: Compara la contraseña con el hash
    alt Credenciales correctas
        API-->>A: 200 access_token (JWT, vence en 24 h)
        A->>A: Guarda el token en almacenamiento seguro
    else Credenciales incorrectas
        API-->>A: 401 Correo o contraseña incorrectos
    end
```

### 4.2 Invitar a un cuidador (HU 7)

```mermaid
sequenceDiagram
    actor T as Titular
    participant A as App Flutter
    participant API as API FastAPI
    participant DB as PostgreSQL

    T->>A: Elige el perfil, escribe el correo del cuidador y sus permisos
    A->>API: POST /perfiles/{id}/cuidadores (JWT del titular)
    API->>DB: Verifica que quien invita sea el titular del perfil
    alt No es el titular
        API-->>A: 403 sin permiso (o 404 si no tiene vínculo)
    else Es el titular
        API->>DB: Busca la cuenta por correo
        alt La cuenta no existe
            API-->>A: 404 No existe una cuenta con ese correo
        else Intenta vincularse a sí mismo o ya está vinculado
            API-->>A: 400 o 409
        else Todo correcto
            API->>DB: Crea PerfilAcceso con permisos y nivel de escalamiento
            API-->>A: 201 Vínculo creado
        end
    end

    Note over T,DB: Para revocar: DELETE /perfiles/{id}/cuidadores/{acceso_id}.<br/>El acceso se pierde de inmediato (el siguiente GET del cuidador da 404).
```

### 4.3 Confirmar una actividad (HU 5)

```mermaid
sequenceDiagram
    actor Q as Titular o cuidador
    participant A as App Flutter
    participant API as API FastAPI
    participant DB as PostgreSQL

    Q->>A: Toca "Confirmar" en una actividad de la agenda
    A->>API: POST /actividades/{id}/confirmar (JWT)
    API->>DB: Busca la actividad y su perfil
    API->>DB: Comprueba el vínculo y el permiso puede_confirmar
    alt Sin vínculo con el perfil
        API-->>A: 404
    else Vínculo sin permiso de confirmar
        API-->>A: 403
    else Con permiso
        API->>DB: estado = confirmada, confirmada_en, confirmada_por_id
        API-->>A: 200 Actividad confirmada
        A->>A: Actualiza la agenda en pantalla
    end

    Note over API,DB: Una actividad confirmada deja de escalar:<br/>el motor de alertas solo mira las pendientes.
```

### 4.4 Recordatorios y alertas escalonadas (HU 9 y 10)

Los plazos son los valores por defecto (`RECORDATORIO_MINUTOS_ANTES=10`, `ALERTA_PLAZO_1_MINUTOS=30`, `ALERTA_PLAZO_2_MINUTOS=60`) y se pueden cambiar con variables de entorno.

```mermaid
sequenceDiagram
    participant TP as Tarea programada (cada 60 s)
    participant SV as Servicios (actividades y alertas)
    participant DB as PostgreSQL
    participant N as Notificador (log)
    actor Tit as Titular
    actor C1 as Cuidador nivel 1
    actor C2 as Cuidador nivel 2

    TP->>SV: generar_actividades (hoy y 2 días adelante)
    SV->>DB: Crea una actividad por horario, sin duplicar
    TP->>SV: procesar_avisos(ahora)
    SV->>DB: Actividades pendientes de días anteriores pasan a vencida

    Note over SV,DB: Actividad pendiente con hora H
    SV->>DB: Desde H menos 10 min: crea recordatorio (nivel 0)
    DB-->>Tit: Recordatorio
    DB-->>C1: Recordatorio (si recibe_alertas)
    DB-->>C2: Recordatorio (si recibe_alertas)

    Note over SV,DB: Pasan 30 min desde H sin confirmar
    SV->>DB: Crea alerta de nivel 1
    DB-->>Tit: Alerta nivel 1
    DB-->>C1: Alerta nivel 1

    Note over SV,DB: Pasan 60 min desde H sin confirmar
    SV->>DB: Crea alerta de nivel 2
    DB-->>C2: Alerta nivel 2

    SV->>N: Envía los avisos nuevos a los dispositivos registrados
    N->>N: Hoy solo escribe en el log (push con FCM pendiente)

    Note over TP,DB: Si alguien confirma la actividad en cualquier momento,<br/>deja de estar pendiente y no se crean más avisos.<br/>La restricción única de la tabla alerta evita avisos repetidos.
```

---

## 5. Diagrama de estados de una actividad

```mermaid
stateDiagram-v2
    [*] --> pendiente: el sistema genera la actividad<br/>(una por horario y día)
    pendiente --> confirmada: confirmar<br/>(titular o cuidador con permiso)
    confirmada --> pendiente: desconfirmar
    pendiente --> vencida: termina el día sin confirmarse
    pendiente --> omitida: reservado para uso futuro
    confirmada --> [*]
    vencida --> [*]
    omitida --> [*]

    note right of pendiente
        Solo en este estado se crean
        recordatorios y alertas.
    end note
```

---

## Trazabilidad con el código

| Diagrama | Fuente en el repositorio |
|---|---|
| Casos de uso | Product Backlog (HU 1 a 22) y rutas en `backend/app/api/routes/` |
| Componentes | `backend/app/main.py`, `backend/docker-compose.yml`, `app_movil/lib/services/` |
| Clases | `backend/app/models/` y `Base de datos/modelo_datos.md` |
| Secuencia 4.1 | `routes/auth.py`, `core/security.py` |
| Secuencia 4.2 | `routes/cuidador.py` |
| Secuencia 4.3 | `routes/actividad.py` |
| Secuencia 4.4 | `services/actividades.py`, `services/alertas.py`, `services/notificador.py` |
| Estados | `models/actividad.py` y `services/alertas.py` |
