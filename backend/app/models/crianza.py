import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EstadoCrianza(str, enum.Enum):
    en_curso = "en_curso"
    cerrada = "cerrada"


class Crianza(Base):
    __tablename__ = "crianzas"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_cierre: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[EstadoCrianza] = mapped_column(
        Enum(EstadoCrianza), default=EstadoCrianza.en_curso
    )
    creado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
