from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class LecturaDiariaGalponCreate(BaseModel):
    fecha: date
    mortandad: int = 0
    lectura_agua: float


class LecturaDiariaGalponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_galpon_id: int
    fecha: date
    mortandad: int
    lectura_agua: float
    cargado_por_id: int
    creado_en: datetime


class LecturaDiariaGranjaCreate(BaseModel):
    fecha: date
    hora_desde: time
    hora_hasta: time
    lectura_gas: float
    lectura_electricidad_activa: float
    lectura_electricidad_reactiva: float


class LecturaDiariaGranjaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_id: int
    fecha: date
    hora_desde: time
    hora_hasta: time
    lectura_gas: float
    lectura_electricidad_activa: float
    lectura_electricidad_reactiva: float
    cargado_por_id: int
    creado_en: datetime
