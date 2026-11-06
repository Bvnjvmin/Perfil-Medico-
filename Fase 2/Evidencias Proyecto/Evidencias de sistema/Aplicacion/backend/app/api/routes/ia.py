"""
Endpoints de HU 15: asistente de IA (orientación general).

POST /perfiles/{id}/ia/consultas   -> hace una pregunta sobre la información del perfil
GET  /perfiles/{id}/ia/consultas   -> historial de preguntas del propio usuario sobre ese perfil

Lo puede usar cualquiera con acceso al perfil. Los últimos indicadores de salud solo se incluyen
en el contexto si quien pregunta puede verlos. Las preguntas que suenan a urgencia no llegan al
modelo: se responde con el aviso de llamar al 131. Hay un tope de consultas por usuario y día
(`IA_MAX_CONSULTAS_DIA`) para controlar el costo.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, obtener_perfil_con_permiso
from app.core.config import settings
from app.db.session import get_db
from app.models.consulta_ia import ConsultaIA
from app.models.usuario import Usuario
from app.schemas.sprint5 import ConsultaIACreate, ConsultaIAOut
from app.services.ia import MENSAJE_URGENCIA, IAError, construir_contexto, es_urgencia, responder

router = APIRouter(prefix="/perfiles/{perfil_id}/ia", tags=["Asistente de IA"])


@router.post("/consultas", response_model=ConsultaIAOut, status_code=status.HTTP_201_CREATED)
def preguntar(
    perfil_id: UUID,
    datos: ConsultaIACreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, acceso = obtener_perfil_con_permiso(perfil_id, db, current_user)
    desde = datetime.now(timezone.utc) - timedelta(hours=24)
    hechas = (
        db.query(ConsultaIA).filter(ConsultaIA.usuario_id == current_user.id, ConsultaIA.creada_en >= desde).count()
    )
    if hechas >= settings.IA_MAX_CONSULTAS_DIA:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Llegaste al máximo de {settings.IA_MAX_CONSULTAS_DIA} consultas por día",
        )

    pregunta = datos.pregunta.strip()
    if es_urgencia(pregunta):
        texto, proveedor, modelo, resumen = MENSAJE_URGENCIA, "reglas", None, "ninguno (respuesta fija de urgencia)"
    else:
        contexto, resumen = construir_contexto(db, perfil, incluir_indicadores=acceso.puede_ver_indicadores)
        try:
            respuesta = responder(pregunta, contexto)
        except IAError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El asistente no está disponible por ahora. Inténtalo de nuevo más tarde.",
            )
        texto, proveedor, modelo = respuesta.texto, respuesta.proveedor, respuesta.modelo

    consulta = ConsultaIA(
        perfil_id=perfil.id, usuario_id=current_user.id, pregunta=pregunta, respuesta=texto,
        proveedor=proveedor, modelo=modelo, contexto_resumen=resumen,
    )
    db.add(consulta)
    db.commit()
    db.refresh(consulta)
    return consulta


@router.get("/consultas", response_model=list[ConsultaIAOut])
def historial(
    perfil_id: UUID,
    limite: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user)
    return (
        db.query(ConsultaIA)
        .filter(ConsultaIA.perfil_id == perfil.id, ConsultaIA.usuario_id == current_user.id)
        .order_by(ConsultaIA.creada_en.desc())
        .limit(limite)
        .all()
    )
