import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TipoInsumo(str, enum.Enum):
    alimento = "alimento"
    cascara = "cascara"


class EntregaInsumo(Base):
    """Alimento y cáscara de girasol/arroz: se registran por remito, no
    diario, a nivel de toda la crianza (no por galpón). Las carga el
    administrador, no el granjero.
    """

    __tablename__ = "entregas_insumo"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_id: Mapped[int] = mapped_column(ForeignKey("crianzas.id"))
    tipo_insumo: Mapped[TipoInsumo] = mapped_column(Enum(TipoInsumo))
    fecha: Mapped[date] = mapped_column(Date)
    remito: Mapped[str] = mapped_column(String(50))
    tipo_alimento: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kilos: Mapped[float] = mapped_column(Numeric(10, 2))
    cargado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
