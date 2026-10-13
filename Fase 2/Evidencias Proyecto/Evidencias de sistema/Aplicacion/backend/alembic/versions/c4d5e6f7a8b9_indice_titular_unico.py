"""Un solo perfil titular por cuenta (HU 6 - Sprint 3)

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-10-13 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'uq_perfil_un_titular_por_cuenta',
        'perfil',
        ['cuenta_titular_id'],
        unique=True,
        postgresql_where=sa.text("tipo = 'titular'"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_perfil_un_titular_por_cuenta', table_name='perfil')
