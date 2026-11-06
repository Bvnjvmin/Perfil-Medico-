"""
Módulo de IA, orientación general (HU 15).

Flujo de una consulta (ver app/api/routes/ia.py):
1. Si la pregunta suena a urgencia, NO se llama al modelo: se responde con un mensaje fijo
   que manda a llamar al 131 (SAMU).
2. Si no, se arma un contexto mínimo del perfil (`construir_contexto`) y se le pide al
   proveedor configurado (`IA_PROVEEDOR`) que responda con las reglas de `SISTEMA`.

Proveedores:
- "simulado": no usa red ni credenciales; devuelve una respuesta de ejemplo con los datos del
  contexto. Es el valor por defecto, sirve para desarrollo, pruebas y demos sin costo.
- "anthropic": llama a la API de Claude (`IA_API_KEY`, `IA_MODELO`). La clave va en el .env,
  nunca en el repositorio.

Privacidad: al modelo solo viaja el nombre de pila, la edad, alergias, medicamentos activos,
el porcentaje de cumplimiento de 7 días y los últimos indicadores (estos últimos solo si quien
pregunta tiene permiso para verlos). Nunca viajan RUT, correo, teléfonos ni contactos.
"""
import logging
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.indicador_salud import IndicadorSalud
from app.models.medicamento import Medicamento
from app.models.perfil import Alergia, Perfil
from app.services.cumplimiento import calcular
from app.services.eventos import aware
from app.services.tiempo import hoy_local, zona

logger = logging.getLogger("perfil_medico.ia")

SISTEMA = (
    "Eres el asistente de orientación general de Perfil Médico+, una app de cuidado de personas "
    "dependientes (adultos mayores y niños). Respondes en español neutro, con frases cortas y claras, "
    "para un cuidador que no es profesional de la salud. Reglas: "
    "1) Das orientación general; no haces diagnósticos ni indicas tratamientos. "
    "2) Nunca indicas, cambias ni suspendes dosis o medicamentos; ante dudas sobre medicamentos, "
    "sugiere consultar al médico o al químico farmacéutico. "
    "3) Usa solo los datos del perfil que se te entregan; si falta información, dilo. "
    "4) Si la pregunta sugiere una urgencia (dolor de pecho, dificultad para respirar, desmayo, convulsión, "
    "sangrado abundante, sospecha de ACV, golpe en la cabeza, intoxicación), indica llamar al 131 (SAMU) de inmediato. "
    "5) Si preguntan por farmacias, precios o temas ajenos a la salud y el cuidado, di que por ahora no puedes ayudar con eso. "
    "6) Responde en un máximo de 150 palabras y termina recordando que no reemplazas a un profesional de la salud."
)

MENSAJE_URGENCIA = (
    "Lo que describes puede ser una urgencia. Llama ahora al 131 (SAMU) o lleva a la persona al servicio de "
    "urgencia más cercano. Si hay riesgo para su vida o la tuya, no esperes una respuesta de esta app. "
    "Si piensas en hacerte daño o en hacer daño a otra persona, también puedes llamar a la línea *4141. "
    "Este asistente no reemplaza a un profesional de la salud."
)

_URGENCIAS = (
    "dolor de pecho", "dolor en el pecho", "duele el pecho", "duele pecho", "presion en el pecho", "opresion en el pecho",
    "cuesta respirar", "falta de aire", "falta el aire", "no respira", "dificultad para respirar", "me ahogo", "se ahoga",
    "desmayo", "se desmay", "inconsciente", "convulsion", "no responde", "sangrado abundante",
    "no deja de sangrar", "derrame", "acv", "infarto", "sobredosis", "envenen", "intoxic",
    "golpe en la cabeza", "suicid",
)


class IAError(Exception):
    """El proveedor de IA no está disponible o respondió mal."""


@dataclass
class RespuestaIA:
    texto: str
    proveedor: str
    modelo: Optional[str] = None


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.lower().split())


def es_urgencia(pregunta: str) -> bool:
    normalizada = _normalizar(pregunta)
    return any(clave in normalizada for clave in _URGENCIAS)


def _numero(valor) -> str:
    """68.00 -> '68'; 72.50 -> '72.5' (sin ceros de relleno)."""
    return format(valor.normalize(), "f")


def _edad(nacimiento: Optional[date], hoy: date) -> Optional[int]:
    if nacimiento is None:
        return None
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))


