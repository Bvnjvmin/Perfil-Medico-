# Manual técnico — Perfil Médico+ (BORRADOR)

**Proyecto:** Perfil Médico+ · Capstone_005D (PTY4614) · Grupo 7 · Duoc UC Sede Plaza Oeste
**Estado del documento:** borrador del 22-nov-2026, armado desde el repositorio `main`. Los pasos con Docker **no fueron ejecutados** al escribirlo (ver la sección 10); la persona que corra el script `prueba_docker_sprint5.sh` debe confirmarlos o corregirlos.
**Por qué existe:** el Cronograma (semana 15) lista como entregable del Informe Final «Informe final + **manual técnico** + README + aplicación funcional con backend en Docker». En `main` no existe un manual técnico; este borrador lo cubre y se sube como `Fase 2/Evidencias Proyecto/Evidencias de sistema/Documentos/Manual_Tecnico.md` (o se convierte a Word).

## 1. Qué es el sistema

Aplicación móvil (Flutter) con un backend propio (FastAPI) y una base de datos PostgreSQL. Una cuenta titular administra perfiles dependientes (adulto mayor, niño), programa medicamentos y rutinas, y vincula cuidadores con permisos. Si una actividad no se confirma a tiempo, el sistema escala el aviso. Incluye indicadores de salud, historial de cumplimiento, botón de asistencia, eventos de seguridad de una pulsera GPS (vía Traccar o simulador) y un asistente de IA de orientación general.

## 2. Arquitectura

```
App Flutter  ──HTTP/JSON (JWT)──►  Backend FastAPI  ──SQLAlchemy──►  PostgreSQL 16
(emulador o celular)                   │   ▲                              (migraciones Alembic)
                                       │   └── POST /traccar/posiciones ◄── Servidor Traccar ◄── pulsera GPS (o simulador)
                                       ├──► Asistente de IA (proveedor "simulado" o API de modelo de lenguaje)
                                       └──► Notificador (hoy: registra en el log; FCM preparado y apagado)
```

| Componente | Tecnología | Carpeta |
|---|---|---|
| App móvil | Flutter / Dart | `Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/app_movil` |
| Backend | Python 3.12 (imagen Docker), FastAPI, SQLAlchemy 2, Pydantic 2, JWT (HS256) | `.../Aplicacion/backend/app` |
| Base de datos | PostgreSQL 16 (Docker `postgres:16-alpine`) y Alembic (15 migraciones) | `.../backend/alembic`, modelo en `.../Base de datos/modelo_datos.md` |
| Pulsera | Servidor Traccar (opcional) y simulador `scripts/simular_pulsera.py` | `.../backend/traccar`, `.../backend/scripts` |
| Contenedores | Docker Compose (`db` y `api`; Traccar en un archivo aparte) | `.../backend/docker-compose.yml` |

Cifras verificadas desde el código el 22-nov-2026: **17 tablas**, **43 rutas** (65 operaciones HTTP), **216 pruebas automáticas** recolectadas por pytest.

## 3. Requisitos

- **Para el backend con Docker:** Docker Desktop (Windows o macOS) o Docker Engine con el plugin Compose. En Windows, la virtualización debe estar activa en la BIOS (SVM Mode en AMD, VT-x en Intel).
- **Para el backend sin Docker:** Python 3.12 o superior, PostgreSQL 16 y `pip`.
- **Para la app:** Flutter con Dart 3 (`sdk: >=3.0.0 <4.0.0`), Android Studio y un emulador Android (o un celular con depuración USB).

## 4. Puesta en marcha del backend con Docker Compose

Desde la carpeta `backend`:

1. `cp .env.example .env` y editarlo: **cambiar `SECRET_KEY` por una clave larga y aleatoria** (por ejemplo `openssl rand -hex 32`). El `.env` no se sube a GitHub (está en `.gitignore`).
2. `docker compose up --build -d` — construye la imagen, levanta `db` y `api`, aplica las migraciones (`alembic upgrade head`) y arranca la API en el puerto 8000.
3. Comprobar: `docker compose ps` (db *healthy*, api *Up*), `curl http://localhost:8000/health` y abrir `http://localhost:8000/docs` (Swagger).
4. Apagar: `docker compose down` (agregar `-v` solo si se quiere **borrar los datos**).

Servicios y puertos: API 8000; PostgreSQL 5432 (usuario `postgres`, base `perfil_medico`; credenciales de desarrollo, no usar en producción). Con Docker Compose la tarea programada de avisos viene activada (`TAREAS_PROGRAMADAS=true`).

## 5. Puesta en marcha del backend sin Docker (alternativa)

