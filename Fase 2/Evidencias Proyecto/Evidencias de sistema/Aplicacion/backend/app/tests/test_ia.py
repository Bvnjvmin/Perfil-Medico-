"""Pruebas de HU 15: asistente de IA (orientación general)."""
import httpx
import pytest

from app.core.config import settings
from app.models.consulta_ia import ConsultaIA
from app.models.perfil import Perfil
from app.services import ia as servicio
from app.tests.conftest import TestingSessionLocal
from app.tests.helpers import crear_medicamento, headers
from app.tests.helpers_s5 import escenario


def _preguntar(client, token, pid, pregunta="¿Qué debo cuidar con sus medicamentos?"):
    return client.post(f"/perfiles/{pid}/ia/consultas", json={"pregunta": pregunta}, headers=headers(token))


def test_consulta_en_modo_simulado_usa_los_datos_del_perfil(client):
    e = escenario(client, "ia1")
    crear_medicamento(client, e["titular"], e["pid"], "Losartán", "08:00:00")
    client.post(f"/perfiles/{e['pid']}/alergias", json={"sustancia": "Penicilina", "severidad": "alta"}, headers=headers(e["titular"]))
    r = _preguntar(client, e["titular"], e["pid"])
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["proveedor"] == "simulado" and "Modo simulado" in cuerpo["respuesta"]
    assert "Losartán" in cuerpo["respuesta"] and "Penicilina" in cuerpo["respuesta"]
    assert "131" in cuerpo["aviso"]
    db = TestingSessionLocal()
    try:
        guardada = db.query(ConsultaIA).one()
        assert "alergias" in guardada.contexto_resumen and "medicamentos activos" in guardada.contexto_resumen
    finally:
        db.close()


def test_el_contexto_no_incluye_datos_sensibles(client):
    e = escenario(client, "ia2")
    db = TestingSessionLocal()
    try:
        from uuid import UUID
        perfil = db.get(Perfil, UUID(e["pid"]))
        perfil.rut = "12.345.678-5"
        db.commit()
        contexto, _ = servicio.construir_contexto(db, perfil, incluir_indicadores=True)
    finally:
        db.close()
    assert "12.345.678" not in contexto and "perfilmedico.cl" not in contexto
    assert contexto.startswith("Perfil: Abuela (dependiente)")      # solo el nombre de pila (sin apellido)


def test_los_indicadores_solo_se_incluyen_si_quien_pregunta_puede_verlos(client):
    e = escenario(client, "ia3")                              # el cuidador NO tiene puede_ver_indicadores
    client.post(f"/perfiles/{e['pid']}/indicadores", json={"tipo": "peso", "valor": "68"}, headers=headers(e["titular"]))
    del_titular = _preguntar(client, e["titular"], e["pid"]).json()["respuesta"]
    del_cuidador = _preguntar(client, e["cuidador"], e["pid"]).json()["respuesta"]
    assert "peso 68 kg" in del_titular
    assert "Últimos indicadores" not in del_cuidador and "68" not in del_cuidador


def test_una_urgencia_no_llega_al_modelo(client, monkeypatch):
    def no_debe_llamarse(*args, **kwargs):
        raise AssertionError("no debía llamar al proveedor")

    monkeypatch.setattr("app.api.routes.ia.responder", no_debe_llamarse)
    e = escenario(client, "ia4")
    for texto in ("Mi abuela tiene dolor de pecho y está sudando", "NO RESPIRA bien", "tuvo una convulsión", "Se DESMAYÓ hace un rato"):
        r = _preguntar(client, e["titular"], e["pid"], texto)
        assert r.status_code == 201 and r.json()["proveedor"] == "reglas" and "131" in r.json()["respuesta"]


