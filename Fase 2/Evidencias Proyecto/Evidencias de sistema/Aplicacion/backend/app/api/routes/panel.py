"""
Endpoint de HU 8 (versión inicial): panel de estado diario.

GET /panel?fecha=AAAA-MM-DD -> por cada perfil al que el usuario tiene acceso
(propios y compartidos): cuántas actividades tiene el día, cuántas están
confirmadas y cuántas pendientes.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, perfiles_accesibles
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.perfil import AccesoOut
from app.services.actividades import asegurar_actividades

router = APIRouter(tags=["Panel"])


class PanelPerfil(BaseModel):
    id: str
    nombre: str
    tipo: str
    subtipo: Optional[str] = None


class PanelItem(BaseModel):
    perfil: PanelPerfil
    mi_acceso: AccesoOut
    total: int
    confirmadas: int
    pendientes: int


@router.get("/panel", response_model=list[PanelItem])
def panel_del_dia(
    fecha: date = Query(description="Día a consultar, formato AAAA-MM-DD (la fecha del celular)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Avance del día de cada perfil propio o compartido (solo perfiles activos)."""
    items = []
    for perfil, acceso in perfiles_accesibles(db, current_user):
        if perfil.activo is False:
            continue
        actividades = asegurar_actividades(db, perfil, fecha)
        confirmadas = sum(1 for a in actividades if a.estado == "confirmada")
        items.append(
            PanelItem(
                perfil=PanelPerfil(
                    id=str(perfil.id), nombre=perfil.nombre, tipo=perfil.tipo, subtipo=perfil.subtipo
                ),
                mi_acceso=AccesoOut(
                    rol=acceso.rol,
                    puede_confirmar=acceso.puede_confirmar,
                    puede_editar_rutinas=acceso.puede_editar_rutinas,
                ),
                total=len(actividades),
                confirmadas=confirmadas,
                pendientes=len(actividades) - confirmadas,
            )
        )
    return items
