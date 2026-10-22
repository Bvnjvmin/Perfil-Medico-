"""
Modelo de datos de HU 9 y HU 10: recordatorios y alertas escalonadas.

Una fila es un aviso dirigido a un usuario por una actividad concreta:
- tipo 'recordatorio' (nivel 0): la actividad se acerca y sigue pendiente (HU 9).
- tipo 'alerta' (nivel 1, 2, ...): la actividad pasó su hora sin confirmarse y el
  aviso escala de nivel (HU 10). El nivel coincide con
  `perfil_acceso.nivel_escalamiento` de los cuidadores que lo reciben.

La restricción única evita avisar dos veces al mismo usuario por lo mismo, así
la tarea programada puede correr cada minuto sin duplicar. Si se borra la
actividad o el usuario, sus avisos se borran con ellos.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Alerta(Base):
    __tablename__ = "alerta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actividad_id = Column(
        UUID(as_uuid=True), ForeignKey("actividad.id", ondelete="CASCADE"), nullable=False
    )
    usuario_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    tipo = Column(String(20), nullable=False)  # 'recordatorio' | 'alerta'
    nivel = Column(Integer, nullable=False)    # 0 recordatorio; 1, 2, ... alertas
    mensaje = Column(Text, nullable=False)
    creada_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    leida_en = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("tipo IN ('recordatorio', 'alerta')", name="ck_alerta_tipo_valido"),
        CheckConstraint("nivel >= 0", name="ck_alerta_nivel_valido"),
        UniqueConstraint("actividad_id", "usuario_id", "tipo", "nivel", name="uq_alerta_actividad_usuario_nivel"),
        Index("ix_alerta_usuario_creada", "usuario_id", "creada_en"),
    )
