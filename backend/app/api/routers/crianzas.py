from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.crianza import Crianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.usuario import RolUsuario, Usuario
from app.schemas.crianza import (
    CrianzaCreate,
    CrianzaGalponCreate,
    CrianzaGalponOut,
    CrianzaOut,
)

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
    crianza = Crianza(fecha_inicio=payload.fecha_inicio, creado_por_id=admin.id)
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
