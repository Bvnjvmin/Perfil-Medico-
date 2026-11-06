"""Interruptor de la decisión 9 del Sprint 4: que la alerta de nivel 2 también llegue al titular."""
from datetime import date, datetime, time

from app.core.config import settings
from app.services.alertas import procesar_avisos
from app.services.tiempo import zona
from app.tests.conftest import TestingSessionLocal
from app.tests.helpers import actividades, crear_medicamento, crear_perfil, headers, registrar_y_loguear, vincular


def _escenario(client, prefijo):
    titular = registrar_y_loguear(client, f"{prefijo}-t@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, f"{prefijo}-c@perfilmedico.cl")
    perfil = crear_perfil(client, titular, nombre="Abuela", tipo="dependiente", subtipo="adulto_mayor")
    crear_medicamento(client, titular, perfil["id"], "Losartán", "08:00:00")
    vincular(client, titular, perfil["id"], f"{prefijo}-c@perfilmedico.cl", nivel_escalamiento=2)
    actividades(client, titular, perfil["id"])
    return titular, cuidador


def _nivel2_a_las_9():
    db = TestingSessionLocal()
    try:
        procesar_avisos(db, datetime.combine(date.today(), time(9, 0), tzinfo=zona()))
    finally:
        db.close()


def _niveles(client, token):
    return sorted(a["nivel"] for a in client.get("/alertas", headers=headers(token)).json())


def test_por_defecto_el_nivel_2_no_llega_al_titular(client):
    titular, cuidador = _escenario(client, "n2a")
    _nivel2_a_las_9()
    assert _niveles(client, titular) == [1] and _niveles(client, cuidador) == [2]


def test_con_el_interruptor_el_titular_tambien_recibe_el_nivel_2(client, monkeypatch):
    monkeypatch.setattr(settings, "ALERTA_NIVEL_2_INCLUYE_TITULAR", True)
    titular, cuidador = _escenario(client, "n2b")
    _nivel2_a_las_9()
    assert _niveles(client, titular) == [1, 2] and _niveles(client, cuidador) == [2]
