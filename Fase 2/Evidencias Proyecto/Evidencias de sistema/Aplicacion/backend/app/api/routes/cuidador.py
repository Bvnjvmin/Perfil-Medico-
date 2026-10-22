"""
Endpoints de HU 7: vincular cuidadores a un perfil y administrar sus permisos.

POST   /perfiles/{perfil_id}/cuidadores               -> vincula a una cuenta existente por correo
GET    /perfiles/{perfil_id}/cuidadores               -> lista los vínculos del perfil
PUT    /perfiles/{perfil_id}/cuidadores/{acceso_id}   -> cambia los permisos de un vínculo
DELETE /perfiles/{perfil_id}/cuidadores/{acceso_id}   -> revoca el vínculo (el acceso se pierde de inmediato)

Solo el titular dueño del perfil puede administrar cuidadores: un cuidador o
una persona de solo lectura recibe 403 y una cuenta sin vínculo recibe 404.

Decisiones del sprint (a confirmar por el equipo):
- Solo se puede vincular a quien ya tiene cuenta; si el correo no existe se
  responde 404. Esto revela si un correo está registrado: se acepta para el MVP.
- Se pueden compartir tanto perfiles dependientes como el perfil titular.
- El rol 'lectura' nunca puede confirmar ni editar rutinas.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_TITULAR, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.perfil_acceso import PerfilAcceso
from app.models.usuario import Usuario
from app.schemas.cuidador import CuidadorCreate, CuidadorOut, CuidadorUpdate

router = APIRouter(prefix="/perfiles/{perfil_id}/cuidadores", tags=["Cuidadores y permisos"])


def _a_salida(vinculo: PerfilAcceso, usuario: Usuario) -> CuidadorOut:
    es_lectura = vinculo.rol_vinculo == "lectura"
    return CuidadorOut(
        id=vinculo.id,
        perfil_id=vinculo.perfil_id,
        usuario_id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        rol_vinculo=vinculo.rol_vinculo,
        puede_confirmar=False if es_lectura else vinculo.puede_confirmar,
        puede_editar_rutinas=False if es_lectura else vinculo.puede_editar_rutinas,
        recibe_alertas=vinculo.recibe_alertas,
        nivel_escalamiento=vinculo.nivel_escalamiento,
    )


def _obtener_vinculo(perfil_id: UUID, acceso_id: UUID, db: Session) -> PerfilAcceso:
    vinculo = db.get(PerfilAcceso, acceso_id)
    if vinculo is None or vinculo.perfil_id != perfil_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vínculo no encontrado")
    return vinculo


@router.post("", response_model=CuidadorOut, status_code=status.HTTP_201_CREATED)
def vincular_cuidador(
    perfil_id: UUID,
    datos: CuidadorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Vincula a una cuenta existente (por correo) con el perfil, con los permisos indicados."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    invitado = (
        db.query(Usuario).filter(func.lower(Usuario.email) == datos.email.lower()).first()
    )
    if invitado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No existe una cuenta con ese correo"
        )
    if invitado.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes vincularte a tu propio perfil",
        )
    ya_vinculado = (
        db.query(PerfilAcceso)
        .filter(PerfilAcceso.perfil_id == perfil.id, PerfilAcceso.usuario_id == invitado.id)
        .first()
    )
    if ya_vinculado is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Esa cuenta ya está vinculada a este perfil"
        )
    es_lectura = datos.rol_vinculo == "lectura"
    vinculo = PerfilAcceso(
        usuario_id=invitado.id,
        perfil_id=perfil.id,
        rol_vinculo=datos.rol_vinculo,
        puede_confirmar=False if es_lectura else datos.puede_confirmar,
        puede_editar_rutinas=False if es_lectura else datos.puede_editar_rutinas,
        recibe_alertas=datos.recibe_alertas,
        nivel_escalamiento=datos.nivel_escalamiento,
    )
    db.add(vinculo)
    db.commit()
    db.refresh(vinculo)
    return _a_salida(vinculo, invitado)


@router.get("", response_model=list[CuidadorOut])
def listar_cuidadores(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las personas vinculadas al perfil y sus permisos."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    filas = (
        db.query(PerfilAcceso, Usuario)
        .join(Usuario, Usuario.id == PerfilAcceso.usuario_id)
        .filter(PerfilAcceso.perfil_id == perfil.id)
        .order_by(Usuario.nombre)
        .all()
    )
    return [_a_salida(v, u) for v, u in filas]


@router.put("/{acceso_id}", response_model=CuidadorOut)
def actualizar_cuidador(
    perfil_id: UUID,
    acceso_id: UUID,
    datos: CuidadorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cambia el rol o los permisos de un vínculo (los campos no enviados quedan igual)."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    vinculo = _obtener_vinculo(perfil.id, acceso_id, db)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        if valor is not None:
            setattr(vinculo, campo, valor)
    if vinculo.rol_vinculo == "lectura":
        vinculo.puede_confirmar = False
        vinculo.puede_editar_rutinas = False
    db.commit()
    db.refresh(vinculo)
    return _a_salida(vinculo, db.get(Usuario, vinculo.usuario_id))


@router.delete("/{acceso_id}", status_code=status.HTTP_204_NO_CONTENT)
def revocar_cuidador(
    perfil_id: UUID,
    acceso_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Revoca el vínculo: esa persona deja de ver el perfil de inmediato."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    vinculo = _obtener_vinculo(perfil.id, acceso_id, db)
    db.delete(vinculo)
    db.commit()
