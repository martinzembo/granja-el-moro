from datetime import date

from sqlalchemy import Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TablaLiquidacion(Base):
    """Tabla de doble entrada: precio por pollo según índices de conversión y crecimiento.

    Borrador — pendiente de validar contra la tabla real del contrato con la
    integradora (ver docs/modelo-datos.md).
    """

    __tablename__ = "tabla_liquidacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    indice_conversion_min: Mapped[float] = mapped_column(Numeric(6, 3))
    indice_conversion_max: Mapped[float] = mapped_column(Numeric(6, 3))
    indice_crecimiento_min: Mapped[float] = mapped_column(Numeric(8, 2))
    indice_crecimiento_max: Mapped[float] = mapped_column(Numeric(8, 2))
    precio_por_kg: Mapped[float] = mapped_column(Numeric(10, 2))
    vigente_desde: Mapped[date] = mapped_column(Date)
