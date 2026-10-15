"""
Pruebas de HU 6: perfiles de dependientes (adulto mayor o niño) validados y
con borrado completo.
"""
from app.tests.helpers import (
    actividades, crear_medicamento, crear_perfil, crear_rutina, headers, registrar_y_loguear, vincular,
)


def test_crear_dependiente_valido(client):
    token = registrar_y_loguear(client, "dep1@perfilmedico.cl")
    crear_perfil(client, token)
    for subtipo in ("adulto_mayor", "nino"):
        perfil = crear_perfil(client, token, "Rosa", "dependiente", subtipo)
        assert perfil["tipo"] == "dependiente"
        assert perfil["subtipo"] == subtipo
        assert perfil["mi_acceso"]["rol"] == "titular"


def test_dependiente_sin_subtipo_se_rechaza(client):
    token = registrar_y_loguear(client, "dep2@perfilmedico.cl")
    respuesta = client.post("/perfiles", json={"tipo": "dependiente", "nombre": "Rosa"}, headers=headers(token))
    assert respuesta.status_code == 422


def test_subtipo_invalido_se_rechaza(client):
    token = registrar_y_loguear(client, "dep3@perfilmedico.cl")
    respuesta = client.post(
        "/perfiles",
        json={"tipo": "dependiente", "nombre": "Rosa", "subtipo": "mascota"},
        headers=headers(token),
    )
    assert respuesta.status_code == 422


def test_tipo_invalido_se_rechaza(client):
    token = registrar_y_loguear(client, "dep4@perfilmedico.cl")
    respuesta = client.post("/perfiles", json={"tipo": "cuidador", "nombre": "Ana"}, headers=headers(token))
    assert respuesta.status_code == 422


def test_titular_con_subtipo_se_rechaza(client):
    token = registrar_y_loguear(client, "dep5@perfilmedico.cl")
    respuesta = client.post(
        "/perfiles",
        json={"tipo": "titular", "nombre": "Ana", "subtipo": "adulto_mayor"},
        headers=headers(token),
    )
    assert respuesta.status_code == 422


def test_segundo_titular_responde_409(client):
    token = registrar_y_loguear(client, "dep6@perfilmedico.cl")
    crear_perfil(client, token)
    respuesta = client.post("/perfiles", json={"tipo": "titular", "nombre": "Otro"}, headers=headers(token))
    assert respuesta.status_code == 409


def test_dos_cuentas_pueden_tener_cada_una_su_titular(client):
    a = registrar_y_loguear(client, "dep7a@perfilmedico.cl")
    b = registrar_y_loguear(client, "dep7b@perfilmedico.cl")
    crear_perfil(client, a)
    crear_perfil(client, b)


def test_listado_trae_titular_y_dependientes_en_orden(client):
    token = registrar_y_loguear(client, "dep8@perfilmedico.cl")
    crear_perfil(client, token, "Yo")
    crear_perfil(client, token, "Rosa", "dependiente", "adulto_mayor")
    crear_perfil(client, token, "Tomás", "dependiente", "nino")
    lista = client.get("/perfiles", headers=headers(token)).json()
    assert [p["nombre"] for p in lista] == ["Yo", "Rosa", "Tomás"]
    assert [p["tipo"] for p in lista] == ["titular", "dependiente", "dependiente"]


def test_actualizar_subtipo_de_dependiente(client):
    token = registrar_y_loguear(client, "dep9@perfilmedico.cl")
    dep = crear_perfil(client, token, "Rosa", "dependiente", "adulto_mayor")
    ok = client.put(f"/perfiles/{dep['id']}", json={"subtipo": "nino"}, headers=headers(token))
    assert ok.status_code == 200 and ok.json()["subtipo"] == "nino"
    malo = client.put(f"/perfiles/{dep['id']}", json={"subtipo": "otro"}, headers=headers(token))
    assert malo.status_code == 422
    sin = client.put(f"/perfiles/{dep['id']}", json={"subtipo": None}, headers=headers(token))
    assert sin.status_code == 422


def test_titular_no_puede_recibir_subtipo_al_actualizar(client):
    token = registrar_y_loguear(client, "dep10@perfilmedico.cl")
    titular = crear_perfil(client, token)
    respuesta = client.put(f"/perfiles/{titular['id']}", json={"subtipo": "nino"}, headers=headers(token))
    assert respuesta.status_code == 422


def test_borrar_perfil_con_todo_lo_asociado(client):
    """Antes fallaba en PostgreSQL: el perfil tenía medicamentos, rutinas y actividades."""
    token = registrar_y_loguear(client, "dep11@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "cuidador11@perfilmedico.cl")
    crear_perfil(client, token)
    dep = crear_perfil(client, token, "Rosa", "dependiente", "adulto_mayor")
    crear_medicamento(client, token, dep["id"])
    crear_rutina(client, token, dep["id"])
    client.post(f"/perfiles/{dep['id']}/alergias", json={"sustancia": "Penicilina", "severidad": "grave"}, headers=headers(token))
    client.post(
        f"/perfiles/{dep['id']}/contactos-emergencia",
        json={"nombre": "Hijo", "telefono": "+56911111111"},
        headers=headers(token),
    )
    vincular(client, token, dep["id"], "cuidador11@perfilmedico.cl")
    assert len(actividades(client, token, dep["id"]).json()) == 2

    assert client.delete(f"/perfiles/{dep['id']}", headers=headers(token)).status_code == 204
    assert client.get(f"/perfiles/{dep['id']}", headers=headers(token)).status_code == 404
    # El cuidador ya no ve el perfil y el titular conserva el suyo.
    assert [p["tipo"] for p in client.get("/perfiles", headers=headers(cuidador)).json()] == []
    assert [p["tipo"] for p in client.get("/perfiles", headers=headers(token)).json()] == ["titular"]
