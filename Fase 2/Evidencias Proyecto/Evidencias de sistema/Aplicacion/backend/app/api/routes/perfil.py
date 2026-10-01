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

Todos los endpoints requieren autenticación y están acotados al titular
dueño del token: un usuario nunca puede ver ni modificar perfiles,
alergias o contactos de otra cuenta (ver `obtener_perfil_propio` en
app/api/deps.py).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, obtener_perfil_propio
from app.db.session import get_db
from app.models.perfil import Alergia, ContactoEmergencia, Perfil
from app.models.usuario import Usuario
from app.schemas.perfil import (
    AlergiaCreate,
    AlergiaOut,
    ContactoEmergenciaCreate,
    ContactoEmergenciaOut,
    PerfilCreate,
    PerfilOut,
    PerfilUpdate,
)

router = APIRouter(prefix="/perfiles", tags=["Perfil de salud"])


@router.post("", response_model=PerfilOut, status_code=status.HTTP_201_CREATED)
def crear_perfil(
    datos: PerfilCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un perfil de salud (RUT, grupo sanguíneo, etc.) para el titular autenticado."""
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
    db.commit()
    db.refresh(nuevo_perfil)
    return nuevo_perfil


@router.get("", response_model=list[PerfilOut])
def listar_perfiles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista los perfiles de salud que pertenecen al titular autenticado."""
    return (
        db.query(Perfil)
        .filter(Perfil.cuenta_titular_id == current_user.id)
        .order_by(Perfil.creado_en)
        .all()
    )


@router.get("/{perfil_id}", response_model=PerfilOut)
def obtener_perfil(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Consulta un perfil propio por id."""
    return obtener_perfil_propio(perfil_id, db, current_user)


@router.put("/{perfil_id}", response_model=PerfilOut)
def actualizar_perfil(
    perfil_id: UUID,
    datos: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los campos enviados de un perfil propio (los no enviados quedan igual)."""
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(perfil, campo, valor)
    db.commit()
    db.refresh(perfil)
    return perfil


@router.delete("/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_perfil(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina un perfil propio (y, en cascada, sus alergias y contactos)."""
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
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
    """Agrega una alergia a un perfil propio."""
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
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
    """Lista las alergias registradas en un perfil propio."""
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
    return db.query(Alergia).filter(Alergia.perfil_id == perfil.id).all()


@router.delete("/{perfil_id}/alergias/{alergia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_alergia(
    perfil_id: UUID,
    alergia_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina una alergia de un perfil propio."""
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
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
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
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
    """Lista los contactos de emergencia de un perfil propio, por prioridad."""
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
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
    perfil = obtener_perfil_propio(perfil_id, db, current_user)
    contacto = db.get(ContactoEmergencia, contacto_id)
    if contacto is None or contacto.perfil_id != perfil.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
    db.delete(contacto)
    db.commit()
