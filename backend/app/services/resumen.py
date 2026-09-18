"""Resumen "en vivo" de una crianza: los números reales que hoy el
administrador arma a mano mirando el Excel — edad, mortandad y agua por
galpón, alimento entregado y gas/electricidad de toda la granja. Reusa los
mismos cálculos y umbrales que app/services/alertas.py, para no tener dos
criterios distintos de "cuánto se esperaba" en el mismo sistema.

A propósito NO incluye índice de crecimiento/conversión/IE: esos necesitan
peso, y acá no se pesa a las aves hasta que salen a faena (RetiroCamion) —
eso se calcula recién al cierre, ver app/services/calculos.py.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models.crianza import Crianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.entrega_insumo import EntregaInsumo, TipoInsumo
from app.models.estandar import Estandar
from app.models.galpon import Galpon
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.lectura_diaria_granja import LecturaDiariaGranja
from app.models.usuario import Usuario
from app.services.alertas import FACTOR_CAUDALIMETRO, GRANJA_VENTANA_DIAS
from app.services.aves import (
    aves_netas_totales,
    aves_vivas_disponibles,
    edad_dias,
    mortandad_acumulada,
)


def _resumen_galpon(db: Session, cg: CrianzaGalpon, hoy: date) -> dict:
    galpon = db.get(Galpon, cg.galpon_id)
    granjero = db.get(Usuario, cg.granjero_id)
    edad = edad_dias(db, cg.id, hoy)
    aves_netas = aves_netas_totales(db, cg.id)
    mortandad = mortandad_acumulada(db, cg.id)
    vivas = aves_vivas_disponibles(db, cg.id)
    mortandad_pct = (mortandad / aves_netas) if aves_netas else 0.0

    mortandad_esperada_pct = None
    agua_esperada_litros_pollo_hoy = None
    if edad is not None:
        estandar = db.query(Estandar).filter(Estandar.dia_vida == edad).first()
        if estandar:
            mortandad_esperada_pct = float(estandar.mortandad_acumulada_esperada)
            agua_esperada_litros_pollo_hoy = float(estandar.agua_litros_pollo_esperado)

    lecturas_agua = (
        db.query(LecturaDiariaGalpon)
        .filter(LecturaDiariaGalpon.crianza_galpon_id == cg.id)
        .order_by(LecturaDiariaGalpon.fecha)
        .all()
    )
    # Acumulado histórico: suma de cada delta día a día (mismo factor que
    # las alertas). Un delta negativo (medidor reiniciado/cambiado) se
    # ignora en vez de restar, para no ensuciar el acumulado.
    agua_acumulada_litros = 0.0
    for anterior, actual in zip(lecturas_agua, lecturas_agua[1:]):
        delta = (float(actual.lectura_agua) - float(anterior.lectura_agua)) * FACTOR_CAUDALIMETRO
        if delta >= 0:
            agua_acumulada_litros += delta

    agua_litros_pollo_hoy = None
    if len(lecturas_agua) >= 2 and vivas > 0:
        ultima, anteultima = lecturas_agua[-1], lecturas_agua[-2]
        delta_hoy = (float(ultima.lectura_agua) - float(anteultima.lectura_agua)) * FACTOR_CAUDALIMETRO
        if delta_hoy >= 0:
            agua_litros_pollo_hoy = delta_hoy / vivas

    return {
        "crianza_galpon_id": cg.id,
        "galpon_nombre": galpon.nombre,
        "granjero_nombre": granjero.nombre,
        "edad_dias": edad,
        "aves_netas": aves_netas,
        "aves_vivas": vivas,
        "mortandad_acumulada": mortandad,
        "mortandad_pct": mortandad_pct,
        "mortandad_esperada_pct": mortandad_esperada_pct,
        "agua_acumulada_litros": agua_acumulada_litros,
        "agua_litros_pollo_hoy": agua_litros_pollo_hoy,
        "agua_esperada_litros_pollo_hoy": agua_esperada_litros_pollo_hoy,
    }


def _promedio_movil(historial: list[LecturaDiariaGranja], campo: str) -> tuple[float | None, float | None]:
    """Delta de hoy y promedio de los últimos GRANJA_VENTANA_DIAS, mismo
    cálculo que app/services/alertas.py — devuelve (consumo_hoy, promedio).
    Cualquiera de los dos puede ser None si todavía no hay historial
    suficiente (a diferencia de la alerta, acá no hace falta el mínimo para
    disparar algo, solo se muestra lo que hay)."""
    valores = [float(getattr(l, campo)) for l in historial]
    deltas = [b - a for a, b in zip(valores, valores[1:])]
    if not deltas:
        return None, None
    hoy = deltas[-1]
    historicos = deltas[:-1][-GRANJA_VENTANA_DIAS:]
    promedio = sum(historicos) / len(historicos) if historicos else None
    return (hoy if hoy >= 0 else None), promedio


def _resumen_granja(db: Session, crianza_id: int) -> dict:
    historial = (
        db.query(LecturaDiariaGranja)
        .filter(LecturaDiariaGranja.crianza_id == crianza_id)
        .order_by(LecturaDiariaGranja.fecha)
        .all()
    )
    ultima = historial[-1] if historial else None
    gas_hoy, gas_prom = _promedio_movil(historial, "lectura_gas")
    activa_hoy, activa_prom = _promedio_movil(historial, "lectura_electricidad_activa")
    reactiva_hoy, reactiva_prom = _promedio_movil(historial, "lectura_electricidad_reactiva")
    return {
        "fecha": ultima.fecha if ultima else None,
        "consumo_gas_hoy": gas_hoy,
        "promedio_gas_3_dias": gas_prom,
        "consumo_electricidad_activa_hoy": activa_hoy,
        "promedio_electricidad_activa_3_dias": activa_prom,
        "consumo_electricidad_reactiva_hoy": reactiva_hoy,
        "promedio_electricidad_reactiva_3_dias": reactiva_prom,
    }


def resumen_crianza(db: Session, crianza: Crianza, hoy: date | None = None) -> dict:
    """`hoy` es la fecha de referencia para calcular edad — por defecto la
    fecha real de hoy (la edad del lote no depende de si ya se cargó el dato
    del día, es un hecho de calendario). Parametrizable solo para poder
    testear de forma determinística contra fechas fijas."""
    hoy = hoy or date.today()
    crianza_galpones = (
        db.query(CrianzaGalpon).filter(CrianzaGalpon.crianza_id == crianza.id).all()
    )
    alimento_entregado_kg = float(
        sum(
            k
            for (k,) in db.query(EntregaInsumo.kilos)
            .filter(
                EntregaInsumo.crianza_id == crianza.id,
                EntregaInsumo.tipo_insumo == TipoInsumo.alimento,
            )
            .all()
        )
    )
    return {
        "crianza_id": crianza.id,
        "alimento_entregado_kg": alimento_entregado_kg,
        "granja": _resumen_granja(db, crianza.id),
        "galpones": [_resumen_galpon(db, cg, hoy) for cg in crianza_galpones],
    }
