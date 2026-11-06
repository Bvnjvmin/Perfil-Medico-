"""
Historial de cumplimiento (HU 13): porcentaje de actividades confirmadas.

Cuenta las actividades ya exigibles de un perfil en un rango de fechas:
- confirmada -> cumplida.
- vencida (terminó el día sin confirmarse) -> no cumplida.
- pendiente de un día anterior, o de hoy con la hora ya pasada -> no cumplida (todavía).
- pendiente de hoy sin hora o con la hora por venir, y las 'omitida' -> no se cuentan.

Se agrupan en medicamentos, hidratación, alimentación y otras rutinas. Solo cuenta lo que
ya se generó en la agenda (la tarea programada crea hoy y los 2 días siguientes), así que
un día sin actividades generadas no suma ni resta.
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.actividad import Actividad
from app.models.medicamento import RutinaCuidado
from app.models.perfil import Perfil
from app.services.tiempo import ahora_local, momento

CATEGORIAS = ("medicamentos", "hidratacion", "alimentacion", "otras")


def _porcentaje(total: int, cumplidas: int) -> Optional[float]:
    return round(100 * cumplidas / total, 1) if total else None


def _categoria(actividad: Actividad, tipo_rutina: Optional[str]) -> str:
    if actividad.medicamento_id is not None:
        return "medicamentos"
    return tipo_rutina if tipo_rutina in ("hidratacion", "alimentacion") else "otras"


def _exigible(actividad: Actividad, ahora: datetime) -> bool:
    if actividad.estado in ("confirmada", "vencida"):
        return True
    if actividad.estado != "pendiente":
        return False
    if actividad.fecha < ahora.date():
        return True
    return actividad.fecha == ahora.date() and actividad.hora is not None and ahora >= momento(actividad.fecha, actividad.hora)


def calcular(db: Session, perfil: Perfil, desde: date, hasta: date, ahora: Optional[datetime] = None) -> dict:
    ahora = ahora or ahora_local()
    filas = (
        db.query(Actividad, RutinaCuidado.tipo)
        .outerjoin(RutinaCuidado, RutinaCuidado.id == Actividad.rutina_id)
        .filter(Actividad.perfil_id == perfil.id, Actividad.fecha >= desde, Actividad.fecha <= hasta)
        .all()
    )
    total = cumplidas = 0
    por_categoria = {c: [0, 0] for c in CATEGORIAS}
    por_dia: dict[date, list[int]] = {}
    for actividad, tipo_rutina in filas:
        if not _exigible(actividad, ahora):
            continue
        cumple = int(actividad.estado == "confirmada")
        total += 1
        cumplidas += cumple
        cat = por_categoria[_categoria(actividad, tipo_rutina)]
        cat[0] += 1
        cat[1] += cumple
        dia = por_dia.setdefault(actividad.fecha, [0, 0])
        dia[0] += 1
        dia[1] += cumple
    return {
        "perfil_id": perfil.id, "desde": desde, "hasta": hasta,
        "total": total, "cumplidas": cumplidas, "porcentaje": _porcentaje(total, cumplidas),
        "por_categoria": {
            c: {"total": t, "cumplidas": k, "porcentaje": _porcentaje(t, k)} for c, (t, k) in por_categoria.items()
        },
        "por_dia": [
            {"fecha": f, "total": t, "cumplidas": k, "porcentaje": _porcentaje(t, k)}
            for f, (t, k) in sorted(por_dia.items())
        ],
    }
