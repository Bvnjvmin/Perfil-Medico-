"""Borrado en cascada de las tablas que cuelgan de perfil (HU 6 - Sprint 3)

Vuelve a crear las llaves foráneas de alergia, contacto_emergencia,
medicamento y rutina_cuidado hacia perfil con ON DELETE CASCADE. Es la
segunda protección del borrado de perfiles (la primera es el borrado
explícito en el código).

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-10-13 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, Sequence[str], None] = 'd5e6f7a8b9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# PostgreSQL nombra estas llaves como <tabla>_perfil_id_fkey.
TABLAS = ['alergia', 'contacto_emergencia', 'medicamento', 'rutina_cuidado']


def upgrade() -> None:
    """Upgrade schema."""
    for tabla in TABLAS:
        nombre = f'{tabla}_perfil_id_fkey'
        op.drop_constraint(nombre, tabla, type_='foreignkey')
        op.create_foreign_key(nombre, tabla, 'perfil', ['perfil_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    for tabla in TABLAS:
        nombre = f'{tabla}_perfil_id_fkey'
        op.drop_constraint(nombre, tabla, type_='foreignkey')
        op.create_foreign_key(nombre, tabla, 'perfil', ['perfil_id'], ['id'])
