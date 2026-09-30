"""crear tabla usuarios

Revision ID: 22222d1ae8f4
Revises: 
Create Date: 2026-09-16 01:30:21.191394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22222d1ae8f4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    rol_usuario_enum = sa.Enum("titular", "cuidador", name="rolusuario")
    op.create_table(
        "usuarios",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("rol", rol_usuario_enum, nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    sa.Enum(name="rolusuario").drop(op.get_bind(), checkfirst=True)
