"""
Pruebas de HU 8 (versión inicial): panel de estado diario.
"""
from app.tests.helpers import (
    FECHA, actividades, crear_medicamento, crear_perfil, crear_rutina, headers, registrar_y_loguear, vincular,
)


def _panel(client, token, fecha=FECHA):
    return client.get("/panel", params={"fecha": fecha}, headers=headers(token))


def test_usuario_sin_perfiles_recibe_lista_vacia(client):
    token = registrar_y_loguear(client, "pan1@perfilmedico.cl")
    respuesta = _panel(client, token)
    assert respuesta.status_code == 200 and respuesta.json() == []


def test_fecha_obligatoria_y_requiere_sesion(client):
    token = registrar_y_loguear(client, "pan2@perfilmedico.cl")
    assert client.get("/panel", headers=headers(token)).status_code == 422
    assert client.get("/panel", params={"fecha": FECHA}).status_code == 401


def test_panel_con_perfil_propio_y_compartido(client):
    yo = registrar_y_loguear(client, "pan3@perfilmedico.cl")
    otro = registrar_y_loguear(client, "pan3otro@perfilmedico.cl")
    mio = crear_perfil(client, yo, "Yo")
    crear_medicamento(client, yo, mio["id"], "Med A", "08:00:00")
    crear_medicamento(client, yo, mio["id"], "Med B", "09:00:00")
    ajeno = crear_perfil(client, otro, "Rosa", "dependiente", "adulto_mayor")
    crear_rutina(client, otro, ajeno["id"])
    vincular(client, otro, ajeno["id"], "pan3@perfilmedico.cl", puede_confirmar=True)

    items = _panel(client, yo).json()
    assert [i["perfil"]["nombre"] for i in items] == ["Yo", "Rosa"]
    propio, compartido = items
    assert (propio["total"], propio["confirmadas"], propio["pendientes"]) == (2, 0, 2)
    assert propio["mi_acceso"]["rol"] == "titular"
    assert (compartido["total"], compartido["confirmadas"], compartido["pendientes"]) == (1, 0, 1)
    assert compartido["mi_acceso"]["rol"] == "cuidador"
    assert compartido["perfil"]["subtipo"] == "adulto_mayor"


def test_los_contadores_cambian_al_confirmar(client):
    token = registrar_y_loguear(client, "pan4@perfilmedico.cl")
    perfil = crear_perfil(client, token)
    crear_medicamento(client, token, perfil["id"], "Med A", "08:00:00")
    crear_medicamento(client, token, perfil["id"], "Med B", "09:00:00")
    primera = actividades(client, token, perfil["id"]).json()[0]
    client.post(f"/actividades/{primera['id']}/confirmar", headers=headers(token))
    item = _panel(client, token).json()[0]
    assert (item["total"], item["confirmadas"], item["pendientes"]) == (2, 1, 1)
    client.post(f"/actividades/{primera['id']}/desconfirmar", headers=headers(token))
    item = _panel(client, token).json()[0]
    assert (item["confirmadas"], item["pendientes"]) == (0, 2)


def test_panel_no_incluye_perfiles_ajenos_ni_revocados(client):
    yo = registrar_y_loguear(client, "pan5@perfilmedico.cl")
    otro = registrar_y_loguear(client, "pan5otro@perfilmedico.cl")
    ajeno = crear_perfil(client, otro, "Rosa", "dependiente", "adulto_mayor")
    assert _panel(client, yo).json() == []
    vinculo = vincular(client, otro, ajeno["id"], "pan5@perfilmedico.cl")
    assert len(_panel(client, yo).json()) == 1
    client.delete(f"/perfiles/{ajeno['id']}/cuidadores/{vinculo['id']}", headers=headers(otro))
    assert _panel(client, yo).json() == []


def test_panel_omite_perfiles_inactivos(client):
    token = registrar_y_loguear(client, "pan6@perfilmedico.cl")
    crear_perfil(client, token)
    dep = crear_perfil(client, token, "Rosa", "dependiente", "adulto_mayor")
    client.put(f"/perfiles/{dep['id']}", json={"activo": False}, headers=headers(token))
    assert [i["perfil"]["nombre"] for i in _panel(client, token).json()] == ["Titular"]
