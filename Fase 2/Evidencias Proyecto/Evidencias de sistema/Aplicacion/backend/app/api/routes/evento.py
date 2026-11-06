"""
Endpoints de HU 14 y HU 19: botón «Necesito ayuda» y eventos de seguridad.

POST /perfiles/{id}/asistencia      -> el botón «Necesito ayuda» (201; 200 si ya se había pedido hace menos de 1 minuto)
GET  /eventos                       -> eventos de los perfiles que el usuario debe atender, los más nuevos primero
POST /eventos/{evento_id}/atendido  -> marca el evento como atendido

Un evento lo ven el titular de la cuenta y los cuidadores con `recibe_alertas`. El botón lo puede
presionar quien puede confirmar actividades en el perfil (el titular, que usa el modo simplificado
del dependiente, o un cuidador con ese permiso). Los avisos al celular salen por el notificador.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_CONFIRMAR, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.evento_seguridad import EventoSeguridad
from app.models.perfil import Perfil
from app.models.perfil_acceso import PerfilAcceso
from app.models.usuario import Usuario
from app.schemas.sprint5 import AsistenciaCreate, EventoOut
from app.services.eventos import crear_evento

router = APIRouter(tags=["Botón de asistencia y eventos de seguridad"])


def _evento_out(evento: EventoSeguridad, perfil: Perfil) -> EventoOut:
    return EventoOut(
        id=evento.id, perfil_id=evento.perfil_id, perfil_nombre=perfil.nombre, tipo=evento.tipo,
        origen=evento.origen, mensaje=evento.mensaje, creado_en=evento.creado_en,
        atendido_en=evento.atendido_en, atendido_por_id=evento.atendido_por_id,
    )


def _perfiles_a_atender(db: Session, usuario: Usuario) -> dict:
    """Perfiles cuyos eventos debe ver el usuario: los propios y aquellos donde recibe alertas."""
    propios = db.query(Perfil).filter(Perfil.cuenta_titular_id == usuario.id).all()
    vinculados = (
        db.query(Perfil)
        .join(PerfilAcceso, PerfilAcceso.perfil_id == Perfil.id)
        .filter(PerfilAcceso.usuario_id == usuario.id, PerfilAcceso.recibe_alertas.is_(True))
        .all()
    )
    return {p.id: p for p in propios + vinculados}


@router.post("/perfiles/{perfil_id}/asistencia", response_model=EventoOut, status_code=status.HTTP_201_CREATED)
def pedir_ayuda(
    perfil_id: UUID,
    response: Response,
    datos: Optional[AsistenciaCreate] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Botón «Necesito ayuda»: avisa al titular y a los cuidadores con alertas."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_CONFIRMAR)
    mensaje = f"{perfil.nombre} pidió ayuda con el botón «Necesito ayuda»."
    if datos and datos.mensaje and datos.mensaje.strip():
        mensaje += f" Mensaje: {datos.mensaje.strip()}"
    evento, creado = crear_evento(
        db, perfil, "asistencia", "app", mensaje, creado_por_id=current_user.id, ventana_minutos=1
    )
    if not creado:
        response.status_code = status.HTTP_200_OK
    return _evento_out(evento, perfil)


@router.get("/eventos", response_model=list[EventoOut])
def listar_eventos(
    solo_pendientes: bool = Query(default=False),
    limite: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfiles = _perfiles_a_atender(db, current_user)
    if not perfiles:
        return []
    consulta = db.query(EventoSeguridad).filter(EventoSeguridad.perfil_id.in_(list(perfiles)))
    if solo_pendientes:
        consulta = consulta.filter(EventoSeguridad.atendido_en.is_(None))
    eventos = consulta.order_by(EventoSeguridad.creado_en.desc()).limit(limite).all()
    return [_evento_out(e, perfiles[e.perfil_id]) for e in eventos]


@router.post("/eventos/{evento_id}/atendido", response_model=EventoOut)
def marcar_atendido(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    evento = db.get(EventoSeguridad, evento_id)
    perfiles = _perfiles_a_atender(db, current_user)
    if evento is None or evento.perfil_id not in perfiles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    if evento.atendido_en is None:
        evento.atendido_en = datetime.now(timezone.utc)
        evento.atendido_por_id = current_user.id
        db.commit()
        db.refresh(evento)
    return _evento_out(evento, perfiles[evento.perfil_id])
