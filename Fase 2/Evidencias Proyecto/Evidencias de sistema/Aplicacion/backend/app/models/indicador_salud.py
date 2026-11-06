"""
Modelo de datos de HU 12 y HU 18: indicadores de salud de un perfil.

Una fila es una medición: peso, presión arterial, glucosa o frecuencia cardíaca.
Se registra a mano (`fuente = 'manual'`) o llega desde la pulsera por Health
Connect (`fuente = 'pulsera'`). La presión usa dos valores (sistólica en `valor`,
diastólica en `valor_secundario`); el resto usa solo `valor`.

Si se borra el perfil, sus mediciones se borran con él. Si se borra la cuenta
que las registró, la medición se conserva (`registrado_por_id` queda en NULL).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Index, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

TIPOS_INDICADOR = ("peso", "presion", "glucosa", "frecuencia_cardiaca")


class IndicadorSalud(Base):
    __tablename__ = "indicador_salud"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    tipo = Column(String(20), nullable=False)
    valor = Column(Numeric(7, 2), nullable=False)
    valor_secundario = Column(Numeric(7, 2), nullable=True)   # diastólica (solo presión)
    unidad = Column(String(10), nullable=False)               # kg, mmHg, mg/dL, lpm
    fuente = Column(String(10), nullable=False, default="manual")
    medido_en = Column(DateTime(timezone=True), nullable=False)
    nota = Column(Text, nullable=True)
    registrado_por_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    creado_en = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('peso', 'presion', 'glucosa', 'frecuencia_cardiaca')",
            name="ck_indicador_tipo_valido",
        ),
        CheckConstraint("fuente IN ('manual', 'pulsera')", name="ck_indicador_fuente_valida"),
        CheckConstraint("valor > 0", name="ck_indicador_valor_positivo"),
        CheckConstraint(
            "(tipo = 'presion' AND valor_secundario IS NOT NULL) OR "
            "(tipo <> 'presion' AND valor_secundario IS NULL)",
            name="ck_indicador_presion_dos_valores",
        ),
        Index("ix_indicador_perfil_tipo_medido", "perfil_id", "tipo", "medido_en"),
    )
