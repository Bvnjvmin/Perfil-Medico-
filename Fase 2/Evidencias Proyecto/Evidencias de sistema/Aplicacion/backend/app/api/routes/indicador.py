"""
Endpoints de HU 12 y HU 18: indicadores de salud de un perfil.

POST   /perfiles/{id}/indicadores              -> registra una medición (a mano o desde la pulsera)
GET    /perfiles/{id}/indicadores              -> lista (filtros: tipo, desde, hasta, limite)
GET    /perfiles/{id}/indicadores/ultimos      -> la medición más reciente de cada tipo
GET    /perfiles/{id}/indicadores/serie        -> puntos para el gráfico de evolución de un tipo
DELETE /perfiles/{id}/indicadores/{ind_id}     -> borra una medición (titular o quien la registró)

Ver los indicadores exige ser el titular o tener `puede_ver_indicadores`. Registrar exige además
poder confirmar (el rol 'lectura' nunca registra). Los valores fuera de rango se rechazan para
atajar errores de tipeo; la API no interpreta si un valor es bueno o malo.
"""
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import PERMISO_VER_INDICADORES, get_current_user, obtener_perfil_con_permiso
from app.db.session import get_db
from app.models.indicador_salud import IndicadorSalud
from app.models.usuario import Usuario
from app.schemas.sprint5 import (
    UNIDADES, IndicadorCreate, IndicadorOut, PuntoSerie, SerieOut, TipoIndicador, UltimoIndicadorOut,
)
from app.services.tiempo import hoy_local, zona

router = APIRouter(prefix="/perfiles/{perfil_id}/indicadores", tags=["Indicadores de salud"])


def _inicio_dia(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=zona()).astimezone(timezone.utc)


@router.post("", response_model=IndicadorOut, status_code=status.HTTP_201_CREATED)
def registrar_indicador(
    perfil_id: UUID,
    datos: IndicadorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, acceso = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    if not acceso.puede_confirmar:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para registrar indicadores")
    ahora = datetime.now(timezone.utc)
    medido_en = datos.medido_en or ahora
    if medido_en.tzinfo is None:
        medido_en = medido_en.replace(tzinfo=zona())
    medido_en = medido_en.astimezone(timezone.utc)
    if medido_en > ahora + timedelta(minutes=5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de la medición no puede estar en el futuro")
    indicador = IndicadorSalud(
        perfil_id=perfil.id, tipo=datos.tipo, valor=datos.valor, valor_secundario=datos.valor_secundario,
        unidad=UNIDADES[datos.tipo], fuente=datos.fuente, medido_en=medido_en, nota=datos.nota,
        registrado_por_id=current_user.id,
    )
    db.add(indicador)
    db.commit()
    db.refresh(indicador)
    return indicador


@router.get("", response_model=list[IndicadorOut])
def listar_indicadores(
    perfil_id: UUID,
    tipo: Optional[TipoIndicador] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    consulta = db.query(IndicadorSalud).filter(IndicadorSalud.perfil_id == perfil.id)
    if tipo:
        consulta = consulta.filter(IndicadorSalud.tipo == tipo)
    if desde:
        consulta = consulta.filter(IndicadorSalud.medido_en >= _inicio_dia(desde))
    if hasta:
        consulta = consulta.filter(IndicadorSalud.medido_en < _inicio_dia(hasta + timedelta(days=1)))
    return consulta.order_by(IndicadorSalud.medido_en.desc()).limit(limite).all()


@router.get("/ultimos", response_model=UltimoIndicadorOut)
def ultimos_indicadores(
    perfil_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    ultimos = []
    for tipo in UNIDADES:
        ind = (
            db.query(IndicadorSalud).filter(IndicadorSalud.perfil_id == perfil.id, IndicadorSalud.tipo == tipo)
            .order_by(IndicadorSalud.medido_en.desc()).first()
        )
        if ind is not None:
            ultimos.append(ind)
    return UltimoIndicadorOut(perfil_id=perfil.id, ultimos=ultimos)


@router.get("/serie", response_model=SerieOut)
def serie_indicador(
    perfil_id: UUID,
    tipo: TipoIndicador,
    dias: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Puntos de los últimos `dias` días (incluido hoy), del más antiguo al más nuevo."""
    perfil, _ = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    hasta = hoy_local()
    desde = hasta - timedelta(days=dias - 1)
    filas = (
        db.query(IndicadorSalud)
        .filter(
            IndicadorSalud.perfil_id == perfil.id, IndicadorSalud.tipo == tipo,
            IndicadorSalud.medido_en >= _inicio_dia(desde),
            IndicadorSalud.medido_en < _inicio_dia(hasta + timedelta(days=1)),
        )
        .order_by(IndicadorSalud.medido_en)
        .all()
    )
    valores = [f.valor for f in filas]
    return SerieOut(
        perfil_id=perfil.id, tipo=tipo, unidad=UNIDADES[tipo], desde=desde, hasta=hasta,
        puntos=[PuntoSerie(medido_en=f.medido_en, valor=f.valor, valor_secundario=f.valor_secundario, fuente=f.fuente) for f in filas],
        minimo=min(valores) if valores else None,
        maximo=max(valores) if valores else None,
        promedio=(sum(valores) / Decimal(len(valores))).quantize(Decimal("0.01")) if valores else None,
    )


@router.delete("/{indicador_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_indicador(
    perfil_id: UUID,
    indicador_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    perfil, acceso = obtener_perfil_con_permiso(perfil_id, db, current_user, PERMISO_VER_INDICADORES)
    indicador = db.get(IndicadorSalud, indicador_id)
    if indicador is None or indicador.perfil_id != perfil.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicador no encontrado")
    if acceso.rol != "titular" and indicador.registrado_por_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el titular o quien lo registró puede borrarlo")
    db.delete(indicador)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
