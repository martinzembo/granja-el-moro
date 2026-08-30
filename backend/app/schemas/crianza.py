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
    """No usa from_attributes: se arma a mano en el router con un join a
    Galpon/Usuario (ver app/api/routers/crianzas.py), porque CrianzaGalpon
    no tiene relationships de SQLAlchemy (convención del proyecto, ver
    CLAUDE.md) y la app necesita los nombres, no solo los ids."""

    id: int
    crianza_id: int
    galpon_id: int
    galpon_nombre: str
    granjero_id: int
    granjero_nombre: str


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
