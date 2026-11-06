"""
Endpoint de HU 13: historial de cumplimiento.

GET /perfiles/{id}/cumplimiento?desde=YYYY-MM-DD&hasta=YYYY-MM-DD
    -> porcentaje de actividades confirmadas, por categoría y por día.
       Sin parámetros: los últimos 7 días (hoy incluido). El rango máximo es de 92 días.

Lo puede ver cualquiera con acceso al perfil (es lo mismo que ya ve en la agenda).
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.sprint5 import CumplimientoOut
from app.services.cumplimiento import calcular
from app.services.tiempo import hoy_local

router = APIRouter(tags=["Historial de cumplimiento"])

MAX_DIAS = 92


@router.get("/perfiles/{perfil_id}/cumplimiento", response_model=CumplimientoOut)
def cumplimiento_del_perfil(
    perfil_id: UUID,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    hasta = hasta or hoy_local()
    desde = desde or hasta - timedelta(days=6)
    if desde > hasta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'desde' no puede ser posterior a 'hasta'")
    if (hasta - desde).days + 1 > MAX_DIAS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El rango máximo es de {MAX_DIAS} días")
    return calcular(db, perfil, desde, hasta)
