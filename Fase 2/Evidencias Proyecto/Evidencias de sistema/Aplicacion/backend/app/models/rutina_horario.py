"""
Modelo de datos del Sprint 4: horarios de un medicamento o una rutina.

Un medicamento o una rutina puede tomarse varias veces al día ("tres veces al
día" = tres horas). Cada fila es una hora del día y apunta a su origen con dos
llaves opcionales (medicamento_id o rutina_id): exactamente una de las dos debe
tener valor, igual que en `actividad`. Si se borra el medicamento o la rutina,
sus horarios se borran con ellos.

Si un origen no tiene horarios, la agenda sigue usando su hora única
(`hora_inicio` en medicamento, `hora` en rutina), como en el Sprint 3.
"""
import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class RutinaHorario(Base):
    __tablename__ = "rutina_horario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medicamento_id = Column(
        UUID(as_uuid=True), ForeignKey("medicamento.id", ondelete="CASCADE"), nullable=True
    )
    rutina_id = Column(
        UUID(as_uuid=True), ForeignKey("rutina_cuidado.id", ondelete="CASCADE"), nullable=True
    )
    hora = Column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(medicamento_id IS NOT NULL AND rutina_id IS NULL) OR "
            "(medicamento_id IS NULL AND rutina_id IS NOT NULL)",
            name="ck_rutina_horario_un_solo_origen",
        ),
        UniqueConstraint("medicamento_id", "hora", name="uq_rutina_horario_medicamento_hora"),
        UniqueConstraint("rutina_id", "hora", name="uq_rutina_horario_rutina_hora"),
    )
