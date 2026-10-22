"""
Pruebas del Sprint 4 (habilitador): horarios de medicamentos y rutinas, y su efecto
en la agenda y en la generación programada de actividades.
"""
from app.models.actividad import Actividad
from app.models.rutina_horario import RutinaHorario
from app.services.actividades import generar_actividades_programadas
from app.tests.conftest import TestingSessionLocal
from app.tests.helpers import (
    MANANA, actividades, crear_medicamento, crear_perfil, crear_rutina, headers, registrar_y_loguear, vincular,
)


def _preparar(client, email):
    token = registrar_y_loguear(client, email)
    perfil = crear_perfil(client, token)
    medicamento = crear_medicamento(client, token, perfil["id"], "Metformina", "08:00:00")
    return token, perfil, medicamento


def _agregar(client, token, medicamento_id, hora):
    return client.post(f"/medicamentos/{medicamento_id}/horarios", json={"hora": hora}, headers=headers(token))


def test_agrega_y_lista_horarios_ordenados(client):
    token, _, med = _preparar(client, "hor1@perfilmedico.cl")
    assert _agregar(client, token, med["id"], "20:00").status_code == 201
    assert _agregar(client, token, med["id"], "08:00").status_code == 201

    lista = client.get(f"/medicamentos/{med['id']}/horarios", headers=headers(token)).json()
    assert [h["hora"] for h in lista] == ["08:00:00", "20:00:00"]
    assert all(h["medicamento_id"] == med["id"] and h["rutina_id"] is None for h in lista)


def test_la_agenda_usa_los_horarios_en_vez_de_la_hora_unica(client):
    token, perfil, med = _preparar(client, "hor2@perfilmedico.cl")
    _agregar(client, token, med["id"], "09:00")
    _agregar(client, token, med["id"], "21:00")

    agenda = actividades(client, token, perfil["id"]).json()
    assert [a["hora"] for a in agenda] == ["09:00:00", "21:00:00"]
    assert {a["titulo"] for a in agenda} == {"Metformina"}


def test_sin_horarios_se_mantiene_la_hora_unica(client):
    token, perfil, _ = _preparar(client, "hor3@perfilmedico.cl")
    agenda = actividades(client, token, perfil["id"]).json()
    assert [a["hora"] for a in agenda] == ["08:00:00"]


def test_hora_repetida_devuelve_409(client):
    token, _, med = _preparar(client, "hor4@perfilmedico.cl")
    assert _agregar(client, token, med["id"], "10:00").status_code == 201
    repetida = _agregar(client, token, med["id"], "10:00")
    assert repetida.status_code == 409
    assert repetida.json()["detail"] == "Ya existe un horario a esa hora"


def test_hora_invalida_devuelve_422(client):
    token, _, med = _preparar(client, "hor5@perfilmedico.cl")
    assert _agregar(client, token, med["id"], "25:99").status_code == 422


def test_quitar_un_horario_ajusta_la_agenda(client):
    token, perfil, med = _preparar(client, "hor6@perfilmedico.cl")
    a = _agregar(client, token, med["id"], "09:00").json()
    _agregar(client, token, med["id"], "21:00")
    assert len(actividades(client, token, perfil["id"]).json()) == 2

    assert client.delete(f"/horarios/{a['id']}", headers=headers(token)).status_code == 204
    agenda = actividades(client, token, perfil["id"]).json()
    assert [x["hora"] for x in agenda] == ["21:00:00"]
    assert client.delete(f"/horarios/{a['id']}", headers=headers(token)).status_code == 404


def test_horarios_de_una_rutina(client):
    token = registrar_y_loguear(client, "hor7@perfilmedico.cl")
    perfil = crear_perfil(client, token)
    rutina = crear_rutina(client, token, perfil["id"], "hidratacion", "Vaso de agua")
    for hora in ("10:00", "12:00", "16:00"):
        assert client.post(f"/rutinas/{rutina['id']}/horarios", json={"hora": hora}, headers=headers(token)).status_code == 201
    lista = client.get(f"/rutinas/{rutina['id']}/horarios", headers=headers(token)).json()
    assert [h["hora"] for h in lista] == ["10:00:00", "12:00:00", "16:00:00"]
    assert all(h["rutina_id"] == rutina["id"] for h in lista)
    assert len(actividades(client, token, perfil["id"]).json()) == 3


def test_permisos_de_los_horarios(client):
    titular = registrar_y_loguear(client, "hor8-titular@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "hor8-cuidador@perfilmedico.cl")
    editor = registrar_y_loguear(client, "hor8-editor@perfilmedico.cl")
    ajena = registrar_y_loguear(client, "hor8-ajena@perfilmedico.cl")
    perfil = crear_perfil(client, titular)
    med = crear_medicamento(client, titular, perfil["id"])
    vincular(client, titular, perfil["id"], "hor8-cuidador@perfilmedico.cl")
    vincular(client, titular, perfil["id"], "hor8-editor@perfilmedico.cl", puede_editar_rutinas=True)

    # El cuidador sin permiso de edición puede ver pero no agregar ni quitar.
    assert client.get(f"/medicamentos/{med['id']}/horarios", headers=headers(cuidador)).status_code == 200
    assert _agregar(client, cuidador, med["id"], "11:00").status_code == 403
    # Con permiso de edición puede agregar y quitar.
    creado = _agregar(client, editor, med["id"], "11:00")
    assert creado.status_code == 201
    assert client.delete(f"/horarios/{creado.json()['id']}", headers=headers(cuidador)).status_code == 403
    assert client.delete(f"/horarios/{creado.json()['id']}", headers=headers(editor)).status_code == 204
    # Una cuenta sin vínculo recibe 404 en todo.
    assert client.get(f"/medicamentos/{med['id']}/horarios", headers=headers(ajena)).status_code == 404
    assert _agregar(client, ajena, med["id"], "12:00").status_code == 404


def test_borrar_el_medicamento_borra_sus_horarios_y_actividades(client):
    token, perfil, med = _preparar(client, "hor9@perfilmedico.cl")
    _agregar(client, token, med["id"], "09:00")
    _agregar(client, token, med["id"], "21:00")
    actividades(client, token, perfil["id"])

    assert client.delete(f"/medicamentos/{med['id']}", headers=headers(token)).status_code == 204
    db = TestingSessionLocal()
    try:
        assert db.query(RutinaHorario).count() == 0
        assert db.query(Actividad).count() == 0
    finally:
        db.close()


def test_generacion_programada_crea_hoy_y_manana_sin_duplicar(client):
    token, perfil, med = _preparar(client, "hor10@perfilmedico.cl")
    _agregar(client, token, med["id"], "09:00")
    _agregar(client, token, med["id"], "21:00")

    db = TestingSessionLocal()
    try:
        assert generar_actividades_programadas(db) == 1
        generar_actividades_programadas(db)  # una segunda corrida no duplica
        assert db.query(Actividad).count() == 4  # 2 horas x (hoy y mañana)
    finally:
        db.close()
    # Lo generado por la tarea es lo mismo que ve la agenda de mañana.
    assert len(actividades(client, token, perfil["id"], MANANA).json()) == 2
