"""Crear tabla consulta_ia (Sprint 5, HU 15)

Preguntas al asistente de IA con su respuesta, quién preguntó, qué proveedor
contestó y un resumen de los datos del perfil que se enviaron al modelo.

Revision ID: a5b6c7d8e9f0
Revises: f3a4b5c6d7e8
Create Date: 2026-11-05 20:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a5b6c7d8e9f0'
down_revision: Union[str, Sequence[str], None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'consulta_ia',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('perfil_id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.String(length=36), nullable=False),
        sa.Column('pregunta', sa.Text(), nullable=False),
        sa.Column('respuesta', sa.Text(), nullable=False),
        sa.Column('proveedor', sa.String(length=20), nullable=False),
        sa.Column('modelo', sa.String(length=60), nullable=True),
        sa.Column('contexto_resumen', sa.Text(), nullable=True),
        sa.Column('creada_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['perfil_id'], ['perfil.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_consulta_ia_perfil_creada', 'consulta_ia', ['perfil_id', 'creada_en'])
    op.create_index('ix_consulta_ia_usuario_creada', 'consulta_ia', ['usuario_id', 'creada_en'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_consulta_ia_usuario_creada', table_name='consulta_ia')
    op.drop_index('ix_consulta_ia_perfil_creada', table_name='consulta_ia')
    op.drop_table('consulta_ia')
