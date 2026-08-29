from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.alerta import TipoAlerta


class AlertaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lectura_diaria_galpon_id: int | None
    lectura_diaria_granja_id: int | None
    tipo: TipoAlerta
    descripcion: str
    fecha: datetime
    resuelta: bool
