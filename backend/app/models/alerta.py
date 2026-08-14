import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TipoAlerta(str, enum.Enum):
    mortandad = "mortandad"
    agua = "agua"
    alimento = "alimento"
    peso = "peso"


class Alerta(Base):
    """Generada automáticamente cuando un RegistroDiario se desvía de un Estandar."""

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    registro_diario_id: Mapped[int] = mapped_column(ForeignKey("registros_diarios.id"))
    tipo: Mapped[TipoAlerta] = mapped_column(Enum(TipoAlerta))
    descripcion: Mapped[str] = mapped_column(String(255))
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resuelta: Mapped[bool] = mapped_column(Boolean, default=False)
