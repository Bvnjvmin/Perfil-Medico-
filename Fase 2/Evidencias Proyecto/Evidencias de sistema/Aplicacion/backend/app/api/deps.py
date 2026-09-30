"""
Dependencia reutilizable de FastAPI: a partir del token JWT que viene en el
header 'Authorization: Bearer <token>', averigua qué usuario está haciendo
el request. Cualquier endpoint que necesite "saber quién está conectado"
simplemente pide esta dependencia (ver ejemplo en api/routes/auth.py: /me).
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
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
