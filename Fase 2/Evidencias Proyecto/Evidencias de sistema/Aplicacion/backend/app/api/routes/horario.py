"""
Endpoints del Sprint 4 (habilitador): horarios de medicamentos y rutinas.

POST   /medicamentos/{medicamento_id}/horarios  -> agrega una hora del día
GET    /medicamentos/{medicamento_id}/horarios  -> lista las horas, ordenadas
POST   /rutinas/{rutina_id}/horarios            -> agrega una hora del día
GET    /rutinas/{rutina_id}/horarios            -> lista las horas, ordenadas
DELETE /horarios/{horario_id}                   -> quita una hora

Ver los horarios puede hacerlo cualquiera con acceso al perfil; agregarlos o quitarlos
requiere ser titular o cuidador con `puede_editar_rutinas` (si no, 403). Quien no tiene
acceso recibe 404. Una hora repetida para el mismo medicamento o rutina devuelve 409.
Las actividades de hoy en adelante se ajustan solas la próxima vez que se genera la agenda.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_EDITAR_RUTINAS, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.medicamento import Medicamento, RutinaCuidado
from app.models.rutina_horario import RutinaHorario
from app.models.usuario import Usuario
from app.schemas.aviso import HorarioCreate, HorarioOut

router = APIRouter(tags=["Horarios"])


def _medicamento(medicamento_id: UUID, db: Session, user: Usuario, permiso: str | None) -> Medicamento:
    medicamento = db.get(Medicamento, medicamento_id)
    if medicamento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento no encontrado")
    obtener_perfil_con_permiso(medicamento.perfil_id, db, user, permiso)
    return medicamento


def _rutina(rutina_id: UUID, db: Session, user: Usuario, permiso: str | None) -> RutinaCuidado:
    rutina = db.get(RutinaCuidado, rutina_id)
    if rutina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    obtener_perfil_con_permiso(rutina.perfil_id, db, user, permiso)
    return rutina


def _agregar(db: Session, datos: HorarioCreate, **origen) -> RutinaHorario:
    hora = datos.hora.replace(tzinfo=None, second=0, microsecond=0)
    existe = db.query(RutinaHorario).filter_by(hora=hora, **origen).first()
    if existe is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un horario a esa hora")
    horario = RutinaHorario(hora=hora, **origen)
    db.add(horario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un horario a esa hora")
    db.refresh(horario)
    return horario


@router.post(
    "/medicamentos/{medicamento_id}/horarios", response_model=HorarioOut, status_code=status.HTTP_201_CREATED
)
def agregar_horario_medicamento(
    medicamento_id: UUID,
    datos: HorarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Agrega una hora del día a un medicamento (por ejemplo, 08:00 y 20:00)."""
    medicamento = _medicamento(medicamento_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    return _agregar(db, datos, medicamento_id=medicamento.id)


@router.get("/medicamentos/{medicamento_id}/horarios", response_model=list[HorarioOut])
def listar_horarios_medicamento(
    medicamento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    medicamento = _medicamento(medicamento_id, db, current_user, None)
    return db.query(RutinaHorario).filter_by(medicamento_id=medicamento.id).order_by(RutinaHorario.hora).all()


@router.post("/rutinas/{rutina_id}/horarios", response_model=HorarioOut, status_code=status.HTTP_201_CREATED)
def agregar_horario_rutina(
    rutina_id: UUID,
    datos: HorarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Agrega una hora del día a una rutina de cuidado."""
    rutina = _rutina(rutina_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    return _agregar(db, datos, rutina_id=rutina.id)


@router.get("/rutinas/{rutina_id}/horarios", response_model=list[HorarioOut])
def listar_horarios_rutina(
    rutina_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    rutina = _rutina(rutina_id, db, current_user, None)
    return db.query(RutinaHorario).filter_by(rutina_id=rutina.id).order_by(RutinaHorario.hora).all()


@router.delete("/horarios/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_horario(
    horario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Quita una hora. Sus actividades pendientes de hoy en adelante se eliminan solas."""
    horario = db.get(RutinaHorario, horario_id)
    if horario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario no encontrado")
    if horario.medicamento_id is not None:
        _medicamento(horario.medicamento_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    else:
        _rutina(horario.rutina_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    db.delete(horario)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
