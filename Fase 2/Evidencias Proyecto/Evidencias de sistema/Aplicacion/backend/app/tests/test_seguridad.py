"""Pruebas de las medidas de seguridad del Sprint 6: clave secreta, límite de intentos de login,
CORS cerrado y registro de avisos sin contenido."""
import logging

import pytest

from app.core.config import Settings, settings, validar_secretos
from app.core.limitador import LimitadorIntentos
from app.services.notificador import NotificadorLog

CLAVE_BUENA = "k" * 40


def _config(clave: str) -> Settings:
    return Settings(SECRET_KEY=clave)


def test_arranque_rechaza_la_clave_de_ejemplo():
    with pytest.raises(RuntimeError):
        validar_secretos(_config("cambia-esta-clave-en-produccion-por-una-generada-al-azar"))
    with pytest.raises(RuntimeError):
        validar_secretos(_config("pega-aqui-una-clave-larga-y-aleatoria"))


def test_arranque_rechaza_una_clave_corta():
    with pytest.raises(RuntimeError):
        validar_secretos(_config("corta"))


def test_arranque_acepta_una_clave_larga_y_propia():
    validar_secretos(_config(CLAVE_BUENA))


def test_limitador_bloquea_al_llegar_al_maximo_y_libera_al_pasar_la_ventana():
    ahora = [0.0]
    limitador = LimitadorIntentos(reloj=lambda: ahora[0])
    for _ in range(3):
        assert limitador.segundos_de_espera("a", 3, 60) == 0
        limitador.registrar_fallo("a")
    espera = limitador.segundos_de_espera("a", 3, 60)
    assert 0 < espera <= 60
    assert limitador.segundos_de_espera("otra", 3, 60) == 0  # otra clave no se ve afectada
    ahora[0] = 61.0
    assert limitador.segundos_de_espera("a", 3, 60) == 0


def _login(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_login_se_bloquea_tras_los_intentos_fallidos(client):
    client.post("/auth/register", json={"nombre": "Ana", "email": "ana@ejemplo.cl", "password": "clave-segura-123"})
    for _ in range(settings.LOGIN_MAX_INTENTOS):
        assert _login(client, "ana@ejemplo.cl", "incorrecta-1").status_code == 401
    bloqueado = _login(client, "ana@ejemplo.cl", "clave-segura-123")  # aunque ahora sea la correcta
    assert bloqueado.status_code == 429
    assert int(bloqueado.headers["Retry-After"]) > 0


def test_el_bloqueo_de_una_cuenta_no_afecta_a_otra(client):
    for correo in ("ana@ejemplo.cl", "luis@ejemplo.cl"):
        client.post("/auth/register", json={"nombre": correo[:3], "email": correo, "password": "clave-segura-123"})
    for _ in range(settings.LOGIN_MAX_INTENTOS):
        _login(client, "ana@ejemplo.cl", "incorrecta-1")
    assert _login(client, "ana@ejemplo.cl", "clave-segura-123").status_code == 429
    assert _login(client, "luis@ejemplo.cl", "clave-segura-123").status_code == 200


def test_un_login_correcto_reinicia_el_contador(client):
    client.post("/auth/register", json={"nombre": "Ana", "email": "ana@ejemplo.cl", "password": "clave-segura-123"})
    for _ in range(settings.LOGIN_MAX_INTENTOS - 1):
        _login(client, "ana@ejemplo.cl", "incorrecta-1")
    assert _login(client, "ana@ejemplo.cl", "clave-segura-123").status_code == 200
    for _ in range(settings.LOGIN_MAX_INTENTOS - 1):
        assert _login(client, "ana@ejemplo.cl", "incorrecta-1").status_code == 401


def test_cors_no_se_abre_a_origenes_desconocidos(client):
    r = client.get("/health", headers={"Origin": "https://sitio-malicioso.example"})
    assert r.status_code == 200
    assert "access-control-allow-origin" not in r.headers


def test_el_registro_de_avisos_no_incluye_el_texto_por_defecto(caplog, monkeypatch):
    monkeypatch.setattr(settings, "NOTIFICADOR_LOG_CONTENIDO", False)
    with caplog.at_level(logging.INFO):
        NotificadorLog().enviar(["tok"], "Recordatorio", "Tomar Metformina 850 mg", {"tipo": "recordatorio", "nivel": 0})
    assert "Metformina" not in caplog.text
    assert "tipo=recordatorio" in caplog.text


def test_el_registro_de_avisos_puede_incluir_el_texto_si_se_pide(caplog, monkeypatch):
    monkeypatch.setattr(settings, "NOTIFICADOR_LOG_CONTENIDO", True)
    with caplog.at_level(logging.INFO):
        NotificadorLog().enviar(["tok"], "Recordatorio", "Tomar Metformina 850 mg", {"tipo": "recordatorio", "nivel": 0})
    assert "Metformina" in caplog.text
