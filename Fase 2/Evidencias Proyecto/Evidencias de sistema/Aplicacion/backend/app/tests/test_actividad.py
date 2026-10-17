"""
Pruebas de HU 5 (cierre): agenda diaria con confirmación guardada en el backend.
"""
from app.tests.helpers import (
    FECHA, MANANA, actividades, crear_medicamento, crear_perfil, crear_rutina, headers, registrar_y_loguear,
)


def _preparar(client, email="act1@perfilmedico.cl"):
    token = registrar_y_loguear(client, email)
    perfil = crear_perfil(client, token)
    return token, perfil


def test_genera_la_agenda_del_dia(client):
    token, perfil = _preparar(client)
    crear_medicamento(client, token, perfil["id"], "Paracetamol", "08:00:00")
    crear_rutina(client, token, perfil["id"], "hidratacion", "Vaso de agua", None)

    respuesta = actividades(client, token, perfil["id"])
    assert respuesta.status_code == 200
    lista = respuesta.json()
    assert len(lista) == 2
    # Ordenadas por hora: la que no tiene hora va al final.
    assert lista[0]["titulo"] == "Paracetamol"
    assert lista[0]["origen_tipo"] == "medicamento"
    assert lista[0]["detalle"] == "500 mg · cada 8 horas"
    assert lista[0]["hora"] == "08:00:00"
    assert lista[0]["estado"] == "pendiente"
    assert lista[1]["titulo"] == "Vaso de agua"
    assert lista[1]["origen_tipo"] == "rutina"
    assert lista[1]["detalle"] == "Hidratación · cada 2 horas"
    assert lista[1]["hora"] is None


def test_consultar_dos_veces_no_duplica(client):
    token, perfil = _preparar(client, "act2@perfilmedico.cl")
    crear_medicamento(client, token, perfil["id"])
    primera = actividades(client, token, perfil["id"]).json()
    segunda = actividades(client, token, perfil["id"]).json()
    assert len(primera) == len(segunda) == 1
    assert primera[0]["id"] == segunda[0]["id"]


def test_medicamento_inactivo_no_genera_actividad(client):
    token, perfil = _preparar(client, "act3@perfilmedico.cl")
    med = crear_medicamento(client, token, perfil["id"])
    client.put(f"/medicamentos/{med['id']}", json={"activo": False}, headers=headers(token))
    assert actividades(client, token, perfil["id"]).json() == []


def test_desactivar_despues_de_generar_oculta_la_actividad(client):
    token, perfil = _preparar(client, "act4@perfilmedico.cl")
    med = crear_medicamento(client, token, perfil["id"])
    assert len(actividades(client, token, perfil["id"]).json()) == 1
    client.put(f"/medicamentos/{med['id']}", json={"activo": False}, headers=headers(token))
    assert actividades(client, token, perfil["id"]).json() == []


def test_fecha_es_obligatoria(client):
    token, perfil = _preparar(client, "act5@perfilmedico.cl")
    respuesta = client.get(f"/perfiles/{perfil['id']}/actividades", headers=headers(token))
    assert respuesta.status_code == 422


def test_confirmar_y_desconfirmar_se_conservan(client):
    token, perfil = _preparar(client, "act6@perfilmedico.cl")
    crear_medicamento(client, token, perfil["id"])
    actividad = actividades(client, token, perfil["id"]).json()[0]

    confirmada = client.post(f"/actividades/{actividad['id']}/confirmar", headers=headers(token))
    assert confirmada.status_code == 200
    assert confirmada.json()["estado"] == "confirmada"
    assert confirmada.json()["confirmada_en"] is not None
    assert confirmada.json()["confirmada_por_id"] is not None
    # Se conserva al volver a consultar (esto antes vivía solo en el celular).
    assert actividades(client, token, perfil["id"]).json()[0]["estado"] == "confirmada"

    pendiente = client.post(f"/actividades/{actividad['id']}/desconfirmar", headers=headers(token))
    assert pendiente.status_code == 200
    assert pendiente.json()["estado"] == "pendiente"
    assert pendiente.json()["confirmada_en"] is None
    assert pendiente.json()["confirmada_por_id"] is None
    assert actividades(client, token, perfil["id"]).json()[0]["estado"] == "pendiente"


def test_confirmar_dos_veces_no_falla(client):
    token, perfil = _preparar(client, "act7@perfilmedico.cl")
    crear_medicamento(client, token, perfil["id"])
    actividad = actividades(client, token, perfil["id"]).json()[0]
    primera = client.post(f"/actividades/{actividad['id']}/confirmar", headers=headers(token)).json()
    segunda = client.post(f"/actividades/{actividad['id']}/confirmar", headers=headers(token))
    assert segunda.status_code == 200
    assert segunda.json()["confirmada_en"] == primera["confirmada_en"]


def test_cada_dia_tiene_sus_actividades(client):
    token, perfil = _preparar(client, "act8@perfilmedico.cl")
    crear_medicamento(client, token, perfil["id"])
    hoy = actividades(client, token, perfil["id"], FECHA).json()[0]
    client.post(f"/actividades/{hoy['id']}/confirmar", headers=headers(token))
    manana = actividades(client, token, perfil["id"], MANANA).json()
    assert len(manana) == 1
    assert manana[0]["estado"] == "pendiente"
    assert manana[0]["id"] != hoy["id"]


def test_otra_cuenta_recibe_404(client):
    token, perfil = _preparar(client, "act9@perfilmedico.cl")
    crear_medicamento(client, token, perfil["id"])
    actividad = actividades(client, token, perfil["id"]).json()[0]
    ajeno = registrar_y_loguear(client, "ajeno9@perfilmedico.cl")
    assert actividades(client, ajeno, perfil["id"]).status_code == 404
    assert client.post(f"/actividades/{actividad['id']}/confirmar", headers=headers(ajeno)).status_code == 404
    assert client.post(f"/actividades/{actividad['id']}/desconfirmar", headers=headers(ajeno)).status_code == 404


def test_actividad_inexistente_404(client):
    token, _ = _preparar(client, "act10@perfilmedico.cl")
    respuesta = client.post("/actividades/00000000-0000-0000-0000-000000000000/confirmar", headers=headers(token))
    assert respuesta.status_code == 404


def test_borrar_medicamento_borra_sus_actividades(client):
    token, perfil = _preparar(client, "act11@perfilmedico.cl")
    med = crear_medicamento(client, token, perfil["id"])
    actividad = actividades(client, token, perfil["id"]).json()[0]
    assert client.delete(f"/medicamentos/{med['id']}", headers=headers(token)).status_code == 204
    assert client.post(f"/actividades/{actividad['id']}/confirmar", headers=headers(token)).status_code == 404
    assert actividades(client, token, perfil["id"]).json() == []


def test_borrar_rutina_borra_sus_actividades(client):
    token, perfil = _preparar(client, "act12@perfilmedico.cl")
    rutina = crear_rutina(client, token, perfil["id"])
    actividad = actividades(client, token, perfil["id"]).json()[0]
    assert client.delete(f"/rutinas/{rutina['id']}", headers=headers(token)).status_code == 204
    assert client.post(f"/actividades/{actividad['id']}/confirmar", headers=headers(token)).status_code == 404
