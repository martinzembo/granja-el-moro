from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.crianza import EstadoCrianza


class CrianzaCreate(BaseModel):
    numero: int
    fecha_inicio: date


class CrianzaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    fecha_inicio: date
    fecha_cierre: date | None
    estado: EstadoCrianza
    creado_por_id: int


class CrianzaGalponCreate(BaseModel):
    galpon_id: int
    granjero_id: int


class CrianzaGalponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_id: int
    galpon_id: int
    granjero_id: int


class IngresoAvesCreate(BaseModel):
    fecha: date
    origen: str
    cantidad: int
    muertos_transporte: int = 0


class IngresoAvesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_galpon_id: int
    fecha: date
    origen: str
    cantidad: int
    muertos_transporte: int
    cantidad_neta: int