```bash
cd backend
python -m venv venv && source venv/bin/activate      # en Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # ajustar DATABASE_URL y SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Sin Docker hay que poner `TAREAS_PROGRAMADAS=true` en el `.env` para que se generen actividades y avisos solos.

## 6. Variables de entorno principales (`backend/.env.example`)

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL (con Docker la fija el compose) | `postgresql://postgres:postgres@localhost:5432/perfil_medico` |
| `SECRET_KEY` | Clave de firma de los JWT. **Obligatorio cambiarla** | texto de ejemplo |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token | 1440 |
| `TAREAS_PROGRAMADAS`, `TAREAS_INTERVALO_SEGUNDOS`, `ZONA_HORARIA`, `GENERAR_DIAS_ADELANTE` | Tarea que genera actividades y avisos | false / 60 / America/Santiago / 2 |
| `RECORDATORIO_MINUTOS_ANTES`, `ALERTA_PLAZO_1_MINUTOS`, `ALERTA_PLAZO_2_MINUTOS` | Plazos del recordatorio y de las alertas de nivel 1 y 2 | 10 / 30 / 60 |
| `NOTIFICADOR` (`log` o `fcm`), `FCM_CREDENCIALES`, `FCM_PROYECTO_ID` | Entrega de avisos. `fcm` requiere Firebase y `google-auth`; no verificado | `log` |
| `TRACCAR_TOKEN` | Clave compartida con Traccar; vacía = integración desactivada (503) | vacía |
| `BATERIA_BAJA_PORCENTAJE`, `INACTIVIDAD_MINUTOS` / `_RADIO_METROS` / `_DESDE_HORA` / `_HASTA_HORA` | Reglas de eventos de la pulsera | 15 / 180 / 30 / 8 / 22 |
| `IA_PROVEEDOR` (`simulado` o `anthropic`), `IA_API_KEY`, `IA_MODELO`, `IA_MAX_CONSULTAS_DIA` | Asistente de IA | `simulado` / vacía / `claude-haiku-5-5` / 30 |

Los valores por defecto de la tabla salen del `.env.example` y del código; ante una duda, manda el archivo.

## 7. Base de datos y migraciones

- Modelo entidad-relación de 17 tablas en `Base de datos/modelo_datos.md`.
- `alembic upgrade head` crea todo desde una base vacía; `alembic current` debe mostrar la cabeza `a5b6c7d8e9f0`; `alembic check` no debe detectar diferencias.
- Regla del equipo: **una sola persona crea migraciones** para mantener una única cabeza.

## 8. Pruebas

- Backend: `pytest app/tests -q` (en Docker: `docker compose exec api python -m pytest -q`). Las pruebas usan SQLite en memoria; no necesitan PostgreSQL. Esperado: 216 pruebas.
- Prueba de humo contra una API real: `python scripts/prueba_humo_sprint5.py` (29 comprobaciones; por defecto apunta a `localhost:8010` con el token `tok-humo`, ajustar `B` y `TOK`).
- App: `flutter analyze` y `flutter test`.
- Evidencia: `Aplicacion/app_movil/evidencias/` (capturas por sprint) y `backend/evidencias/`.

## 9. App móvil

1. `cd app_movil && flutter pub get`.
2. La dirección del backend está en `lib/services/api_service.dart` (`baseUrl`). Con el emulador de Android el valor `http://10.0.2.2:8000` apunta al computador donde corre Docker. Con un celular real hay que usar la IP del computador en la misma red.
3. `flutter run` con el emulador abierto. La sesión se guarda en `flutter_secure_storage`.
4. La hora de los avisos se muestra en la zona horaria del dispositivo.

## 10. Pulsera y Traccar (opcional)

- **Con simulador (lo que usa la demo):** poner `TRACCAR_TOKEN` en el `.env`, registrar la pulsera con `POST /perfiles/{id}/pulseras` y ejecutar `python scripts/simular_pulsera.py --token CLAVE --id IMEI posicion|sos|caida|bateria|recorrido` (ejemplos en el encabezado del script).
- **Con Traccar:** `docker compose -f docker-compose.yml -f traccar/docker-compose.traccar.yml up --build -d`; panel en el puerto 8082; puertos 5055 (OsmAnd) y 5093 (protocolo *watch*). El token de `traccar/traccar.xml` debe ser el mismo `TRACCAR_TOKEN`. Sin verificar con una pulsera real. Ver `traccar/README.md`.

## 11. Seguridad

- Contraseñas con bcrypt; sesión con JWT; cada ruta valida el permiso del vínculo con el perfil (una cuenta ajena recibe 404; sin permiso, 403).
- Nunca se suben al repositorio el `.env`, claves de IA, credenciales de Firebase ni el token real de Traccar.
- La IA no recibe RUT, correo ni teléfonos; una pregunta de urgencia recibe una respuesta fija con el 131 (SAMU) y el *4141 sin llamar al modelo; límite de 30 consultas por usuario al día.
- Los datos de prueba del proyecto son ficticios.

## 12. Límites conocidos

Sin push real (FCM) en la app; pulsera y Traccar solo con simulador; IA en modo simulado; frecuencia cardíaca y presión por Health Connect (HU 18) sin iniciar; la prueba de Docker Compose completo con capturas está pendiente; no se desarrollaron recordatorios extendidos ni farmacias vía IA.

## 13. Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Docker no inicia | Virtualización apagada | Activar SVM Mode o VT-x en la BIOS |
| `api` se reinicia | Falta `.env` o `DATABASE_URL` mal escrito | `docker compose logs api` |
| Traccar responde 503 en la API | `TRACCAR_TOKEN` vacío | Definirlo en `.env` y reiniciar `api` |
| La app no conecta | `baseUrl` incorrecto | `10.0.2.2` solo sirve con el emulador de Android |
| Prueba de humo falla por usuarios existentes | Base con datos previos | `docker compose down -v` y repetir (borra los datos) |
| Las alertas tardan en aparecer | La tarea corre cada 60 s | Esperar un minuto o bajar los plazos en `.env` |
