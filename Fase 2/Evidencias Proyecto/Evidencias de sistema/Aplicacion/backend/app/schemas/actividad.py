"""
Esquemas Pydantic de HU 5 (cierre): actividades diarias de la agenda.

Una actividad es "tomar este medicamento" o "hacer esta rutina" en un día
concreto. Los textos (título, detalle, hora) no se guardan en la actividad:
se leen del medicamento o la rutina cada vez que se consulta.
"""
from datetime import date, datetime, time
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class ActividadOut(BaseModel):
    id: UUID
    perfil_id: UUID
    fecha: date
    origen_tipo: Literal["medicamento", "rutina"]
    origen_id: UUID
    titulo: str
    detalle: str
    hora: Optional[time] = None
    estado: Literal["pendiente", "confirmada"]
    confirmada_en: Optional[datetime] = None
    confirmada_por_id: Optional[str] = None
