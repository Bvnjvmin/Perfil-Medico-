"""
Modelo de datos de HU 15: consultas al asistente de IA (orientación general).

Se guarda cada pregunta con su respuesta, quién la hizo y qué proveedor la
contestó. `contexto_resumen` registra QUÉ datos del perfil se enviaron al
modelo (por ejemplo «alergias, medicamentos activos, cumplimiento 7 días»),
no los datos en sí, para poder auditar la privacidad. Si se borra el perfil o
la cuenta, sus consultas se borran con ellos.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class ConsultaIA(Base):
    __tablename__ = "consulta_ia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    usuario_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    proveedor = Column(String(20), nullable=False)       # 'simulado' | 'anthropic' | 'reglas'
    modelo = Column(String(60), nullable=True)
    contexto_resumen = Column(Text, nullable=True)
    creada_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_consulta_ia_perfil_creada", "perfil_id", "creada_en"),
        Index("ix_consulta_ia_usuario_creada", "usuario_id", "creada_en"),
    )
