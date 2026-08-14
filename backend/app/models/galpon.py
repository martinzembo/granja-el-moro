from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Galpon(Base):
    __tablename__ = "galpones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    capacidad_maxima: Mapped[int] = mapped_column(Integer)
