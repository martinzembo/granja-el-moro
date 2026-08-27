from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CierreCrianza(Base):
    """Liquidación total de la crianza.

    indice_tabla / premios / gas_ajuste / ajuste son valores de ENTRADA
    manual que provee la integradora (MIRALEJOS) — no los calculamos
    nosotros, ver docs/modelo-datos.md. precio_x_pollo es la suma de esos
    cuatro, validada (no recalculada) en el endpoint.
    """

    __tablename__ = "cierres_crianza"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_id: Mapped[int] = mapped_column(ForeignKey("crianzas.id"), unique=True)
    total_aves_entregadas: Mapped[int] = mapped_column(Integer)
    peso_total: Mapped[float] = mapped_column(Numeric(12, 2))
    ie_promedio: Mapped[float] = mapped_column(Numeric(8, 2))
    indice_tabla: Mapped[float] = mapped_column(Numeric(10, 2))
    premios: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    gas_ajuste: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    ajuste: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    precio_x_pollo: Mapped[float] = mapped_column(Numeric(10, 2))
    monto_total: Mapped[float] = mapped_column(Numeric(14, 2))
    fecha_cierre: Mapped[date] = mapped_column(Date)
