"""Funciones auxiliares compartidas por las pruebas de HU 5, 6, 7 y 8."""
FECHA = "2026-10-14"


def registrar_y_loguear(client, email: str) -> str:
    """Registra un usuario nuevo y devuelve su token de acceso."""
    client.post(
        "/auth/register",
        json={"nombre": email.split("@")[0], "email": email, "password": "clave-segura-123"},
    )
    login = client.post("/auth/login", data={"username": email, "password": "clave-segura-123"})
    return login.json()["access_token"]


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def crear_perfil(client, token: str, nombre: str = "Titular", tipo: str = "titular", subtipo=None) -> dict:
    cuerpo = {"tipo": tipo, "nombre": nombre}
    if subtipo:
        cuerpo["subtipo"] = subtipo
    respuesta = client.post("/perfiles", json=cuerpo, headers=headers(token))
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def crear_medicamento(client, token: str, perfil_id: str, nombre="Paracetamol", hora="08:00:00") -> dict:
    cuerpo = {"nombre": nombre, "dosis": "500 mg", "frecuencia": "cada 8 horas"}
    if hora:
        cuerpo["hora_inicio"] = hora
    respuesta = client.post(f"/perfiles/{perfil_id}/medicamentos", json=cuerpo, headers=headers(token))
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def crear_rutina(client, token: str, perfil_id: str, tipo="hidratacion", descripcion="Vaso de agua", hora=None) -> dict:
    cuerpo = {"tipo": tipo, "descripcion": descripcion, "frecuencia": "cada 2 horas"}
    if hora:
        cuerpo["hora"] = hora
    respuesta = client.post(f"/perfiles/{perfil_id}/rutinas", json=cuerpo, headers=headers(token))
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def vincular(client, token_titular: str, perfil_id: str, email: str, **permisos) -> dict:
    cuerpo = {"email": email, **permisos}
    respuesta = client.post(f"/perfiles/{perfil_id}/cuidadores", json=cuerpo, headers=headers(token_titular))
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def actividades(client, token: str, perfil_id: str, fecha: str = FECHA):
    return client.get(f"/perfiles/{perfil_id}/actividades", params={"fecha": fecha}, headers=headers(token))
