"""
Modelo de datos de HU 7: vínculo de una persona (cuidador o lectura) con un
perfil, junto con sus permisos sobre él.

El titular NO tiene una fila aquí: su acceso sale de `perfil.cuenta_titular_id`.
Si se borra el usuario o el perfil, sus vínculos se borran con ellos.
"""
import uuid

from sqlalchemy import (
    Boolean, CheckConstraint, Column, ForeignKey, Integer, String,
    UniqueConstraint, false, true,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class PerfilAcceso(Base):
    __tablename__ = "perfil_acceso"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        String(36), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    perfil_id = Column(
        UUID(as_uuid=True), ForeignKey("perfil.id", ondelete="CASCADE"), nullable=False
    )
    rol_vinculo = Column(String(20), nullable=False)  # 'cuidador' | 'lectura'
    puede_confirmar = Column(Boolean, nullable=False, default=True, server_default=true())
    puede_editar_rutinas = Column(Boolean, nullable=False, default=False, server_default=false())
    # Los indicadores llegan en el Sprint 5.
    puede_ver_indicadores = Column(Boolean, nullable=False, default=False, server_default=false())
    # Alertas y escalamiento se usan desde el Sprint 4; se incluyen ahora para
    # no necesitar otra migración después.
    recibe_alertas = Column(Boolean, nullable=False, default=True, server_default=true())
    nivel_escalamiento = Column(Integer, nullable=False, default=1, server_default="1")

    __table_args__ = (
        CheckConstraint(
            "rol_vinculo IN ('cuidador', 'lectura')",
            name="ck_perfil_acceso_rol_valido",
        ),
        UniqueConstraint("usuario_id", "perfil_id", name="uq_perfil_acceso_usuario_perfil"),
    )
