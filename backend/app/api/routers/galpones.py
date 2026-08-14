from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.galpon import Galpon
from app.models.usuario import RolUsuario
from app.schemas.galpon import GalponCreate, GalponOut

router = APIRouter(prefix="/galpones", tags=["galpones"])


@router.get("", response_model=list[GalponOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Galpon).all()


@router.post("", response_model=GalponOut, status_code=201)
def crear(
    payload: GalponCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    galpon = Galpon(**payload.model_dump())
    db.add(galpon)
    db.commit()
    db.refresh(galpon)
    return galpon


@router.get("/{galpon_id}", response_model=GalponOut)
def obtener(galpon_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    galpon = db.get(Galpon, galpon_id)
    if not galpon:
        raise HTTPException(status_code=404, detail="Galpón no encontrado")
    return galpon


@router.put("/{galpon_id}", response_model=GalponOut)
def actualizar(
    galpon_id: int,
    payload: GalponCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    galpon = db.get(Galpon, galpon_id)
    if not galpon:
        raise HTTPException(status_code=404, detail="Galpón no encontrado")
    for key, value in payload.model_dump().items():
        setattr(galpon, key, value)
    db.commit()
    db.refresh(galpon)
    return galpon


@router.delete("/{galpon_id}", status_code=204)
def eliminar(
    galpon_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    galpon = db.get(Galpon, galpon_id)
    if not galpon:
        raise HTTPException(status_code=404, detail="Galpón no encontrado")
    db.delete(galpon)
    db.commit()
