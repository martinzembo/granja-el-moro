from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Estandar(Base):
    """Valores esperados por día de vida, usados para alertas.

    Tabla global por ahora (no distingue línea genética/raza) — sembrada con
    los valores reales de docs/crianza92.xls (ver app/db/seed_estandares.py
    y docs/modelo-datos.md, sección "Alertas").

    mortandad_acumulada_esperada es una FRACCIÓN (0-1) de las aves netas
    ingresadas a ESE galpón, no una cantidad absoluta — así generaliza a
    galpones de cualquier tamaño. agua_litros_pollo_esperado ya es por ave
    (no necesita escalarse).
    """

    __tablename__ = "estandares"

    id: Mapped[int] = mapped_column(primary_key=True)
    dia_vida: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    mortandad_acumulada_esperada: Mapped[float] = mapped_column(Numeric(7, 5))
    agua_litros_pollo_esperado: Mapped[float] = mapped_column(Numeric(10, 4))
