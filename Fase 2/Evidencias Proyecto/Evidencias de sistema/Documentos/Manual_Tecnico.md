# Manual técnico — Perfil Médico+

**Proyecto:** Perfil Médico+ · Capstone_005D (PTY4614) · Grupo 7 · Duoc UC Sede Plaza Oeste
**Estado del documento:** versión del 26-nov-2026, armada desde el repositorio `main`. Los pasos con Docker se confirmaron con la corrida del 23-nov (ver `Evidencia_Docker_Sprint5.md`); falta repetir D4 con el parche y capturar el panel de Traccar (D6). Lo que depende del parche de seguridad está marcado como «con el parche».
**Por qué existe:** el Cronograma (semana 15) lista como entregable del Informe Final «Informe final + **manual técnico** + README + aplicación funcional con backend en Docker». En `main` no existía un manual técnico; este documento lo cubre y se sube como `Fase 2/Evidencias Proyecto/Evidencias de sistema/Documentos/Manual_Tecnico.md` (o se convierte a Word).

## 1. Qué es el sistema

Aplicación móvil (Flutter) con un backend propio (FastAPI) y una base de datos PostgreSQL. Una cuenta titular administra perfiles dependientes (adulto mayor, niño), programa medicamentos y rutinas, y vincula cuidadores con permisos. Si una actividad no se confirma a tiempo, el sistema escala el aviso. Incluye indicadores de salud, historial de cumplimiento, botón de asistencia, eventos de seguridad de una pulsera GPS (vía Traccar o simulador) y un asistente de IA de orientación general.

## 2. Arquitectura

```
App Flutter  ──HTTP/JSON (JWT)──►  Backend FastAPI  ──SQLAlchemy──►  PostgreSQL 16
(emulador o celular)                   │   ▲                              (migraciones Alembic)
                                       │   └── POST /traccar/posiciones ◄── Servidor Traccar ◄── pulsera GPS (o simulador)
                                       ├──► Asistente de IA (proveedor "simulado" o Claude Haiku 5.5, de Anthropic)
                                       └──► Notificador (hoy: registra en el log; FCM preparado y apagado)
```

| Componente | Tecnología | Carpeta |
|---|---|---|
| App móvil | Flutter / Dart | `Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/app_movil` |
| Backend | Python 3.12 (imagen Docker), FastAPI, SQLAlchemy 2, Pydantic 2, JWT (HS256) | `.../Aplicacion/backend/app` |
| Base de datos | PostgreSQL 16 (Docker `postgres:16-alpine`) y Alembic (15 migraciones) | `.../backend/alembic`, modelo en `.../Base de datos/modelo_datos.md` |
| Pulsera | Servidor Traccar (opcional) y simulador `scripts/simular_pulsera.py` | `.../backend/traccar`, `.../backend/scripts` |
| Contenedores | Docker Compose (`db` y `api`; Traccar en un archivo aparte) | `.../backend/docker-compose.yml` |

Cifras verificadas desde el código el 22-nov-2026: **17 tablas**, **43 rutas** (65 operaciones HTTP), **216 pruebas automáticas** recolectadas por pytest (**226** con el parche de seguridad, que agrega 10). La corrida con Docker del 23-nov confirmó 43 rutas, 65 operaciones y la cabeza de migraciones `a5b6c7d8e9f0`.

## 3. Requisitos

- **Para el backend con Docker:** Docker Desktop (Windows o macOS) o Docker Engine con el plugin Compose. En Windows, la virtualización debe estar activa en la BIOS (SVM Mode en AMD, VT-x en Intel).
- **Para el backend sin Docker:** Python 3.12 o superior, PostgreSQL 16 y `pip`.
- **Para la app:** Flutter con Dart 3 (`sdk: >=3.0.0 <4.0.0`), Android Studio y un emulador Android (o un celular con depuración USB).

## 4. Puesta en marcha del backend con Docker Compose

Desde la carpeta `backend`:

1. `cp .env.example .env` y editarlo: **cambiar `SECRET_KEY` por una clave larga y aleatoria** (por ejemplo `openssl rand -hex 32`). El `.env` no se sube a GitHub (está en `.gitignore`). *Con el parche de seguridad la API no arranca si la clave es la de ejemplo o tiene menos de 32 caracteres.*
2. `docker compose up --build -d` — construye la imagen, levanta `db` y `api`, aplica las migraciones (`alembic upgrade head`) y arranca la API en el puerto 8000.
3. Comprobar: `docker compose ps` (db *healthy*, api *Up*), `curl http://localhost:8000/health` y abrir `http://localhost:8000/docs` (Swagger).
4. Apagar: `docker compose down` (agregar `-v` solo si se quiere **borrar los datos**).

