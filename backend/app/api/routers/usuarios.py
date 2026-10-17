from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar(
    rol: RolUsuario | None = None,
    activo: bool = True,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    """Solo admin. Por defecto solo trae activos — pensado para elegir un
    granjero al asignar un galpón (`?rol=granjero`), no tendría sentido
    ofrecer ahí una cuenta que todavía no fue habilitada. Con
    `?activo=false` sirve para la pantalla de "cuentas pendientes" (ver
    PATCH /usuarios/{id}/activar)."""
    query = db.query(Usuario).filter(Usuario.activo == activo)
    if rol is not None:
        query = query.filter(Usuario.rol == rol)
    return query.all()


@router.patch("/{usuario_id}/activar", response_model=UsuarioOut)
def activar(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role(RolUsuario.admin)),
):
    """Habilita una cuenta creada por autoregistro (ver
    app/api/routers/auth.py, `register`) — sin esto el granjero no puede
    loguearse. Idempotente: activar una cuenta ya activa no es error."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario
