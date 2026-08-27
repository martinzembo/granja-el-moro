from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RetiroCamion(Base):
    """Cada camión que retira aves de un galpón para faena. Puede haber
    varios por galpón en los días de retiro.
    """

    __tablename__ = "retiros_camion"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_galpon_id: Mapped[int] = mapped_column(ForeignKey("crianza_galpones.id"))
    fecha: Mapped[date] = mapped_column(Date)
    remito: Mapped[str] = mapped_column(String(50))
    transportista: Mapped[str] = mapped_column(String(120))
    hora_salida: Mapped[time | None] = mapped_column(Time, nullable=True)
    cantidad_aves: Mapped[int] = mapped_column(Integer)
    peso_bruto: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    peso_tara: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    peso_neto: Mapped[float] = mapped_column(Numeric(10, 2))
    cargado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