def construir_contexto(db: Session, perfil: Perfil, incluir_indicadores: bool) -> tuple[str, str]:
    """Devuelve (contexto para el modelo, resumen de qué datos se enviaron)."""
    hoy = hoy_local()
    nombre = perfil.nombre.split()[0] if perfil.nombre else "la persona"
    edad = _edad(perfil.fecha_nacimiento, hoy)
    lineas = [f"Perfil: {nombre}" + (f", {edad} años" if edad is not None else "") + f" ({perfil.tipo})"]
    incluidos = ["nombre de pila", "edad"] if edad is not None else ["nombre de pila"]

    alergias = db.query(Alergia).filter(Alergia.perfil_id == perfil.id).all()
    lineas.append("Alergias: " + (", ".join(f"{a.sustancia} ({a.severidad})" for a in alergias) or "ninguna registrada"))
    incluidos.append("alergias")

    meds = db.query(Medicamento).filter(Medicamento.perfil_id == perfil.id, Medicamento.activo.isnot(False)).all()
    lineas.append("Medicamentos activos: " + (", ".join(f"{m.nombre} {m.dosis}, {m.frecuencia}" for m in meds) or "ninguno registrado"))
    incluidos.append("medicamentos activos")

    cumplimiento = calcular(db, perfil, hoy - timedelta(days=6), hoy)
    if cumplimiento["porcentaje"] is None:
        lineas.append("Cumplimiento de los últimos 7 días: sin datos")
    else:
        lineas.append(
            f"Cumplimiento de los últimos 7 días: {cumplimiento['porcentaje']} % "
            f"({cumplimiento['cumplidas']} de {cumplimiento['total']} actividades)"
        )
    incluidos.append("cumplimiento 7 días")

    if incluir_indicadores:
        ultimos = []
        for tipo in ("peso", "presion", "glucosa", "frecuencia_cardiaca"):
            ind = (
                db.query(IndicadorSalud).filter(IndicadorSalud.perfil_id == perfil.id, IndicadorSalud.tipo == tipo)
                .order_by(IndicadorSalud.medido_en.desc()).first()
            )
            if ind is not None:
                valor = (
                    f"{_numero(ind.valor)}/{_numero(ind.valor_secundario)}"
                    if ind.valor_secundario is not None else _numero(ind.valor)
                )
                dia = aware(ind.medido_en).astimezone(zona()).date().isoformat()
                ultimos.append(f"{tipo.replace('_', ' ')} {valor} {ind.unidad} ({dia})")
        lineas.append("Últimos indicadores: " + ("; ".join(ultimos) or "ninguno registrado"))
        incluidos.append("últimos indicadores")
    return "\n".join(lineas), ", ".join(incluidos)


def _responder_simulado(pregunta: str, contexto: str) -> RespuestaIA:
    texto = (
        "[Modo simulado: esta respuesta no la generó una IA real.]\n"
        "Esto es lo que tengo registrado del perfil:\n"
        f"{contexto}\n\n"
        f"Sobre tu pregunta («{pregunta.strip()[:120]}»): con estos datos puedo ayudarte a ordenar la información, "
        "pero para decidir qué hacer conviene consultarlo con el médico o el químico farmacéutico. "
        "No reemplazo a un profesional de la salud."
    )
    return RespuestaIA(texto=texto, proveedor="simulado")


def _llamar_anthropic(cuerpo: dict) -> dict:
    """Llamada HTTP a la API de Claude (se separa para poder simularla en las pruebas)."""
    respuesta = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.IA_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=cuerpo,
        timeout=settings.IA_TIMEOUT_SEGUNDOS,
    )
    respuesta.raise_for_status()
    return respuesta.json()


def _responder_anthropic(pregunta: str, contexto: str) -> RespuestaIA:
    if not settings.IA_API_KEY:
        raise IAError("IA_API_KEY no está configurada")
    cuerpo = {
        "model": settings.IA_MODELO,
        "max_tokens": settings.IA_MAX_TOKENS,
        "system": SISTEMA,
        "messages": [{"role": "user", "content": f"Datos del perfil:\n{contexto}\n\nPregunta del cuidador: {pregunta.strip()}"}],
    }
    try:
        datos = _llamar_anthropic(cuerpo)
        texto = "".join(b.get("text", "") for b in datos.get("content", []) if b.get("type") == "text").strip()
    except (httpx.HTTPError, ValueError, AttributeError) as error:
        logger.error("Falló la llamada al proveedor de IA: %s", type(error).__name__)
        raise IAError("El proveedor de IA no respondió") from error
    if not texto:
        raise IAError("El proveedor de IA devolvió una respuesta vacía")
    return RespuestaIA(texto=texto, proveedor="anthropic", modelo=settings.IA_MODELO)


def responder(pregunta: str, contexto: str) -> RespuestaIA:
    if settings.IA_PROVEEDOR == "anthropic":
        return _responder_anthropic(pregunta, contexto)
    return _responder_simulado(pregunta, contexto)
