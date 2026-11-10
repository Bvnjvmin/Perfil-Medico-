"""Pruebas del notificador FCM con respuestas simuladas (no se conecta a Firebase)."""
import httpx

from app.services.notificador import NotificadorFCM, NotificadorLog, obtener_notificador


def _cliente(respuestas: list[int], llamadas: list):
    def manejar(request: httpx.Request) -> httpx.Response:
        llamadas.append(request)
        return httpx.Response(respuestas.pop(0) if respuestas else 200, json={"name": "ok"})
    return httpx.Client(transport=httpx.MockTransport(manejar))


def _fcm(llamadas, respuestas=None, **kw):
    return NotificadorFCM(proyecto="proy", credenciales="/x.json", cliente=_cliente(respuestas or [], llamadas),
                          obtener_token=lambda ruta: "acceso-falso", **kw)


def test_envia_un_mensaje_por_dispositivo_con_datos_en_texto():
    llamadas = []
    _fcm(llamadas).enviar(["t1", "t2"], "Titulo", "Cuerpo", {"nivel": 1, "tipo": "alerta"})
    assert len(llamadas) == 2
    r = llamadas[0]
    assert str(r.url) == "https://fcm.googleapis.com/v1/projects/proy/messages:send"
    assert r.headers["authorization"] == "Bearer acceso-falso"
    msg = httpx.Response(200, content=r.content).json()["message"]
    assert msg["token"] == "t1" and msg["notification"] == {"title": "Titulo", "body": "Cuerpo"}
    assert msg["data"] == {"nivel": "1", "tipo": "alerta"}


def test_un_rechazo_no_detiene_los_demas_envios():
    llamadas = []
    _fcm(llamadas, respuestas=[404, 200]).enviar(["t1", "t2"], "T", "C", {})
    assert len(llamadas) == 2


def test_sin_credenciales_no_envia_ni_falla():
    llamadas = []
    n = NotificadorFCM(proyecto="", credenciales="", cliente=_cliente([], llamadas))
    n.enviar(["t1"], "T", "C", {})
    assert llamadas == []


def test_error_al_obtener_el_token_no_propaga():
    llamadas = []
    def falla(ruta): raise RuntimeError("sin credenciales")
    n = NotificadorFCM(proyecto="p", credenciales="/x", cliente=_cliente([], llamadas), obtener_token=falla)
    n.enviar(["t1"], "T", "C", {})
    assert llamadas == []


def test_error_de_conexion_no_propaga():
    def cae(request): raise httpx.ConnectError("sin red")
    cliente = httpx.Client(transport=httpx.MockTransport(cae))
    NotificadorFCM(proyecto="p", credenciales="/x", cliente=cliente,
                   obtener_token=lambda r: "a").enviar(["t1", "t2"], "T", "C", {})


def test_el_notificador_se_elige_por_configuracion(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "NOTIFICADOR", "fcm")
    assert isinstance(obtener_notificador(), NotificadorFCM)
    monkeypatch.setattr(settings, "NOTIFICADOR", "log")
    assert isinstance(obtener_notificador(), NotificadorLog)
    monkeypatch.setattr(settings, "NOTIFICADOR", "otro")
    assert isinstance(obtener_notificador(), NotificadorLog)
