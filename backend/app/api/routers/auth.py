from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import LoginRequest, RegistroCreate, Token, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegistroCreate, db: Session = Depends(get_db)):
    """Registro público, sin login — siempre crea un granjero, activo de
    inmediato. No hay forma de autoregistrarse como admin (ver
    app/schemas/usuario.py, RegistroCreate, y app/db/crear_admin.py)."""
    if db.query(Usuario).filter(Usuario.email == payload.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    usuario = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol=RolUsuario.granjero,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if not usuario or not verify_password(payload.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = create_access_token(subject=str(usuario.id), rol=usuario.rol.value)
    return Token(access_token=token)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario
