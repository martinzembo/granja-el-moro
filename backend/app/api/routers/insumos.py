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
from app.models.entrega_insumo import EntregaInsumo
from app.models.usuario import RolUsuario, Usuario
from app.schemas.entrega_insumo import EntregaInsumoCreate, EntregaInsumoOut

router = APIRouter(prefix="/crianzas/{crianza_id}/entregas", tags=["insumos"])


@router.post("", response_model=EntregaInsumoOut, status_code=201)
def registrar_entrega(
    crianza_id: int,
    payload: EntregaInsumoCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_role(RolUsuario.admin)),
):
    crianza = db.get(Crianza, crianza_id)
    if not crianza:
        raise HTTPException(status_code=404, detail="Crianza no encontrada")
    requiere_crianza_en_curso(crianza)
    requiere_fecha_no_futura(payload.fecha)
    requiere_fecha_no_anterior(payload.fecha, crianza.fecha_inicio, "el inicio de la crianza")

    entrega = EntregaInsumo(
        crianza_id=crianza_id, cargado_por_id=admin.id, **payload.model_dump()
    )
    db.add(entrega)
    db.commit()
    db.refresh(entrega)
    return entrega


@router.get("", response_model=list[EntregaInsumoOut])
def listar_entregas(
    crianza_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return db.query(EntregaInsumo).filter(EntregaInsumo.crianza_id == crianza_id).all()
