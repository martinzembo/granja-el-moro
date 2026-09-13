from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.usuario import RolUsuario


def _normalizar_email(v: str) -> str:
    """Solo recorta espacios — el email es case-sensitive a propósito
    (decisión explícita del cliente, ver historial de commits): "Juan@x.com"
    y "juan@x.com" son cuentas distintas, tanto al registrarse como al
    loguearse. El campo de email en la app fuerza que el teclado no
    autocapitalice, para no generar un mail con mayúsculas por accidente."""
    return v.strip()


class RegistroCreate(BaseModel):
    """Lo que acepta el registro público (`POST /auth/register`, sin login).

    A propósito NO tiene `rol`: el autoregistro siempre crea un granjero
    (ver app/api/routers/auth.py). `model_config` con `extra="forbid"` hace
    que un `rol` colado en el body devuelva 422 en vez de ser ignorado en
    silencio — si alguna vez hace falta dar de alta un admin, se hace con
    app/db/crear_admin.py (fuera de la red), no por acá.
    """

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email", mode="before")
    @classmethod
    def _email_normalizado(cls, v: str) -> str:
        return _normalizar_email(v)


class UsuarioCreate(BaseModel):
    """Para altas internas (semillas/scripts) que sí necesitan elegir rol —
    no está expuesto en ningún endpoint público. Ver RegistroCreate."""

    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    rol: RolUsuario

    @field_validator("email", mode="before")
    @classmethod
    def _email_normalizado(cls, v: str) -> str:
        return _normalizar_email(v)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    rol: RolUsuario
    activo: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def _email_normalizado(cls, v: str) -> str:
        return _normalizar_email(v)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
