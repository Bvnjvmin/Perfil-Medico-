"""
Endpoints de HU 9 y HU 10: dispositivos para notificaciones, recordatorios y alertas.

POST   /dispositivos            -> registra el dispositivo del usuario (201; 200 si ya estaba)
DELETE /dispositivos/{token}    -> quita el dispositivo (al cerrar sesión)
GET    /alertas                 -> recordatorios y alertas propios, los más nuevos primero
POST   /alertas/{alerta_id}/leida -> marca un aviso como leído

Cada usuario solo ve sus propios avisos, y solo los de perfiles a los que todavía tiene
acceso. Un token que ya pertenece a otra cuenta pasa a quien lo registra (el celular
cambió de cuenta). Los avisos los crea la tarea programada (app/services/alertas.py).
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, perfiles_accesibles
from app.db.session import get_db
from app.models.actividad import Actividad
from app.models.alerta import Alerta
from app.models.dispositivo_push import DispositivoPush
from app.models.usuario import Usuario
from app.schemas.aviso import AlertaOut, DispositivoCreate, DispositivoOut

router = APIRouter(tags=["Recordatorios y alertas"])


@router.post("/dispositivos", response_model=DispositivoOut, status_code=status.HTTP_201_CREATED)
def registrar_dispositivo(
    datos: DispositivoCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra el token del celular para recibir notificaciones."""
    dispositivo = db.query(DispositivoPush).filter_by(token=datos.token).first()
    if dispositivo is not None:
        response.status_code = status.HTTP_200_OK
        dispositivo.usuario_id = current_user.id
        dispositivo.plataforma = datos.plataforma
    else:
        dispositivo = DispositivoPush(usuario_id=current_user.id, token=datos.token, plataforma=datos.plataforma)
        db.add(dispositivo)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo


@router.delete("/dispositivos/{token:path}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_dispositivo(
    token: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    dispositivo = db.query(DispositivoPush).filter_by(token=token, usuario_id=current_user.id).first()
    if dispositivo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    db.delete(dispositivo)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _alerta_out(alerta: Alerta, perfil_id: UUID) -> AlertaOut:
    return AlertaOut(
        id=alerta.id, perfil_id=perfil_id, actividad_id=alerta.actividad_id, tipo=alerta.tipo,
        nivel=alerta.nivel, mensaje=alerta.mensaje, creada_en=alerta.creada_en, leida_en=alerta.leida_en,
    )


@router.get("/alertas", response_model=list[AlertaOut])
def listar_alertas(
    solo_no_leidas: bool = Query(default=False),
    limite: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Avisos del usuario (recordatorios y alertas), los más nuevos primero."""
    ids_perfiles = {p.id for p, _ in perfiles_accesibles(db, current_user)}
    consulta = (
        db.query(Alerta, Actividad.perfil_id)
        .join(Actividad, Actividad.id == Alerta.actividad_id)
        .filter(Alerta.usuario_id == current_user.id, Actividad.perfil_id.in_(ids_perfiles))
    )
    if solo_no_leidas:
        consulta = consulta.filter(Alerta.leida_en.is_(None))
    filas = consulta.order_by(Alerta.creada_en.desc()).limit(limite).all()
    return [_alerta_out(a, perfil_id) for a, perfil_id in filas]


@router.post("/alertas/{alerta_id}/leida", response_model=AlertaOut)
def marcar_alerta_leida(
    alerta_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    alerta = db.get(Alerta, alerta_id)
    if alerta is None or alerta.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
    if alerta.leida_en is None:
        alerta.leida_en = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alerta)
    perfil_id = db.get(Actividad, alerta.actividad_id).perfil_id
    return _alerta_out(alerta, perfil_id)
