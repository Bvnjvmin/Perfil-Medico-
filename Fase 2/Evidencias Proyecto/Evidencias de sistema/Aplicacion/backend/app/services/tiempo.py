"""Hora y fecha de Chile (o la zona configurada), independientes de la zona del servidor."""
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.core.config import settings


def zona() -> ZoneInfo:
    return ZoneInfo(settings.ZONA_HORARIA)


def ahora_local() -> datetime:
    """Hora actual con zona horaria (la del .env, por defecto America/Santiago)."""
    return datetime.now(zona())


def hoy_local() -> date:
    return ahora_local().date()


def momento(fecha: date, hora: time) -> datetime:
    """La fecha y hora de una actividad como momento con zona horaria."""
    return datetime.combine(fecha, hora.replace(tzinfo=None), tzinfo=zona())
