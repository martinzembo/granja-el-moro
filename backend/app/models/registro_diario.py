from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RegistroDiario(Base):
    """Un registro por galpón por día: reemplaza el mensaje diario de WhatsApp."""

    __tablename__ = "registros_diarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_galpon_id: Mapped[int] = mapped_column(ForeignKey("crianza_galpones.id"))
    fecha: Mapped[date] = mapped_column(Date)
    dia_de_crianza: Mapped[int] = mapped_column(Integer)
    mortandad: Mapped[int] = mapped_column(Integer, default=0)
    consumo_agua: Mapped[float] = mapped_column(Numeric(10, 2))
    consumo_alimento: Mapped[float] = mapped_column(Numeric(10, 2))
    consumo_gas: Mapped[float] = mapped_column(Numeric(10, 2))
    consumo_electricidad: Mapped[float] = mapped_column(Numeric(10, 2))
    peso_promedio: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    cargado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
