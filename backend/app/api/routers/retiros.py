from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.crianza_galpon import CrianzaGalpon
from app.models.retiro_camion import RetiroCamion
from app.models.usuario import RolUsuario, Usuario
from app.schemas.retiro_camion import RetiroCamionCreate, RetiroCamionOut

router = APIRouter(prefix="/crianzas/{crianza_id}/galpones/{cg_id}/retiros", tags=["retiros"])


def _get_crianza_galpon_o_404(db: Session, crianza_id: int, cg_id: int) -> CrianzaGalpon:
    cg = (
        db.query(CrianzaGalpon)
        .filter(CrianzaGalpon.id == cg_id, CrianzaGalpon.crianza_id == crianza_id)
        .first()
    )
    if not cg:
        raise HTTPException(status_code=404, detail="Galpón no asignado a esta crianza")
    return cg


@router.post("", response_model=RetiroCamionOut, status_code=201)
def registrar_retiro(
    crianza_id: int,
    cg_id: int,
    payload: RetiroCamionCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_role(RolUsuario.admin)),
):
    _get_crianza_galpon_o_404(db, crianza_id, cg_id)
    retiro = RetiroCamion(
        crianza_galpon_id=cg_id, cargado_por_id=admin.id, **payload.model_dump()
    )
    db.add(retiro)
    db.commit()
    db.refresh(retiro)
    return retiro


@router.get("", response_model=list[RetiroCamionOut])
def listar_retiros(
    crianza_id: int,
    cg_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_crianza_galpon_o_404(db, crianza_id, cg_id)
    return db.query(RetiroCamion).filter(RetiroCamion.crianza_galpon_id == cg_id).all()
