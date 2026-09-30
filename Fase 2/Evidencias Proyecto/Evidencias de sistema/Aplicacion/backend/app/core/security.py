"""
Funciones de seguridad: hash de contraseñas (bcrypt) y tokens JWT.

Dos responsabilidades separadas a propósito:
1. Contraseñas: nunca se guardan en texto plano en la base de datos. Se
   guarda un "hash" (una huella irreversible) generado con bcrypt.
2. Tokens JWT: una vez que el usuario inicia sesión, en vez de que envíe su
   contraseña en cada request, le entregamos un token firmado que prueba su
   identidad por un tiempo limitado (ACCESS_TOKEN_EXPIRE_MINUTES).
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Genera el hash de una contraseña para guardarlo en la base de datos."""
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña ingresada contra el hash guardado."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Crea un token JWT firmado. 'subject' es normalmente el ID del usuario:
    es lo que queda "adentro" del token para identificarlo en cada request.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Verifica la firma y vigencia de un token, y devuelve su contenido.
    Lanza jwt.PyJWTError si el token es inválido, falso, o expiró.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
