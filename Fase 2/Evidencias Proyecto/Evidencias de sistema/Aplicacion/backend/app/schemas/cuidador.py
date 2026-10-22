"""
Esquemas Pydantic de HU 7: cuidadores vinculados a un perfil.
"""
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CuidadorCreate(BaseModel):
    """Vincular a una persona (que ya tiene cuenta) con un perfil."""
    email: EmailStr
    rol_vinculo: Literal["cuidador", "lectura"] = "cuidador"
    puede_confirmar: bool = True
    puede_editar_rutinas: bool = False
    # Alertas escalonadas (HU 10): si recibe avisos y en qué nivel (1 = primero en enterarse).
    recibe_alertas: bool = True
    nivel_escalamiento: int = Field(default=1, ge=1, le=3)


class CuidadorUpdate(BaseModel):
    """Cambia los permisos de un vínculo (todos opcionales)."""
    rol_vinculo: Optional[Literal["cuidador", "lectura"]] = None
    puede_confirmar: Optional[bool] = None
    puede_editar_rutinas: Optional[bool] = None
    recibe_alertas: Optional[bool] = None
    nivel_escalamiento: Optional[int] = Field(default=None, ge=1, le=3)


class CuidadorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID               # id del vínculo (se usa en PUT y DELETE)
    perfil_id: UUID
    usuario_id: str
    nombre: str
    email: str
    rol_vinculo: str
    puede_confirmar: bool
    puede_editar_rutinas: bool
    recibe_alertas: bool = True
    nivel_escalamiento: int = 1
