"""Pruebas de HU 17 y HU 19: pulsera, ubicación, geocercas, alarmas e inactividad."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.evento_seguridad import EventoSeguridad
from app.models.perfil import Perfil
from app.models.pulsera import Posicion, Pulsera
from app.services import pulsera as servicio
from app.services.alertas import ejecutar_ciclo
from app.tests.conftest import TestingSessionLocal
from app.tests.helpers import headers
from app.tests.helpers_s5 import CLAVE_TRACCAR, a, activar_traccar, enviar_posicion, escenario, registrar_pulsera

CASA = (-33.4489, -70.6693)          # centro de la geocerca de prueba
LEJOS = (-33.4400, -70.6693)         # ~990 m al norte


def _eventos_bd():
    db = TestingSessionLocal()
    try:
        return [(x.tipo, x.origen, x.mensaje) for x in db.query(EventoSeguridad).order_by(EventoSeguridad.creado_en)]
    finally:
        db.close()


def _crear_geocerca(client, token, pid, nombre="Casa", radio=100, lat=CASA[0], lon=CASA[1]):
    return client.post(
        f"/perfiles/{pid}/geocercas",
        json={"nombre": nombre, "latitud": lat, "longitud": lon, "radio_m": radio},
        headers=headers(token),
    )


# --- Pulsera ---------------------------------------------------------------------

def test_registrar_pulsera_y_permisos(client):
    e = escenario(client, "pul1", puede_ver_indicadores=True)
    r = registrar_pulsera(client, e["titular"], e["pid"])
    assert r.status_code == 201 and r.json()["activa"] is True and r.json()["bateria_pct"] is None
    assert registrar_pulsera(client, e["titular"], e["pid"]).status_code == 409           # identificador repetido
    assert registrar_pulsera(client, e["cuidador"], e["pid"], "999999999").status_code == 403  # solo el titular
    assert registrar_pulsera(client, e["ajena"], e["pid"], "888888888").status_code == 404
    assert len(client.get(f"/perfiles/{e['pid']}/pulseras", headers=headers(e["cuidador"])).json()) == 1


def test_el_cuidador_sin_permiso_no_ve_las_pulseras(client):
    e = escenario(client, "pul2")
    assert client.get(f"/perfiles/{e['pid']}/pulseras", headers=headers(e["cuidador"])).status_code == 403
    assert client.get(f"/perfiles/{e['pid']}/ubicacion", headers=headers(e["cuidador"])).status_code == 403


def test_actualizar_y_quitar_pulsera(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "pul3")
    p = registrar_pulsera(client, e["titular"], e["pid"]).json()
    r = client.patch(f"/perfiles/{e['pid']}/pulseras/{p['id']}", json={"nombre": "Reloj de Rosa"}, headers=headers(e["titular"]))
    assert r.status_code == 200 and r.json()["nombre"] == "Reloj de Rosa"
    enviar_posicion(client)
    db = TestingSessionLocal()
    assert db.query(Posicion).count() == 1
    db.close()
    assert client.delete(f"/perfiles/{e['pid']}/pulseras/{p['id']}", headers=headers(e["titular"])).status_code == 204
    db = TestingSessionLocal()
    assert db.query(Posicion).count() == 0 and db.query(Pulsera).count() == 0
    db.close()
    assert client.delete(f"/perfiles/{e['pid']}/pulseras/{p['id']}", headers=headers(e["titular"])).status_code == 404


# --- Geocercas -------------------------------------------------------------------

def test_crud_de_geocercas(client):
    e = escenario(client, "geo1", puede_ver_indicadores=True)
    g = _crear_geocerca(client, e["titular"], e["pid"])
    assert g.status_code == 201 and g.json()["radio_m"] == 100 and g.json()["activa"] is True
    assert _crear_geocerca(client, e["titular"], e["pid"]).status_code == 409                  # nombre repetido
    assert _crear_geocerca(client, e["titular"], e["pid"], nombre="Mini", radio=5).status_code == 422
    assert _crear_geocerca(client, e["titular"], e["pid"], nombre="Polo", lat=95).status_code == 422
    assert _crear_geocerca(client, e["cuidador"], e["pid"], nombre="Colegio").status_code == 403
    assert len(client.get(f"/perfiles/{e['pid']}/geocercas", headers=headers(e["cuidador"])).json()) == 1
    gid = g.json()["id"]
    r = client.patch(f"/perfiles/{e['pid']}/geocercas/{gid}", json={"radio_m": 250, "activa": False}, headers=headers(e["titular"]))
    assert r.json()["radio_m"] == 250 and r.json()["activa"] is False
    _crear_geocerca(client, e["titular"], e["pid"], nombre="Colegio")
    choque = client.patch(f"/perfiles/{e['pid']}/geocercas/{gid}", json={"nombre": "Colegio"}, headers=headers(e["titular"]))
    assert choque.status_code == 409
    assert client.delete(f"/perfiles/{e['pid']}/geocercas/{gid}", headers=headers(e["titular"])).status_code == 204
    assert client.delete(f"/perfiles/{e['pid']}/geocercas/{gid}", headers=headers(e["titular"])).status_code == 404


def test_limite_de_geocercas(client):
    e = escenario(client, "geo2")
    for i in range(20):
        assert _crear_geocerca(client, e["titular"], e["pid"], nombre=f"Zona {i}").status_code == 201
    assert _crear_geocerca(client, e["titular"], e["pid"], nombre="Una más").status_code == 400


# --- Entrada desde Traccar --------------------------------------------------------

def test_traccar_apagado_sin_token_configurado(client):
    assert client.get("/traccar/posiciones", params={"token": "x", "id": "1", "lat": 1, "lon": 1}).status_code == 503


def test_traccar_rechaza_token_incorrecto_y_datos_incompletos(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "tra1")
    registrar_pulsera(client, e["titular"], e["pid"])
    assert client.get("/traccar/posiciones", params={"token": "otra", "id": "356938035643809", "lat": 1, "lon": 1}).status_code == 401
    assert client.get("/traccar/posiciones", params={"id": "356938035643809", "lat": 1, "lon": 1}).status_code == 401
    assert client.get("/traccar/posiciones", params={"token": CLAVE_TRACCAR, "lat": 1, "lon": 1}).status_code == 422   # sin id
    assert client.get("/traccar/posiciones", params={"token": CLAVE_TRACCAR, "id": "356938035643809"}).status_code == 422  # sin coordenadas
    assert enviar_posicion(client, lat=95).status_code == 422
    assert enviar_posicion(client, identificador="no-existe").status_code == 404
    assert client.post("/traccar/posiciones", params={"token": CLAVE_TRACCAR}, content=b"no es json",
                       headers={"content-type": "application/json"}).status_code == 400


def test_traccar_formato_json_con_nudos_y_bateria(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "tra2", puede_ver_indicadores=True)
    registrar_pulsera(client, e["titular"], e["pid"])
    cuerpo = {
        "position": {"latitude": CASA[0], "longitude": CASA[1], "speed": 10.0, "accuracy": 12,
                     "fixTime": "2026-11-05T15:00:00.000+00:00", "attributes": {"batteryLevel": 80}},
        "device": {"uniqueId": "356938035643809", "name": "Rosa"},
    }
    r = client.post("/traccar/posiciones", params={"token": CLAVE_TRACCAR}, json=cuerpo)
    assert r.status_code == 200 and r.json() == {"ok": True, "eventos": 0}
    u = client.get(f"/perfiles/{e['pid']}/ubicacion", headers=headers(e["cuidador"])).json()
    assert u["posicion"]["velocidad_kmh"] == 18.5 and u["posicion"]["bateria_pct"] == 80
    assert u["posicion"]["registrada_en"].startswith("2026-11-05T15:00:00")
    assert u["pulsera"]["bateria_pct"] == 80 and u["pulsera"]["ultima_conexion"] is not None


def test_traccar_acepta_el_token_en_el_encabezado(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "tra3")
    registrar_pulsera(client, e["titular"], e["pid"])
    r = client.get("/traccar/posiciones", params={"id": "356938035643809", "lat": CASA[0], "lon": CASA[1]},
                   headers={"X-Traccar-Token": CLAVE_TRACCAR})
    assert r.status_code == 200


def test_ubicacion_actual_e_historial(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "tra4")
    assert client.get(f"/perfiles/{e['pid']}/ubicacion", headers=headers(e["titular"])).json()["posicion"] is None
    registrar_pulsera(client, e["titular"], e["pid"])
    _crear_geocerca(client, e["titular"], e["pid"])
    ahora = datetime.now(timezone.utc)
    enviar_posicion(client, lat=LEJOS[0], lon=LEJOS[1], timestamp=int((ahora - timedelta(minutes=30)).timestamp()))
    enviar_posicion(client, lat=CASA[0], lon=CASA[1], timestamp=int(ahora.timestamp()))
    u = client.get(f"/perfiles/{e['pid']}/ubicacion", headers=headers(e["titular"])).json()
    assert abs(u["posicion"]["latitud"] - CASA[0]) < 1e-9 and u["dentro_de"] == ["Casa"]
    historial = client.get(f"/perfiles/{e['pid']}/ubicacion/historial", headers=headers(e["titular"])).json()
    assert len(historial) == 2 and historial[0]["registrada_en"] > historial[1]["registrada_en"]
    reciente = client.get(f"/perfiles/{e['pid']}/ubicacion/historial",
                          params={"desde": (ahora - timedelta(minutes=5)).isoformat()}, headers=headers(e["titular"])).json()
    assert len(reciente) == 1
    assert client.get(f"/perfiles/{e['pid']}/ubicacion", headers=headers(e["ajena"])).status_code == 404


# --- Alarmas de la pulsera -----------------------------------------------------------

def test_alarma_sos_y_caida_crean_eventos(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "ala1")
    registrar_pulsera(client, e["titular"], e["pid"])
    assert enviar_posicion(client, alarm="sos").json()["eventos"] == 1
    assert enviar_posicion(client, alarm="fallDown").json()["eventos"] == 1
    assert enviar_posicion(client, alarm="vibration").json()["eventos"] == 0     # alarmas que no usamos se ignoran
    tipos = [t for t, _, _ in _eventos_bd()]
    assert tipos == ["sos", "caida"]
    eventos = client.get("/eventos", headers=headers(e["cuidador"])).json()
    assert {x["tipo"] for x in eventos} == {"sos", "caida"} and all(x["origen"] == "pulsera" for x in eventos)
    assert all("emergencia" not in x["mensaje"].lower() for x in eventos)


def test_un_sos_repetido_dentro_de_la_ventana_no_duplica(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "ala2")
    registrar_pulsera(client, e["titular"], e["pid"])
    assert enviar_posicion(client, alarm="sos").json()["eventos"] == 1
    assert enviar_posicion(client, alarm="sos").json()["eventos"] == 0
    assert len(_eventos_bd()) == 1


def test_bateria_baja_por_alarma_o_por_porcentaje(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "ala3")
    registrar_pulsera(client, e["titular"], e["pid"])
    assert enviar_posicion(client, batt=50).json()["eventos"] == 0
    assert enviar_posicion(client, batt=10).json()["eventos"] == 1
    assert enviar_posicion(client, batt=9).json()["eventos"] == 0                 # ya se avisó, no se repite
    assert [t for t, _, _ in _eventos_bd()] == ["bateria_baja"]
    assert "(10 %)" in _eventos_bd()[0][2]
    e2 = escenario(client, "ala3b")
    registrar_pulsera(client, e2["titular"], e2["pid"], "111222333")
    assert enviar_posicion(client, identificador="111222333", alarm="lowBattery").json()["eventos"] == 1


def test_salir_de_una_geocerca_crea_un_evento(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "geo3")
    registrar_pulsera(client, e["titular"], e["pid"])
    _crear_geocerca(client, e["titular"], e["pid"])
    base = datetime.now(timezone.utc) - timedelta(hours=1)
    ts = lambda minutos: int((base + timedelta(minutes=minutos)).timestamp())
    assert enviar_posicion(client, lat=CASA[0], lon=CASA[1], timestamp=ts(0)).json()["eventos"] == 0    # primera lectura
    assert enviar_posicion(client, lat=CASA[0] + 0.0003, lon=CASA[1], timestamp=ts(5)).json()["eventos"] == 0  # ~33 m, sigue dentro
    r = enviar_posicion(client, lat=LEJOS[0], lon=LEJOS[1], timestamp=ts(10))
    assert r.json()["eventos"] == 1
    tipo, origen, mensaje = _eventos_bd()[0]
    assert (tipo, origen) == ("geocerca_salida", "pulsera") and "«Casa»" in mensaje
    assert enviar_posicion(client, lat=LEJOS[0] + 0.001, lon=LEJOS[1], timestamp=ts(15)).json()["eventos"] == 0  # ya estaba fuera


def test_una_geocerca_inactiva_no_avisa_y_una_lectura_atrasada_no_se_compara(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "geo4")
    registrar_pulsera(client, e["titular"], e["pid"])
    g = _crear_geocerca(client, e["titular"], e["pid"]).json()
    base = datetime.now(timezone.utc) - timedelta(hours=1)
    ts = lambda minutos: int((base + timedelta(minutes=minutos)).timestamp())
    enviar_posicion(client, lat=CASA[0], lon=CASA[1], timestamp=ts(10))
    # Llega tarde una lectura anterior y lejana: se guarda, pero no dispara la salida.
    assert enviar_posicion(client, lat=LEJOS[0], lon=LEJOS[1], timestamp=ts(0)).json()["eventos"] == 0
    client.patch(f"/perfiles/{e['pid']}/geocercas/{g['id']}", json={"activa": False}, headers=headers(e["titular"]))
    assert enviar_posicion(client, lat=LEJOS[0], lon=LEJOS[1], timestamp=ts(20)).json()["eventos"] == 0
    assert _eventos_bd() == []


def test_una_pulsera_desactivada_guarda_posiciones_pero_no_crea_eventos(client, monkeypatch):
    activar_traccar(monkeypatch)
    e = escenario(client, "ala4")
    p = registrar_pulsera(client, e["titular"], e["pid"]).json()
    client.patch(f"/perfiles/{e['pid']}/pulseras/{p['id']}", json={"activa": False}, headers=headers(e["titular"]))
    assert enviar_posicion(client, alarm="sos").json()["eventos"] == 0
    assert _eventos_bd() == []


# --- Inactividad y limpieza -----------------------------------------------------------

def _cargar_posiciones(pid, minutos_atras, lat=CASA[0], lon=CASA[1], ahora=None):
    """Guarda una posición por cada 'minutos_atras' (lista), sin pasar por la API."""
    ahora = (ahora or a(12)).astimezone(timezone.utc)
    db = TestingSessionLocal()
    try:
        pulsera = db.query(Pulsera).filter(Pulsera.perfil_id == UUID(pid)).first()
        for i, m in enumerate(minutos_atras):
            servicio.registrar_posicion(db, pulsera, lat + 0.00001 * (i % 2), lon, ahora - timedelta(minutes=m))
    finally:
        db.close()


def _inactividad(ahora):
    db = TestingSessionLocal()
    try:
        return servicio.procesar_inactividad(db, ahora)
    finally:
        db.close()


def _con_pulsera(client, prefijo):
    e = escenario(client, prefijo)
    registrar_pulsera(client, e["titular"], e["pid"])
    return e


def test_inactividad_crea_un_evento_una_sola_vez(client):
    e = _con_pulsera(client, "ina1")
    _cargar_posiciones(e["pid"], [175, 120, 60, 5])
    assert _inactividad(a(12)) == 1
    assert _inactividad(a(12, 1)) == 0                                  # dentro de la ventana no se repite
    tipo, origen, mensaje = _eventos_bd()[0]
    assert (tipo, origen) == ("inactividad", "sistema") and "3 horas" in mensaje


def test_inactividad_no_se_crea_si_hubo_movimiento(client):
    e = _con_pulsera(client, "ina2")
    _cargar_posiciones(e["pid"], [175, 120, 60])
    _cargar_posiciones(e["pid"], [5], lat=CASA[0] + 0.001)             # ~110 m: se movió
    assert _inactividad(a(12)) == 0


def test_inactividad_no_se_evalua_de_noche_ni_sin_senal_ni_con_poco_historial(client):
    e = _con_pulsera(client, "ina3")
    _cargar_posiciones(e["pid"], [175, 120, 60, 5], ahora=a(3))
    assert _inactividad(a(3)) == 0                                      # de noche duerme: no se evalúa
    e2 = _con_pulsera_con_otro_id(client, "ina3b", "555000111")
    _cargar_posiciones(e2["pid"], [200, 150, 100, 50], ahora=a(12))
    assert _inactividad(a(12)) == 0                                     # última lectura hace 50 min: falta de señal, no inactividad
    e3 = _con_pulsera_con_otro_id(client, "ina3c", "555000222")
    _cargar_posiciones(e3["pid"], [20, 5], ahora=a(12))
    assert _inactividad(a(12)) == 0                                     # cubre solo 15 minutos de 3 horas


def _con_pulsera_con_otro_id(client, prefijo, identificador):
    e = escenario(client, prefijo)
    registrar_pulsera(client, e["titular"], e["pid"], identificador)
    return e


def test_el_ciclo_programado_incluye_la_pulsera_y_limpia_posiciones_viejas(client):
    e = _con_pulsera(client, "cic1")
    _cargar_posiciones(e["pid"], [60 * 24 * 40, 5])                     # una de hace 40 días y una reciente
    db = TestingSessionLocal()
    try:
        resumen = ejecutar_ciclo(db)
        assert "inactividad" in resumen and resumen["posiciones_borradas"] == 1
        assert db.query(Posicion).count() == 1
    finally:
        db.close()


def test_si_falla_la_pulsera_el_ciclo_de_la_agenda_no_se_detiene(client, monkeypatch):
    def falla(db, ahora=None):
        raise RuntimeError("falla simulada")

    monkeypatch.setattr(servicio, "procesar_inactividad", falla)
    db = TestingSessionLocal()
    try:
        resumen = ejecutar_ciclo(db)
        assert "recordatorios" in resumen and "inactividad" not in resumen
    finally:
        db.close()
