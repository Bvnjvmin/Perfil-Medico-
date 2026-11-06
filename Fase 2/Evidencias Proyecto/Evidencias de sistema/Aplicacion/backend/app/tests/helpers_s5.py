"""Funciones auxiliares de las pruebas del Sprint 5."""
from datetime import date, datetime, time, timedelta

from app.services.tiempo import hoy_local, zona
from app.tests.helpers import crear_perfil, headers, registrar_y_loguear, vincular

CLAVE_TRACCAR = "clave-de-prueba-traccar"


def hoy() -> date:
    """El día de hoy en Chile (la misma fecha que usa el sistema, sin depender del reloj del servidor)."""
    return hoy_local()


def a(hora: int, minuto: int = 0, dias: int = 0) -> datetime:
    """Un momento de hoy (o de otro día) a esa hora, en la zona horaria del sistema."""
    return datetime.combine(hoy() + timedelta(days=dias), time(hora, minuto), tzinfo=zona())


def escenario(client, prefijo: str, **permisos_cuidador) -> dict:
    """Titular con un perfil dependiente, un cuidador vinculado y una cuenta ajena."""
    titular = registrar_y_loguear(client, f"{prefijo}-titular@perfilmedico.cl")
    cuidador = registrar_y_loguear(client, f"{prefijo}-cuidador@perfilmedico.cl")
    ajena = registrar_y_loguear(client, f"{prefijo}-ajena@perfilmedico.cl")
    perfil = crear_perfil(client, titular, nombre="Abuela Rosa", tipo="dependiente", subtipo="adulto_mayor")
    vinculo = vincular(client, titular, perfil["id"], f"{prefijo}-cuidador@perfilmedico.cl", **permisos_cuidador)
    return {"titular": titular, "cuidador": cuidador, "ajena": ajena, "perfil": perfil, "vinculo": vinculo,
            "pid": perfil["id"]}


def activar_traccar(monkeypatch) -> None:
    from app.core.config import settings
    monkeypatch.setattr(settings, "TRACCAR_TOKEN", CLAVE_TRACCAR)


def registrar_pulsera(client, token: str, perfil_id: str, identificador: str = "356938035643809"):
    return client.post(
        f"/perfiles/{perfil_id}/pulseras",
        json={"identificador": identificador, "nombre": "Pulsera de Rosa", "modelo": "GPS-T1"},
        headers=headers(token),
    )


def enviar_posicion(client, lat=-33.4489, lon=-70.6693, identificador="356938035643809", **extra):
    """Simula el reenvío de Traccar con parámetros en la URL (estilo OsmAnd)."""
    params = {"token": CLAVE_TRACCAR, "id": identificador, "lat": lat, "lon": lon, **extra}
    return client.get("/traccar/posiciones", params=params)
