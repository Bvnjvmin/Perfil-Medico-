"""Pruebas de HU 12 y HU 18: indicadores de salud (peso, presión, glucosa, frecuencia cardíaca)."""
from datetime import datetime, timedelta, timezone

from app.tests.helpers import headers
from app.tests.helpers_s5 import escenario


def _registrar(client, token, pid, **cuerpo):
    return client.post(f"/perfiles/{pid}/indicadores", json=cuerpo, headers=headers(token))


def test_registrar_peso_manual(client):
    e = escenario(client, "ind1")
    r = _registrar(client, e["titular"], e["pid"], tipo="peso", valor="70.5")
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["tipo"] == "peso" and cuerpo["unidad"] == "kg" and cuerpo["fuente"] == "manual"
    assert float(cuerpo["valor"]) == 70.5 and cuerpo["valor_secundario"] is None


def test_la_presion_exige_sistolica_y_diastolica(client):
    e = escenario(client, "ind2")
    assert _registrar(client, e["titular"], e["pid"], tipo="presion", valor="120").status_code == 422
    assert _registrar(client, e["titular"], e["pid"], tipo="presion", valor="120", valor_secundario="130").status_code == 422
    ok = _registrar(client, e["titular"], e["pid"], tipo="presion", valor="120", valor_secundario="80")
    assert ok.status_code == 201 and ok.json()["unidad"] == "mmHg"
    assert _registrar(client, e["titular"], e["pid"], tipo="peso", valor="70", valor_secundario="5").status_code == 422


def test_valores_fuera_de_rango_se_rechazan(client):
    e = escenario(client, "ind3")
    assert _registrar(client, e["titular"], e["pid"], tipo="peso", valor="700").status_code == 422
    assert _registrar(client, e["titular"], e["pid"], tipo="glucosa", valor="0").status_code == 422
    assert _registrar(client, e["titular"], e["pid"], tipo="frecuencia_cardiaca", valor="500").status_code == 422
    assert _registrar(client, e["titular"], e["pid"], tipo="altura", valor="170").status_code == 422


def test_no_se_acepta_una_medicion_del_futuro(client):
    e = escenario(client, "ind4")
    futuro = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    assert _registrar(client, e["titular"], e["pid"], tipo="peso", valor="70", medido_en=futuro).status_code == 400


def test_frecuencia_cardiaca_desde_la_pulsera(client):
    e = escenario(client, "ind5")
    r = _registrar(client, e["titular"], e["pid"], tipo="frecuencia_cardiaca", valor="72", fuente="pulsera")
    assert r.status_code == 201 and r.json()["fuente"] == "pulsera" and r.json()["unidad"] == "lpm"


def test_permisos_de_indicadores(client):
    e = escenario(client, "ind6")  # el cuidador se vincula SIN puede_ver_indicadores
    assert _registrar(client, e["cuidador"], e["pid"], tipo="peso", valor="70").status_code == 403
    assert client.get(f"/perfiles/{e['pid']}/indicadores", headers=headers(e["cuidador"])).status_code == 403
    assert _registrar(client, e["ajena"], e["pid"], tipo="peso", valor="70").status_code == 404
    assert client.get(f"/perfiles/{e['pid']}/indicadores", headers=headers(e["ajena"])).status_code == 404


def test_cuidador_con_permiso_registra_y_lectura_solo_ve(client):
    e = escenario(client, "ind7", puede_ver_indicadores=True)
    assert _registrar(client, e["cuidador"], e["pid"], tipo="peso", valor="71").status_code == 201
    assert len(client.get(f"/perfiles/{e['pid']}/indicadores", headers=headers(e["cuidador"])).json()) == 1

    lectura = escenario(client, "ind7b", rol_vinculo="lectura", puede_ver_indicadores=True)
    assert _registrar(client, lectura["titular"], lectura["pid"], tipo="peso", valor="70").status_code == 201
    assert len(client.get(f"/perfiles/{lectura['pid']}/indicadores", headers=headers(lectura["cuidador"])).json()) == 1
    assert _registrar(client, lectura["cuidador"], lectura["pid"], tipo="peso", valor="71").status_code == 403


