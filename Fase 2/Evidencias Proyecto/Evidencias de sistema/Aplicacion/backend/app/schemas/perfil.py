"""
Esquemas Pydantic de HU 2: datos básicos de salud del titular.

Un `Perfil` representa a quién pertenecen los datos de salud: hoy siempre es
el propio titular (el dueño de la cuenta); desde el Sprint 3 podrá ser
también un perfil dependiente a cargo del titular.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PerfilCreate(BaseModel):
    """Datos que llegan al crear un perfil de salud."""
    tipo: str = Field(min_length=2, max_length=50, description="Ej: 'titular'")
    nombre: str = Field(min_length=2, max_length=120)
    rut: Optional[str] = Field(default=None, max_length=12)
    grupo_sanguineo: Optional[str] = Field(default=None, max_length=15)
    fecha_nacimiento: Optional[date] = None
    subtipo: Optional[str] = Field(default=None, max_length=50)


class PerfilUpdate(BaseModel):
    """Datos que se pueden actualizar de un perfil existente (todos opcionales)."""
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    rut: Optional[str] = Field(default=None, max_length=12)
    grupo_sanguineo: Optional[str] = Field(default=None, max_length=15)
    fecha_nacimiento: Optional[date] = None
    subtipo: Optional[str] = Field(default=None, max_length=50)
    activo: Optional[bool] = None


class PerfilOut(BaseModel):
    """Datos de un perfil que se devuelven al cliente."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cuenta_titular_id: str
    tipo: str
    nombre: str
    rut: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    subtipo: Optional[str] = None
    activo: bool
    creado_en: datetime


class AlergiaCreate(BaseModel):
    """Datos que llegan al registrar una alergia en un perfil."""
    sustancia: str = Field(min_length=2, max_length=120)
    severidad: str = Field(min_length=2, max_length=50, description="Ej: 'leve', 'moderada', 'grave'")


class AlergiaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    sustancia: str
    severidad: str


class ContactoEmergenciaCreate(BaseModel):
    """Datos que llegan al registrar un contacto de emergencia en un perfil."""
    nombre: str = Field(min_length=2, max_length=150)
    telefono: str = Field(min_length=6, max_length=20)
    relacion: Optional[str] = Field(default=None, max_length=50, description="Ej: 'hijo/a', 'cónyuge'")
    prioridad: int = Field(default=1, ge=1, description="1 = primer contacto a llamar")


class ContactoEmergenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    nombre: str
    telefono: str
    relacion: Optional[str] = None
    prioridad: int
