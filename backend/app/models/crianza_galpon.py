from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CrianzaGalpon(Base):
    """Qué galpón participa de qué crianza, a cargo de qué granjero."""

    __tablename__ = "crianza_galpones"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_id: Mapped[int] = mapped_column(ForeignKey("crianzas.id"))
    galpon_id: Mapped[int] = mapped_column(ForeignKey("galpones.id"))
    granjero_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    aves_iniciales: Mapped[int] = mapped_column(Integer)
    peso_inicial_promedio: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