def test_listar_filtra_por_tipo_y_fechas(client):
    e = escenario(client, "ind8")
    ahora = datetime.now(timezone.utc)
    _registrar(client, e["titular"], e["pid"], tipo="peso", valor="70", medido_en=(ahora - timedelta(days=10)).isoformat())
    _registrar(client, e["titular"], e["pid"], tipo="peso", valor="71")
    _registrar(client, e["titular"], e["pid"], tipo="glucosa", valor="95")
    url = f"/perfiles/{e['pid']}/indicadores"
    todos = client.get(url, headers=headers(e["titular"])).json()
    assert len(todos) == 3 and todos[0]["medido_en"] >= todos[-1]["medido_en"]  # el más nuevo primero
    assert len(client.get(url, params={"tipo": "peso"}, headers=headers(e["titular"])).json()) == 2
    desde = (ahora - timedelta(days=2)).date().isoformat()
    assert len(client.get(url, params={"tipo": "peso", "desde": desde}, headers=headers(e["titular"])).json()) == 1
    hasta = (ahora - timedelta(days=5)).date().isoformat()
    assert len(client.get(url, params={"hasta": hasta}, headers=headers(e["titular"])).json()) == 1


def test_ultimos_devuelve_el_mas_reciente_de_cada_tipo(client):
    e = escenario(client, "ind9")
    ahora = datetime.now(timezone.utc)
    _registrar(client, e["titular"], e["pid"], tipo="peso", valor="70", medido_en=(ahora - timedelta(days=3)).isoformat())
    _registrar(client, e["titular"], e["pid"], tipo="peso", valor="72")
    _registrar(client, e["titular"], e["pid"], tipo="presion", valor="130", valor_secundario="85")
    r = client.get(f"/perfiles/{e['pid']}/indicadores/ultimos", headers=headers(e["titular"])).json()
    por_tipo = {i["tipo"]: i for i in r["ultimos"]}
    assert set(por_tipo) == {"peso", "presion"} and float(por_tipo["peso"]["valor"]) == 72


def test_serie_para_el_grafico(client):
    e = escenario(client, "ind10")
    ahora = datetime.now(timezone.utc)
    for dias, valor in ((5, "70"), (3, "72"), (1, "71")):
        _registrar(client, e["titular"], e["pid"], tipo="peso", valor=valor, medido_en=(ahora - timedelta(days=dias)).isoformat())
    _registrar(client, e["titular"], e["pid"], tipo="peso", valor="60", medido_en=(ahora - timedelta(days=40)).isoformat())
    r = client.get(f"/perfiles/{e['pid']}/indicadores/serie", params={"tipo": "peso", "dias": 30}, headers=headers(e["titular"]))
    assert r.status_code == 200
    s = r.json()
    assert [float(p["valor"]) for p in s["puntos"]] == [70, 72, 71]   # del más antiguo al más nuevo, sin el de hace 40 días
    assert float(s["minimo"]) == 70 and float(s["maximo"]) == 72 and float(s["promedio"]) == 71
    assert s["unidad"] == "kg"
    vacia = client.get(f"/perfiles/{e['pid']}/indicadores/serie", params={"tipo": "glucosa"}, headers=headers(e["titular"])).json()
    assert vacia["puntos"] == [] and vacia["minimo"] is None and vacia["promedio"] is None
    assert client.get(f"/perfiles/{e['pid']}/indicadores/serie", params={"tipo": "peso", "dias": 0}, headers=headers(e["titular"])).status_code == 422


def test_borrar_indicador(client):
    e = escenario(client, "ind11", puede_ver_indicadores=True)
    del_titular = _registrar(client, e["titular"], e["pid"], tipo="peso", valor="70").json()["id"]
    del_cuidador = _registrar(client, e["cuidador"], e["pid"], tipo="peso", valor="71").json()["id"]
    base = f"/perfiles/{e['pid']}/indicadores"
    assert client.delete(f"{base}/{del_titular}", headers=headers(e["cuidador"])).status_code == 403   # no es suyo
    assert client.delete(f"{base}/{del_cuidador}", headers=headers(e["cuidador"])).status_code == 204  # sí es suyo
    assert client.delete(f"{base}/{del_titular}", headers=headers(e["titular"])).status_code == 204     # el titular borra cualquiera
    assert client.delete(f"{base}/{del_titular}", headers=headers(e["titular"])).status_code == 404


def test_un_indicador_de_otro_perfil_no_se_puede_borrar(client):
    e = escenario(client, "ind12")
    otro = escenario(client, "ind12b")
    ajeno = _registrar(client, otro["titular"], otro["pid"], tipo="peso", valor="70").json()["id"]
    assert client.delete(f"/perfiles/{e['pid']}/indicadores/{ajeno}", headers=headers(e["titular"])).status_code == 404
