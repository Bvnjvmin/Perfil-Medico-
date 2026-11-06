"""Pruebas de HU 14: botón «Necesito ayuda» y lista de eventos de seguridad."""
from app.tests.helpers import headers
from app.tests.helpers_s5 import escenario


def _pedir(client, token, pid, **cuerpo):
    return client.post(f"/perfiles/{pid}/asistencia", json=cuerpo or None, headers=headers(token))


def _eventos(client, token, **params):
    return client.get("/eventos", params=params, headers=headers(token)).json()


def test_el_boton_crea_un_evento_que_ven_titular_y_cuidador(client):
    e = escenario(client, "asi1")
    r = _pedir(client, e["titular"], e["pid"])
    assert r.status_code == 201, r.text
    evento = r.json()
    assert evento["tipo"] == "asistencia" and evento["origen"] == "app" and evento["perfil_nombre"] == "Abuela Rosa"
    assert "pidió ayuda" in evento["mensaje"] and evento["atendido_en"] is None
    assert [x["id"] for x in _eventos(client, e["titular"])] == [evento["id"]]
    assert [x["id"] for x in _eventos(client, e["cuidador"])] == [evento["id"]]
    assert _eventos(client, e["ajena"]) == []


def test_el_cuidador_sin_recibe_alertas_no_ve_el_evento(client):
    e = escenario(client, "asi2", recibe_alertas=False)
    _pedir(client, e["titular"], e["pid"])
    assert _eventos(client, e["cuidador"]) == []
    assert len(_eventos(client, e["titular"])) == 1


def test_pedir_ayuda_dos_veces_seguidas_no_duplica(client):
    e = escenario(client, "asi3")
    primero = _pedir(client, e["titular"], e["pid"])
    segundo = _pedir(client, e["titular"], e["pid"])
    assert primero.status_code == 201 and segundo.status_code == 200
    assert primero.json()["id"] == segundo.json()["id"]
    assert len(_eventos(client, e["titular"])) == 1


def test_mensaje_opcional(client):
    e = escenario(client, "asi4")
    r = _pedir(client, e["titular"], e["pid"], mensaje="Me caí en el baño")
    assert r.status_code == 201 and r.json()["mensaje"].endswith("Mensaje: Me caí en el baño")


def test_permisos_del_boton(client):
    e = escenario(client, "asi5", rol_vinculo="lectura")
    assert _pedir(client, e["cuidador"], e["pid"]).status_code == 403   # lectura no puede
    assert _pedir(client, e["ajena"], e["pid"]).status_code == 404
    e2 = escenario(client, "asi5b")
    assert _pedir(client, e2["cuidador"], e2["pid"]).status_code == 201  # un cuidador que puede confirmar sí


def test_marcar_atendido(client):
    e = escenario(client, "asi6")
    evento = _pedir(client, e["titular"], e["pid"]).json()
    assert client.post(f"/eventos/{evento['id']}/atendido", headers=headers(e["ajena"])).status_code == 404
    r = client.post(f"/eventos/{evento['id']}/atendido", headers=headers(e["cuidador"]))
    assert r.status_code == 200 and r.json()["atendido_en"] is not None
    atendido_por = r.json()["atendido_por_id"]
    # Idempotente: otra persona que lo marque después no cambia quién fue.
    de_nuevo = client.post(f"/eventos/{evento['id']}/atendido", headers=headers(e["titular"]))
    assert de_nuevo.json()["atendido_por_id"] == atendido_por
    assert _eventos(client, e["titular"], solo_pendientes=True) == []
    assert len(_eventos(client, e["titular"])) == 1


def test_el_aviso_llega_al_cuidador_y_no_a_quien_presiono_el_boton(client, monkeypatch):
    e = escenario(client, "asi7")
    client.post("/dispositivos", json={"token": "tok-titular"}, headers=headers(e["titular"]))
    client.post("/dispositivos", json={"token": "tok-cuidador"}, headers=headers(e["cuidador"]))
    enviados = []

    class Falso:
        def enviar(self, tokens, titulo, cuerpo, datos):
            enviados.append((tokens, titulo, datos["tipo"]))

    monkeypatch.setattr("app.services.eventos.obtener_notificador", lambda: Falso())
    _pedir(client, e["titular"], e["pid"])
    assert enviados == [(["tok-cuidador"], "Pidieron ayuda", "asistencia")]
