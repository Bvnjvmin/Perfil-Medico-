"""
Modelo de datos de HU 17 y HU 19: pulsera inteligente, sus posiciones y las geocercas.

- `pulsera`: el dispositivo de un perfil dependiente. `identificador` es el
  `uniqueId` con que lo registra el servidor Traccar (normalmente el IMEI) y es único.
- `posicion`: cada lectura de GPS que Traccar reenvía a la API. Las más viejas se
  borran en el ciclo programado (`POSICIONES_DIAS_RETENCION`).
- `geocerca`: zona circular (centro y radio) de un perfil, por ejemplo la casa o el colegio.

Todo cuelga del perfil o de la pulsera: al borrar el perfil se borra todo.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Index, Integer,
    String, UniqueConstraint, true,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Pulsera(Base):
    __tablename__ = "pulsera"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    identificador = Column(String(64), nullable=False, unique=True)
    nombre = Column(String(80), nullable=False)
    modelo = Column(String(80), nullable=True)
    activa = Column(Boolean, nullable=False, default=True, server_default=true())
    bateria_pct = Column(Integer, nullable=True)
    ultima_conexion = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint(
            "bateria_pct IS NULL OR (bateria_pct >= 0 AND bateria_pct <= 100)",
            name="ck_pulsera_bateria_valida",
        ),
        Index("ix_pulsera_perfil", "perfil_id"),
    )


class Posicion(Base):
    __tablename__ = "posicion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pulsera_id = Column(
        UUID(as_uuid=True), ForeignKey("pulsera.id", ondelete="CASCADE"), nullable=False
    )
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    precision_m = Column(Float, nullable=True)
    velocidad_kmh = Column(Float, nullable=True)
    bateria_pct = Column(Integer, nullable=True)
    registrada_en = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint("latitud >= -90 AND latitud <= 90", name="ck_posicion_latitud"),
        CheckConstraint("longitud >= -180 AND longitud <= 180", name="ck_posicion_longitud"),
        Index("ix_posicion_pulsera_registrada", "pulsera_id", "registrada_en"),
    )


class Geocerca(Base):
    __tablename__ = "geocerca"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    nombre = Column(String(80), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    radio_m = Column(Integer, nullable=False)
    activa = Column(Boolean, nullable=False, default=True, server_default=true())
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("radio_m >= 20 AND radio_m <= 50000", name="ck_geocerca_radio_valido"),
        CheckConstraint("latitud >= -90 AND latitud <= 90", name="ck_geocerca_latitud"),
        CheckConstraint("longitud >= -180 AND longitud <= 180", name="ck_geocerca_longitud"),
        UniqueConstraint("perfil_id", "nombre", name="uq_geocerca_perfil_nombre"),
    )
