"""
Esquemas Pydantic: definen la "forma" de los datos que entran y salen de la API.

Por qué son distintos de los modelos SQLAlchemy (app/models/usuario.py):
los modelos describen la tabla en la base de datos; estos esquemas describen
el JSON que viaja por HTTP. Por ejemplo, nunca se envía el hashed_password
de vuelta al cliente — por eso UsuarioOut no lo incluye.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.usuario import RolUsuario


class UsuarioCreate(BaseModel):
    """Datos que llegan al registrar un usuario nuevo."""
    nombre: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    rol: RolUsuario = RolUsuario.TITULAR


class UsuarioOut(BaseModel):
    """Datos que se devuelven al cliente (nunca la contraseña)."""
    model_config = ConfigDict(from_attributes=True)  # permite construirlo directo desde el modelo SQLAlchemy

    id: str
    nombre: str
    email: EmailStr
    rol: RolUsuario
    creado_en: datetime


class Token(BaseModel):
    """Respuesta del endpoint de login."""
    access_token: str
    token_type: str = "bearer"
