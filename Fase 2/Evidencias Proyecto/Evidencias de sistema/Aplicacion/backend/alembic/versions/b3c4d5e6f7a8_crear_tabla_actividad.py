"""Crear tabla actividad (cierre de HU 5 - Sprint 3)

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-10-13 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'actividad',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('medicamento_id', sa.UUID(), nullable=True),
        sa.Column('rutina_id', sa.UUID(), nullable=True),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('confirmada_en', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmada_por_id', sa.String(length=36), nullable=True),
        sa.CheckConstraint(
            "(medicamento_id IS NOT NULL AND rutina_id IS NULL) OR "
            "(medicamento_id IS NULL AND rutina_id IS NOT NULL)",
            name='ck_actividad_un_solo_origen',
        ),
        sa.CheckConstraint(
            "estado IN ('pendiente', 'confirmada')",
            name='ck_actividad_estado_valido',
        ),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medicamento_id'], ['medicamento.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rutina_id'], ['rutina_cuidado.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['confirmada_por_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('medicamento_id', 'fecha', name='uq_actividad_medicamento_fecha'),
        sa.UniqueConstraint('rutina_id', 'fecha', name='uq_actividad_rutina_fecha'),
    )
    op.create_index('ix_actividad_perfil_fecha', 'actividad', ['perfil_id', 'fecha'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_actividad_perfil_fecha', table_name='actividad')
    op.drop_table('actividad')
