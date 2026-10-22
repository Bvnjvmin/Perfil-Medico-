"""
Endpoints de HU 2: datos básicos de salud del titular (perfil, alergias y
contactos de emergencia).

POST   /perfiles                                -> crea el perfil de salud del titular autenticado
GET    /perfiles                                -> lista los perfiles del titular autenticado
GET    /perfiles/{perfil_id}                    -> consulta un perfil propio
PUT    /perfiles/{perfil_id}                    -> actualiza un perfil propio
DELETE /perfiles/{perfil_id}                    -> elimina un perfil propio

POST   /perfiles/{perfil_id}/alergias           -> agrega una alergia al perfil
GET    /perfiles/{perfil_id}/alergias           -> lista las alergias del perfil
DELETE /perfiles/{perfil_id}/alergias/{alergia_id}

POST   /perfiles/{perfil_id}/contactos-emergencia          -> agrega un contacto de emergencia
GET    /perfiles/{perfil_id}/contactos-emergencia          -> lista los contactos de emergencia
DELETE /perfiles/{perfil_id}/contactos-emergencia/{contacto_id}

Todos los endpoints requieren autenticación. Ver un perfil, sus alergias y
contactos lo puede hacer el titular y quien tenga un vínculo con el perfil
(cuidador o lectura, HU 7); crear, editar o borrar lo puede hacer solo el
titular. Quien no tiene ningún acceso recibe 404 y quien tiene acceso pero
no el permiso recibe 403 (ver `obtener_perfil_con_permiso` en app/api/deps.py).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import (
    PERMISO_TITULAR,
    Acceso,
    get_current_user,
    obtener_perfil_con_permiso,
    perfiles_accesibles,
)
from app.db.session import get_db
from app.models.actividad import Actividad
from app.models.alerta import Alerta
from app.models.rutina_horario import RutinaHorario
from app.models.medicamento import Medicamento, RutinaCuidado
from app.models.perfil import Alergia, ContactoEmergencia, Perfil
from app.models.perfil_acceso import PerfilAcceso
from app.models.usuario import Usuario
from app.schemas.perfil import (
    AccesoOut,
    AlergiaCreate,
    AlergiaOut,
    ContactoEmergenciaCreate,
    ContactoEmergenciaOut,
    PerfilCreate,
    PerfilOut,
    PerfilUpdate,
)

router = APIRouter(prefix="/perfiles", tags=["Perfil de salud"])


def perfil_con_acceso(perfil: Perfil, acceso: Acceso) -> PerfilOut:
    """Arma la respuesta de un perfil incluyendo qué puede hacer quien consulta."""
    salida = PerfilOut.model_validate(perfil)
    salida.mi_acceso = AccesoOut(
        rol=acceso.rol,
        puede_confirmar=acceso.puede_confirmar,
        puede_editar_rutinas=acceso.puede_editar_rutinas,
    )
    return salida


@router.post("", response_model=PerfilOut, status_code=status.HTTP_201_CREATED)
def crear_perfil(
    datos: PerfilCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crea un perfil de salud para la cuenta autenticada: su perfil titular o un
    perfil dependiente (adulto mayor o niño) a su cargo. Cada cuenta tiene un
    solo perfil titular.
    """
    if datos.tipo == "titular":
        ya_tiene = (
            db.query(Perfil)
            .filter(Perfil.cuenta_titular_id == current_user.id, Perfil.tipo == "titular")
            .first()
        )
        if ya_tiene is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta cuenta ya tiene un perfil titular",
            )
    nuevo_perfil = Perfil(
        cuenta_titular_id=current_user.id,
        tipo=datos.tipo,
        nombre=datos.nombre,
        rut=datos.rut,
        grupo_sanguineo=datos.grupo_sanguineo,
        fecha_nacimiento=datos.fecha_nacimiento,
        subtipo=datos.subtipo,
    )
    db.add(nuevo_perfil)
    try:
        db.commit()
    except IntegrityError:
        # Dos solicitudes simultáneas: el índice único de la base de datos lo detiene.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta cuenta ya tiene un perfil titular",
        )
    db.refresh(nuevo_perfil)
    return perfil_con_acceso(nuevo_perfil, Acceso("titular", True, True))


@router.get("", response_model=list[PerfilOut])
def listar_perfiles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lista los perfiles a los que el usuario tiene acceso: primero los propios
    (titular y dependientes) y después los que otros le compartieron. Cada uno
    trae `mi_acceso` con lo que puede hacer.
    """
    return [perfil_con_acceso(p, a) for p, a in perfiles_accesibles(db, current_user)]


@router.get("/{perfil_id}", response_model=PerfilOut)
def obtener_perfil(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Consulta un perfil propio o compartido por id."""
    perfil, acceso = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return perfil_con_acceso(perfil, acceso)


