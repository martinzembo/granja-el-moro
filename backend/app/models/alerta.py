import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TipoAlerta(str, enum.Enum):
    mortandad = "mortandad"
    agua = "agua"
    gas = "gas"
    electricidad = "electricidad"


class Alerta(Base):
    """Generada cuando una lectura se desvía de un Estandar (Semana 3).

    Referencia una de las dos tablas de lectura según el tipo: mortandad y
    agua vienen de LecturaDiariaGalpon; gas y electricidad de
    LecturaDiariaGranja. Solo una de las dos FK va cargada según el caso.
    """

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    lectura_diaria_galpon_id: Mapped[int | None] = mapped_column(
        ForeignKey("lecturas_diarias_galpon.id"), nullable=True
    )
    lectura_diaria_granja_id: Mapped[int | None] = mapped_column(
        ForeignKey("lecturas_diarias_granja.id"), nullable=True
    )
    tipo: Mapped[TipoAlerta] = mapped_column(Enum(TipoAlerta))
    descripcion: Mapped[str] = mapped_column(String(255))
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resuelta: Mapped[bool] = mapped_column(Boolean, default=False)
