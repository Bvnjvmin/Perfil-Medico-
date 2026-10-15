"""
Lógica de HU 5 (cierre): generar y leer las actividades de un día.

Las actividades de una fecha NO se crean con un job programado: se generan
cuando alguien consulta ese día (agenda o panel). Por cada medicamento o
rutina activo del perfil se crea, si falta, una actividad pendiente. Pedir la
misma fecha varias veces no duplica nada (la base de datos tiene restricciones
únicas por medicamento+fecha y rutina+fecha).
"""
from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.actividad import Actividad
from app.models.medicamento import Medicamento, RutinaCuidado
from app.models.perfil import Perfil
from app.schemas.actividad import ActividadOut

_TIPOS_RUTINA = {
    "alimentacion": "Alimentación",
    "hidratacion": "Hidratación",
    "vitaminas": "Vitaminas",
}


def _tipo_legible(tipo: str) -> str:
    return _TIPOS_RUTINA.get(tipo, tipo.replace("_", " ").capitalize())


def _existian_en(origen, fecha: date) -> bool:
    """
    No se generan actividades para días anteriores a la creación del
    medicamento o rutina (con un día de holgura por la zona horaria: la fecha
    guardada está en UTC y la de la agenda es la del celular).
    """
    creado = getattr(origen, "creado_en", None)
    return creado is None or fecha >= creado.date() - timedelta(days=1)


def asegurar_actividades(db: Session, perfil: Perfil, fecha: date) -> list[ActividadOut]:
    """Crea las actividades que falten para `fecha` y devuelve las del día, ordenadas por hora."""
    medicamentos = db.query(Medicamento).filter(Medicamento.perfil_id == perfil.id).all()
    rutinas = db.query(RutinaCuidado).filter(RutinaCuidado.perfil_id == perfil.id).all()

    existentes = db.query(Actividad).filter(
        Actividad.perfil_id == perfil.id, Actividad.fecha == fecha
    ).all()
    con_actividad_med = {a.medicamento_id for a in existentes if a.medicamento_id}
    con_actividad_rut = {a.rutina_id for a in existentes if a.rutina_id}

    nuevas = [
        Actividad(perfil_id=perfil.id, medicamento_id=m.id, fecha=fecha, estado="pendiente")
        for m in medicamentos
        if m.activo and m.id not in con_actividad_med and _existian_en(m, fecha)
    ] + [
        Actividad(perfil_id=perfil.id, rutina_id=r.id, fecha=fecha, estado="pendiente")
        for r in rutinas
        if r.activo and r.id not in con_actividad_rut and _existian_en(r, fecha)
    ]
    if nuevas:
        db.add_all(nuevas)
        try:
            db.commit()
        except IntegrityError:
            # Otra consulta del mismo día se adelantó: las restricciones únicas
            # evitaron el duplicado; se descartan las nuestras y se relee.
            db.rollback()

    actividades = db.query(Actividad).filter(
        Actividad.perfil_id == perfil.id, Actividad.fecha == fecha
    ).all()
    por_medicamento = {m.id: m for m in medicamentos}
    por_rutina = {r.id: r for r in rutinas}

    salida = []
    for a in actividades:
        out = construir_actividad_out(a, por_medicamento, por_rutina)
        if out is not None:
            salida.append(out)
    # Por hora; las que no tienen hora van al final.
    salida.sort(key=lambda x: (x.hora is None, x.hora, x.titulo))
    return salida


def construir_actividad_out(actividad: Actividad, por_medicamento: dict, por_rutina: dict):
    """
    Arma la respuesta de una actividad leyendo los textos de su medicamento o
    rutina. Devuelve None si el origen está inactivo o ya no existe (por
    ejemplo, se desactivó después de generar la actividad).
    """
    if actividad.medicamento_id is not None:
        m = por_medicamento.get(actividad.medicamento_id)
        if m is None or not m.activo:
            return None
        origen_tipo, origen_id = "medicamento", m.id
        titulo, detalle, hora = m.nombre, f"{m.dosis} · {m.frecuencia}", m.hora_inicio
    else:
        r = por_rutina.get(actividad.rutina_id)
        if r is None or not r.activo:
            return None
        origen_tipo, origen_id = "rutina", r.id
        titulo = r.descripcion or _tipo_legible(r.tipo)
        detalle, hora = f"{_tipo_legible(r.tipo)} · {r.frecuencia}", r.hora

    return ActividadOut(
        id=actividad.id,
        perfil_id=actividad.perfil_id,
        fecha=actividad.fecha,
        origen_tipo=origen_tipo,
        origen_id=origen_id,
        titulo=titulo,
        detalle=detalle,
        hora=hora,
        estado=actividad.estado,
        confirmada_en=actividad.confirmada_en,
        confirmada_por_id=actividad.confirmada_por_id,
    )


def actividad_out_desde_bd(db: Session, actividad: Actividad):
    """Respuesta de una sola actividad (usada al confirmar o desconfirmar)."""
    por_medicamento, por_rutina = {}, {}
    if actividad.medicamento_id is not None:
        m = db.get(Medicamento, actividad.medicamento_id)
        por_medicamento = {m.id: m} if m else {}
    else:
        r = db.get(RutinaCuidado, actividad.rutina_id)
        por_rutina = {r.id: r} if r else {}
    return construir_actividad_out(actividad, por_medicamento, por_rutina)
