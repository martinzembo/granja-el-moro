from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CierreCrianza(Base):
    """Resultado de liquidación al cerrar una Crianza."""

    __tablename__ = "cierres_crianza"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_id: Mapped[int] = mapped_column(ForeignKey("crianzas.id"), unique=True)
    total_aves_entregadas: Mapped[int] = mapped_column(Integer)
    peso_total_kg: Mapped[float] = mapped_column(Numeric(12, 2))
    indice_crecimiento: Mapped[float] = mapped_column(Numeric(8, 2))
    indice_conversion: Mapped[float] = mapped_column(Numeric(6, 3))
    precio_por_kg_resultante: Mapped[float] = mapped_column(Numeric(10, 2))
    monto_total: Mapped[float] = mapped_column(Numeric(14, 2))
    fecha_cierre: Mapped[date] = mapped_column(Date)
