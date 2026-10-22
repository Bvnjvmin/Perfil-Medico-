"""Crear tabla rutina_horario (Sprint 4)

Horarios de un medicamento o una rutina de cuidado: una fila por hora del día.
Apunta a su origen con dos llaves opcionales (exactamente una con valor), con
borrado en cascada. Es la base de la generación programada de actividades.

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-10-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f7a8b9c0d1e2'
down_revision: Union[str, Sequence[str], None] = 'e6f7a8b9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'rutina_horario',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('medicamento_id', sa.UUID(), nullable=True),
        sa.Column('rutina_id', sa.UUID(), nullable=True),
        sa.Column('hora', sa.Time(), nullable=False),
        sa.CheckConstraint(
            "(medicamento_id IS NOT NULL AND rutina_id IS NULL) OR "
            "(medicamento_id IS NULL AND rutina_id IS NOT NULL)",
            name='ck_rutina_horario_un_solo_origen',
        ),
        sa.ForeignKeyConstraint(['medicamento_id'], ['medicamento.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rutina_id'], ['rutina_cuidado.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('medicamento_id', 'hora', name='uq_rutina_horario_medicamento_hora'),
        sa.UniqueConstraint('rutina_id', 'hora', name='uq_rutina_horario_rutina_hora'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('rutina_horario')
