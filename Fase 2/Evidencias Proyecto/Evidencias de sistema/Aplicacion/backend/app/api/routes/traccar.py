"""
Entrada de posiciones desde el servidor Traccar (HU 17 y HU 19).

GET/POST /traccar/posiciones

Traccar recibe el GPS de la pulsera y lo reenvía aquí (`forward.url` en su configuración, ver la
guía de Traccar del Sprint 5). Se aceptan dos formatos, porque depende de cómo se configure el reenvío:

1. JSON (`forward.type = json`): {"position": {...}, "device": {"uniqueId": "..."}}; la velocidad
   de Traccar viene en nudos y la hora en `fixTime` (ISO 8601).
2. Parámetros en la URL, estilo OsmAnd: `id`, `lat`, `lon`, `timestamp`, `speed`, `batt`, `alarm`, `accuracy`.

Autenticación: la clave compartida `TRACCAR_TOKEN` en el parámetro `token` o en el encabezado
`X-Traccar-Token`. Si `TRACCAR_TOKEN` está vacío, la ruta está apagada (503). La pulsera debe estar
registrada en el perfil (`POST /perfiles/{id}/pulseras`) con el mismo identificador que usa Traccar.
"""
import hmac
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.pulsera import Pulsera
from app.services.pulsera import registrar_posicion

router = APIRouter(tags=["Integración Traccar"])

NUDOS_A_KMH = 1.852


def _numero(valor: Any) -> Optional[float]:
    try:
        return float(valor) if valor not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _momento(valor: Any) -> datetime:
    """Acepta ISO 8601 o segundos/milisegundos desde 1970; si no hay, el momento actual."""
    if valor in (None, ""):
        return datetime.now(timezone.utc)
    try:
        numero = float(valor)
        return datetime.fromtimestamp(numero / 1000 if numero > 1e11 else numero, tz=timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        momento = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)
    return momento if momento.tzinfo else momento.replace(tzinfo=timezone.utc)


def extraer_lectura(params: dict, cuerpo: Optional[dict]) -> dict:
    """Normaliza los dos formatos a un solo diccionario con las claves que usa el servicio."""
    posicion = (cuerpo or {}).get("position") or (cuerpo or {})
    dispositivo = (cuerpo or {}).get("device") or {}
    atributos = posicion.get("attributes") or {}
    bruta = {**params}  # parámetros de la URL
    identificador = (
        dispositivo.get("uniqueId") or posicion.get("uniqueId") or bruta.get("id")
        or bruta.get("uniqueId") or bruta.get("deviceid")
    )
    velocidad_nudos = _numero(posicion.get("speed", bruta.get("speed")))
    bateria = _numero(atributos.get("batteryLevel", bruta.get("batt", bruta.get("batteryLevel"))))
    return {
        "identificador": str(identificador).strip() if identificador else None,
        "latitud": _numero(posicion.get("latitude", bruta.get("lat"))),
        "longitud": _numero(posicion.get("longitude", bruta.get("lon"))),
        "momento": _momento(
            posicion.get("fixTime") or posicion.get("deviceTime") or bruta.get("timestamp") or bruta.get("fixTime")
        ),
        "velocidad_kmh": round(velocidad_nudos * NUDOS_A_KMH, 1) if velocidad_nudos is not None else None,
        "precision_m": _numero(posicion.get("accuracy", bruta.get("accuracy"))),
        "bateria_pct": int(round(bateria)) if bateria is not None and 0 <= bateria <= 100 else None,
        "alarma": atributos.get("alarm") or bruta.get("alarm"),
    }


@router.post("/traccar/posiciones")
async def recibir_posicion_post(
    request: Request,
    db: Session = Depends(get_db),
    x_traccar_token: Optional[str] = Header(default=None),
):
    """Reenvío en JSON (o con parámetros en la URL)."""
    return await _procesar(request, db, x_traccar_token)


@router.get("/traccar/posiciones")
async def recibir_posicion_get(
    request: Request,
    db: Session = Depends(get_db),
    x_traccar_token: Optional[str] = Header(default=None),
):
    """Reenvío con parámetros en la URL (estilo OsmAnd)."""
    return await _procesar(request, db, x_traccar_token)


async def _procesar(request: Request, db: Session, x_traccar_token: Optional[str]) -> dict:
    if not settings.TRACCAR_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="La integración con Traccar está desactivada")
    params = dict(request.query_params)
    enviado = x_traccar_token or params.pop("token", None) or ""
    params.pop("token", None)
    if not hmac.compare_digest(enviado.encode(), settings.TRACCAR_TOKEN.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Traccar inválido")

    cuerpo = None
    if request.method == "POST" and await request.body():
        try:
            cuerpo = await request.json()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El cuerpo no es un JSON válido")
        if not isinstance(cuerpo, dict):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El cuerpo debe ser un objeto JSON")

    lectura = extraer_lectura(params, cuerpo)
    if not lectura["identificador"]:
        raise HTTPException(status_code=422, detail="Falta el identificador de la pulsera")
    lat, lon = lectura["latitud"], lectura["longitud"]
    if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(status_code=422, detail="Faltan las coordenadas o son inválidas")

    pulsera = db.query(Pulsera).filter(Pulsera.identificador == lectura["identificador"]).first()
    if pulsera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pulsera no registrada")

    resumen = registrar_posicion(
        db, pulsera, latitud=lat, longitud=lon, momento=lectura["momento"],
        velocidad_kmh=lectura["velocidad_kmh"], precision_m=lectura["precision_m"],
        bateria_pct=lectura["bateria_pct"], alarma=lectura["alarma"],
    )
    return {"ok": True, **resumen}