def test_proveedor_anthropic_arma_la_llamada_y_devuelve_el_texto(client, monkeypatch):
    llamadas = []

    def falsa(cuerpo):
        llamadas.append(cuerpo)
        return {"content": [{"type": "text", "text": "Mantén los horarios y consulta al médico."}]}

    monkeypatch.setattr(servicio, "_llamar_anthropic", falsa)
    monkeypatch.setattr(settings, "IA_PROVEEDOR", "anthropic")
    monkeypatch.setattr(settings, "IA_API_KEY", "clave-falsa")
    e = escenario(client, "ia5")
    crear_medicamento(client, e["titular"], e["pid"], "Losartán", "08:00:00")
    r = _preguntar(client, e["titular"], e["pid"], "¿Puede tomar el medicamento con el desayuno?")
    assert r.status_code == 201 and r.json()["proveedor"] == "anthropic"
    assert r.json()["respuesta"] == "Mantén los horarios y consulta al médico."
    cuerpo = llamadas[0]
    assert cuerpo["model"] == settings.IA_MODELO and cuerpo["max_tokens"] == settings.IA_MAX_TOKENS
    assert cuerpo["system"] == servicio.SISTEMA
    contenido = cuerpo["messages"][0]["content"]
    assert "Losartán" in contenido and "con el desayuno" in contenido and "perfilmedico.cl" not in contenido


def test_si_el_proveedor_falla_responde_503_y_no_guarda_nada(client, monkeypatch):
    def cae(cuerpo):
        raise httpx.ConnectError("sin red")

    monkeypatch.setattr(servicio, "_llamar_anthropic", cae)
    monkeypatch.setattr(settings, "IA_PROVEEDOR", "anthropic")
    monkeypatch.setattr(settings, "IA_API_KEY", "clave-falsa")
    e = escenario(client, "ia6")
    r = _preguntar(client, e["titular"], e["pid"])
    assert r.status_code == 503 and "no está disponible" in r.json()["detail"]
    assert client.get(f"/perfiles/{e['pid']}/ia/consultas", headers=headers(e["titular"])).json() == []


def test_sin_clave_configurada_responde_503(client, monkeypatch):
    monkeypatch.setattr(settings, "IA_PROVEEDOR", "anthropic")
    monkeypatch.setattr(settings, "IA_API_KEY", "")
    e = escenario(client, "ia7")
    assert _preguntar(client, e["titular"], e["pid"]).status_code == 503


def test_tope_diario_de_consultas(client, monkeypatch):
    monkeypatch.setattr(settings, "IA_MAX_CONSULTAS_DIA", 2)
    e = escenario(client, "ia8")
    assert _preguntar(client, e["titular"], e["pid"]).status_code == 201
    assert _preguntar(client, e["titular"], e["pid"]).status_code == 201
    assert _preguntar(client, e["titular"], e["pid"]).status_code == 429
    assert _preguntar(client, e["cuidador"], e["pid"]).status_code == 201     # el tope es por usuario


def test_historial_propio_y_permisos(client):
    e = escenario(client, "ia9")
    _preguntar(client, e["titular"], e["pid"], "Primera pregunta")
    _preguntar(client, e["titular"], e["pid"], "Segunda pregunta")
    _preguntar(client, e["cuidador"], e["pid"], "Pregunta del cuidador")
    propio = client.get(f"/perfiles/{e['pid']}/ia/consultas", headers=headers(e["titular"])).json()
    assert [x["pregunta"] for x in propio] == ["Segunda pregunta", "Primera pregunta"]
    assert len(client.get(f"/perfiles/{e['pid']}/ia/consultas", headers=headers(e["cuidador"])).json()) == 1
    assert client.get(f"/perfiles/{e['pid']}/ia/consultas", headers=headers(e["ajena"])).status_code == 404
    assert _preguntar(client, e["ajena"], e["pid"]).status_code == 404
    assert _preguntar(client, e["titular"], e["pid"], "ab").status_code == 422
    assert _preguntar(client, e["titular"], e["pid"], "x" * 1001).status_code == 422


@pytest.mark.parametrize("pregunta", [
    "Me duele el pecho y me cuesta respirar",
    "Mi mamá se desmayó esta mañana",
    "Tengo dolor de pecho desde anoche",
    "Siente falta de aire al caminar",
])
def test_frases_comunes_de_urgencia_se_detectan(pregunta):
    from app.services.ia import es_urgencia
    assert es_urgencia(pregunta)


def test_una_pregunta_normal_no_es_urgencia():
    from app.services.ia import es_urgencia
    assert not es_urgencia("¿Para qué sirve el Losartán?")
    assert not es_urgencia("¿Puedo tomar el paracetamol con el desayuno?")
