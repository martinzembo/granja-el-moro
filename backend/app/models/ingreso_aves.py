from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class IngresoAves(Base):
    """Una partida de pollitos BB que entra a un galpón.

    Un galpón puede tener varias partidas (orígenes/fechas distintas) dentro
    de la misma crianza. La fecha del primer IngresoAves de un galpón define
    su "día 0" de edad.
    """

    __tablename__ = "ingresos_aves"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_galpon_id: Mapped[int] = mapped_column(ForeignKey("crianza_galpones.id"))
    fecha: Mapped[date] = mapped_column(Date)
    origen: Mapped[str] = mapped_column(String(120))
    cantidad: Mapped[int] = mapped_column(Integer)
    muertos_transporte: Mapped[int] = mapped_column(Integer, default=0)
    cantidad_neta: Mapped[int] = mapped_column(Integer)
