"""
Pruebas de HU 7: cuidadores vinculados a un perfil y matriz de permisos.

Se usan tres cuentas: el dueño (titular), un cuidador, una persona de solo
lectura y una cuenta ajena sin ningún vínculo.
"""
import pytest

from app.tests.helpers import (
    actividades, crear_medicamento, crear_perfil, crear_rutina, headers, registrar_y_loguear, vincular,
)


@pytest.fixture()
def escenario(client):
    """Dueño con un dependiente que tiene medicamento y rutina; cuidador (confirma), lectura y ajena."""
    dueno = registrar_y_loguear(client, "dueno@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "cuidador@perfilmedico.cl")
    lectura = registrar_y_loguear(client, "lectura@perfilmedico.cl")
    ajena = registrar_y_loguear(client, "ajena@perfilmedico.cl")
    crear_perfil(client, dueno, "Dueño")
    perfil = crear_perfil(client, dueno, "Rosa", "dependiente", "adulto_mayor")
    med = crear_medicamento(client, dueno, perfil["id"])
    rutina = crear_rutina(client, dueno, perfil["id"])
    client.post(f"/perfiles/{perfil['id']}/alergias", json={"sustancia": "Polen", "severidad": "leve"}, headers=headers(dueno))
    vincular(client, dueno, perfil["id"], "cuidador@perfilmedico.cl", rol_vinculo="cuidador", puede_confirmar=True, puede_editar_rutinas=False)
    vincular(client, dueno, perfil["id"], "lectura@perfilmedico.cl", rol_vinculo="lectura")
    act = actividades(client, dueno, perfil["id"]).json()[0]
    return {
        "client": client, "perfil": perfil["id"], "med": med["id"], "rutina": rutina["id"], "act": act["id"],
        "dueno": dueno, "cuidador": cuidador, "lectura": lectura, "ajena": ajena,
    }


def _status(e, quien, metodo, ruta, **kw):
    return getattr(e["client"], metodo)(ruta, headers=headers(e[quien]), **kw).status_code


# --- Ver: dueño, cuidador y lectura pueden; la ajena recibe 404 -----------

@pytest.mark.parametrize("quien,esperado", [("dueno", 200), ("cuidador", 200), ("lectura", 200), ("ajena", 404)])
@pytest.mark.parametrize(
    "ruta",
    ["", "/alergias", "/contactos-emergencia", "/medicamentos", "/rutinas", "/actividades?fecha=2026-10-14"],
)
def test_ver_el_perfil(escenario, ruta, quien, esperado):
    assert _status(escenario, quien, "get", f"/perfiles/{escenario['perfil']}{ruta}") == esperado


@pytest.mark.parametrize("quien,esperado", [("dueno", 200), ("cuidador", 200), ("lectura", 200), ("ajena", 404)])
def test_ver_un_medicamento_y_una_rutina(escenario, quien, esperado):
    assert _status(escenario, quien, "get", f"/medicamentos/{escenario['med']}") == esperado
    assert _status(escenario, quien, "get", f"/rutinas/{escenario['rutina']}") == esperado


# --- Confirmar: dueño sí; cuidador con puede_confirmar sí; lectura 403; ajena 404 ---

@pytest.mark.parametrize("quien,esperado", [("dueno", 200), ("cuidador", 200), ("lectura", 403), ("ajena", 404)])
def test_confirmar_y_desconfirmar(escenario, quien, esperado):
    assert _status(escenario, quien, "post", f"/actividades/{escenario['act']}/confirmar") == esperado
    assert _status(escenario, quien, "post", f"/actividades/{escenario['act']}/desconfirmar") == esperado


def test_cuidador_sin_puede_confirmar_recibe_403(escenario):
    c = escenario["client"]
    acceso = c.get(f"/perfiles/{escenario['perfil']}/cuidadores", headers=headers(escenario["dueno"])).json()
    vinculo = next(v for v in acceso if v["email"] == "cuidador@perfilmedico.cl")
    c.put(
        f"/perfiles/{escenario['perfil']}/cuidadores/{vinculo['id']}",
        json={"puede_confirmar": False},
        headers=headers(escenario["dueno"]),
    )
    assert _status(escenario, "cuidador", "post", f"/actividades/{escenario['act']}/confirmar") == 403
    # Sigue viendo el perfil.
    assert _status(escenario, "cuidador", "get", f"/perfiles/{escenario['perfil']}") == 200


def test_quien_confirma_queda_registrado(escenario):
    c = escenario["client"]
    respuesta = c.post(f"/actividades/{escenario['act']}/confirmar", headers=headers(escenario["cuidador"])).json()
    yo = c.get("/auth/me", headers=headers(escenario["cuidador"])).json()
    assert respuesta["confirmada_por_id"] == yo["id"]
    # El dueño ve la confirmación del cuidador.
    vista = actividades(c, escenario["dueno"], escenario["perfil"]).json()
    assert next(a for a in vista if a["id"] == escenario["act"])["estado"] == "confirmada"


# --- Crear/editar/borrar medicamentos y rutinas ------------------------------

@pytest.mark.parametrize("quien,esperado", [("dueno", 201), ("cuidador", 403), ("lectura", 403), ("ajena", 404)])
def test_crear_medicamento_y_rutina(escenario, quien, esperado):
    med = {"nombre": "Ibuprofeno", "dosis": "400 mg", "frecuencia": "cada 12 horas"}
    rut = {"tipo": "vitaminas", "frecuencia": "una vez al día"}
    assert _status(escenario, quien, "post", f"/perfiles/{escenario['perfil']}/medicamentos", json=med) == esperado
    assert _status(escenario, quien, "post", f"/perfiles/{escenario['perfil']}/rutinas", json=rut) == esperado


@pytest.mark.parametrize("quien,esperado", [("cuidador", 403), ("lectura", 403), ("ajena", 404)])
def test_editar_y_borrar_medicamento_sin_permiso(escenario, quien, esperado):
    assert _status(escenario, quien, "put", f"/medicamentos/{escenario['med']}", json={"activo": False}) == esperado
    assert _status(escenario, quien, "delete", f"/medicamentos/{escenario['med']}") == esperado
    assert _status(escenario, quien, "put", f"/rutinas/{escenario['rutina']}", json={"activo": False}) == esperado
    assert _status(escenario, quien, "delete", f"/rutinas/{escenario['rutina']}") == esperado


def test_cuidador_con_puede_editar_rutinas_si_puede(client):
    dueno = registrar_y_loguear(client, "d2@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "c2@perfilmedico.cl")
    perfil = crear_perfil(client, dueno, "Rosa", "dependiente", "adulto_mayor")
    vincular(client, dueno, perfil["id"], "c2@perfilmedico.cl", puede_editar_rutinas=True)
    med = crear_medicamento(client, cuidador, perfil["id"], "Aspirina")
    assert client.put(f"/medicamentos/{med['id']}", json={"dosis": "100 mg"}, headers=headers(cuidador)).status_code == 200
    assert client.delete(f"/medicamentos/{med['id']}", headers=headers(cuidador)).status_code == 204


# --- Editar/borrar el perfil, alergias y contactos: solo el dueño -------------

@pytest.mark.parametrize("quien,esperado", [("cuidador", 403), ("lectura", 403), ("ajena", 404)])
def test_editar_y_borrar_el_perfil_sin_ser_dueno(escenario, quien, esperado):
    assert _status(escenario, quien, "put", f"/perfiles/{escenario['perfil']}", json={"nombre": "Otro"}) == esperado
    assert _status(escenario, quien, "delete", f"/perfiles/{escenario['perfil']}") == esperado


@pytest.mark.parametrize("quien,esperado", [("cuidador", 403), ("lectura", 403), ("ajena", 404)])
def test_agregar_alergia_y_contacto_sin_ser_dueno(escenario, quien, esperado):
    alergia = {"sustancia": "Nueces", "severidad": "grave"}
    contacto = {"nombre": "Hijo", "telefono": "+56922222222"}
    assert _status(escenario, quien, "post", f"/perfiles/{escenario['perfil']}/alergias", json=alergia) == esperado
    assert _status(escenario, quien, "post", f"/perfiles/{escenario['perfil']}/contactos-emergencia", json=contacto) == esperado


# --- Administrar cuidadores: solo el dueño -------------------------------------

@pytest.mark.parametrize("quien,esperado", [("dueno", 200), ("cuidador", 403), ("lectura", 403), ("ajena", 404)])
def test_listar_cuidadores(escenario, quien, esperado):
    assert _status(escenario, quien, "get", f"/perfiles/{escenario['perfil']}/cuidadores") == esperado


@pytest.mark.parametrize("quien,esperado", [("cuidador", 403), ("lectura", 403), ("ajena", 404)])
def test_vincular_sin_ser_dueno(escenario, quien, esperado):
    assert _status(
        escenario, quien, "post", f"/perfiles/{escenario['perfil']}/cuidadores", json={"email": "ajena@perfilmedico.cl"}
    ) == esperado


# --- Vincular, duplicar, errores, permisos y revocación ----------------------

def test_vincular_y_ver_el_perfil_en_el_listado(client):
    dueno = registrar_y_loguear(client, "d3@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "c3@perfilmedico.cl")
    crear_perfil(client, cuidador, "Mi perfil")
    perfil = crear_perfil(client, dueno, "Rosa", "dependiente", "adulto_mayor")
    vinculo = vincular(client, dueno, perfil["id"], "c3@perfilmedico.cl", puede_confirmar=True, puede_editar_rutinas=False)
    assert vinculo["email"] == "c3@perfilmedico.cl" and vinculo["rol_vinculo"] == "cuidador"

    lista = client.get("/perfiles", headers=headers(cuidador)).json()
    assert [p["nombre"] for p in lista] == ["Mi perfil", "Rosa"]  # primero los propios
    assert lista[0]["mi_acceso"]["rol"] == "titular"
    assert lista[1]["mi_acceso"] == {"rol": "cuidador", "puede_confirmar": True, "puede_editar_rutinas": False}
    # Y por id.
    uno = client.get(f"/perfiles/{perfil['id']}", headers=headers(cuidador)).json()
    assert uno["mi_acceso"]["rol"] == "cuidador"


def test_vincular_correo_inexistente_404(client):
    dueno = registrar_y_loguear(client, "d4@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    respuesta = client.post(
        f"/perfiles/{perfil['id']}/cuidadores", json={"email": "nadie@perfilmedico.cl"}, headers=headers(dueno)
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "No existe una cuenta con ese correo"


def test_vincular_dos_veces_409(client):
    dueno = registrar_y_loguear(client, "d5@perfilmedico.cl")
    registrar_y_loguear(client, "c5@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    vincular(client, dueno, perfil["id"], "c5@perfilmedico.cl")
    otra = client.post(f"/perfiles/{perfil['id']}/cuidadores", json={"email": "c5@perfilmedico.cl"}, headers=headers(dueno))
    assert otra.status_code == 409


def test_vincularse_a_si_mismo_400(client):
    dueno = registrar_y_loguear(client, "d6@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    respuesta = client.post(f"/perfiles/{perfil['id']}/cuidadores", json={"email": "d6@perfilmedico.cl"}, headers=headers(dueno))
    assert respuesta.status_code == 400


def test_correo_se_busca_sin_distinguir_mayusculas(client):
    dueno = registrar_y_loguear(client, "d7@perfilmedico.cl")
    registrar_y_loguear(client, "c7@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    respuesta = client.post(f"/perfiles/{perfil['id']}/cuidadores", json={"email": "C7@PerfilMedico.cl"}, headers=headers(dueno))
    assert respuesta.status_code == 201


def test_se_puede_compartir_el_perfil_titular(client):
    dueno = registrar_y_loguear(client, "d8@perfilmedico.cl")
    registrar_y_loguear(client, "c8@perfilmedico.cl")
    titular = crear_perfil(client, dueno)
    respuesta = client.post(f"/perfiles/{titular['id']}/cuidadores", json={"email": "c8@perfilmedico.cl"}, headers=headers(dueno))
    assert respuesta.status_code == 201


def test_rol_lectura_nunca_confirma_ni_edita(client):
    dueno = registrar_y_loguear(client, "d9@perfilmedico.cl")
    registrar_y_loguear(client, "c9@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    vinculo = vincular(client, dueno, perfil["id"], "c9@perfilmedico.cl", rol_vinculo="lectura", puede_confirmar=True, puede_editar_rutinas=True)
    assert vinculo["puede_confirmar"] is False and vinculo["puede_editar_rutinas"] is False


def test_cambiar_permisos_de_un_vinculo(client):
    dueno = registrar_y_loguear(client, "d10@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "c10@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    vinculo = vincular(client, dueno, perfil["id"], "c10@perfilmedico.cl", puede_editar_rutinas=False)
    cambio = client.put(
        f"/perfiles/{perfil['id']}/cuidadores/{vinculo['id']}",
        json={"puede_editar_rutinas": True},
        headers=headers(dueno),
    )
    assert cambio.status_code == 200 and cambio.json()["puede_editar_rutinas"] is True
    assert client.get("/perfiles", headers=headers(cuidador)).json()[0]["mi_acceso"]["puede_editar_rutinas"] is True
    # Pasarlo a solo lectura apaga los permisos.
    lectura = client.put(
        f"/perfiles/{perfil['id']}/cuidadores/{vinculo['id']}", json={"rol_vinculo": "lectura"}, headers=headers(dueno)
    ).json()
    assert lectura["puede_confirmar"] is False and lectura["puede_editar_rutinas"] is False


def test_revocar_quita_el_acceso_de_inmediato(client):
    dueno = registrar_y_loguear(client, "d11@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, "c11@perfilmedico.cl")
    perfil = crear_perfil(client, dueno)
    vinculo = vincular(client, dueno, perfil["id"], "c11@perfilmedico.cl")
    assert client.get(f"/perfiles/{perfil['id']}", headers=headers(cuidador)).status_code == 200
    assert client.delete(f"/perfiles/{perfil['id']}/cuidadores/{vinculo['id']}", headers=headers(dueno)).status_code == 204
    assert client.get(f"/perfiles/{perfil['id']}", headers=headers(cuidador)).status_code == 404
    assert client.get("/perfiles", headers=headers(cuidador)).json() == []
    assert client.get(f"/perfiles/{perfil['id']}/cuidadores", headers=headers(dueno)).json() == []


def test_vinculo_de_otro_perfil_no_se_puede_tocar(client):
    dueno = registrar_y_loguear(client, "d12@perfilmedico.cl")
    registrar_y_loguear(client, "c12@perfilmedico.cl")
    a = crear_perfil(client, dueno, "Ana", "dependiente", "nino")
    b = crear_perfil(client, dueno, "Beto", "dependiente", "nino")
    vinculo = vincular(client, dueno, a["id"], "c12@perfilmedico.cl")
    # Se intenta usar el id del vínculo de A a través de la ruta de B.
    assert client.delete(f"/perfiles/{b['id']}/cuidadores/{vinculo['id']}", headers=headers(dueno)).status_code == 404
