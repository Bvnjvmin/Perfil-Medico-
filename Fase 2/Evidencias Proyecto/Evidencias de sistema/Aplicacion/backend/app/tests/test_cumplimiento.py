"""Pruebas de HU 13: historial de cumplimiento."""
from datetime import date, time, timedelta
from uuid import UUID

from app.models.actividad import Actividad
from app.models.perfil import Perfil
from app.services.cumplimiento import calcular
from app.tests.conftest import TestingSessionLocal
from app.tests.helpers import actividades, crear_medicamento, crear_rutina, headers
from app.tests.helpers_s5 import a, escenario, hoy


def _ayer() -> date:
    return hoy() - timedelta(days=1)


def _calcular(pid, desde, hasta, ahora):
    db = TestingSessionLocal()
    try:
        return calcular(db, db.get(Perfil, UUID(pid)), desde, hasta, ahora)
    finally:
        db.close()


def _con_dos_actividades(client, prefijo):
    e = escenario(client, prefijo)
    e["med"] = crear_medicamento(client, e["titular"], e["pid"], "Losartán", "08:00:00")
    e["rut"] = crear_rutina(client, e["titular"], e["pid"], tipo="hidratacion", descripcion="Vaso de agua", hora="09:00:00")
    return e


def _actividades_de_ayer(e) -> list:
    """
    Crea directamente en la base las actividades de ayer (a las 08:00 y 09:00). Por la API no se
    generan días pasados cuando la fecha UTC ya cambió, y aquí solo importa cómo se calcula.
    """
    db = TestingSessionLocal()
    try:
        filas = [
            Actividad(perfil_id=UUID(e["pid"]), medicamento_id=UUID(e["med"]["id"]), fecha=_ayer(), hora=time(8), estado="pendiente"),
            Actividad(perfil_id=UUID(e["pid"]), rutina_id=UUID(e["rut"]["id"]), fecha=_ayer(), hora=time(9), estado="pendiente"),
        ]
        db.add_all(filas)
        db.commit()
        return [(f.id, f.estado) for f in filas]
    finally:
        db.close()


def _estado(actividad_id, estado):
    db = TestingSessionLocal()
    try:
        db.get(Actividad, actividad_id).estado = estado
        db.commit()
    finally:
        db.close()


def test_cumplimiento_de_un_dia_anterior_por_categoria(client):
    e = _con_dos_actividades(client, "cum1")
    medicamento, _ = _actividades_de_ayer(e)
    _estado(medicamento[0], "confirmada")
    r = _calcular(e["pid"], _ayer(), _ayer(), a(12))
    assert (r["total"], r["cumplidas"], r["porcentaje"]) == (2, 1, 50.0)
    assert r["por_categoria"]["medicamentos"] == {"total": 1, "cumplidas": 1, "porcentaje": 100.0}
    assert r["por_categoria"]["hidratacion"] == {"total": 1, "cumplidas": 0, "porcentaje": 0.0}
    assert r["por_categoria"]["alimentacion"]["porcentaje"] is None
    assert r["por_dia"] == [{"fecha": _ayer(), "total": 2, "cumplidas": 1, "porcentaje": 50.0}]


def test_una_actividad_de_hoy_con_la_hora_por_venir_no_cuenta(client):
    e = _con_dos_actividades(client, "cum2")
    actividades(client, e["titular"], e["pid"], hoy().isoformat())
    r = _calcular(e["pid"], hoy(), hoy(), a(7, 0))
    assert r["total"] == 0 and r["porcentaje"] is None


def test_una_actividad_de_hoy_con_la_hora_pasada_sin_confirmar_cuenta_como_no_cumplida(client):
    e = _con_dos_actividades(client, "cum3")
    actividades(client, e["titular"], e["pid"], hoy().isoformat())
    r = _calcular(e["pid"], hoy(), hoy(), a(12))
    assert (r["total"], r["cumplidas"], r["porcentaje"]) == (2, 0, 0.0)
    # A las 08:30 solo venció la de las 08:00.
    assert _calcular(e["pid"], hoy(), hoy(), a(8, 30))["total"] == 1


def test_vencida_cuenta_y_omitida_no(client):
    e = _con_dos_actividades(client, "cum4")
    primera, segunda = _actividades_de_ayer(e)
    _estado(primera[0], "vencida")
    _estado(segunda[0], "omitida")
    r = _calcular(e["pid"], _ayer(), _ayer(), a(12))
    assert (r["total"], r["cumplidas"]) == (1, 0)


def test_endpoint_de_cumplimiento(client):
    e = _con_dos_actividades(client, "cum5")
    del_dia = actividades(client, e["titular"], e["pid"], hoy().isoformat()).json()
    medicamento = next(x for x in del_dia if x["origen_tipo"] == "medicamento")
    client.post(f"/actividades/{medicamento['id']}/confirmar", headers=headers(e["titular"]))
    r = client.get(f"/perfiles/{e['pid']}/cumplimiento", headers=headers(e["titular"]))
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    assert cuerpo["cumplidas"] == 1 and cuerpo["por_categoria"]["medicamentos"]["cumplidas"] == 1
    assert cuerpo["hasta"] == hoy().isoformat()
    assert cuerpo["desde"] == (hoy() - timedelta(days=6)).isoformat()
    # El cuidador (sin permiso de indicadores) también lo ve: es lo mismo que ya ve en la agenda.
    assert client.get(f"/perfiles/{e['pid']}/cumplimiento", headers=headers(e["cuidador"])).status_code == 200
    assert client.get(f"/perfiles/{e['pid']}/cumplimiento", headers=headers(e["ajena"])).status_code == 404


def test_rangos_invalidos(client):
    e = escenario(client, "cum6")
    url = f"/perfiles/{e['pid']}/cumplimiento"
    assert client.get(url, params={"desde": "2026-11-05", "hasta": "2026-11-01"}, headers=headers(e["titular"])).status_code == 400
    assert client.get(url, params={"desde": "2026-01-01", "hasta": "2026-11-01"}, headers=headers(e["titular"])).status_code == 400
    sin_datos = client.get(url, headers=headers(e["titular"])).json()
    assert sin_datos["total"] == 0 and sin_datos["porcentaje"] is None
