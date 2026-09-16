"""
Pruebas del flujo de autenticación: registro, login, y consulta del usuario
actual con el token. Cubren tanto el camino feliz como los errores esperados
(correo duplicado, contraseña incorrecta, token inválido).
"""


def test_registrar_usuario_nuevo(client):
    respuesta = client.post(
        "/auth/register",
        json={
            "nombre": "Benjamín Leiva",
            "email": "benjamin@perfilmedico.cl",
            "password": "clave-segura-123",
            "rol": "titular",
        },
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["email"] == "benjamin@perfilmedico.cl"
    assert datos["rol"] == "titular"
    assert "hashed_password" not in datos  # nunca se debe filtrar la contraseña


def test_no_permite_correo_duplicado(client):
    payload = {
        "nombre": "Sergio Ocares",
        "email": "sergio@perfilmedico.cl",
        "password": "clave-segura-123",
        "rol": "cuidador",
    }
    primera = client.post("/auth/register", json=payload)
    assert primera.status_code == 201

    segunda = client.post("/auth/register", json=payload)
    assert segunda.status_code == 400
    assert "ya existe" in segunda.json()["detail"].lower()


def test_login_exitoso_devuelve_token(client):
    client.post(
        "/auth/register",
        json={
            "nombre": "Matías Pizarro",
            "email": "matias@perfilmedico.cl",
            "password": "clave-segura-123",
            "rol": "titular",
        },
    )

    respuesta = client.post(
        "/auth/login",
        data={"username": "matias@perfilmedico.cl", "password": "clave-segura-123"},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert "access_token" in datos
    assert datos["token_type"] == "bearer"


def test_login_con_contrasena_incorrecta_falla(client):
    client.post(
        "/auth/register",
        json={
            "nombre": "Usuario Prueba",
            "email": "prueba@perfilmedico.cl",
            "password": "clave-correcta",
            "rol": "titular",
        },
    )

    respuesta = client.post(
        "/auth/login",
        data={"username": "prueba@perfilmedico.cl", "password": "clave-incorrecta"},
    )
    assert respuesta.status_code == 401


def test_me_devuelve_usuario_del_token(client):
    client.post(
        "/auth/register",
        json={
            "nombre": "Ana Cuidadora",
            "email": "ana@perfilmedico.cl",
            "password": "clave-segura-123",
            "rol": "cuidador",
        },
    )
    login = client.post(
        "/auth/login",
        data={"username": "ana@perfilmedico.cl", "password": "clave-segura-123"},
    )
    token = login.json()["access_token"]

    respuesta = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == "ana@perfilmedico.cl"


def test_me_sin_token_rechaza_acceso(client):
    respuesta = client.get("/auth/me")
    assert respuesta.status_code == 401


def test_me_con_token_invalido_rechaza_acceso(client):
    respuesta = client.get(
        "/auth/me", headers={"Authorization": "Bearer token-falso-e-invalido"}
    )
    assert respuesta.status_code == 401