@router.put("/{perfil_id}", response_model=PerfilOut)
def actualizar_perfil(
    perfil_id: UUID,
    datos: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los campos enviados de un perfil propio (los no enviados quedan igual)."""
    perfil, acceso = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    cambios = datos.model_dump(exclude_unset=True)
    if "subtipo" in cambios:
        if perfil.tipo == "titular" and cambios["subtipo"] is not None:
            raise HTTPException(
                status_code=422,
                detail="El perfil titular no lleva subtipo",
            )
        if perfil.tipo == "dependiente" and cambios["subtipo"] is None:
            raise HTTPException(
                status_code=422,
                detail="Un perfil dependiente requiere subtipo",
            )
    for campo, valor in cambios.items():
        setattr(perfil, campo, valor)
    db.commit()
    db.refresh(perfil)
    return perfil_con_acceso(perfil, acceso)


@router.delete("/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_perfil(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina un perfil propio con todo lo que cuelga de él.

    El borrado es explícito y en orden (de lo más dependiente a lo menos), sin
    confiar solo en ON DELETE CASCADE: las pruebas usan SQLite, que no valida
    llaves foráneas, y así el mismo código funciona igual en PostgreSQL.
    """
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    ids_actividades = db.query(Actividad.id).filter(Actividad.perfil_id == perfil.id)
    db.query(Alerta).filter(Alerta.actividad_id.in_(ids_actividades)).delete(synchronize_session=False)
    db.query(Actividad).filter(Actividad.perfil_id == perfil.id).delete()
    ids_medicamentos = db.query(Medicamento.id).filter(Medicamento.perfil_id == perfil.id)
    ids_rutinas = db.query(RutinaCuidado.id).filter(RutinaCuidado.perfil_id == perfil.id)
    db.query(RutinaHorario).filter(RutinaHorario.medicamento_id.in_(ids_medicamentos)).delete(synchronize_session=False)
    db.query(RutinaHorario).filter(RutinaHorario.rutina_id.in_(ids_rutinas)).delete(synchronize_session=False)
    db.query(Medicamento).filter(Medicamento.perfil_id == perfil.id).delete()
    db.query(RutinaCuidado).filter(RutinaCuidado.perfil_id == perfil.id).delete()
    db.query(PerfilAcceso).filter(PerfilAcceso.perfil_id == perfil.id).delete()
    db.query(Alergia).filter(Alergia.perfil_id == perfil.id).delete()
    db.query(ContactoEmergencia).filter(ContactoEmergencia.perfil_id == perfil.id).delete()
    db.delete(perfil)
    db.commit()


# --- Alergias -----------------------------------------------------------

@router.post(
    "/{perfil_id}/alergias",
    response_model=AlergiaOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_alergia(
    perfil_id: UUID,
    datos: AlergiaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Agrega una alergia a un perfil propio (solo el titular)."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    alergia = Alergia(perfil_id=perfil.id, sustancia=datos.sustancia, severidad=datos.severidad)
    db.add(alergia)
    db.commit()
    db.refresh(alergia)
    return alergia


@router.get("/{perfil_id}/alergias", response_model=list[AlergiaOut])
def listar_alergias(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las alergias de un perfil propio o compartido."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return db.query(Alergia).filter(Alergia.perfil_id == perfil.id).all()


@router.delete("/{perfil_id}/alergias/{alergia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_alergia(
    perfil_id: UUID,
    alergia_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina una alergia de un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    alergia = db.get(Alergia, alergia_id)
    if alergia is None or alergia.perfil_id != perfil.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alergia no encontrada")
    db.delete(alergia)
    db.commit()


# --- Contactos de emergencia --------------------------------------------

@router.post(
    "/{perfil_id}/contactos-emergencia",
    response_model=ContactoEmergenciaOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_contacto_emergencia(
    perfil_id: UUID,
    datos: ContactoEmergenciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Agrega un contacto de emergencia a un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    contacto = ContactoEmergencia(
        perfil_id=perfil.id,
        nombre=datos.nombre,
        telefono=datos.telefono,
        relacion=datos.relacion,
        prioridad=datos.prioridad,
    )
    db.add(contacto)
    db.commit()
    db.refresh(contacto)
    return contacto


@router.get("/{perfil_id}/contactos-emergencia", response_model=list[ContactoEmergenciaOut])
def listar_contactos_emergencia(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista los contactos de emergencia de un perfil propio o compartido, por prioridad."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return (
        db.query(ContactoEmergencia)
        .filter(ContactoEmergencia.perfil_id == perfil.id)
        .order_by(ContactoEmergencia.prioridad)
        .all()
    )


@router.delete(
    "/{perfil_id}/contactos-emergencia/{contacto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_contacto_emergencia(
    perfil_id: UUID,
    contacto_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina un contacto de emergencia de un perfil propio."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    contacto = db.get(ContactoEmergencia, contacto_id)
    if contacto is None or contacto.perfil_id != perfil.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
    db.delete(contacto)
    db.commit()
