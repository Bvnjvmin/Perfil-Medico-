import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class Perfil(Base):
    __tablename__ = "perfil"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuenta_titular_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String(50), nullable=False)
    nombre = Column(String(120), nullable=False)
    rut = Column(String(12), nullable=True)
    grupo_sanguineo = Column(String(15), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    subtipo = Column(String(50), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Alergia(Base):
    __tablename__ = "alergia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(UUID(as_uuid=True), ForeignKey("perfil.id"), nullable=False)
    sustancia = Column(String(120), nullable=False)
    severidad = Column(String(50), nullable=False)

class ContactoEmergencia(Base):
    __tablename__ = "contacto_emergencia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(UUID(as_uuid=True), ForeignKey("perfil.id"), nullable=False)
    nombre = Column(String(150), nullable=False)
    telefono = Column(String(20), nullable=False)
    relacion = Column(String(50), nullable=True)
    prioridad = Column(Integer, default=1)