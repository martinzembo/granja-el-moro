from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CierreGalpon(Base):
    """Resultado por galpón al cerrar la crianza. Fórmulas en
    app/services/calculos.py, verificadas contra datos reales — ver
    docs/modelo-datos.md.
    """

    __tablename__ = "cierres_galpon"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_galpon_id: Mapped[int] = mapped_column(ForeignKey("crianza_galpones.id"), unique=True)
    # Fraccionaria: un galpón con orígenes/fechas de ingreso mixtos tiene una
    # edad promedio ponderada, no un entero de días — ver edad_ponderada().
    edad_dias: Mapped[float] = mapped_column(Numeric(8, 4))
    peso_promedio: Mapped[float] = mapped_column(Numeric(10, 3))
    alimento_consumido: Mapped[float] = mapped_column(Numeric(12, 2))
    indice_crecimiento: Mapped[float] = mapped_column(Numeric(10, 3))
    conversion: Mapped[float] = mapped_column(Numeric(6, 4))
    mortandad_pct: Mapped[float] = mapped_column(Numeric(7, 5))
    indice_eficiencia: Mapped[float] = mapped_column(Numeric(8, 2))
