"""
Modelo de datos de HU 5 (cierre): actividades diarias de la agenda.

Una actividad es "tomar este medicamento" o "hacer esta rutina" en un día
concreto, y guarda si ya fue confirmada. Apunta a su origen con dos llaves
opcionales (medicamento_id o rutina_id): exactamente una de las dos debe
tener valor. Así la base de datos garantiza la integridad y, si se borra el
medicamento o la rutina, sus actividades se borran con ellos.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint, Column, Date, DateTime, ForeignKey, Index, String, Time,
    UniqueConstraint, text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Actividad(Base):
    __tablename__ = "actividad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    medicamento_id = Column(
        UUID(as_uuid=True), ForeignKey("medicamento.id", ondelete="CASCADE"), nullable=True
    )
    rutina_id = Column(
        UUID(as_uuid=True), ForeignKey("rutina_cuidado.id", ondelete="CASCADE"), nullable=True
    )
    fecha = Column(Date, nullable=False)
    # Hora de esta toma. Es NULL solo cuando el origen no tiene hora (ni horarios).
    hora = Column(Time, nullable=True)
    # 'pendiente' | 'confirmada' | 'vencida' (pasó el día sin confirmarse) | 'omitida' (reservado)
    estado = Column(String(20), nullable=False, default="pendiente")
    confirmada_en = Column(DateTime(timezone=True), nullable=True)
    confirmada_por_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "(medicamento_id IS NOT NULL AND rutina_id IS NULL) OR "
            "(medicamento_id IS NULL AND rutina_id IS NOT NULL)",
            name="ck_actividad_un_solo_origen",
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'confirmada', 'vencida', 'omitida')",
            name="ck_actividad_estado_valido",
        ),
        # Una actividad por origen, día y hora (un origen puede tener varias horas por día).
        UniqueConstraint("medicamento_id", "fecha", "hora", name="uq_actividad_medicamento_fecha_hora"),
        UniqueConstraint("rutina_id", "fecha", "hora", name="uq_actividad_rutina_fecha_hora"),
        # Con hora NULL la restricción anterior no basta (NULL nunca es igual a NULL):
        # estos índices parciales mantienen una sola actividad sin hora por origen y día.
        Index(
            "uq_actividad_medicamento_fecha_sin_hora", "medicamento_id", "fecha", unique=True,
            postgresql_where=text("hora IS NULL"), sqlite_where=text("hora IS NULL"),
        ),
        Index(
            "uq_actividad_rutina_fecha_sin_hora", "rutina_id", "fecha", unique=True,
            postgresql_where=text("hora IS NULL"), sqlite_where=text("hora IS NULL"),
        ),
        Index("ix_actividad_perfil_fecha", "perfil_id", "fecha"),
    )