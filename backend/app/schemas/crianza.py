from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.crianza import EstadoCrianza


class CrianzaCreate(BaseModel):
    fecha_inicio: date


class CrianzaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_inicio: date
    fecha_cierre: date | None
    estado: EstadoCrianza
    creado_por_id: int


class CrianzaGalponCreate(BaseModel):
    galpon_id: int
    granjero_id: int
    aves_iniciales: int
    peso_inicial_promedio: float | None = None


class CrianzaGalponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_id: int
    galpon_id: int
    granjero_id: int
    aves_iniciales: int
    peso_inicial_promedio: float | None
