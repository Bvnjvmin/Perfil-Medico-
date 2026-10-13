"""Crear tabla perfil_acceso (HU 7 - Sprint 3)

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-10-13 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'perfil_acceso',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.String(length=36), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('rol_vinculo', sa.String(length=20), nullable=False),
        sa.Column('puede_confirmar', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('puede_editar_rutinas', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('puede_ver_indicadores', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('recibe_alertas', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('nivel_escalamiento', sa.Integer(), server_default='1', nullable=False),
        sa.CheckConstraint(
            "rol_vinculo IN ('cuidador', 'lectura')",
            name='ck_perfil_acceso_rol_valido',
        ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'perfil_id', name='uq_perfil_acceso_usuario_perfil'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('perfil_acceso')
