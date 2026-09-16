"""
Punto de entrada de la API de Perfil Médico+.

Para correrla en desarrollo (fuera de Docker):
    uvicorn app.main:app --reload

Documentación interactiva una vez corriendo:
    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

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


@app.get("/health", tags=["Estado"])
def health_check():
    """Endpoint simple para confirmar que la API está viva (útil para Docker)."""
    return {"status": "ok", "service": settings.PROJECT_NAME}
