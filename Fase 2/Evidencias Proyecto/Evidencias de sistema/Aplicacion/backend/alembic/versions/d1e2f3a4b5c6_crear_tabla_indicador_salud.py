"""Crear tabla indicador_salud (Sprint 5, HU 12 y HU 18)

Mediciones de peso, presión, glucosa y frecuencia cardíaca de un perfil, a mano
o desde la pulsera. La presión exige dos valores; los demás tipos, uno.

Revision ID: d1e2f3a4b5c6
Revises: c0d1e2f3a4b5
Create Date: 2026-11-05 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c0d1e2f3a4b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'indicador_salud',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('valor', sa.Numeric(7, 2), nullable=False),
        sa.Column('valor_secundario', sa.Numeric(7, 2), nullable=True),
        sa.Column('unidad', sa.String(length=10), nullable=False),
        sa.Column('fuente', sa.String(length=10), nullable=False),
        sa.Column('medido_en', sa.DateTime(timezone=True), nullable=False),
        sa.Column('nota', sa.Text(), nullable=True),
        sa.Column('registrado_por_id', sa.String(length=36), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "tipo IN ('peso', 'presion', 'glucosa', 'frecuencia_cardiaca')",
            name='ck_indicador_tipo_valido',
        ),
        sa.CheckConstraint("fuente IN ('manual', 'pulsera')", name='ck_indicador_fuente_valida'),
        sa.CheckConstraint('valor > 0', name='ck_indicador_valor_positivo'),
        sa.CheckConstraint(
            "(tipo = 'presion' AND valor_secundario IS NOT NULL) OR "
            "(tipo <> 'presion' AND valor_secundario IS NULL)",
            name='ck_indicador_presion_dos_valores',
        ),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['registrado_por_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_indicador_perfil_tipo_medido', 'indicador_salud', ['perfil_id', 'tipo', 'medido_en']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_indicador_perfil_tipo_medido', table_name='indicador_salud')
    op.drop_table('indicador_salud')
