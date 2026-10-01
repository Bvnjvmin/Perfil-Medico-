"""Crear tablas medicamento y rutina_cuidado (HU 4 - Sprint 2)

Revision ID: a1b2c3d4e5f6
Revises: 39dd888f4030
Create Date: 2026-09-30 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '39dd888f4030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'medicamento',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('nombre', sa.String(length=120), nullable=False),
        sa.Column('dosis', sa.String(length=50), nullable=False),
        sa.Column('frecuencia', sa.String(length=50), nullable=False),
        sa.Column('hora_inicio', sa.Time(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'rutina_cuidado',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.String(length=200), nullable=True),
        sa.Column('frecuencia', sa.String(length=50), nullable=False),
        sa.Column('hora', sa.Time(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('rutina_cuidado')
    op.drop_table('medicamento')
