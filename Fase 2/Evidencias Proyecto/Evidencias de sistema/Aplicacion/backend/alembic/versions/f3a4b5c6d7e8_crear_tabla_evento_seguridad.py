"""Crear tabla evento_seguridad (Sprint 5, HU 14 y HU 19)

Eventos que un cuidador debe atender y que no dependen de una actividad: el botón
«Necesito ayuda» de la app y lo que detecta la pulsera (SOS, caída, batería baja,
inactividad, salida de una geocerca).

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-11-05 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'evento_seguridad',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('pulsera_id', sa.UUID(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('origen', sa.String(length=10), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atendido_en', sa.DateTime(timezone=True), nullable=True),
        sa.Column('atendido_por_id', sa.String(length=36), nullable=True),
        sa.Column('creado_por_id', sa.String(length=36), nullable=True),
        sa.CheckConstraint(
            "tipo IN ('asistencia', 'sos', 'caida', 'bateria_baja', 'inactividad', 'geocerca_salida')",
            name='ck_evento_tipo_valido',
        ),
        sa.CheckConstraint("origen IN ('app', 'pulsera', 'sistema')", name='ck_evento_origen_valido'),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pulsera_id'], ['pulsera.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['atendido_por_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evento_perfil_creado', 'evento_seguridad', ['perfil_id', 'creado_en'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_evento_perfil_creado', table_name='evento_seguridad')
    op.drop_table('evento_seguridad')
