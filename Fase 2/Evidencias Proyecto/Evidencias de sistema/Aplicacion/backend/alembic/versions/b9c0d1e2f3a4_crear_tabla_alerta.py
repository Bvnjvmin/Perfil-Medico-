"""Crear tabla alerta (Sprint 4, HU 9 y HU 10)

Recordatorios (nivel 0) y alertas escalonadas (nivel 1, 2, ...) dirigidos a un
usuario por una actividad. La restricción única evita avisar dos veces por lo
mismo. Borrado en cascada desde la actividad y el usuario.

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Create Date: 2026-10-22 10:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b9c0d1e2f3a4'
down_revision: Union[str, Sequence[str], None] = 'a8b9c0d1e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'alerta',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('actividad_id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.String(length=36), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('nivel', sa.Integer(), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('creada_en', sa.DateTime(timezone=True), nullable=False),
        sa.Column('leida_en', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("tipo IN ('recordatorio', 'alerta')", name='ck_alerta_tipo_valido'),
        sa.CheckConstraint('nivel >= 0', name='ck_alerta_nivel_valido'),
        sa.ForeignKeyConstraint(['actividad_id'], ['actividad.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'actividad_id', 'usuario_id', 'tipo', 'nivel', name='uq_alerta_actividad_usuario_nivel'
        ),
    )
    op.create_index('ix_alerta_usuario_creada', 'alerta', ['usuario_id', 'creada_en'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_alerta_usuario_creada', table_name='alerta')
    op.drop_table('alerta')
