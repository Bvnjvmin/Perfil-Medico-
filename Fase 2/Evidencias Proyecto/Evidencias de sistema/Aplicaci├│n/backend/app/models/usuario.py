"""
Modelo de datos: Usuario.

Representa a cualquier persona que puede iniciar sesión en Perfil Médico+:
un titular (administra su propio perfil de salud y puede crear perfiles
dependientes) o un cuidador (invitado a un perfil dependiente específico).

Los perfiles dependientes (adultos mayores no valentes, niños) se modelan
en una tabla separada más adelante (Sprint 3) — este archivo cubre solo
lo que necesita la autenticación del Sprint 1.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RolUsuario(str, enum.Enum):
    TITULAR = "titular"
    CUIDADOR = "cuidador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario), default=RolUsuario.TITULAR, nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email} rol={self.rol}>"
