"""
Endpoints de HU 5 (cierre): agenda diaria con confirmación guardada en el backend.

GET  /perfiles/{perfil_id}/actividades?fecha=AAAA-MM-DD  -> actividades del día (se generan si faltan)
POST /actividades/{actividad_id}/confirmar               -> marca la actividad como confirmada
POST /actividades/{actividad_id}/desconfirmar            -> la devuelve a pendiente

La `fecha` es obligatoria y la envía la app (la fecha del celular), porque el
servidor puede estar en otra zona horaria que Chile.

Ver las actividades puede hacerlo cualquiera con acceso al perfil; confirmar o
desconfirmar requiere ser titular o cuidador con `puede_confirmar` (si no, 403).
"""
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_CONFIRMAR, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.actividad import Actividad
from app.models.usuario import Usuario
from app.schemas.actividad import ActividadOut
from app.services.actividades import actividad_out_desde_bd, asegurar_actividades

router = APIRouter(tags=["Agenda diaria"])


def _obtener_actividad(actividad_id: UUID, db: Session, current_user: Usuario) -> Actividad:
    actividad = db.get(Actividad, actividad_id)
    if actividad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    # 404 si no tiene acceso al perfil; 403 si tiene acceso pero no puede confirmar.
    obtener_perfil_con_permiso(actividad.perfil_id, db, current_user, PERMISO_CONFIRMAR)
    return actividad


def _respuesta(db: Session, actividad: Actividad) -> ActividadOut:
    salida = actividad_out_desde_bd(db, actividad)
    if salida is None:  # su medicamento o rutina está inactivo o ya no existe
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    return salida


@router.get("/perfiles/{perfil_id}/actividades", response_model=list[ActividadOut])
def listar_actividades(
    perfil_id: UUID,
    fecha: date = Query(description="Día a consultar, formato AAAA-MM-DD (la fecha del celular)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actividades del día de un perfil propio o compartido, ordenadas por hora."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return asegurar_actividades(db, perfil, fecha)


@router.post("/actividades/{actividad_id}/confirmar", response_model=ActividadOut)
def confirmar_actividad(
    actividad_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Confirma una actividad. Si ya estaba confirmada, devuelve la misma sin error."""
    actividad = _obtener_actividad(actividad_id, db, current_user)
    if actividad.estado != "confirmada":
        actividad.estado = "confirmada"
        actividad.confirmada_en = datetime.now(timezone.utc)
        actividad.confirmada_por_id = current_user.id
        db.commit()
        db.refresh(actividad)
    return _respuesta(db, actividad)


@router.post("/actividades/{actividad_id}/desconfirmar", response_model=ActividadOut)
def desconfirmar_actividad(
    actividad_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve una actividad a pendiente y limpia quién y cuándo la confirmó."""
    actividad = _obtener_actividad(actividad_id, db, current_user)
    if actividad.estado != "pendiente":
        actividad.estado = "pendiente"
        actividad.confirmada_en = None
        actividad.confirmada_por_id = None
        db.commit()
        db.refresh(actividad)
    return _respuesta(db, actividad)
