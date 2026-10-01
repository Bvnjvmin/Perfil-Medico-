"""
Modelos de datos de HU 4: medicamentos y rutinas de cuidado del propio
perfil (alimentación, hidratación, vitaminas, etc.).

Ambas tablas cuelgan de `perfil` (no de `usuarios` directamente), igual que
`alergia` y `contacto_emergencia`: así, desde el Sprint 3, un titular podrá
registrar medicamentos y rutinas también para un perfil dependiente a su
cargo, sin cambiar este esquema.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Medicamento(Base):
    __tablename__ = "medicamento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(UUID(as_uuid=True), ForeignKey("perfil.id"), nullable=False)
    nombre = Column(String(120), nullable=False)
    dosis = Column(String(50), nullable=False)
    frecuencia = Column(String(50), nullable=False)
    hora_inicio = Column(Time, nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RutinaCuidado(Base):
    """
    Rutina de cuidado recurrente que no es un medicamento: alimentación,
    hidratación, vitaminas u otra actividad que el titular quiera agendar
    y confirmar (ver también HU 5, agenda diaria, a cargo de la app).
    """
    __tablename__ = "rutina_cuidado"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(UUID(as_uuid=True), ForeignKey("perfil.id"), nullable=False)
    tipo = Column(String(50), nullable=False)  # ej: 'alimentacion', 'hidratacion', 'vitaminas'
    descripcion = Column(String(200), nullable=True)
    frecuencia = Column(String(50), nullable=False)
    hora = Column(Time, nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
