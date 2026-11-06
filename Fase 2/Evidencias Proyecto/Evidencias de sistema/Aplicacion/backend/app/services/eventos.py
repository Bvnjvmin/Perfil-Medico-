"""
Eventos de seguridad (HU 14 y HU 19): botón «Necesito ayuda» y alarmas de la pulsera.

`crear_evento` guarda el evento, evita repetirlo dentro de una ventana de tiempo
y avisa al titular y a los cuidadores con `recibe_alertas` por el notificador
(los mismos dispositivos registrados en HU 9). Los mensajes informan lo que se
detectó; no afirman que haya una emergencia.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.dispositivo_push import DispositivoPush
from app.models.evento_seguridad import EventoSeguridad
from app.models.perfil import Perfil
from app.models.perfil_acceso import PerfilAcceso
from app.models.pulsera import Pulsera
from app.services.notificador import obtener_notificador

logger = logging.getLogger("perfil_medico.eventos")

TITULOS = {
    "asistencia": "Pidieron ayuda",
    "sos": "Botón SOS de la pulsera",
    "caida": "Posible caída",
    "bateria_baja": "Batería baja de la pulsera",
    "inactividad": "Sin movimiento",
    "geocerca_salida": "Salió de una zona",
}


def aware(momento: datetime) -> datetime:
    """SQLite devuelve fechas sin zona; en la base real siempre vienen en UTC."""
    return momento if momento.tzinfo else momento.replace(tzinfo=timezone.utc)


def destinatarios(db: Session, perfil: Perfil) -> list[str]:
    """Titular y cuidadores con `recibe_alertas`, sin repetidos y en orden."""
    vinculados = (
        db.query(PerfilAcceso.usuario_id)
        .filter(PerfilAcceso.perfil_id == perfil.id, PerfilAcceso.recibe_alertas.is_(True))
        .all()
    )
    return list(dict.fromkeys([perfil.cuenta_titular_id] + [u for (u,) in vinculados]))


def crear_evento(
    db: Session,
    perfil: Perfil,
    tipo: str,
    origen: str,
    mensaje: str,
    pulsera: Optional[Pulsera] = None,
    creado_por_id: Optional[str] = None,
    ventana_minutos: Optional[int] = None,
    por_mensaje: bool = False,
    ahora: Optional[datetime] = None,
) -> tuple[EventoSeguridad, bool]:
    """
    Crea el evento y avisa. Si ya hay uno igual del mismo perfil dentro de la ventana
    devuelve ese (`creado = False`) y no avisa otra vez. `por_mensaje` exige además el
    mismo mensaje (así dos geocercas distintas no se confunden).
    """
    ahora = ahora or datetime.now(timezone.utc)
    ventana = settings.EVENTO_VENTANA_DEDUP_MINUTOS if ventana_minutos is None else ventana_minutos
    consulta = db.query(EventoSeguridad).filter(
        EventoSeguridad.perfil_id == perfil.id,
        EventoSeguridad.tipo == tipo,
        EventoSeguridad.creado_en >= ahora - timedelta(minutes=ventana),
    )
    if por_mensaje:
        consulta = consulta.filter(EventoSeguridad.mensaje == mensaje)
    previo = consulta.order_by(EventoSeguridad.creado_en.desc()).first()
    if previo is not None:
        return previo, False

    evento = EventoSeguridad(
        perfil_id=perfil.id, pulsera_id=pulsera.id if pulsera else None, tipo=tipo,
        origen=origen, mensaje=mensaje, creado_en=ahora, creado_por_id=creado_por_id,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    _avisar(db, perfil, evento, excluir=creado_por_id)
    return evento, True


def _avisar(db: Session, perfil: Perfil, evento: EventoSeguridad, excluir: Optional[str]) -> None:
    ids = [u for u in destinatarios(db, perfil) if u != excluir]
    if not ids:
        return
    tokens = [d.token for d in db.query(DispositivoPush).filter(DispositivoPush.usuario_id.in_(ids))]
    if not tokens:
        return
    try:
        obtener_notificador().enviar(
            tokens, TITULOS.get(evento.tipo, "Aviso"), evento.mensaje,
            {"tipo": evento.tipo, "evento_id": str(evento.id), "perfil_id": str(perfil.id)},
        )
    except Exception:  # un fallo de envío no debe perder el evento ya guardado
        logger.exception("No se pudo enviar el evento %s", evento.id)
