from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.entrega_insumo import TipoInsumo


class EntregaInsumoCreate(BaseModel):
    tipo_insumo: TipoInsumo
    fecha: date
    remito: str
    tipo_alimento: int | None = None
    kilos: float


class EntregaInsumoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_id: int
    tipo_insumo: TipoInsumo
    fecha: date
    remito: str
    tipo_alimento: int | None
    kilos: float
    cargado_por_id: int
