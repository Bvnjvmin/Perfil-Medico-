"""Crear tablas pulsera, posicion y geocerca (Sprint 5, HU 17 y HU 19)

La pulsera de un perfil dependiente, las posiciones de GPS que reenvía Traccar y
las zonas circulares (geocercas) del perfil. Borrado en cascada desde el perfil.

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-11-05 20:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'pulsera',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('identificador', sa.String(length=64), nullable=False),
        sa.Column('nombre', sa.String(length=80), nullable=False),
        sa.Column('modelo', sa.String(length=80), nullable=True),
        sa.Column('activa', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('bateria_pct', sa.Integer(), nullable=True),
        sa.Column('ultima_conexion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            'bateria_pct IS NULL OR (bateria_pct >= 0 AND bateria_pct <= 100)',
            name='ck_pulsera_bateria_valida',
        ),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identificador'),
    )
    op.create_index('ix_pulsera_perfil', 'pulsera', ['perfil_id'])

    op.create_table(
        'posicion',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('pulsera_id', sa.UUID(), nullable=False),
        sa.Column('latitud', sa.Float(), nullable=False),
        sa.Column('longitud', sa.Float(), nullable=False),
        sa.Column('precision_m', sa.Float(), nullable=True),
        sa.Column('velocidad_kmh', sa.Float(), nullable=True),
        sa.Column('bateria_pct', sa.Integer(), nullable=True),
        sa.Column('registrada_en', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('latitud >= -90 AND latitud <= 90', name='ck_posicion_latitud'),
        sa.CheckConstraint('longitud >= -180 AND longitud <= 180', name='ck_posicion_longitud'),
        sa.ForeignKeyConstraint(['pulsera_id'], ['pulsera.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_posicion_pulsera_registrada', 'posicion', ['pulsera_id', 'registrada_en'])

    op.create_table(
        'geocerca',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('nombre', sa.String(length=80), nullable=False),
        sa.Column('latitud', sa.Float(), nullable=False),
        sa.Column('longitud', sa.Float(), nullable=False),
        sa.Column('radio_m', sa.Integer(), nullable=False),
        sa.Column('activa', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('radio_m >= 20 AND radio_m <= 50000', name='ck_geocerca_radio_valido'),
        sa.CheckConstraint('latitud >= -90 AND latitud <= 90', name='ck_geocerca_latitud'),
        sa.CheckConstraint('longitud >= -180 AND longitud <= 180', name='ck_geocerca_longitud'),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('perfil_id', 'nombre', name='uq_geocerca_perfil_nombre'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('geocerca')
    op.drop_index('ix_posicion_pulsera_registrada', table_name='posicion')
    op.drop_table('posicion')
    op.drop_index('ix_pulsera_perfil', table_name='pulsera')
    op.drop_table('pulsera')
