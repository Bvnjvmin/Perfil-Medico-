"""
Pruebas de HU 2: datos básicos de salud del titular (perfil, alergias y
contactos de emergencia). Cubren el camino feliz de cada endpoint y que
un titular nunca pueda ver ni modificar el perfil de otro.
"""


def _registrar_y_loguear(client, email: str) -> str:
    """Registra un usuario nuevo y devuelve su token de acceso."""
    client.post(
        "/auth/register",
        json={"nombre": "Usuario de prueba", "email": email, "password": "clave-segura-123"},
    )
    login = client.post(
        "/auth/login",
        data={"username": email, "password": "clave-segura-123"},
    )
    return login.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_crear_perfil(client):
    token = _registrar_y_loguear(client, "titular1@perfilmedico.cl")
    respuesta = client.post(
        "/perfiles",
        json={"tipo": "titular", "nombre": "Ana Cuidadora", "rut": "11.111.111-1", "grupo_sanguineo": "O+"},
        headers=_headers(token),
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["nombre"] == "Ana Cuidadora"
    assert datos["grupo_sanguineo"] == "O+"
    assert datos["activo"] is True


def test_crear_perfil_sin_token_rechaza_acceso(client):
    respuesta = client.post("/perfiles", json={"tipo": "titular", "nombre": "Sin token"})
    assert respuesta.status_code == 401


def test_listar_perfiles_devuelve_solo_los_propios(client):
    token_a = _registrar_y_loguear(client, "titular-a@perfilmedico.cl")
    token_b = _registrar_y_loguear(client, "titular-b@perfilmedico.cl")

    client.post("/perfiles", json={"tipo": "titular", "nombre": "Perfil de A"}, headers=_headers(token_a))
    client.post("/perfiles", json={"tipo": "titular", "nombre": "Perfil de B"}, headers=_headers(token_b))

    respuesta = client.get("/perfiles", headers=_headers(token_a))
    assert respuesta.status_code == 200
    nombres = [p["nombre"] for p in respuesta.json()]
    assert nombres == ["Perfil de A"]


def test_obtener_perfil_de_otro_titular_devuelve_404(client):
    token_a = _registrar_y_loguear(client, "a2@perfilmedico.cl")
    token_b = _registrar_y_loguear(client, "b2@perfilmedico.cl")

    creado = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Perfil de A"}, headers=_headers(token_a)
    ).json()

    respuesta = client.get(f"/perfiles/{creado['id']}", headers=_headers(token_b))
    assert respuesta.status_code == 404


def test_actualizar_perfil_propio(client):
    token = _registrar_y_loguear(client, "actualiza@perfilmedico.cl")
    creado = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Nombre viejo"}, headers=_headers(token)
    ).json()

    respuesta = client.put(
        f"/perfiles/{creado['id']}",
        json={"nombre": "Nombre nuevo", "grupo_sanguineo": "A-"},
        headers=_headers(token),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Nombre nuevo"
    assert respuesta.json()["grupo_sanguineo"] == "A-"


def test_eliminar_perfil_propio(client):
    token = _registrar_y_loguear(client, "elimina@perfilmedico.cl")
    creado = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Perfil a borrar"}, headers=_headers(token)
    ).json()

    respuesta = client.delete(f"/perfiles/{creado['id']}", headers=_headers(token))
    assert respuesta.status_code == 204

    consulta = client.get(f"/perfiles/{creado['id']}", headers=_headers(token))
    assert consulta.status_code == 404


def test_agregar_y_listar_alergias(client):
    token = _registrar_y_loguear(client, "alergias@perfilmedico.cl")
    perfil = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Con alergias"}, headers=_headers(token)
    ).json()

    respuesta = client.post(
        f"/perfiles/{perfil['id']}/alergias",
        json={"sustancia": "Penicilina", "severidad": "grave"},
        headers=_headers(token),
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["sustancia"] == "Penicilina"

    listado = client.get(f"/perfiles/{perfil['id']}/alergias", headers=_headers(token))
    assert listado.status_code == 200
    assert len(listado.json()) == 1


def test_agregar_alergia_a_perfil_ajeno_devuelve_404(client):
    token_a = _registrar_y_loguear(client, "a3@perfilmedico.cl")
    token_b = _registrar_y_loguear(client, "b3@perfilmedico.cl")
    perfil_a = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Perfil de A"}, headers=_headers(token_a)
    ).json()

    respuesta = client.post(
        f"/perfiles/{perfil_a['id']}/alergias",
        json={"sustancia": "Maní", "severidad": "leve"},
        headers=_headers(token_b),
    )
    assert respuesta.status_code == 404


def test_agregar_y_listar_contactos_emergencia(client):
    token = _registrar_y_loguear(client, "contactos@perfilmedico.cl")
    perfil = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Con contactos"}, headers=_headers(token)
    ).json()

    respuesta = client.post(
        f"/perfiles/{perfil['id']}/contactos-emergencia",
        json={"nombre": "Pedro Pérez", "telefono": "+56912345678", "relacion": "hijo", "prioridad": 1},
        headers=_headers(token),
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Pedro Pérez"

    listado = client.get(f"/perfiles/{perfil['id']}/contactos-emergencia", headers=_headers(token))
    assert listado.status_code == 200
    assert len(listado.json()) == 1


def test_eliminar_contacto_emergencia(client):
    token = _registrar_y_loguear(client, "elimina-contacto@perfilmedico.cl")
    perfil = client.post(
        "/perfiles", json={"tipo": "titular", "nombre": "Con contacto a borrar"}, headers=_headers(token)
    ).json()
    contacto = client.post(
        f"/perfiles/{perfil['id']}/contactos-emergencia",
        json={"nombre": "Contacto temporal", "telefono": "+56900000000"},
        headers=_headers(token),
    ).json()

    respuesta = client.delete(
        f"/perfiles/{perfil['id']}/contactos-emergencia/{contacto['id']}", headers=_headers(token)
    )
    assert respuesta.status_code == 204

    listado = client.get(f"/perfiles/{perfil['id']}/contactos-emergencia", headers=_headers(token))
    assert listado.json() == []
