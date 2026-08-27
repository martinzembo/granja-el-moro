from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.crianza import Crianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.lectura_diaria_granja import LecturaDiariaGranja
from app.models.usuario import RolUsuario, Usuario
from app.schemas.lectura import (
    LecturaDiariaGalponCreate,
    LecturaDiariaGalponOut,
    LecturaDiariaGranjaCreate,
    LecturaDiariaGranjaOut,
)

router = APIRouter(tags=["lecturas"])


def _get_crianza_galpon_o_404(db: Session, crianza_id: int, cg_id: int) -> CrianzaGalpon:
    cg = (
        db.query(CrianzaGalpon)
        .filter(CrianzaGalpon.id == cg_id, CrianzaGalpon.crianza_id == crianza_id)
        .first()
    )
    if not cg:
        raise HTTPException(status_code=404, detail="Galpón no asignado a esta crianza")
    return cg


def _requiere_granjero_del_galpon_o_admin(usuario: Usuario, cg: CrianzaGalpon) -> None:
    if usuario.rol != RolUsuario.admin and usuario.id != cg.granjero_id:
        raise HTTPException(
            status_code=403, detail="Solo el granjero asignado a este galpón puede cargar datos"
        )


def _requiere_granjero_de_la_crianza_o_admin(
    db: Session, usuario: Usuario, crianza_id: int
) -> None:
    if usuario.rol == RolUsuario.admin:
        return
    asignado = (
        db.query(CrianzaGalpon)
        .filter(CrianzaGalpon.crianza_id == crianza_id, CrianzaGalpon.granjero_id == usuario.id)
        .first()
    )
    if not asignado:
        raise HTTPException(
            status_code=403,
            detail="Solo un granjero asignado a esta crianza puede cargar datos de granja",
        )


@router.post(
    "/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
    response_model=LecturaDiariaGalponOut,
    status_code=201,
)
def registrar_lectura_galpon(
    crianza_id: int,
    cg_id: int,
    payload: LecturaDiariaGalponCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    cg = _get_crianza_galpon_o_404(db, crianza_id, cg_id)
    _requiere_granjero_del_galpon_o_admin(usuario, cg)

    ya_existe = (
        db.query(LecturaDiariaGalpon)
        .filter(
            LecturaDiariaGalpon.crianza_galpon_id == cg_id,
            LecturaDiariaGalpon.fecha == payload.fecha,
        )
        .first()
    )
    if ya_existe:
        raise HTTPException(status_code=400, detail="Ya existe una lectura para ese galpón y fecha")

    lectura = LecturaDiariaGalpon(
        crianza_galpon_id=cg_id, cargado_por_id=usuario.id, **payload.model_dump()
    )
    db.add(lectura)
    db.commit()
    db.refresh(lectura)
    return lectura


@router.get(
    "/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
    response_model=list[LecturaDiariaGalponOut],
)
def listar_lecturas_galpon(
    crianza_id: int,
    cg_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_crianza_galpon_o_404(db, crianza_id, cg_id)
    return (
        db.query(LecturaDiariaGalpon)
        .filter(LecturaDiariaGalpon.crianza_galpon_id == cg_id)
        .order_by(LecturaDiariaGalpon.fecha)
        .all()
    )


@router.post(
    "/crianzas/{crianza_id}/lecturas-granja",
    response_model=LecturaDiariaGranjaOut,
    status_code=201,
)
def registrar_lectura_granja(
    crianza_id: int,
    payload: LecturaDiariaGranjaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    crianza = db.get(Crianza, crianza_id)
    if not crianza:
        raise HTTPException(status_code=404, detail="Crianza no encontrada")
    _requiere_granjero_de_la_crianza_o_admin(db, usuario, crianza_id)

    ya_existe = (
        db.query(LecturaDiariaGranja)
        .filter(
            LecturaDiariaGranja.crianza_id == crianza_id,
            LecturaDiariaGranja.fecha == payload.fecha,
        )
        .first()
    )
    if ya_existe:
        raise HTTPException(status_code=400, detail="Ya existe una lectura de granja para esa fecha")

    lectura = LecturaDiariaGranja(
        crianza_id=crianza_id, cargado_por_id=usuario.id, **payload.model_dump()
    )
    db.add(lectura)
    db.commit()
    db.refresh(lectura)
    return lectura


@router.get(
    "/crianzas/{crianza_id}/lecturas-granja",
    response_model=list[LecturaDiariaGranjaOut],
)
def listar_lecturas_granja(
    crianza_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return (
        db.query(LecturaDiariaGranja)
        .filter(LecturaDiariaGranja.crianza_id == crianza_id)
        .order_by(LecturaDiariaGranja.fecha)
        .all()
    )