Servicios y puertos: API 8000; PostgreSQL 5432 (usuario `postgres`, base `perfil_medico`; credenciales de desarrollo, no usar en producción). Sin el parche, el puerto 5432 queda publicado en todas las interfaces (visto en la corrida del 23-nov); con el parche solo escucha en `127.0.0.1` y la clave sale de `POSTGRES_PASSWORD`. Con Docker Compose la tarea programada de avisos viene activada (`TAREAS_PROGRAMADAS=true`).

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
| `SECRET_KEY` | Clave de firma de los JWT. **Obligatorio cambiarla**; con el parche, mínimo 32 caracteres | texto de ejemplo |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token | 1440 |
| `TAREAS_PROGRAMADAS`, `TAREAS_INTERVALO_SEGUNDOS`, `ZONA_HORARIA`, `GENERAR_DIAS_ADELANTE` | Tarea que genera actividades y avisos | false / 60 / America/Santiago / 2 |
| `RECORDATORIO_MINUTOS_ANTES`, `ALERTA_PLAZO_1_MINUTOS`, `ALERTA_PLAZO_2_MINUTOS` | Plazos del recordatorio y de las alertas de nivel 1 y 2 | 10 / 30 / 60 |
| `NOTIFICADOR` (`log` o `fcm`), `FCM_CREDENCIALES`, `FCM_PROYECTO_ID` | Entrega de avisos. `fcm` requiere Firebase y `google-auth`; no verificado | `log` |
| `TRACCAR_TOKEN` | Clave compartida con Traccar; vacía = integración desactivada (503) | vacía |
| `BATERIA_BAJA_PORCENTAJE`, `INACTIVIDAD_MINUTOS` / `_RADIO_METROS` / `_DESDE_HORA` / `_HASTA_HORA` | Reglas de eventos de la pulsera | 15 / 180 / 30 / 8 / 22 |
| `IA_PROVEEDOR` (`simulado` o `anthropic`), `IA_API_KEY`, `IA_MODELO`, `IA_MAX_CONSULTAS_DIA` | Asistente de IA. El modelo decidido por el equipo es **Claude Haiku 5.5, de Anthropic** (`anthropic`); la clave va solo en el `.env` local | `simulado` / vacía / `claude-haiku-5-5` / 30 |
| `CORS_ORIGENES` *(con el parche)* | Orígenes web autorizados a llamar a la API desde un navegador; vacío = cerrado. La app móvil no lo necesita | vacío |
| `LOGIN_MAX_INTENTOS`, `LOGIN_MAX_INTENTOS_IP`, `LOGIN_VENTANA_MINUTOS` *(con el parche)* | Límite de intentos fallidos de inicio de sesión (por cuenta e IP, y por IP) | 5 / 20 / 15 |
| `NOTIFICADOR_LOG_CONTENIDO` *(con el parche)* | Si es `true`, el modo `log` escribe el texto de los avisos; por defecto solo el tipo y el nivel | `false` |
| `POSTGRES_PASSWORD` *(con el parche)* | Clave de PostgreSQL del compose. Cambiarla no afecta a un volumen ya creado (ver `.env.example`) | `postgres` |

Los valores por defecto de la tabla salen del `.env.example` y del código; ante una duda, manda el archivo.

## 7. Base de datos y migraciones

- Modelo entidad-relación de 17 tablas en `Base de datos/modelo_datos.md`.
- `alembic upgrade head` crea todo desde una base vacía; `alembic current` debe mostrar la cabeza `a5b6c7d8e9f0`; `alembic check` no debe detectar diferencias.
- Regla del equipo: **una sola persona crea migraciones** para mantener una única cabeza.

## 8. Pruebas

- Backend: `pytest app/tests -q` (en Docker: `docker compose exec api python -m pytest -q`). Las pruebas usan SQLite en memoria; no necesitan PostgreSQL. Esperado: 216 pruebas (226 con el parche de seguridad). La corrida con Docker del 23-nov dio 215 de 216 por un test que suponía el token de Traccar vacío; el arreglo es `fix_D4_test_traccar.patch`.
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

## 11. Seguridad y datos personales

Los datos del sistema son datos de salud, que la ley chilena trata como sensibles. **Ningún sistema puede garantizar que sus datos no serán robados**; este apartado dice qué se hace, qué se probó y qué queda declarado. La evaluación completa está en `Seguridad_de_datos_evaluacion_y_plan.md`.

