from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CrianzaGalpon(Base):
    """Qué galpón participa de qué crianza, a cargo de qué granjero.

    No guarda cantidad de aves ni peso inicial directo: un galpón puede
    recibir pollitos de varios orígenes en fechas distintas (ver
    IngresoAves) — el total sale de sumarlos.
    """

    __tablename__ = "crianza_galpones"

    id: Mapped[int] = mapped_column(primary_key=True)
    crianza_id: Mapped[int] = mapped_column(ForeignKey("crianzas.id"))
    galpon_id: Mapped[int] = mapped_column(ForeignKey("galpones.id"))
    granjero_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
