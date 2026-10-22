"""
Lógica de HU 9 y HU 10: recordatorios y alertas escalonadas.

`procesar_avisos` corre cada minuto (ver app/main.py) y, para cada actividad
pendiente de hoy con hora, crea los avisos que correspondan según cuánto falta
o cuánto pasó desde su hora:

- Recordatorio (nivel 0, HU 9): desde `RECORDATORIO_MINUTOS_ANTES` antes de la
  hora y hasta el primer plazo. Va al titular y a los vinculados con `recibe_alertas`.
- Alerta de nivel 1 (HU 10): pasados `ALERTA_PLAZO_1_MINUTOS` sin confirmar. Va al
  titular y a los vinculados con `recibe_alertas` y `nivel_escalamiento = 1`.
- Alerta de nivel 2 (HU 10): pasados `ALERTA_PLAZO_2_MINUTOS`. Va a los vinculados con
  `recibe_alertas` y `nivel_escalamiento = 2`.

Confirmar la actividad detiene el escalamiento (solo se miran las pendientes). Un
mismo aviso no se repite aunque la tarea corra muchas veces: la tabla `alerta` tiene
una restricción única por actividad, usuario, tipo y nivel. Cuando termina el día, las
actividades que siguen pendientes pasan a 'vencida'. Los mensajes informan que la
actividad no fue confirmada; no afirman que haya una emergencia.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.actividad import Actividad
from app.models.alerta import Alerta
from app.models.dispositivo_push import DispositivoPush
from app.models.perfil import Perfil
from app.models.perfil_acceso import PerfilAcceso
from app.services.actividades import actividad_out_desde_bd
from app.services.notificador import obtener_notificador
from app.services.tiempo import ahora_local, momento

logger = logging.getLogger("perfil_medico.alertas")


def _destinatarios(db: Session, perfil: Perfil, nivel: int) -> list[str]:
    """Ids de los usuarios que deben recibir el aviso de ese nivel."""
    vinculos = (
        db.query(PerfilAcceso)
        .filter(PerfilAcceso.perfil_id == perfil.id, PerfilAcceso.recibe_alertas.is_(True))
        .all()
    )
    if nivel == 0:
        ids = [perfil.cuenta_titular_id] + [v.usuario_id for v in vinculos]
    elif nivel == 1:
        ids = [perfil.cuenta_titular_id] + [v.usuario_id for v in vinculos if v.nivel_escalamiento == 1]
    else:
        ids = [v.usuario_id for v in vinculos if v.nivel_escalamiento == nivel]
    return list(dict.fromkeys(ids))  # sin repetidos, en orden


def _mensaje(nivel: int, titulo: str, perfil: Perfil, hora_txt: str) -> str:
    if nivel == 0:
        return f"Recordatorio: «{titulo}» de {perfil.nombre} es a las {hora_txt}."
    base = f"La actividad «{titulo}» de {perfil.nombre} (programada a las {hora_txt}) aún no fue confirmada."
    return base if nivel == 1 else base + " Sigue sin confirmarse."


def _crear_avisos(db: Session, actividad: Actividad, perfil: Perfil, titulo: str, nivel: int, hora_txt: str) -> list[Alerta]:
    destinatarios = _destinatarios(db, perfil, nivel)
    if not destinatarios:
        return []
    tipo = "recordatorio" if nivel == 0 else "alerta"
    ya = {
        a.usuario_id
        for a in db.query(Alerta).filter(
            Alerta.actividad_id == actividad.id, Alerta.tipo == tipo, Alerta.nivel == nivel
        )
    }
    nuevas = [
        Alerta(
            actividad_id=actividad.id, usuario_id=u, tipo=tipo, nivel=nivel,
            mensaje=_mensaje(nivel, titulo, perfil, hora_txt),
        )
        for u in destinatarios
        if u not in ya
    ]
    db.add_all(nuevas)
    return nuevas


def _enviar(db: Session, avisos: list[Alerta], actividad: Actividad) -> None:
    """Pasa los avisos recién creados al notificador, con los dispositivos de cada usuario."""
    notificador = obtener_notificador()
    for aviso in avisos:
        tokens = [
            d.token for d in db.query(DispositivoPush).filter(DispositivoPush.usuario_id == aviso.usuario_id)
        ]
        if not tokens:
            continue
        titulo = "Recordatorio" if aviso.tipo == "recordatorio" else "Actividad sin confirmar"
        try:
            notificador.enviar(
                tokens, titulo, aviso.mensaje,
                {"tipo": aviso.tipo, "nivel": aviso.nivel, "perfil_id": str(actividad.perfil_id),
                 "actividad_id": str(actividad.id)},
            )
        except Exception:  # un fallo de envío no debe detener al resto de los avisos
            logger.exception("No se pudo enviar el aviso %s", aviso.id)


def procesar_avisos(db: Session, ahora: Optional[datetime] = None) -> dict:
    """
    Marca como vencidas las actividades de días anteriores y crea los recordatorios y
    alertas que correspondan a `ahora` (por defecto, la hora actual de Chile). Devuelve
    un resumen con las cantidades, útil para el log y las pruebas.
    """
    ahora = ahora or ahora_local()
    hoy = ahora.date()

    vencidas = (
        db.query(Actividad)
        .filter(Actividad.estado == "pendiente", Actividad.fecha < hoy)
        .update({"estado": "vencida"}, synchronize_session=False)
    )
    db.commit()

    resumen = {"vencidas": vencidas, "recordatorios": 0, "alertas": 0}
    pendientes = (
        db.query(Actividad)
        .filter(Actividad.estado == "pendiente", Actividad.fecha == hoy, Actividad.hora.isnot(None))
        .all()
    )
    for actividad in pendientes:
        origen = actividad_out_desde_bd(db, actividad)
        if origen is None:  # su medicamento o rutina está inactivo o ya no existe
            continue
        perfil = db.get(Perfil, actividad.perfil_id)
        if perfil is None or perfil.activo is False:
            continue

        minutos = (ahora - momento(actividad.fecha, actividad.hora)).total_seconds() / 60
        hora_txt = actividad.hora.strftime("%H:%M")
        creados: list[Alerta] = []
        if -settings.RECORDATORIO_MINUTOS_ANTES <= minutos < settings.ALERTA_PLAZO_1_MINUTOS:
            nuevos = _crear_avisos(db, actividad, perfil, origen.titulo, 0, hora_txt)
            resumen["recordatorios"] += len(nuevos)
            creados += nuevos
        if minutos >= settings.ALERTA_PLAZO_1_MINUTOS:
            nuevos = _crear_avisos(db, actividad, perfil, origen.titulo, 1, hora_txt)
            resumen["alertas"] += len(nuevos)
            creados += nuevos
        if minutos >= settings.ALERTA_PLAZO_2_MINUTOS:
            nuevos = _crear_avisos(db, actividad, perfil, origen.titulo, 2, hora_txt)
            resumen["alertas"] += len(nuevos)
            creados += nuevos
        if creados:
            db.commit()
            _enviar(db, creados, actividad)
    return resumen


def ejecutar_ciclo(db: Session) -> dict:
    """Un ciclo de la tarea programada: generar actividades y procesar avisos."""
    from app.services.actividades import generar_actividades_programadas

    perfiles = generar_actividades_programadas(db)
    resumen = procesar_avisos(db)
    resumen["perfiles"] = perfiles
    return resumen
