from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.api.validaciones import (
    requiere_crianza_en_curso,
    requiere_fecha_no_anterior,
    requiere_fecha_no_futura,
)
from app.db.session import get_db
from app.models.crianza import Crianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.galpon import Galpon
from app.models.ingreso_aves import IngresoAves
from app.models.usuario import RolUsuario, Usuario
from app.schemas.crianza import (
    CrianzaCreate,
    CrianzaGalponCreate,
    CrianzaGalponOut,
    CrianzaOut,
    IngresoAvesCreate,
    IngresoAvesOut,
)
from app.services.aves import aves_netas_totales

router = APIRouter(prefix="/crianzas", tags=["crianzas"])


@router.get("", response_model=list[CrianzaOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Crianza).all()


@router.post("", response_model=CrianzaOut, status_code=201)
def crear(
    payload: CrianzaCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_role(RolUsuario.admin)),
):
    if db.query(Crianza).filter(Crianza.numero == payload.numero).first():
        raise HTTPException(status_code=400, detail="Ya existe una crianza con ese número")
    crianza = Crianza(
        numero=payload.numero, fecha_inicio=payload.fecha_inicio, creado_por_id=admin.id
    )
    db.add(crianza)
    db.commit()
    db.refresh(crianza)
    return crianza


@router.get("/{crianza_id}", response_model=CrianzaOut)
def obtener(crianza_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    crianza = db.get(Crianza, crianza_id)
    if not crianza:
        raise HTTPException(status_code=404, detail="Crianza no encontrada")
    return crianza


@router.post(
    "/{crianza_id}/galpones", response_model=CrianzaGalponOut, status_code=201
)
def asignar_galpon(
    crianza_id: int,
    payload: CrianzaGalponCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    crianza = db.get(Crianza, crianza_id)
    if not crianza:
        raise HTTPException(status_code=404, detail="Crianza no encontrada")
    requiere_crianza_en_curso(crianza)

    ya_asignado = (
        db.query(CrianzaGalpon)
        .filter(
            CrianzaGalpon.crianza_id == crianza_id,
            CrianzaGalpon.galpon_id == payload.galpon_id,
        )
        .first()
    )
    if ya_asignado:
        raise HTTPException(status_code=400, detail="Ese galpón ya está asignado a esta crianza")

    asignacion = CrianzaGalpon(crianza_id=crianza_id, **payload.model_dump())
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


@router.get("/{crianza_id}/galpones", response_model=list[CrianzaGalponOut])
def listar_galpones_asignados(
    crianza_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return (
        db.query(CrianzaGalpon).filter(CrianzaGalpon.crianza_id == crianza_id).all()
    )


def _get_crianza_galpon_o_404(db: Session, crianza_id: int, cg_id: int) -> CrianzaGalpon:
    cg = (
        db.query(CrianzaGalpon)
        .filter(CrianzaGalpon.id == cg_id, CrianzaGalpon.crianza_id == crianza_id)
        .first()
    )
    if not cg:
        raise HTTPException(status_code=404, detail="Galpón no asignado a esta crianza")
    return cg


@router.post(
    "/{crianza_id}/galpones/{cg_id}/ingresos",
    response_model=IngresoAvesOut,
    status_code=201,
)
def registrar_ingreso(
    crianza_id: int,
    cg_id: int,
    payload: IngresoAvesCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    cg = _get_crianza_galpon_o_404(db, crianza_id, cg_id)
    crianza = db.get(Crianza, crianza_id)
    requiere_crianza_en_curso(crianza)
    requiere_fecha_no_futura(payload.fecha)
    requiere_fecha_no_anterior(payload.fecha, crianza.fecha_inicio, "el inicio de la crianza")

    if payload.muertos_transporte > payload.cantidad:
        raise HTTPException(
            status_code=400, detail="Los muertos en transporte no pueden superar la cantidad despachada"
        )

    galpon = db.get(Galpon, cg.galpon_id)
    total_previo = aves_netas_totales(db, cg_id)
    cantidad_neta = payload.cantidad - payload.muertos_transporte
    if total_previo + cantidad_neta > galpon.capacidad_maxima:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Este ingreso llevaría al galpón a {total_previo + cantidad_neta} aves, "
                f"por encima de su capacidad máxima ({galpon.capacidad_maxima})"
            ),
        )

    ingreso = IngresoAves(
        crianza_galpon_id=cg_id,
        cantidad_neta=cantidad_neta,
        **payload.model_dump(),
    )
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)
    return ingreso


@router.get(
    "/{crianza_id}/galpones/{cg_id}/ingresos", response_model=list[IngresoAvesOut]
)
def listar_ingresos(
    crianza_id: int,
    cg_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_crianza_galpon_o_404(db, crianza_id, cg_id)
    return db.query(IngresoAves).filter(IngresoAves.crianza_galpon_id == cg_id).all()
