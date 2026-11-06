"""
Pulsera inteligente (HU 17 y HU 19): posiciones, geocercas y alarmas.

Traccar recibe el GPS de la pulsera y lo reenvía a `POST /traccar/posiciones`.
`registrar_posicion` guarda la lectura y, según lo que trae, crea eventos de seguridad:

- Alarma SOS de la pulsera                    -> evento `sos`.
- Alarma de caída                             -> evento `caida`.
- Alarma de batería baja o batería <= umbral  -> evento `bateria_baja`.
- Salir de una geocerca activa del perfil     -> evento `geocerca_salida`.

`procesar_inactividad` corre dentro del ciclo programado y crea el evento `inactividad`
cuando la pulsera sigue reportando pero no se movió en `INACTIVIDAD_MINUTOS`, solo de día.
Ningún mensaje afirma que haya una emergencia.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.perfil import Perfil
from app.models.pulsera import Geocerca, Posicion, Pulsera
from app.services.eventos import aware, crear_evento
from app.services.geo import dentro, distancia_m
from app.services.tiempo import ahora_local

logger = logging.getLogger("perfil_medico.pulsera")

# Valores del atributo `alarm` de Traccar que nos interesan -> tipo de evento.
ALARMAS = {
    "sos": "sos",
    "falldown": "caida",
    "lowbattery": "bateria_baja",
    "lowpower": "bateria_baja",
}
VENTANA_BATERIA_MINUTOS = 120


def _mensaje(tipo: str, perfil: Perfil, detalle: str = "") -> str:
    nombre = perfil.nombre
    if tipo == "sos":
        return f"La pulsera de {nombre} registró que se presionó el botón SOS."
    if tipo == "caida":
        return f"La pulsera de {nombre} detectó una posible caída."
    if tipo == "bateria_baja":
        return f"La pulsera de {nombre} tiene la batería baja{detalle}."
    if tipo == "inactividad":
        return f"La pulsera de {nombre} no registró movimiento{detalle}."
    return f"{nombre} salió de la zona «{detalle}»."


def registrar_posicion(
    db: Session,
    pulsera: Pulsera,
    latitud: float,
    longitud: float,
    momento: datetime,
    velocidad_kmh: Optional[float] = None,
    precision_m: Optional[float] = None,
    bateria_pct: Optional[int] = None,
    alarma: Optional[str] = None,
) -> dict:
    """Guarda la lectura y crea los eventos que correspondan. Devuelve un resumen."""
    perfil = db.get(Perfil, pulsera.perfil_id)
    momento = aware(momento)
    ultima = (
        db.query(Posicion).filter(Posicion.pulsera_id == pulsera.id)
        .order_by(Posicion.registrada_en.desc()).first()
    )
    # Una lectura vieja que llega tarde se guarda, pero no se compara con las geocercas.
    es_la_mas_reciente = ultima is None or momento >= aware(ultima.registrada_en)

    db.add(Posicion(
        pulsera_id=pulsera.id, latitud=latitud, longitud=longitud, precision_m=precision_m,
        velocidad_kmh=velocidad_kmh, bateria_pct=bateria_pct, registrada_en=momento,
    ))
    if pulsera.ultima_conexion is None or momento >= aware(pulsera.ultima_conexion):
        pulsera.ultima_conexion = momento
        if bateria_pct is not None:
            pulsera.bateria_pct = bateria_pct
    db.commit()

    resumen = {"eventos": 0}
    if perfil is None or perfil.activo is False or not pulsera.activa:
        return resumen

    def evento(tipo: str, mensaje: str, **opciones) -> None:
        _, creado = crear_evento(db, perfil, tipo, "pulsera", mensaje, pulsera=pulsera, **opciones)
        resumen["eventos"] += int(creado)

    tipo_alarma = ALARMAS.get((alarma or "").replace("_", "").lower())
    if tipo_alarma == "sos":
        evento("sos", _mensaje("sos", perfil))
    elif tipo_alarma == "caida":
        evento("caida", _mensaje("caida", perfil))

    bateria_baja = tipo_alarma == "bateria_baja" or (
        bateria_pct is not None and bateria_pct <= settings.BATERIA_BAJA_PORCENTAJE
    )
    if bateria_baja:
        detalle = f" ({bateria_pct} %)" if bateria_pct is not None else ""
        evento("bateria_baja", _mensaje("bateria_baja", perfil, detalle), ventana_minutos=VENTANA_BATERIA_MINUTOS)

    if es_la_mas_reciente and ultima is not None:
        geocercas = db.query(Geocerca).filter(Geocerca.perfil_id == perfil.id, Geocerca.activa.is_(True)).all()
        for g in geocercas:
            estaba = dentro(ultima.latitud, ultima.longitud, g.latitud, g.longitud, g.radio_m)
            esta = dentro(latitud, longitud, g.latitud, g.longitud, g.radio_m)
            if estaba and not esta:
                evento("geocerca_salida", _mensaje("geocerca_salida", perfil, g.nombre), por_mensaje=True)
    return resumen


def geocercas_donde_esta(db: Session, perfil_id, posicion: Posicion) -> list[str]:
    """Nombres de las geocercas activas del perfil que contienen la posición."""
    geocercas = db.query(Geocerca).filter(Geocerca.perfil_id == perfil_id, Geocerca.activa.is_(True)).all()
    return [g.nombre for g in geocercas if dentro(posicion.latitud, posicion.longitud, g.latitud, g.longitud, g.radio_m)]


def procesar_inactividad(db: Session, ahora: Optional[datetime] = None) -> int:
    """Crea eventos de inactividad. Devuelve cuántos creó."""
    ahora = ahora or ahora_local()
    if not (settings.INACTIVIDAD_DESDE_HORA <= ahora.hour < settings.INACTIVIDAD_HASTA_HORA):
        return 0
    ahora_utc = ahora.astimezone(timezone.utc)
    ventana = timedelta(minutes=settings.INACTIVIDAD_MINUTOS)
    creados = 0
    for pulsera in db.query(Pulsera).filter(Pulsera.activa.is_(True)).all():
        perfil = db.get(Perfil, pulsera.perfil_id)
        if perfil is None or perfil.activo is False or pulsera.ultima_conexion is None:
            continue
        # Si la pulsera dejó de reportar hace rato, es falta de señal y no inactividad.
        if aware(pulsera.ultima_conexion) < ahora_utc - timedelta(minutes=30):
            continue
        posiciones = (
            db.query(Posicion)
            .filter(Posicion.pulsera_id == pulsera.id, Posicion.registrada_en >= ahora_utc - ventana)
            .order_by(Posicion.registrada_en)
            .all()
        )
        if len(posiciones) < 2:
            continue
        cubierto = aware(posiciones[-1].registrada_en) - aware(posiciones[0].registrada_en)
        if cubierto < ventana * 0.8:
            continue
        ultima = posiciones[-1]
        if any(distancia_m(p.latitud, p.longitud, ultima.latitud, ultima.longitud) > settings.INACTIVIDAD_RADIO_METROS
               for p in posiciones):
            continue
        horas = settings.INACTIVIDAD_MINUTOS / 60
        detalle = f" en las últimas {horas:g} horas"
        _, creado = crear_evento(
            db, perfil, "inactividad", "sistema", _mensaje("inactividad", perfil, detalle),
            pulsera=pulsera, ventana_minutos=settings.INACTIVIDAD_MINUTOS, ahora=ahora_utc,
        )
        creados += int(creado)
    return creados


def limpiar_posiciones(db: Session, ahora: Optional[datetime] = None) -> int:
    """Borra las posiciones más viejas que `POSICIONES_DIAS_RETENCION`. Devuelve cuántas."""
    ahora = (ahora or datetime.now(timezone.utc)).astimezone(timezone.utc)
    limite = ahora - timedelta(days=settings.POSICIONES_DIAS_RETENCION)
    borradas = db.query(Posicion).filter(Posicion.registrada_en < limite).delete(synchronize_session=False)
    db.commit()
    return borradas
