"""
Pruebas de HU 9 y HU 10: dispositivos, recordatorios y alertas escalonadas.

Las horas se controlan pasando `ahora` a `procesar_avisos`, sin esperar plazos reales
ni depender de la hora del día en que corran las pruebas.
"""
from datetime import date, datetime, time, timedelta
from uuid import UUID

from app.models.actividad import Actividad
from app.models.alerta import Alerta
from app.models.perfil_acceso import PerfilAcceso
from app.services import alertas as servicio
from app.services.alertas import procesar_avisos
from app.services.tiempo import zona
from app.tests.conftest import TestingSessionLocal
from app.tests.helpers import (
    actividades, crear_medicamento, crear_perfil, headers, registrar_y_loguear, vincular,
)


def _a(hora: int, minuto: int = 0, dias: int = 0) -> datetime:
    """Un momento de hoy (o de otro día) a esa hora, en la zona horaria del sistema."""
    return datetime.combine(date.today() + timedelta(days=dias), time(hora, minuto), tzinfo=zona())


def _escenario(client, prefijo):
    """Titular con un perfil y una actividad a las 08:00, más un cuidador y una cuenta ajena."""
    titular = registrar_y_loguear(client, f"{prefijo}-titular@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, f"{prefijo}-cuidador@perfilmedico.cl")
    ajena = registrar_y_loguear(client, f"{prefijo}-ajena@perfilmedico.cl")
    perfil = crear_perfil(client, titular, nombre="Abuela", tipo="dependiente", subtipo="adulto_mayor")
    crear_medicamento(client, titular, perfil["id"], "Losartán", "08:00:00")
    vinculo = vincular(client, titular, perfil["id"], f"{prefijo}-cuidador@perfilmedico.cl")
    actividad = actividades(client, titular, perfil["id"]).json()[0]
    return {"titular": titular, "cuidador": cuidador, "ajena": ajena, "perfil": perfil,
            "vinculo": vinculo, "actividad": actividad}


def _procesar(ahora):
    db = TestingSessionLocal()
    try:
        return procesar_avisos(db, ahora)
    finally:
        db.close()


def _avisos(client, token, **params):
    return client.get("/alertas", params=params, headers=headers(token)).json()


def _vinculo_en_bd(vinculo_id, **cambios):
    db = TestingSessionLocal()
    try:
        fila = db.get(PerfilAcceso, UUID(vinculo_id))
        for k, v in cambios.items():
            setattr(fila, k, v)
        db.commit()
    finally:
        db.close()


# --- HU 9: recordatorios -----------------------------------------------------

def test_recordatorio_antes_de_la_hora(client):
    e = _escenario(client, "av1")
    assert _procesar(_a(7, 55)) == {"vencidas": 0, "recordatorios": 2, "alertas": 0}
    titular = _avisos(client, e["titular"])
    assert len(titular) == 1
    assert titular[0]["tipo"] == "recordatorio" and titular[0]["nivel"] == 0
    assert titular[0]["mensaje"] == "Recordatorio: «Losartán» de Abuela es a las 08:00."
    assert titular[0]["perfil_id"] == e["perfil"]["id"]
    assert titular[0]["actividad_id"] == e["actividad"]["id"]
    assert len(_avisos(client, e["cuidador"])) == 1  # el cuidador también lo recibe
    assert _avisos(client, e["ajena"]) == []


def test_no_hay_recordatorio_antes_de_tiempo_ni_se_repite(client):
    e = _escenario(client, "av2")
    assert _procesar(_a(7, 30))["recordatorios"] == 0       # faltan más de 10 minutos
    assert _procesar(_a(7, 55))["recordatorios"] == 2
    assert _procesar(_a(7, 56))["recordatorios"] == 0       # no se repite
    assert len(_avisos(client, e["titular"])) == 1


def test_una_actividad_confirmada_no_genera_recordatorio(client):
    e = _escenario(client, "av3")
    client.post(f"/actividades/{e['actividad']['id']}/confirmar", headers=headers(e["titular"]))
    assert _procesar(_a(7, 55)) == {"vencidas": 0, "recordatorios": 0, "alertas": 0}
    assert _avisos(client, e["titular"]) == []


def test_el_cuidador_sin_recibe_alertas_no_recibe_avisos(client):
    e = _escenario(client, "av4")
    _vinculo_en_bd(e["vinculo"]["id"], recibe_alertas=False)
    _procesar(_a(7, 55))
    assert len(_avisos(client, e["titular"])) == 1
    assert _avisos(client, e["cuidador"]) == []


# --- HU 10: alertas escalonadas ---------------------------------------------

def test_alerta_de_nivel_1_pasado_el_primer_plazo(client):
    e = _escenario(client, "av5")
    resumen = _procesar(_a(8, 30))
    assert resumen["alertas"] == 2  # titular y cuidador de nivel 1
    avisos = _avisos(client, e["titular"])
    alerta = next(a for a in avisos if a["tipo"] == "alerta")
    assert alerta["nivel"] == 1
    assert alerta["mensaje"] == "La actividad «Losartán» de Abuela (programada a las 08:00) aún no fue confirmada."
    assert any(a["tipo"] == "alerta" for a in _avisos(client, e["cuidador"]))


def test_la_alerta_escala_al_nivel_2_solo_para_quien_corresponde(client):
    e = _escenario(client, "av6")
    nivel2 = registrar_y_loguear(client, "av6-nivel2@perfilmedico.cl")
    vinculo2 = vincular(client, e["titular"], e["perfil"]["id"], "av6-nivel2@perfilmedico.cl", nivel_escalamiento=2)
    assert vinculo2["nivel_escalamiento"] == 2

    _procesar(_a(8, 30))
    assert [a for a in _avisos(client, nivel2) if a["tipo"] == "alerta"] == []  # aún no le toca
    _procesar(_a(9, 0))
    alertas_n2 = [a for a in _avisos(client, nivel2) if a["tipo"] == "alerta"]
    assert len(alertas_n2) == 1 and alertas_n2[0]["nivel"] == 2
    assert alertas_n2[0]["mensaje"].endswith("Sigue sin confirmarse.")
    # Los de nivel 1 no reciben otra alerta en el segundo plazo: ya se enteraron en el primero.
    assert len([a for a in _avisos(client, e["cuidador"]) if a["tipo"] == "alerta"]) == 1


def test_confirmar_detiene_el_escalamiento(client):
    e = _escenario(client, "av7")
    _procesar(_a(8, 30))
    client.post(f"/actividades/{e['actividad']['id']}/confirmar", headers=headers(e["cuidador"]))
    assert _procesar(_a(9, 0))["alertas"] == 0
    db = TestingSessionLocal()
    try:
        assert db.query(Alerta).filter(Alerta.nivel == 2).count() == 0
    finally:
        db.close()


def test_las_alertas_no_se_repiten_aunque_la_tarea_corra_muchas_veces(client):
    e = _escenario(client, "av8")
    assert _procesar(_a(8, 30))["alertas"] == 2
    assert _procesar(_a(8, 31))["alertas"] == 0
    assert _procesar(_a(8, 45))["alertas"] == 0
    assert len([a for a in _avisos(client, e["titular"]) if a["tipo"] == "alerta"]) == 1


def test_actividad_del_dia_anterior_pasa_a_vencida(client):
    e = _escenario(client, "av9")
    resumen = _procesar(_a(0, 10, dias=1))
    assert resumen["vencidas"] == 1 and resumen["alertas"] == 0
    agenda = actividades(client, e["titular"], e["perfil"]["id"]).json()
    assert agenda[0]["estado"] == "vencida"
    # Se puede confirmar igual (el cuidador la tomó tarde) y vuelve a contar como confirmada.
    ok = client.post(f"/actividades/{e['actividad']['id']}/confirmar", headers=headers(e["titular"]))
    assert ok.status_code == 200 and ok.json()["estado"] == "confirmada"


def test_no_hay_avisos_si_el_medicamento_esta_inactivo(client):
    e = _escenario(client, "av10")
    client.put(f"/medicamentos/{e['actividad']['origen_id']}", json={"activo": False}, headers=headers(e["titular"]))
    assert _procesar(_a(8, 30)) == {"vencidas": 0, "recordatorios": 0, "alertas": 0}


def test_cada_alerta_queda_registrada_y_se_puede_consultar(client):
    e = _escenario(client, "av11")
    _procesar(_a(8, 30))
    db = TestingSessionLocal()
    try:
        filas = db.query(Alerta).filter(Alerta.nivel == 1).all()
        assert {f.usuario_id for f in filas} and all(f.mensaje and f.creada_en for f in filas)
    finally:
        db.close()
    assert _avisos(client, e["ajena"]) == []   # la cuenta sin vínculo no ve ninguna


def test_quien_pierde_el_acceso_deja_de_ver_los_avisos(client):
    e = _escenario(client, "av12")
    _procesar(_a(8, 30))
    assert len(_avisos(client, e["cuidador"])) >= 1
    client.delete(f"/perfiles/{e['perfil']['id']}/cuidadores/{e['vinculo']['id']}", headers=headers(e["titular"]))
    assert _avisos(client, e["cuidador"]) == []


def test_el_vinculo_acepta_y_devuelve_los_campos_de_alertas(client):
    titular = registrar_y_loguear(client, "av13-titular@perfilmedico.cl")
    registrar_y_loguear(client, "av13-cuidador@perfilmedico.cl")
    perfil = crear_perfil(client, titular)
    v = vincular(client, titular, perfil["id"], "av13-cuidador@perfilmedico.cl", recibe_alertas=False, nivel_escalamiento=3)
    assert v["recibe_alertas"] is False and v["nivel_escalamiento"] == 3
    r = client.put(f"/perfiles/{perfil['id']}/cuidadores/{v['id']}", json={"nivel_escalamiento": 2}, headers=headers(titular))
    assert r.json()["nivel_escalamiento"] == 2 and r.json()["recibe_alertas"] is False
    malo = client.put(f"/perfiles/{perfil['id']}/cuidadores/{v['id']}", json={"nivel_escalamiento": 9}, headers=headers(titular))
    assert malo.status_code == 422


# --- Leer y marcar avisos ---------------------------------------------------

def test_marcar_leida_y_filtrar_no_leidas(client):
    e = _escenario(client, "av14")
    _procesar(_a(7, 55))
    aviso = _avisos(client, e["titular"])[0]
    assert aviso["leida_en"] is None
    hecho = client.post(f"/alertas/{aviso['id']}/leida", headers=headers(e["titular"]))
    assert hecho.status_code == 200 and hecho.json()["leida_en"] is not None
    assert _avisos(client, e["titular"], solo_no_leidas=True) == []
    assert len(_avisos(client, e["titular"])) == 1
    # El aviso de otra persona no se puede tocar: 404.
    assert client.post(f"/alertas/{aviso['id']}/leida", headers=headers(e["ajena"])).status_code == 404


# --- Dispositivos y notificador ---------------------------------------------

def test_registrar_dispositivo(client):
    uno = registrar_y_loguear(client, "disp1@perfilmedico.cl")
    otro = registrar_y_loguear(client, "disp2@perfilmedico.cl")
    primero = client.post("/dispositivos", json={"token": "tok:abc-123_x"}, headers=headers(uno))
    assert primero.status_code == 201 and primero.json()["plataforma"] == "android"
    repetido = client.post("/dispositivos", json={"token": "tok:abc-123_x"}, headers=headers(uno))
    assert repetido.status_code == 200 and repetido.json()["id"] == primero.json()["id"]
    # Si el celular cambia de cuenta, el token pasa a la nueva.
    cambio = client.post("/dispositivos", json={"token": "tok:abc-123_x"}, headers=headers(otro))
    assert cambio.status_code == 200
    assert client.delete("/dispositivos/tok:abc-123_x", headers=headers(uno)).status_code == 404
    assert client.delete("/dispositivos/tok:abc-123_x", headers=headers(otro)).status_code == 204


def test_dispositivo_invalido_o_sin_sesion(client):
    uno = registrar_y_loguear(client, "disp3@perfilmedico.cl")
    assert client.post("/dispositivos", json={"token": ""}, headers=headers(uno)).status_code == 422
    assert client.post("/dispositivos", json={"token": "x", "plataforma": "otra"}, headers=headers(uno)).status_code == 422
    assert client.post("/dispositivos", json={"token": "x"}).status_code == 401
    assert client.get("/alertas").status_code == 401


def test_los_avisos_se_entregan_a_los_dispositivos_registrados(client, monkeypatch):
    e = _escenario(client, "av15")
    client.post("/dispositivos", json={"token": "token-titular"}, headers=headers(e["titular"]))
    enviados = []

    class Registro:
        def enviar(self, tokens, titulo, cuerpo, datos):
            enviados.append((tokens, titulo, cuerpo, datos))

    monkeypatch.setattr(servicio, "obtener_notificador", lambda: Registro())
    _procesar(_a(7, 55))
    assert len(enviados) == 1  # el cuidador no tiene dispositivo registrado
    tokens, titulo, cuerpo, datos = enviados[0]
    assert tokens == ["token-titular"] and titulo == "Recordatorio"
    assert datos["perfil_id"] == e["perfil"]["id"] and datos["tipo"] == "recordatorio"


def test_un_fallo_del_notificador_no_detiene_los_avisos(client, monkeypatch):
    e = _escenario(client, "av16")
    client.post("/dispositivos", json={"token": "token-roto"}, headers=headers(e["titular"]))

    class Roto:
        def enviar(self, *args):
            raise RuntimeError("sin red")

    monkeypatch.setattr(servicio, "obtener_notificador", lambda: Roto())
    assert _procesar(_a(7, 55))["recordatorios"] == 2
    assert len(_avisos(client, e["titular"])) == 1


def test_borrar_la_actividad_borra_sus_avisos(client):
    e = _escenario(client, "av17")
    _procesar(_a(8, 30))
    client.delete(f"/medicamentos/{e['actividad']['origen_id']}", headers=headers(e["titular"]))
    db = TestingSessionLocal()
    try:
        assert db.query(Alerta).count() == 0
        assert db.query(Actividad).count() == 0
    finally:
        db.close()
