from datetime import date

from pydantic import BaseModel, ConfigDict


class CierreGalponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_galpon_id: int
    edad_dias: float
    peso_promedio: float
    alimento_consumido: float
    indice_crecimiento: float
    conversion: float
    mortandad_pct: float
    indice_eficiencia: float


class CierreCrianzaCreate(BaseModel):
    """Lo que carga el administrador manualmente al cerrar: los componentes
    de la liquidación que provee la integradora. El resto (aves entregadas,
    peso, IE, precio final) lo calcula el sistema — ver
    app/services/calculos.py.
    """

    fecha_cierre: date
    indice_tabla: float
    premios: float = 0
    gas_ajuste: float = 0
    ajuste: float = 0


class CierreCrianzaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crianza_id: int
    total_aves_entregadas: int
    peso_total: float
    ie_promedio: float
    indice_tabla: float
    premios: float
    gas_ajuste: float
    ajuste: float
    precio_x_pollo: float
    monto_total: float
    fecha_cierre: date
