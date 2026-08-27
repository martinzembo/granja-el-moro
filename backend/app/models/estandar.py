from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Estandar(Base):
    """Valores esperados por día de vida, usados para alertas (Semana 3).

    Tabla global por ahora (no distingue línea genética/raza) — ver
    docs/modelo-datos.md.
    """

    __tablename__ = "estandares"

    id: Mapped[int] = mapped_column(primary_key=True)
    dia_vida: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    mortandad_acumulada_esperada: Mapped[int] = mapped_column(Integer)
    agua_litros_pollo_esperado: Mapped[float] = mapped_column(Numeric(10, 4))
