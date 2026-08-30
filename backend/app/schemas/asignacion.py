from pydantic import BaseModel

from app.models.crianza import EstadoCrianza


class AsignacionOut(BaseModel):
    """A qué galpón, dentro de qué crianza, está asignado un granjero.

    Pensado para que la app móvil no tenga que traer todas las crianzas y
    filtrar del lado del cliente — ver app/api/routers/me.py.
    """

    crianza_galpon_id: int
    crianza_id: int
    crianza_numero: int
    crianza_estado: EstadoCrianza
    galpon_id: int
    galpon_nombre: str
