"""
Modelo de datos de HU 9: dispositivos que pueden recibir notificaciones.

La app registra aquí el identificador (token) que entrega el servicio de
notificaciones push del celular. Un token es único: si otra cuenta inicia
sesión en el mismo celular, el token pasa a ella. Si se borra el usuario, sus
dispositivos se borran con él.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class DispositivoPush(Base):
    __tablename__ = "dispositivo_push"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    token = Column(Text, nullable=False, unique=True)
    plataforma = Column(String(20), nullable=False, default="android")
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("ix_dispositivo_push_usuario", "usuario_id"),)
