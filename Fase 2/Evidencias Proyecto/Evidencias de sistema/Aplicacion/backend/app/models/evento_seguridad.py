"""
Modelo de datos de HU 14 y HU 19: eventos de seguridad de un perfil.

Un evento es algo que un cuidador debe atender y que no depende de una actividad
de la agenda: el botón «Necesito ayuda» de la app, o lo que detecta la pulsera
(botón SOS, caída, batería baja, inactividad inusual, salida de una geocerca).

Es una fila por evento, no por destinatario: lo ven el titular y los cuidadores
con `recibe_alertas` (la lista se calcula al consultar). Cuando alguien lo
atiende queda `atendido_en` y quién fue. Los mensajes no afirman que haya una
emergencia: informan lo que se detectó.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

TIPOS_EVENTO = ("asistencia", "sos", "caida", "bateria_baja", "inactividad", "geocerca_salida")


class EventoSeguridad(Base):
    __tablename__ = "evento_seguridad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    pulsera_id = Column(
        UUID(as_uuid=True), ForeignKey("pulsera.id", ondelete="SET NULL"), nullable=True
    )
    tipo = Column(String(20), nullable=False)
    origen = Column(String(10), nullable=False)   # 'app' | 'pulsera' | 'sistema'
    mensaje = Column(Text, nullable=False)
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    atendido_en = Column(DateTime(timezone=True), nullable=True)
    atendido_por_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    # Quién lo disparó cuando viene de la app (el botón lo presiona una persona con sesión).
    creado_por_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('asistencia', 'sos', 'caida', 'bateria_baja', 'inactividad', 'geocerca_salida')",
            name="ck_evento_tipo_valido",
        ),
        CheckConstraint("origen IN ('app', 'pulsera', 'sistema')", name="ck_evento_origen_valido"),
        Index("ix_evento_perfil_creado", "perfil_id", "creado_en"),
    )
