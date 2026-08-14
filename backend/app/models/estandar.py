from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Estandar(Base):
    """Valores esperados por día de crianza, usados para detectar desvíos."""

    __tablename__ = "estandares"

    id: Mapped[int] = mapped_column(primary_key=True)
    dia_de_crianza: Mapped[int] = mapped_column(Integer)
    mortandad_max_esperada: Mapped[float] = mapped_column(Numeric(10, 2))
    consumo_agua_esperado: Mapped[float] = mapped_column(Numeric(10, 2))
    consumo_alimento_esperado: Mapped[float] = mapped_column(Numeric(10, 2))
    peso_esperado: Mapped[float] = mapped_column(Numeric(10, 2))