**Controles que existen (verificados en el código):**
- Contraseñas con bcrypt (mínimo 8 caracteres); sesión con JWT firmado (HS256) que vence a las 24 horas; en el celular el token vive en `flutter_secure_storage`.
- Cada ruta valida el permiso del vínculo con el perfil: una cuenta ajena recibe 404 y sin permiso, 403.
- La IA recibe un contexto mínimo: sin RUT, correo, teléfonos, ubicación ni pulsera; una pregunta de urgencia recibe una respuesta fija con el 131 (SAMU) y el *4141 sin llamar al modelo; límite de 30 consultas por usuario al día.
- La pulsera solo entra con la clave compartida `TRACCAR_TOKEN`; si está vacía, la ruta responde 503.
- Nunca se suben al repositorio el `.env`, claves de IA, credenciales de Firebase ni el token real de Traccar. Los datos de prueba son ficticios.

**Controles que agrega el parche de seguridad (226 pruebas pasan):** la API no arranca con una `SECRET_KEY` de ejemplo o menor a 32 caracteres; límite de intentos de inicio de sesión (429 con `Retry-After`); CORS cerrado por defecto; PostgreSQL solo en `127.0.0.1`; el registro de avisos no escribe el texto; y PyJWT sube de 2.7.0 a 2.15.1 (la versión anterior tenía 17 vulnerabilidades conocidas según `pip-audit`).

**Límites declarados (trabajo futuro):** HTTPS en producción (la demo es local con `http`), cifrado de datos en reposo, auditoría de accesos, revocación de tokens al cerrar sesión, respaldos, RUT en texto plano (campo opcional) y el token de la pulsera en la URL (Traccar lo envía así; el encabezado `X-Traccar-Token` ya está soportado). El límite de intentos vive en la memoria de un proceso.

**Ley de datos personales:** la Ley 21.719 (que reforma la 19.628) regula los datos de salud como sensibles. Su entrada en vigencia, antes el 1-dic-2026, se postergó al **15-oct-2027** con la Ley 21.855, publicada en el Diario Oficial el 23-nov-2026. El proyecto aplica desde ahora la minimización de datos en la IA y los permisos por perfil, y declara como pendientes el aviso de privacidad dentro de la app, el consentimiento guardado en el servidor y las funciones de descarga y eliminación de la cuenta. *Esto no es asesoría legal.*

## 12. Límites conocidos

Sin push real (FCM) en la app; pulsera y Traccar solo con simulador; IA en modo simulado en la demo (el modelo previsto es Claude Haiku 5.5, de Anthropic, y su prueba con datos ficticios se documenta aparte); frecuencia cardíaca y presión por Health Connect (HU 18) sin iniciar; la prueba de Docker Compose se hizo el 23-nov y falta repetir D4 con el parche y capturar el panel de Traccar (D6); no se desarrollaron recordatorios extendidos ni farmacias vía IA; los límites de seguridad están en la sección 11.

## 13. Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Docker no inicia | Virtualización apagada | Activar SVM Mode o VT-x en la BIOS |
| `api` se reinicia | Falta `.env` o `DATABASE_URL` mal escrito | `docker compose logs api` |
| Traccar responde 503 en la API | `TRACCAR_TOKEN` vacío | Definirlo en `.env` y reiniciar `api` |
| La app no conecta | `baseUrl` incorrecto | `10.0.2.2` solo sirve con el emulador de Android |
| Prueba de humo falla por usuarios existentes | Base con datos previos | `docker compose down -v` y repetir (borra los datos) |
| Las alertas tardan en aparecer | La tarea corre cada 60 s | Esperar un minuto o bajar los plazos en `.env` |
| La API se cae al iniciar con «SECRET_KEY insegura» *(con el parche)* | Falta `SECRET_KEY` o es la de ejemplo | Poner una clave de 32 caracteres o más en `.env` (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| El inicio de sesión responde 429 *(con el parche)* | Demasiados intentos fallidos en 15 minutos | Esperar el `Retry-After` o reiniciar la API |
| Un test de Traccar falla en Docker (`..._apagado_sin_token_configurado`) | El `.env` trae `TRACCAR_TOKEN` | Aplicar `fix_D4_test_traccar.patch` |
| Cambié `POSTGRES_PASSWORD` y la API no conecta | El volumen ya existe con la clave anterior | Dejar la clave anterior o recrear el volumen con `docker compose down -v` (borra los datos) |
