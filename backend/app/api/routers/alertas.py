from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.alerta import Alerta
from app.models.crianza_galpon import CrianzaGalpon
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.lectura_diaria_granja import LecturaDiariaGranja
from app.models.usuario import RolUsuario, Usuario
from app.schemas.alerta import AlertaOut

router = APIRouter(prefix="/crianzas/{crianza_id}/alertas", tags=["alertas"])


@router.get("", response_model=list[AlertaOut])
def listar_alertas(
    crianza_id: int,
    resuelta: bool | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    de_galpon = (
        db.query(Alerta)
        .join(LecturaDiariaGalpon, Alerta.lectura_diaria_galpon_id == LecturaDiariaGalpon.id)
        .join(CrianzaGalpon, LecturaDiariaGalpon.crianza_galpon_id == CrianzaGalpon.id)
        .filter(CrianzaGalpon.crianza_id == crianza_id)
    )
    de_granja = (
        db.query(Alerta)
        .join(LecturaDiariaGranja, Alerta.lectura_diaria_granja_id == LecturaDiariaGranja.id)
        .filter(LecturaDiariaGranja.crianza_id == crianza_id)
    )
    if resuelta is not None:
        de_galpon = de_galpon.filter(Alerta.resuelta == resuelta)
        de_granja = de_granja.filter(Alerta.resuelta == resuelta)

    alertas = de_galpon.all() + de_granja.all()
    alertas.sort(key=lambda a: a.fecha, reverse=True)
    return alertas


@router.patch("/{alerta_id}/resolver", response_model=AlertaOut)
def resolver_alerta(
    crianza_id: int,
    alerta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role(RolUsuario.admin)),
):
    alerta = db.get(Alerta, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta.resuelta = True
    db.commit()
    db.refresh(alerta)
    return alerta
