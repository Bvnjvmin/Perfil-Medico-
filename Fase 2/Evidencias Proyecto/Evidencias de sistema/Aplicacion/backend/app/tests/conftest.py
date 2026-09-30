"""
Configuración compartida de las pruebas (pytest fixtures).

Las pruebas NO se conectan a la PostgreSQL real: usan una base SQLite en
memoria, que se crea limpia para cada prueba y desaparece al terminar. Esto
hace las pruebas rápidas y evita que dependan de tener Docker corriendo.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user  # noqa: F401 (referenciado por claridad)
from app.db.session import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool: SQLite ':memory:' crea una base nueva por cada conexión nueva.
# StaticPool obliga a reutilizar SIEMPRE la misma conexión, para que las
# tablas creadas en el fixture sean las mismas que ve la app al responder
# cada request de la prueba.
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
