"""
Endpoints de HU 17: pulsera, ubicación y geocercas de un perfil.

POST   /perfiles/{id}/pulseras                  -> registra la pulsera (titular)
GET    /perfiles/{id}/pulseras                  -> lista
PATCH  /perfiles/{id}/pulseras/{pulsera_id}     -> renombra, activa o desactiva (titular)
DELETE /perfiles/{id}/pulseras/{pulsera_id}     -> la quita con sus posiciones (titular)
GET    /perfiles/{id}/ubicacion                 -> última ubicación y geocercas donde está
GET    /perfiles/{id}/ubicacion/historial       -> posiciones entre dos momentos
POST   /perfiles/{id}/geocercas                 -> crea una zona circular (titular)
GET    /perfiles/{id}/geocercas                 -> lista
PATCH  /perfiles/{id}/geocercas/{geocerca_id}   -> edita o activa/desactiva (titular)
DELETE /perfiles/{id}/geocercas/{geocerca_id}   -> borra (titular)

Ver ubicación y geocercas exige ser titular o tener `puede_ver_indicadores`; administrar la pulsera y
las zonas, ser el titular. Las posiciones las crea Traccar en `POST /traccar/posiciones`.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_TITULAR, PERMISO_VER_INDICADORES, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.evento_seguridad import EventoSeguridad
from app.models.pulsera import Geocerca, Posicion, Pulsera
from app.models.usuario import Usuario
from app.schemas.sprint5 import (
    GeocercaCreate, GeocercaOut, GeocercaUpdate, PosicionOut, PulseraCreate, PulseraOut, PulseraUpdate, UbicacionOut,
)
from app.services.eventos import aware
from app.services.pulsera import geocercas_donde_esta

router = APIRouter(prefix="/perfiles/{perfil_id}", tags=["Pulsera y geocercas"])

MAX_GEOCERCAS = 20


def _pulsera_del_perfil(db: Session, perfil_id: UUID, pulsera_id: UUID) -> Pulsera:
    pulsera = db.get(Pulsera, pulsera_id)
    if pulsera is None or pulsera.perfil_id != perfil_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pulsera no encontrada")
    return pulsera


def _geocerca_del_perfil(db: Session, perfil_id: UUID, geocerca_id: UUID) -> Geocerca:
    geocerca = db.get(Geocerca, geocerca_id)
    if geocerca is None or geocerca.perfil_id != perfil_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geocerca no encontrada")
    return geocerca


# --- Pulsera -------------------------------------------------------------------

@router.post("/pulseras", response_model=PulseraOut, status_code=status.HTTP_201_CREATED)
def registrar_pulsera(
    perfil_id: UUID,
    datos: PulseraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    if db.query(Pulsera).filter(Pulsera.identificador == datos.identificador.strip()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esa pulsera ya está registrada")
    pulsera = Pulsera(
        perfil_id=perfil.id, identificador=datos.identificador.strip(), nombre=datos.nombre.strip(), modelo=datos.modelo
    )
    db.add(pulsera)
    db.commit()
    db.refresh(pulsera)
    return pulsera


@router.get("/pulseras", response_model=list[PulseraOut])
def listar_pulseras(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    return db.query(Pulsera).filter(Pulsera.perfil_id == perfil.id).order_by(Pulsera.creado_en).all()


@router.patch("/pulseras/{pulsera_id}", response_model=PulseraOut)
def actualizar_pulsera(
    perfil_id: UUID,
    pulsera_id: UUID,
    datos: PulseraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    pulsera = _pulsera_del_perfil(db, perfil.id, pulsera_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        if valor is not None:
            setattr(pulsera, campo, valor)
    db.commit()
    db.refresh(pulsera)
    return pulsera


@router.delete("/pulseras/{pulsera_id}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_pulsera(
    perfil_id: UUID,
    pulsera_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    pulsera = _pulsera_del_perfil(db, perfil.id, pulsera_id)
    # En SQLite (pruebas) no hay cascada de llaves foráneas: se borra explícitamente.
    db.query(Posicion).filter(Posicion.pulsera_id == pulsera.id).delete(synchronize_session=False)
    db.query(EventoSeguridad).filter(EventoSeguridad.pulsera_id == pulsera.id).update(
        {"pulsera_id": None}, synchronize_session=False
    )
    db.delete(pulsera)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Ubicación -------------------------------------------------------------------

@router.get("/ubicacion", response_model=UbicacionOut)
def ubicacion_actual(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Última posición entre las pulseras activas del perfil (vacía si aún no hay ninguna)."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    ids = [p.id for p in db.query(Pulsera).filter(Pulsera.perfil_id == perfil.id, Pulsera.activa.is_(True)).all()]
    posicion = (
        db.query(Posicion).filter(Posicion.pulsera_id.in_(ids)).order_by(Posicion.registrada_en.desc()).first()
        if ids else None
    )
    if posicion is None:
        return UbicacionOut(perfil_id=perfil.id)
    return UbicacionOut(
        perfil_id=perfil.id,
        pulsera=db.get(Pulsera, posicion.pulsera_id),
        posicion=posicion,
        dentro_de=geocercas_donde_esta(db, perfil.id, posicion),
    )


@router.get("/ubicacion/historial", response_model=list[PosicionOut])
def historial_ubicacion(
    perfil_id: UUID,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    limite: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    ids = [p.id for p in db.query(Pulsera).filter(Pulsera.perfil_id == perfil.id).all()]
    if not ids:
        return []
    consulta = db.query(Posicion).filter(Posicion.pulsera_id.in_(ids))
    if desde:
        consulta = consulta.filter(Posicion.registrada_en >= aware(desde))
    if hasta:
        consulta = consulta.filter(Posicion.registrada_en <= aware(hasta))
    return consulta.order_by(Posicion.registrada_en.desc()).limit(limite).all()


# --- Geocercas ---------------------------------------------------------------------

@router.post("/geocercas", response_model=GeocercaOut, status_code=status.HTTP_201_CREATED)
def crear_geocerca(
    perfil_id: UUID,
    datos: GeocercaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    if db.query(Geocerca).filter(Geocerca.perfil_id == perfil.id).count() >= MAX_GEOCERCAS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Máximo {MAX_GEOCERCAS} zonas por perfil")
    if db.query(Geocerca).filter(Geocerca.perfil_id == perfil.id, Geocerca.nombre == datos.nombre.strip()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una zona con ese nombre")
    geocerca = Geocerca(perfil_id=perfil.id, **{**datos.model_dump(), "nombre": datos.nombre.strip()})
    db.add(geocerca)
    db.commit()
    db.refresh(geocerca)
    return geocerca


@router.get("/geocercas", response_model=list[GeocercaOut])
def listar_geocercas(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    return db.query(Geocerca).filter(Geocerca.perfil_id == perfil.id).order_by(Geocerca.nombre).all()


@router.patch("/geocercas/{geocerca_id}", response_model=GeocercaOut)
def actualizar_geocerca(
    perfil_id: UUID,
    geocerca_id: UUID,
    datos: GeocercaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    geocerca = _geocerca_del_perfil(db, perfil.id, geocerca_id)
    cambios = {k: v for k, v in datos.model_dump(exclude_unset=True).items() if v is not None}
    nuevo_nombre = cambios.get("nombre", geocerca.nombre).strip()
    if nuevo_nombre != geocerca.nombre and db.query(Geocerca).filter(
        Geocerca.perfil_id == perfil.id, Geocerca.nombre == nuevo_nombre
    ).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una zona con ese nombre")
    if "nombre" in cambios:
        cambios["nombre"] = nuevo_nombre
    for campo, valor in cambios.items():
        setattr(geocerca, campo, valor)
    db.commit()
    db.refresh(geocerca)
    return geocerca


@router.delete("/geocercas/{geocerca_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_geocerca(
    perfil_id: UUID,
    geocerca_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    db.delete(_geocerca_del_perfil(db, perfil.id, geocerca_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
