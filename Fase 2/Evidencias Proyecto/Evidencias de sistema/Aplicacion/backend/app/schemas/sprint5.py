"""
Esquemas Pydantic del Sprint 5: indicadores de salud (HU 12 y 18), cumplimiento
(HU 13), botón de asistencia y eventos de seguridad (HU 14 y 19), pulsera y
geocercas (HU 17) y consultas de IA (HU 15).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

TipoIndicador = Literal["peso", "presion", "glucosa", "frecuencia_cardiaca"]
TipoEvento = Literal["asistencia", "sos", "caida", "bateria_baja", "inactividad", "geocerca_salida"]

UNIDADES = {"peso": "kg", "presion": "mmHg", "glucosa": "mg/dL", "frecuencia_cardiaca": "lpm"}

# Rangos plausibles: rechazan errores de tipeo (un peso de 700 kg), no hacen diagnóstico.
RANGOS = {
    "peso": (1, 400),
    "presion": (30, 300),            # sistólica
    "glucosa": (10, 1000),
    "frecuencia_cardiaca": (20, 300),
}
RANGO_DIASTOLICA = (20, 200)


# --- Indicadores de salud -------------------------------------------------

class IndicadorCreate(BaseModel):
    tipo: TipoIndicador
    valor: Decimal
    # Solo para la presión: `valor` es la sistólica y este campo, la diastólica.
    valor_secundario: Optional[Decimal] = None
    # Si no se envía, se usa el momento del registro. No puede estar en el futuro.
    medido_en: Optional[datetime] = None
    fuente: Literal["manual", "pulsera"] = "manual"
    nota: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _validar(self):
        minimo, maximo = RANGOS[self.tipo]
        if not (minimo <= self.valor <= maximo):
            raise ValueError(f"El valor de {self.tipo} debe estar entre {minimo} y {maximo}")
        if self.tipo == "presion":
            if self.valor_secundario is None:
                raise ValueError("La presión necesita sistólica (valor) y diastólica (valor_secundario)")
            bajo, alto = RANGO_DIASTOLICA
            if not (bajo <= self.valor_secundario <= alto):
                raise ValueError(f"La diastólica debe estar entre {bajo} y {alto}")
            if self.valor_secundario >= self.valor:
                raise ValueError("La diastólica debe ser menor que la sistólica")
        elif self.valor_secundario is not None:
            raise ValueError("Solo la presión usa valor_secundario")
        return self


class IndicadorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    tipo: TipoIndicador
    valor: Decimal
    valor_secundario: Optional[Decimal] = None
    unidad: str
    fuente: str
    medido_en: datetime
    nota: Optional[str] = None
    registrado_por_id: Optional[str] = None


class PuntoSerie(BaseModel):
    medido_en: datetime
    valor: Decimal
    valor_secundario: Optional[Decimal] = None
    fuente: str


class SerieOut(BaseModel):
    """Serie lista para graficar la evolución de un indicador."""
    perfil_id: UUID
    tipo: TipoIndicador
    unidad: str
    desde: date
    hasta: date
    puntos: list[PuntoSerie]
    minimo: Optional[Decimal] = None
    maximo: Optional[Decimal] = None
    promedio: Optional[Decimal] = None


class UltimoIndicadorOut(BaseModel):
    perfil_id: UUID
    ultimos: list[IndicadorOut]   # el más reciente de cada tipo que tenga mediciones


# --- Cumplimiento -----------------------------------------------------------

class CumplimientoParcial(BaseModel):
    total: int
    cumplidas: int
    porcentaje: Optional[float] = None   # None si no hubo actividades exigibles


class CumplimientoDia(CumplimientoParcial):
    fecha: date


class CumplimientoOut(CumplimientoParcial):
    perfil_id: UUID
    desde: date
    hasta: date
    por_categoria: dict[str, CumplimientoParcial]
    por_dia: list[CumplimientoDia]


# --- Botón de asistencia y eventos de seguridad ------------------------------

class AsistenciaCreate(BaseModel):
    """Cuerpo opcional del botón «Necesito ayuda»."""
    mensaje: Optional[str] = Field(default=None, max_length=200)


class EventoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    perfil_nombre: str
    tipo: TipoEvento
    origen: str
    mensaje: str
    creado_en: datetime
    atendido_en: Optional[datetime] = None
    atendido_por_id: Optional[str] = None


# --- Pulsera, posiciones y geocercas ---------------------------------------

class PulseraCreate(BaseModel):
    identificador: str = Field(min_length=3, max_length=64)   # uniqueId en Traccar (p. ej. el IMEI)
    nombre: str = Field(min_length=1, max_length=80)
    modelo: Optional[str] = Field(default=None, max_length=80)


class PulseraUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    modelo: Optional[str] = Field(default=None, max_length=80)
    activa: Optional[bool] = None


class PulseraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    identificador: str
    nombre: str
    modelo: Optional[str] = None
    activa: bool
    bateria_pct: Optional[int] = None
    ultima_conexion: Optional[datetime] = None


class PosicionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitud: float
    longitud: float
    precision_m: Optional[float] = None
    velocidad_kmh: Optional[float] = None
    bateria_pct: Optional[int] = None
    registrada_en: datetime


class UbicacionOut(BaseModel):
    """Última ubicación conocida del perfil y en qué geocercas está."""
    perfil_id: UUID
    pulsera: Optional[PulseraOut] = None
    posicion: Optional[PosicionOut] = None
    dentro_de: list[str] = []


class GeocercaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    radio_m: int = Field(ge=20, le=50000)


class GeocercaUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    latitud: Optional[float] = Field(default=None, ge=-90, le=90)
    longitud: Optional[float] = Field(default=None, ge=-180, le=180)
    radio_m: Optional[int] = Field(default=None, ge=20, le=50000)
    activa: Optional[bool] = None


class GeocercaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    nombre: str
    latitud: float
    longitud: float
    radio_m: int
    activa: bool


# --- Módulo de IA ------------------------------------------------------------

class ConsultaIACreate(BaseModel):
    pregunta: str = Field(min_length=3, max_length=1000)


class ConsultaIAOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    perfil_id: UUID
    pregunta: str
    respuesta: str
    proveedor: str
    creada_en: datetime
    aviso: str = (
        "Orientación general: no reemplaza a un profesional de la salud. "
        "Ante una urgencia llama al 131."
    )
