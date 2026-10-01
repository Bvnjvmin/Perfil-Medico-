"""
Esquemas Pydantic de HU 4: medicamentos y rutinas de cuidado de un perfil.
"""
from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MedicamentoCreate(BaseModel):
    """Datos que llegan al registrar un medicamento en un perfil."""
    nombre: str = Field(min_length=2, max_length=120)
    dosis: str = Field(min_length=1, max_length=50, description="Ej: '500 mg'")
    frecuencia: str = Field(min_length=2, max_length=50, description="Ej: 'cada 8 horas'")
    hora_inicio: Optional[time] = None


class MedicamentoUpdate(BaseModel):
    """Campos que se pueden actualizar de un medicamento (todos opcionales)."""
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    dosis: Optional[str] = Field(default=None, min_length=1, max_length=50)
    frecuencia: Optional[str] = Field(default=None, min_length=2, max_length=50)
    hora_inicio: Optional[time] = None
    activo: Optional[bool] = None


class MedicamentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    nombre: str
    dosis: str
    frecuencia: str
    hora_inicio: Optional[time] = None
    activo: bool
    creado_en: datetime


class RutinaCuidadoCreate(BaseModel):
    """Datos que llegan al registrar una rutina de cuidado en un perfil."""
    tipo: str = Field(min_length=2, max_length=50, description="Ej: 'alimentacion', 'hidratacion', 'vitaminas'")
    descripcion: Optional[str] = Field(default=None, max_length=200)
    frecuencia: str = Field(min_length=2, max_length=50, description="Ej: '3 veces al día'")
    hora: Optional[time] = None


class RutinaCuidadoUpdate(BaseModel):
    """Campos que se pueden actualizar de una rutina de cuidado (todos opcionales)."""
    tipo: Optional[str] = Field(default=None, min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    frecuencia: Optional[str] = Field(default=None, min_length=2, max_length=50)
    hora: Optional[time] = None
    activo: Optional[bool] = None


class RutinaCuidadoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    tipo: str
    descripcion: Optional[str] = None
    frecuencia: str
    hora: Optional[time] = None
    activo: bool
    creado_en: datetime
