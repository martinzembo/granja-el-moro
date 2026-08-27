from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LecturaDiariaGalpon(Base):
    """Lo que manda el granjero todos los días, por galpón: mortandad y
    lectura cruda del caudalímetro de agua.

    El consumo de agua del día (lectura_hoy - lectura_ayer) x 10 se calcula
    en la capa de negocio, no se guarda derivado acá — ver docs/modelo-datos.md.
    """

    __tablename__ = "lecturas_diarias_galpon"
    __table_args__ = (UniqueConstraint("crianza_galpon_id", "fecha"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_galpon_id: Mapped[int] = mapped_column(ForeignKey("crianza_galpones.id"))
    fecha: Mapped[date] = mapped_column(Date)
    mortandad: Mapped[int] = mapped_column(Integer, default=0)
    lectura_agua: Mapped[float] = mapped_column(Numeric(12, 2))
    cargado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
