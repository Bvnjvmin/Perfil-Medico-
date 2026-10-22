"""
Lógica de HU 5 (cierre) y del Sprint 4: generar y leer las actividades de un día.

Las actividades de una fecha se generan por dos caminos: cuando alguien consulta
ese día (agenda o panel) y, desde el Sprint 4, con la tarea programada que las
crea con 24 a 48 h de anticipación (`generar_actividades_programadas`). Por cada
medicamento o rutina activo del perfil se crea, si falta, una actividad pendiente
por cada hora: las de `rutina_horario` si tiene, o su hora única si no. Pedir la
misma fecha varias veces no duplica nada (la base de datos tiene restricciones
únicas por origen, fecha y hora).
"""
from datetime import date, time, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.actividad import Actividad
from app.models.medicamento import Medicamento, RutinaCuidado
from app.models.perfil import Perfil
from app.models.rutina_horario import RutinaHorario
from app.core.config import settings
from app.schemas.actividad import ActividadOut
from app.services.tiempo import hoy_local

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


def _horas_de(origen, horarios: dict) -> list:
    """
    Horas del día del origen: las de `rutina_horario` si tiene; si no, su hora única
    (`hora_inicio` de un medicamento, `hora` de una rutina); y si tampoco, una
    actividad sin hora (`None`).
    """
    horas = sorted(horarios.get(origen.id, []))
    if horas:
        return horas
    unica = origen.hora_inicio if isinstance(origen, Medicamento) else origen.hora
    return [unica]


def _horarios_del_perfil(db: Session, medicamentos: list, rutinas: list) -> dict:
    ids_med = [m.id for m in medicamentos]
    ids_rut = [r.id for r in rutinas]
    filas = []
    if ids_med:
        filas += db.query(RutinaHorario).filter(RutinaHorario.medicamento_id.in_(ids_med)).all()
    if ids_rut:
        filas += db.query(RutinaHorario).filter(RutinaHorario.rutina_id.in_(ids_rut)).all()
    horarios: dict = {}
    for f in filas:
        horarios.setdefault(f.medicamento_id or f.rutina_id, []).append(f.hora)
    return horarios


def asegurar_actividades(db: Session, perfil: Perfil, fecha: date) -> list[ActividadOut]:
    """Crea las actividades que falten para `fecha` y devuelve las del día, ordenadas por hora."""
    medicamentos = db.query(Medicamento).filter(Medicamento.perfil_id == perfil.id).all()
    rutinas = db.query(RutinaCuidado).filter(RutinaCuidado.perfil_id == perfil.id).all()
    horarios = _horarios_del_perfil(db, medicamentos, rutinas)

    existentes = db.query(Actividad).filter(
        Actividad.perfil_id == perfil.id, Actividad.fecha == fecha
    ).all()

    # Lo que debería haber hoy: (tipo de origen, id del origen, hora) por cada origen activo.
    esperadas = []
    for m in medicamentos:
        if m.activo and _existian_en(m, fecha):
            esperadas += [("medicamento", m.id, h) for h in _horas_de(m, horarios)]
    for r in rutinas:
        if r.activo and _existian_en(r, fecha):
            esperadas += [("rutina", r.id, h) for h in _horas_de(r, horarios)]

    def clave(a: Actividad):
        return ("medicamento", a.medicamento_id, a.hora) if a.medicamento_id else ("rutina", a.rutina_id, a.hora)

    claves_existentes = {clave(a) for a in existentes}
    claves_esperadas = set(esperadas)

    # Una actividad pendiente que ya no corresponde (se quitó o cambió el horario) se
    # elimina, pero solo de hoy en adelante: el historial pasado no se toca.
    huerfanas = [
        a for a in existentes
        if a.estado == "pendiente" and clave(a) not in claves_esperadas and fecha >= hoy_local() - timedelta(days=1)
    ]
    for a in huerfanas:
        db.delete(a)

    nuevas = []
    for tipo, origen_id, hora in esperadas:
        if (tipo, origen_id, hora) in claves_existentes:
            continue
        if tipo == "medicamento":
            nuevas.append(Actividad(perfil_id=perfil.id, medicamento_id=origen_id, fecha=fecha, hora=hora, estado="pendiente"))
        else:
            nuevas.append(Actividad(perfil_id=perfil.id, rutina_id=origen_id, fecha=fecha, hora=hora, estado="pendiente"))

    if nuevas or huerfanas:
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
    salida.sort(key=lambda x: (x.hora is None, x.hora or time.min, x.titulo))
    return salida


def generar_actividades_programadas(db: Session) -> int:
    """
    Tarea programada: deja creadas las actividades de hoy y de los días siguientes
    (`GENERAR_DIAS_ADELANTE`, por defecto hoy y mañana) de todos los perfiles activos.
    Devuelve cuántos perfiles recorrió.
    """
    hoy = hoy_local()
    perfiles = db.query(Perfil).filter(Perfil.activo.isnot(False)).all()
    for perfil in perfiles:
        for dias in range(max(settings.GENERAR_DIAS_ADELANTE, 1)):
            asegurar_actividades(db, perfil, hoy + timedelta(days=dias))
    return len(perfiles)


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
        hora=actividad.hora if actividad.hora is not None else hora,
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
