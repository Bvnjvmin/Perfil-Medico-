"""
Punto de entrada de la API de Perfil Médico+.

Para correrla en desarrollo (fuera de Docker):
    uvicorn app.main:app --reload

Documentación interactiva una vez corriendo:
    http://localhost:8000/docs
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import actividad, auth, aviso, cuidador, horario, medicamento, panel, perfil
from app.core.config import settings

logger = logging.getLogger("perfil_medico.tareas")


def _ejecutar_ciclo() -> None:
    """Un ciclo de la tarea programada, con su propia sesión de base de datos."""
    from app.db.session import SessionLocal
    from app.services.alertas import ejecutar_ciclo

    db = SessionLocal()
    try:
        resumen = ejecutar_ciclo(db)
        logger.info("Ciclo de tareas programadas: %s", resumen)
    except Exception:  # una falla no debe detener la tarea ni la API
        logger.exception("Falló el ciclo de tareas programadas")
    finally:
        db.close()


async def _bucle_tareas() -> None:
    while True:
        await asyncio.to_thread(_ejecutar_ciclo)
        await asyncio.sleep(settings.TAREAS_INTERVALO_SEGUNDOS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Con TAREAS_PROGRAMADAS=true, corre la generación de actividades y los avisos cada minuto."""
    tarea = asyncio.create_task(_bucle_tareas()) if settings.TAREAS_PROGRAMADAS else None
    yield
    if tarea is not None:
        tarea.cancel()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Permite que la app Flutter (u otra herramienta) llame a la API desde
# cualquier origen. Se puede restringir más adelante a dominios específicos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(perfil.router)
app.include_router(medicamento.router)
app.include_router(horario.router)
app.include_router(actividad.router)
app.include_router(cuidador.router)
app.include_router(panel.router)
app.include_router(aviso.router)


@app.get("/health", tags=["Estado"])
def health_check():
    """Endpoint simple para confirmar que la API está viva (útil para Docker)."""
    return {"status": "ok", "service": settings.PROJECT_NAME}
