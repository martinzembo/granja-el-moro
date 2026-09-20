from datetime import date

from pydantic import BaseModel


class ResumenGalponOut(BaseModel):
    crianza_galpon_id: int
    galpon_nombre: str
    granjero_nombre: str
    edad_dias: int | None
    aves_netas: int
    aves_vivas: int
    mortandad_acumulada: int
    mortandad_pct: float
    mortandad_esperada_pct: float | None
    agua_acumulada_litros: float
    agua_litros_pollo_hoy: float | None
    agua_esperada_litros_pollo_hoy: float | None


class ResumenGranjaOut(BaseModel):
    fecha: date | None
    consumo_gas_hoy: float | None
    promedio_gas_3_dias: float | None
    consumo_electricidad_activa_hoy: float | None
    promedio_electricidad_activa_3_dias: float | None
    consumo_electricidad_reactiva_hoy: float | None
    promedio_electricidad_reactiva_3_dias: float | None


class ResumenCrianzaOut(BaseModel):
    crianza_id: int
    alimento_entregado_kg: float
    granja: ResumenGranjaOut
    galpones: list[ResumenGalponOut]
