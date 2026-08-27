from datetime import date, time

from pydantic import BaseModel, ConfigDict


class RetiroCamionCreate(BaseModel):
    fecha: date
    remito: str
    transportista: str
    hora_salida: time | None = None
    cantidad_aves: int
    peso_bruto: float | None = None
    peso_tara: float | None = None
    peso_neto: float


class RetiroCamionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_galpon_id: int
    fecha: date
    remito: str
    transportista: str
    hora_salida: time | None
    cantidad_aves: int
    peso_bruto: float | None
    peso_tara: float | None
    peso_neto: float
    cargado_por_id: int
