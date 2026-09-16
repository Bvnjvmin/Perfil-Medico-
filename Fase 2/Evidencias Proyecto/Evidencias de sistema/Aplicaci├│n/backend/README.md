# Backend — Perfil Médico+

API construida con **FastAPI + PostgreSQL**, gestionada con **SQLAlchemy** y migraciones con **Alembic**.

## Estado actual (Sprint 1 — Autenticación)

- [x] Estructura base del proyecto
- [x] Conexión a PostgreSQL (vía Docker)
- [x] Modelo `Usuario` (titular / cuidador)
- [x] Registro de usuario (`POST /auth/register`)
- [x] Login con JWT (`POST /auth/login`)
- [x] Endpoint protegido de ejemplo (`GET /auth/me`)
- [x] Migración inicial con Alembic
- [x] Pruebas automatizadas (7/7 pasando)

Lo que sigue en próximos sprints: modelo de `PerfilDependiente`, permisos de cuidadores, rutinas de cuidado, etc. (ver Plan de Trabajo en el 1.5).

## Cómo correrlo con Docker (recomendado)

1. Copiar `.env.example` a `.env` (y opcionalmente generar una `SECRET_KEY` propia).
2. Levantar todo:

   ```bash
   docker compose up --build
   ```

3. La API queda disponible en `http://localhost:8000`, y la documentación interactiva en `http://localhost:8000/docs`.

La primera vez que se levanta, el contenedor `api` aplica automáticamente las migraciones de Alembic antes de arrancar (ver `command` en `docker-compose.yml`).

## Cómo correrlo sin Docker (para desarrollo rápido)

Requiere tener PostgreSQL corriendo localmente (o usar SQLite temporalmente cambiando `DATABASE_URL` en `.env`).

```bash
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head               # crea las tablas
uvicorn app.main:app --reload
```

## Cómo correr las pruebas

Las pruebas usan una base SQLite en memoria — no necesitan Docker ni PostgreSQL corriendo:

```bash
pytest app/tests/ -v
```

## Estructura del proyecto

```
app/
  core/       -> configuración (.env) y seguridad (hash de contraseñas, JWT)
  db/         -> conexión a la base de datos (SQLAlchemy)
  models/     -> tablas de la base de datos (SQLAlchemy)
  schemas/    -> forma del JSON que entra/sale de la API (Pydantic)
  api/
    deps.py       -> dependencias reutilizables (ej. "quién es el usuario actual")
    routes/        -> los endpoints, agrupados por tema
  tests/      -> pruebas automatizadas (pytest)
  main.py     -> arranque de la aplicación FastAPI
alembic/      -> historial de cambios a la base de datos (migraciones)
```

## Cómo agregar un nuevo modelo en el futuro (ej. PerfilDependiente)

1. Crear el modelo en `app/models/` (heredando de `Base`).
2. Crear los esquemas Pydantic en `app/schemas/`.
3. Generar la migración: `alembic revision --autogenerate -m "crear tabla perfiles_dependientes"`.
4. Revisar el archivo generado en `alembic/versions/` antes de aplicarlo.
5. Aplicar: `alembic upgrade head`.
6. Crear las rutas en `app/api/routes/` y registrarlas en `app/main.py`.
