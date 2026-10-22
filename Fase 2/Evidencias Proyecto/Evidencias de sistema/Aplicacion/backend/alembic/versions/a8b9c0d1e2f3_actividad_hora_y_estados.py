"""Actividad con hora propia y estados nuevos (Sprint 4)

- Agrega `hora` a `actividad`, para que un medicamento o rutina con varias
  horas por día tenga una actividad por hora. Las filas existentes copian la
  hora de su origen (`hora_inicio` o `hora`).
- Cambia las restricciones únicas de (origen, fecha) a (origen, fecha, hora) y
  agrega índices parciales para las actividades sin hora.
- Amplía los estados permitidos con 'vencida' y 'omitida'.

El downgrade conserva solo la primera actividad de cada origen y día, y
devuelve a 'pendiente' las actividades vencidas u omitidas.

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-10-22 10:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, Sequence[str], None] = 'f7a8b9c0d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('actividad', sa.Column('hora', sa.Time(), nullable=True))
    op.execute(
        "UPDATE actividad SET hora = (SELECT m.hora_inicio FROM medicamento m "
        "WHERE m.id = actividad.medicamento_id) WHERE medicamento_id IS NOT NULL"
    )
    op.execute(
        "UPDATE actividad SET hora = (SELECT r.hora FROM rutina_cuidado r "
        "WHERE r.id = actividad.rutina_id) WHERE rutina_id IS NOT NULL"
    )

    op.drop_constraint('uq_actividad_medicamento_fecha', 'actividad', type_='unique')
    op.drop_constraint('uq_actividad_rutina_fecha', 'actividad', type_='unique')
    op.create_unique_constraint(
        'uq_actividad_medicamento_fecha_hora', 'actividad', ['medicamento_id', 'fecha', 'hora']
    )
    op.create_unique_constraint(
        'uq_actividad_rutina_fecha_hora', 'actividad', ['rutina_id', 'fecha', 'hora']
    )
    op.create_index(
        'uq_actividad_medicamento_fecha_sin_hora', 'actividad', ['medicamento_id', 'fecha'],
        unique=True, postgresql_where=sa.text('hora IS NULL'),
    )
    op.create_index(
        'uq_actividad_rutina_fecha_sin_hora', 'actividad', ['rutina_id', 'fecha'],
        unique=True, postgresql_where=sa.text('hora IS NULL'),
    )

    op.drop_constraint('ck_actividad_estado_valido', 'actividad', type_='check')
    op.create_check_constraint(
        'ck_actividad_estado_valido', 'actividad',
        "estado IN ('pendiente', 'confirmada', 'vencida', 'omitida')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_actividad_estado_valido', 'actividad', type_='check')
    op.execute("UPDATE actividad SET estado = 'pendiente' WHERE estado IN ('vencida', 'omitida')")
    op.create_check_constraint(
        'ck_actividad_estado_valido', 'actividad', "estado IN ('pendiente', 'confirmada')"
    )

    op.drop_index('uq_actividad_rutina_fecha_sin_hora', table_name='actividad')
    op.drop_index('uq_actividad_medicamento_fecha_sin_hora', table_name='actividad')
    op.drop_constraint('uq_actividad_rutina_fecha_hora', 'actividad', type_='unique')
    op.drop_constraint('uq_actividad_medicamento_fecha_hora', 'actividad', type_='unique')

    # Una sola actividad por origen y día: se conserva la de hora más temprana.
    for origen in ('medicamento_id', 'rutina_id'):
        op.execute(
            f"DELETE FROM actividad a USING actividad b WHERE a.{origen} = b.{origen} "
            "AND a.fecha = b.fecha AND a.id <> b.id "
            "AND (COALESCE(a.hora, TIME '23:59:59.999999'), a.id::text) > "
            "(COALESCE(b.hora, TIME '23:59:59.999999'), b.id::text)"
        )
    op.create_unique_constraint(
        'uq_actividad_medicamento_fecha', 'actividad', ['medicamento_id', 'fecha']
    )
    op.create_unique_constraint('uq_actividad_rutina_fecha', 'actividad', ['rutina_id', 'fecha'])
    op.drop_column('actividad', 'hora')
