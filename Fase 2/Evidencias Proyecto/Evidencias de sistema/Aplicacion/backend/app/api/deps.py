"""
Dependencia reutilizable de FastAPI: a partir del token JWT que viene en el
header 'Authorization: Bearer <token>', averigua qué usuario está haciendo
el request. Cualquier endpoint que necesite "saber quién está conectado"
simplemente pide esta dependencia (ver ejemplo en api/routes/auth.py: /me).
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.perfil import Perfil
from app.models.perfil_acceso import PerfilAcceso
from app.models.usuario import Usuario

# Le dice a FastAPI (y a la documentación /docs) que el login vive en /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar la credencial",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.get(Usuario, user_id)
    if user is None:
        raise credentials_exception
    return user


@dataclass
class Acceso:
    """
    Qué puede hacer un usuario sobre un perfil (HU 7).

    rol: 'titular' (dueño de la cuenta del perfil), 'cuidador' o 'lectura'
    (estos dos salen de la tabla `perfil_acceso`).
    """
    rol: str
    puede_confirmar: bool
    puede_editar_rutinas: bool
    acceso_id: Optional[UUID] = None


# Permisos que pueden pedir las rutas. Si no se pide ninguno, basta con
# tener cualquier acceso al perfil (solo ver).
PERMISO_TITULAR = "titular"                 # editar/borrar perfil, alergias, contactos; administrar cuidadores
PERMISO_CONFIRMAR = "confirmar"             # confirmar o desconfirmar actividades
PERMISO_EDITAR_RUTINAS = "editar_rutinas"   # crear, editar o borrar medicamentos y rutinas


def _acceso_desde_vinculo(vinculo: PerfilAcceso) -> Acceso:
    # El rol 'lectura' nunca puede confirmar ni editar, aunque la fila diga otra cosa.
    es_lectura = vinculo.rol_vinculo == "lectura"
    return Acceso(
        rol=vinculo.rol_vinculo,
        puede_confirmar=False if es_lectura else bool(vinculo.puede_confirmar),
        puede_editar_rutinas=False if es_lectura else bool(vinculo.puede_editar_rutinas),
        acceso_id=vinculo.id,
    )


def calcular_acceso(perfil: Perfil, db: Session, usuario: Usuario) -> Optional[Acceso]:
    """Devuelve el acceso del usuario al perfil, o None si no tiene ninguno."""
    if perfil.cuenta_titular_id == usuario.id:
        return Acceso(rol="titular", puede_confirmar=True, puede_editar_rutinas=True)
    vinculo = (
        db.query(PerfilAcceso)
        .filter(PerfilAcceso.perfil_id == perfil.id, PerfilAcceso.usuario_id == usuario.id)
        .first()
    )
    return _acceso_desde_vinculo(vinculo) if vinculo else None


def obtener_perfil_con_permiso(
    perfil_id: UUID,
    db: Session,
    current_user: Usuario,
    permiso: Optional[str] = None,
) -> tuple[Perfil, Acceso]:
    """
    Busca un perfil y confirma que el usuario autenticado puede hacer lo que pide.

    - Sin ningún acceso (o perfil inexistente): 404, para no revelar que el id existe.
    - Con acceso pero sin el permiso pedido: 403.

    `permiso` puede ser None (solo ver), PERMISO_TITULAR, PERMISO_CONFIRMAR o
    PERMISO_EDITAR_RUTINAS.
    """
    perfil = db.get(Perfil, perfil_id)
    acceso = calcular_acceso(perfil, db, current_user) if perfil is not None else None
    if acceso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado",
        )
    permitido = (
        permiso is None
        or (permiso == PERMISO_TITULAR and acceso.rol == "titular")
        or (permiso == PERMISO_CONFIRMAR and acceso.puede_confirmar)
        or (permiso == PERMISO_EDITAR_RUTINAS and acceso.puede_editar_rutinas)
    )
    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para realizar esta acción en este perfil",
        )
    return perfil, acceso


def obtener_perfil_propio(perfil_id: UUID, db: Session, current_user: Usuario) -> Perfil:
    """Perfil que pertenece al usuario autenticado (solo el titular; otros reciben 403/404)."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_TITULAR)
    return perfil


def perfiles_accesibles(db: Session, usuario: Usuario) -> list[tuple[Perfil, Acceso]]:
    """
    Todos los perfiles a los que el usuario tiene acceso: primero los propios
    (por fecha de creación) y después los que otros titulares le compartieron.
    """
    propios = (
        db.query(Perfil)
        .filter(Perfil.cuenta_titular_id == usuario.id)
        .order_by(Perfil.creado_en)
        .all()
    )
    resultado = [(p, Acceso(rol="titular", puede_confirmar=True, puede_editar_rutinas=True)) for p in propios]
    vinculos = (
        db.query(PerfilAcceso, Perfil)
        .join(Perfil, Perfil.id == PerfilAcceso.perfil_id)
        .filter(PerfilAcceso.usuario_id == usuario.id)
        .order_by(Perfil.creado_en)
        .all()
    )
    resultado += [(perfil, _acceso_desde_vinculo(vinculo)) for vinculo, perfil in vinculos]
    return resultado
