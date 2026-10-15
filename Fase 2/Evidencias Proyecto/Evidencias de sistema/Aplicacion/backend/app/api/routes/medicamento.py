"""
Endpoints de HU 4: medicamentos y rutinas de cuidado (alimentación,
hidratación, vitaminas) de un perfil propio.

POST   /perfiles/{perfil_id}/medicamentos          -> registra un medicamento
GET    /perfiles/{perfil_id}/medicamentos          -> lista los medicamentos del perfil
GET    /medicamentos/{medicamento_id}              -> consulta un medicamento propio
PUT    /medicamentos/{medicamento_id}              -> actualiza un medicamento propio
DELETE /medicamentos/{medicamento_id}              -> elimina un medicamento propio

POST   /perfiles/{perfil_id}/rutinas               -> registra una rutina de cuidado
GET    /perfiles/{perfil_id}/rutinas               -> lista las rutinas del perfil
GET    /rutinas/{rutina_id}                        -> consulta una rutina propia
PUT    /rutinas/{rutina_id}                        -> actualiza una rutina propia
DELETE /rutinas/{rutina_id}                        -> elimina una rutina propia

El acceso se decide con `obtener_perfil_con_permiso` (app/api/deps.py): ver
medicamentos y rutinas lo puede hacer el titular y cualquiera con un vínculo
al perfil; crearlos, editarlos o borrarlos requiere ser titular o cuidador
con `puede_editar_rutinas`. Quien no tiene acceso recibe 404.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_EDITAR_RUTINAS, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.actividad import Actividad
from app.models.medicamento import Medicamento, RutinaCuidado
from app.models.usuario import Usuario
from app.schemas.medicamento import (
    MedicamentoCreate,
    MedicamentoOut,
    MedicamentoUpdate,
    RutinaCuidadoCreate,
    RutinaCuidadoOut,
    RutinaCuidadoUpdate,
)

router = APIRouter(tags=["Medicamentos y rutinas de cuidado"])


def _obtener_medicamento_propio(
    medicamento_id: UUID, db: Session, current_user: Usuario, permiso: str | None = None
) -> Medicamento:
    medicamento = db.get(Medicamento, medicamento_id)
    if medicamento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento no encontrado")
    # Confirma que el usuario tiene acceso al perfil dueño del medicamento
    # (y el permiso pedido, si la acción modifica datos).
    obtener_perfil_con_permiso(medicamento.perfil_id, db, current_user, permiso)
    return medicamento


def _obtener_rutina_propia(
    rutina_id: UUID, db: Session, current_user: Usuario, permiso: str | None = None
) -> RutinaCuidado:
    rutina = db.get(RutinaCuidado, rutina_id)
    if rutina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rutina no encontrada")
    obtener_perfil_con_permiso(rutina.perfil_id, db, current_user, permiso)
    return rutina


# --- Medicamentos --------------------------------------------------------

@router.post(
    "/perfiles/{perfil_id}/medicamentos",
    response_model=MedicamentoOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_medicamento(
    perfil_id: UUID,
    datos: MedicamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra un medicamento (nombre, dosis, frecuencia) en un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    medicamento = Medicamento(
        perfil_id=perfil.id,
        nombre=datos.nombre,
        dosis=datos.dosis,
        frecuencia=datos.frecuencia,
        hora_inicio=datos.hora_inicio,
    )
    db.add(medicamento)
    db.commit()
    db.refresh(medicamento)
    return medicamento


@router.get("/perfiles/{perfil_id}/medicamentos", response_model=list[MedicamentoOut])
def listar_medicamentos(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista los medicamentos registrados en un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return db.query(Medicamento).filter(Medicamento.perfil_id == perfil.id).all()


@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoOut)
def obtener_medicamento(
    medicamento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Consulta un medicamento propio por id."""
    return _obtener_medicamento_propio(medicamento_id, db, current_user)


@router.put("/medicamentos/{medicamento_id}", response_model=MedicamentoOut)
def actualizar_medicamento(
    medicamento_id: UUID,
    datos: MedicamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los campos enviados de un medicamento propio."""
    medicamento = _obtener_medicamento_propio(medicamento_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(medicamento, campo, valor)
    db.commit()
    db.refresh(medicamento)
    return medicamento


@router.delete("/medicamentos/{medicamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medicamento(
    medicamento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina un medicamento propio."""
    medicamento = _obtener_medicamento_propio(medicamento_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    # Sus actividades se borran explícitamente (SQLite no aplica ON DELETE CASCADE).
    db.query(Actividad).filter(Actividad.medicamento_id == medicamento.id).delete()
    db.delete(medicamento)
    db.commit()


# --- Rutinas de cuidado ----------------------------------------------------

@router.post(
    "/perfiles/{perfil_id}/rutinas",
    response_model=RutinaCuidadoOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_rutina(
    perfil_id: UUID,
    datos: RutinaCuidadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra una rutina de cuidado (alimentación, hidratación, vitaminas, etc.) en un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    rutina = RutinaCuidado(
        perfil_id=perfil.id,
        tipo=datos.tipo,
        descripcion=datos.descripcion,
        frecuencia=datos.frecuencia,
        hora=datos.hora,
    )
    db.add(rutina)
    db.commit()
    db.refresh(rutina)
    return rutina


@router.get("/perfiles/{perfil_id}/rutinas", response_model=list[RutinaCuidadoOut])
def listar_rutinas(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las rutinas de cuidado registradas en un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return db.query(RutinaCuidado).filter(RutinaCuidado.perfil_id == perfil.id).all()


@router.get("/rutinas/{rutina_id}", response_model=RutinaCuidadoOut)
def obtener_rutina(
    rutina_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Consulta una rutina de cuidado propia por id."""
    return _obtener_rutina_propia(rutina_id, db, current_user)


@router.put("/rutinas/{rutina_id}", response_model=RutinaCuidadoOut)
def actualizar_rutina(
    rutina_id: UUID,
    datos: RutinaCuidadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los campos enviados de una rutina de cuidado propia."""
    rutina = _obtener_rutina_propia(rutina_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(rutina, campo, valor)
    db.commit()
    db.refresh(rutina)
    return rutina


@router.delete("/rutinas/{rutina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rutina(
    rutina_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina una rutina de cuidado propia."""
    rutina = _obtener_rutina_propia(rutina_id, db, current_user, PERMISO_EDITAR_RUTINAS)
    db.query(Actividad).filter(Actividad.rutina_id == rutina.id).delete()
    db.delete(rutina)
    db.commit()
