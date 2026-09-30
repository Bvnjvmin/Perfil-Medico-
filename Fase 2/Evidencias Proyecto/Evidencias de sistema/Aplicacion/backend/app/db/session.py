"""
Configuración de la conexión a la base de datos con SQLAlchemy.

'engine' es la conexión real a PostgreSQL (definida por DATABASE_URL).
'SessionLocal' crea una "sesión" de trabajo por cada request — así cada
petición HTTP tiene su propia conversación con la base de datos, que se
cierra automáticamente al terminar (ver get_db() más abajo).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos (tablas)."""
    pass


def get_db():
    """
    Dependencia de FastAPI: abre una sesión de base de datos para el request
    actual, la entrega al endpoint que la pidió, y la cierra al finalizar
    (incluso si el endpoint lanzó un error).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
