from pydantic import BaseModel, ConfigDict


class GalponCreate(BaseModel):
    nombre: str
    capacidad_maxima: int


class GalponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    capacidad_maxima: int
