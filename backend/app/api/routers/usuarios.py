from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar(
    rol: RolUsuario | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    """Solo admin — pensado para elegir un granjero al asignar un galpón
    (`?rol=granjero`), no es un directorio general de usuarios."""
    query = db.query(Usuario).filter(Usuario.activo)
    if rol is not None:
        query = query.filter(Usuario.rol == rol)
    return query.all()
