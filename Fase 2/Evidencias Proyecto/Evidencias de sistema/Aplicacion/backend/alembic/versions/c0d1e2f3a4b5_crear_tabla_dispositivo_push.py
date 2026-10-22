"""Crear tabla dispositivo_push (Sprint 4, HU 9)

Dispositivos (tokens del servicio de notificaciones) registrados por cada
usuario. El token es único. Borrado en cascada desde el usuario.

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-10-22 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c0d1e2f3a4b5'
down_revision: Union[str, Sequence[str], None] = 'b9c0d1e2f3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'dispositivo_push',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.String(length=36), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('plataforma', sa.String(length=20), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_dispositivo_push_token'),
    )
    op.create_index('ix_dispositivo_push_usuario', 'dispositivo_push', ['usuario_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_dispositivo_push_usuario', table_name='dispositivo_push')
    op.drop_table('dispositivo_push')
