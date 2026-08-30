from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.cierre_crianza import CierreCrianza
from app.models.cierre_galpon import CierreGalpon
from app.models.crianza import Crianza, EstadoCrianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.usuario import RolUsuario, Usuario
from app.schemas.cierre import CierreCrianzaCreate, CierreCrianzaOut, CierreGalponOut
from app.services.calculos import cerrar_crianza

router = APIRouter(prefix="/crianzas/{crianza_id}/cierre", tags=["cierre"])


@router.post("", response_model=CierreCrianzaOut, status_code=201)
def cerrar(
    crianza_id: int,
    payload: CierreCrianzaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role(RolUsuario.admin)),
):
    crianza = db.get(Crianza, crianza_id)
    if not crianza:
        raise HTTPException(status_code=404, detail="Crianza no encontrada")
    if crianza.estado == EstadoCrianza.cerrada:
        raise HTTPException(status_code=400, detail="La crianza ya está cerrada")

    try:
        return cerrar_crianza(db, crianza, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=CierreCrianzaOut)
def obtener_cierre(
    crianza_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    cierre = db.query(CierreCrianza).filter(CierreCrianza.crianza_id == crianza_id).first()
    if not cierre:
        raise HTTPException(status_code=404, detail="Esta crianza todavía no tiene liquidación")
    return cierre


@router.get("/galpones", response_model=list[CierreGalponOut])
def obtener_cierre_por_galpon(
    crianza_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return (
        db.query(CierreGalpon)
        .join(CrianzaGalpon, CierreGalpon.crianza_galpon_id == CrianzaGalpon.id)
        .filter(CrianzaGalpon.crianza_id == crianza_id)
        .all()
    )
