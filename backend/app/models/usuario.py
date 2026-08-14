import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RolUsuario(str, enum.Enum):
    admin = "admin"
    granjero = "granjero"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
