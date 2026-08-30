from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.crianza import Crianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.galpon import Galpon
from app.models.usuario import Usuario
from app.schemas.asignacion import AsignacionOut

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/asignaciones", response_model=list[AsignacionOut])
def mis_asignaciones(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """Los galpones (y su crianza) donde el usuario logueado es el granjero
    responsable — pensado para la pantalla de inicio del granjero en la app."""
    filas = (
        db.query(CrianzaGalpon, Crianza, Galpon)
        .join(Crianza, CrianzaGalpon.crianza_id == Crianza.id)
        .join(Galpon, CrianzaGalpon.galpon_id == Galpon.id)
        .filter(CrianzaGalpon.granjero_id == usuario.id)
        .all()
    )
    return [
        AsignacionOut(
            crianza_galpon_id=cg.id,
            crianza_id=crianza.id,
            crianza_numero=crianza.numero,
            crianza_estado=crianza.estado,
            galpon_id=galpon.id,
            galpon_nombre=galpon.nombre,
        )
        for cg, crianza, galpon in filas
    ]
