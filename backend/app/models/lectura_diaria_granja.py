from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LecturaDiariaGranja(Base):
    """Gas y electricidad: un solo medidor de cada uno para toda la granja
    (no por galpón), reportado en una ventana horaria fija.
    """

    __tablename__ = "lecturas_diarias_granja"
    __table_args__ = (UniqueConstraint("crianza_id", "fecha"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_id: Mapped[int] = mapped_column(ForeignKey("crianzas.id"))
    fecha: Mapped[date] = mapped_column(Date)
    hora_desde: Mapped[time] = mapped_column(Time)
    hora_hasta: Mapped[time] = mapped_column(Time)
    lectura_gas: Mapped[float] = mapped_column(Numeric(12, 2))
    lectura_electricidad_activa: Mapped[float] = mapped_column(Numeric(12, 2))
    lectura_electricidad_reactiva: Mapped[float] = mapped_column(Numeric(12, 2))
    cargado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
