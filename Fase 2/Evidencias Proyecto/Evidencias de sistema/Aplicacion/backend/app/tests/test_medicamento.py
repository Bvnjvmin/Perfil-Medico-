"""
Pruebas de HU 4: medicamentos y rutinas de cuidado de un perfil propio.
Cubren el camino feliz de cada endpoint y que un titular nunca pueda ver
ni modificar los medicamentos o rutinas del perfil de otro.
"""


def _registrar_y_loguear(client, email: str) -> str:
    client.post(
        "/auth/register",
        json={"nombre": "Usuario de prueba", "email": email, "password": "clave-segura-123"},
    )
    login = client.post("/auth/login", data={"username": email, "password": "clave-segura-123"})
    return login.json()["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_perfil(client, token: str, nombre: str = "Perfil de prueba") -> dict:
    return client.post(
        "/perfiles", json={"tipo": "titular", "nombre": nombre}, headers=_headers(token)
    ).json()


def test_registrar_y_listar_medicamento(client):
    token = _registrar_y_loguear(client, "med1@perfilmedico.cl")
    perfil = _crear_perfil(client, token)

    respuesta = client.post(
        f"/perfiles/{perfil['id']}/medicamentos",
        json={"nombre": "Paracetamol", "dosis": "500 mg", "frecuencia": "cada 8 horas"},
        headers=_headers(token),
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["nombre"] == "Paracetamol"
    assert datos["activo"] is True

    listado = client.get(f"/perfiles/{perfil['id']}/medicamentos", headers=_headers(token))
    assert listado.status_code == 200
    assert len(listado.json()) == 1


def test_actualizar_medicamento_propio(client):
    token = _registrar_y_loguear(client, "med2@perfilmedico.cl")
    perfil = _crear_perfil(client, token)
    medicamento = client.post(
        f"/perfiles/{perfil['id']}/medicamentos",
        json={"nombre": "Ibuprofeno", "dosis": "400 mg", "frecuencia": "cada 12 horas"},
        headers=_headers(token),
    ).json()

    respuesta = client.put(
        f"/medicamentos/{medicamento['id']}",
        json={"activo": False},
        headers=_headers(token),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False


def test_eliminar_medicamento_propio(client):
    token = _registrar_y_loguear(client, "med3@perfilmedico.cl")
    perfil = _crear_perfil(client, token)
    medicamento = client.post(
        f"/perfiles/{perfil['id']}/medicamentos",
        json={"nombre": "Vitamina D", "dosis": "1 gota", "frecuencia": "una vez al día"},
        headers=_headers(token),
    ).json()

    respuesta = client.delete(f"/medicamentos/{medicamento['id']}", headers=_headers(token))
    assert respuesta.status_code == 204

    consulta = client.get(f"/medicamentos/{medicamento['id']}", headers=_headers(token))
    assert consulta.status_code == 404


def test_medicamento_de_perfil_ajeno_devuelve_404(client):
    token_a = _registrar_y_loguear(client, "med-a@perfilmedico.cl")
    token_b = _registrar_y_loguear(client, "med-b@perfilmedico.cl")
    perfil_a = _crear_perfil(client, token_a, "Perfil de A")
    medicamento = client.post(
        f"/perfiles/{perfil_a['id']}/medicamentos",
        json={"nombre": "Amoxicilina", "dosis": "250 mg", "frecuencia": "cada 8 horas"},
        headers=_headers(token_a),
    ).json()

    respuesta = client.get(f"/medicamentos/{medicamento['id']}", headers=_headers(token_b))
    assert respuesta.status_code == 404


def test_registrar_y_listar_rutina_cuidado(client):
    token = _registrar_y_loguear(client, "rutina1@perfilmedico.cl")
    perfil = _crear_perfil(client, token)

    respuesta = client.post(
        f"/perfiles/{perfil['id']}/rutinas",
        json={"tipo": "hidratacion", "descripcion": "Vaso de agua", "frecuencia": "cada 2 horas"},
        headers=_headers(token),
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["tipo"] == "hidratacion"

    listado = client.get(f"/perfiles/{perfil['id']}/rutinas", headers=_headers(token))
    assert listado.status_code == 200
    assert len(listado.json()) == 1


def test_actualizar_rutina_cuidado_propia(client):
    token = _registrar_y_loguear(client, "rutina2@perfilmedico.cl")
    perfil = _crear_perfil(client, token)
    rutina = client.post(
        f"/perfiles/{perfil['id']}/rutinas",
        json={"tipo": "alimentacion", "frecuencia": "3 veces al día"},
        headers=_headers(token),
    ).json()

    respuesta = client.put(
        f"/rutinas/{rutina['id']}",
        json={"descripcion": "Desayuno, almuerzo y cena", "activo": True},
        headers=_headers(token),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["descripcion"] == "Desayuno, almuerzo y cena"


def test_eliminar_rutina_cuidado_propia(client):
    token = _registrar_y_loguear(client, "rutina3@perfilmedico.cl")
    perfil = _crear_perfil(client, token)
    rutina = client.post(
        f"/perfiles/{perfil['id']}/rutinas",
        json={"tipo": "vitaminas", "frecuencia": "una vez al día"},
        headers=_headers(token),
    ).json()

    respuesta = client.delete(f"/rutinas/{rutina['id']}", headers=_headers(token))
    assert respuesta.status_code == 204

    consulta = client.get(f"/rutinas/{rutina['id']}", headers=_headers(token))
    assert consulta.status_code == 404


def test_rutina_de_perfil_ajeno_devuelve_404(client):
    token_a = _registrar_y_loguear(client, "rutina-a@perfilmedico.cl")
    token_b = _registrar_y_loguear(client, "rutina-b@perfilmedico.cl")
    perfil_a = _crear_perfil(client, token_a, "Perfil de A")
    rutina = client.post(
        f"/perfiles/{perfil_a['id']}/rutinas",
        json={"tipo": "hidratacion", "frecuencia": "cada 2 horas"},
        headers=_headers(token_a),
    ).json()

    respuesta = client.get(f"/rutinas/{rutina['id']}", headers=_headers(token_b))
    assert respuesta.status_code == 404
