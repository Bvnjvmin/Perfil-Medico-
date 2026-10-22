"""
Esquemas Pydantic del Sprint 4: horarios de medicamentos y rutinas (habilitador),
dispositivos para notificaciones (HU 9) y alertas (HU 10).
"""
from datetime import datetime, time
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HorarioCreate(BaseModel):
    hora: time


class HorarioOut(BaseModel):
    id: UUID
    hora: time
    medicamento_id: Optional[UUID] = None
    rutina_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class DispositivoCreate(BaseModel):
    token: str = Field(min_length=1, max_length=4096)
    plataforma: Literal["android", "ios"] = "android"


class DispositivoOut(BaseModel):
    id: UUID
    plataforma: str
    creado_en: datetime

    model_config = {"from_attributes": True}


class AlertaOut(BaseModel):
    id: UUID
    perfil_id: UUID
    actividad_id: UUID
    tipo: Literal["recordatorio", "alerta"]
    nivel: int
    mensaje: str
    creada_en: datetime
    leida_en: Optional[datetime] = None
