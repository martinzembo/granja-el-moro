"""Fórmulas de cierre de crianza, verificadas contra datos reales de la
granja (docs/crianza92.xls) — ver docs/modelo-datos.md para el detalle de
cada verificación.

No van inline en el router de cierre porque son la pieza de lógica de
negocio no trivial que CLAUDE.md pide sacar de los endpoints.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models.crianza import Crianza, EstadoCrianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.entrega_insumo import EntregaInsumo, TipoInsumo
from app.models.ingreso_aves import IngresoAves
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.retiro_camion import RetiroCamion
from app.models.cierre_galpon import CierreGalpon
from app.models.cierre_crianza import CierreCrianza
from app.schemas.cierre import CierreCrianzaCreate


def edad_ponderada(ingresos: list[IngresoAves], fecha_retiro: date) -> float:
    """Edad promedio del galpón, ponderada por la cantidad de aves de cada
    partida de ingreso (un galpón puede tener orígenes/fechas distintas).

    Verificado exacto contra el Excel real: Galpón 1 con partidas de 15718
    aves a 49 días y 5828 aves a 47 días da edad=48.459017915... — el mismo
    valor que trae la planilla de la granja.
    """
    total_aves = sum(i.cantidad_neta for i in ingresos)
    if not total_aves:
        return 0.0
    return sum(i.cantidad_neta * (fecha_retiro - i.fecha).days for i in ingresos) / total_aves


def indice_crecimiento(peso_promedio_kg: float, edad_dias: float) -> float:
    """Gramos por día. Verificado: 3.104kg / 48.459 días -> 64.05 g/día."""
    return (peso_promedio_kg * 1000) / edad_dias


def conversion(alimento_consumido_kg: float, peso_producido_kg: float) -> float:
    """kg de alimento por kg de peso producido."""
    return alimento_consumido_kg / peso_producido_kg


def indice_eficiencia(
    mortandad_pct: float, peso_promedio_kg: float, edad_dias: float, conversion_: float
) -> float:
    """Índice de Eficiencia Productiva (IEP/EPEF), estándar de la industria
    avícola. Verificado exacto: mortandad=11.88%, peso=3.104kg, edad=48.459d,
    conversión=1.8149 -> IE=311.0.
    """
    viabilidad_pct = (1 - mortandad_pct) * 100
    return (viabilidad_pct * peso_promedio_kg) / (edad_dias * conversion_) * 100


class _DatosGalpon:
    """Agrupa lo que se necesita leer una sola vez por galpón antes de poder
    calcular nada (el prorrateo de alimento necesita la edad de TODOS los
    galpones antes de poder cerrar cualquiera)."""

    def __init__(self, cg: CrianzaGalpon, ingresos: list[IngresoAves], retiros: list[RetiroCamion]):
        self.cg = cg
        self.ingresos = ingresos
        self.retiros = retiros
        self.cantidad_neta_total = sum(i.cantidad_neta for i in ingresos)
        self.peso_neto_total = float(sum(r.peso_neto for r in retiros))
        self.aves_retiradas_total = sum(r.cantidad_aves for r in retiros)
        self.fecha_retiro = max(r.fecha for r in retiros)
        self.edad_dias = edad_ponderada(ingresos, self.fecha_retiro)
        self.ave_dias = self.cantidad_neta_total * self.edad_dias


def _cerrar_galpon(db: Session, datos: _DatosGalpon, alimento_total_crianza: float, suma_ave_dias: float) -> CierreGalpon:
    mortandad_total = sum(
        m
        for (m,) in db.query(LecturaDiariaGalpon.mortandad)
        .filter(LecturaDiariaGalpon.crianza_galpon_id == datos.cg.id)
        .all()
    )
    mortandad_pct = (
        mortandad_total / datos.cantidad_neta_total if datos.cantidad_neta_total else 0.0
    )

    # Reparto de alimento proporcional a la exposición ave-días de este
    # galpón sobre el total de la crianza. Es una aproximación: el Excel de
    # la granja hace un reparto día a día según población viva real de cada
    # galpón, esto pondera por (aves netas x edad) como proxy — ver
    # docs/modelo-datos.md, sección "pendiente de validar".
    alimento_consumido = (
        alimento_total_crianza * (datos.ave_dias / suma_ave_dias) if suma_ave_dias else 0.0
    )

    peso_promedio = datos.peso_neto_total / datos.aves_retiradas_total
    conv = conversion(alimento_consumido, datos.peso_neto_total)
    ic = indice_crecimiento(peso_promedio, datos.edad_dias)
    ie = indice_eficiencia(mortandad_pct, peso_promedio, datos.edad_dias, conv)

    cierre = (
        db.query(CierreGalpon).filter(CierreGalpon.crianza_galpon_id == datos.cg.id).first()
    )
    if cierre is None:
        cierre = CierreGalpon(crianza_galpon_id=datos.cg.id)
        db.add(cierre)

    cierre.edad_dias = datos.edad_dias
    cierre.peso_promedio = peso_promedio
    cierre.alimento_consumido = alimento_consumido
    cierre.indice_crecimiento = ic
    cierre.conversion = conv
    cierre.mortandad_pct = mortandad_pct
    cierre.indice_eficiencia = ie

    return cierre


def cerrar_crianza(db: Session, crianza: Crianza, datos_liquidacion: CierreCrianzaCreate) -> CierreCrianza:
    """Calcula el cierre por galpón y la liquidación total, y persiste todo.

    indice_tabla/premios/gas_ajuste/ajuste son datos de entrada manual (la
    integradora los provee con su propia fórmula interna, ver
    docs/modelo-datos.md) — acá solo se suman y validan, no se recalculan.
    """
    crianza_galpones = (
        db.query(CrianzaGalpon).filter(CrianzaGalpon.crianza_id == crianza.id).all()
    )
    if not crianza_galpones:
        raise ValueError("La crianza no tiene galpones asignados")

    alimento_total_crianza = float(
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

    datos_por_galpon = []
    for cg in crianza_galpones:
        ingresos = db.query(IngresoAves).filter(IngresoAves.crianza_galpon_id == cg.id).all()
        retiros = db.query(RetiroCamion).filter(RetiroCamion.crianza_galpon_id == cg.id).all()
        if not ingresos:
            raise ValueError(f"El galpón (crianza_galpon {cg.id}) no tiene ingresos de aves cargados")
        if not retiros:
            raise ValueError(f"El galpón (crianza_galpon {cg.id}) no tiene retiros cargados")
        datos_por_galpon.append(_DatosGalpon(cg, ingresos, retiros))

    suma_ave_dias = sum(d.ave_dias for d in datos_por_galpon)

    cierres_galpon = [
        _cerrar_galpon(db, d, alimento_total_crianza, suma_ave_dias) for d in datos_por_galpon
    ]

    total_aves_entregadas = sum(d.aves_retiradas_total for d in datos_por_galpon)
    peso_total = sum(d.peso_neto_total for d in datos_por_galpon)
    ie_promedio = (
        sum(c.indice_eficiencia * d.aves_retiradas_total for c, d in zip(cierres_galpon, datos_por_galpon))
        / total_aves_entregadas
        if total_aves_entregadas
        else 0.0
    )

    precio_x_pollo = (
        datos_liquidacion.indice_tabla
        + datos_liquidacion.premios
        + datos_liquidacion.gas_ajuste
        + datos_liquidacion.ajuste
    )
    monto_total = precio_x_pollo * total_aves_entregadas

    cierre_crianza = (
        db.query(CierreCrianza).filter(CierreCrianza.crianza_id == crianza.id).first()
    )
    if cierre_crianza is None:
        cierre_crianza = CierreCrianza(crianza_id=crianza.id)
        db.add(cierre_crianza)

    cierre_crianza.total_aves_entregadas = total_aves_entregadas
    cierre_crianza.peso_total = peso_total
    cierre_crianza.ie_promedio = ie_promedio
    cierre_crianza.indice_tabla = datos_liquidacion.indice_tabla
    cierre_crianza.premios = datos_liquidacion.premios
    cierre_crianza.gas_ajuste = datos_liquidacion.gas_ajuste
    cierre_crianza.ajuste = datos_liquidacion.ajuste
    cierre_crianza.precio_x_pollo = precio_x_pollo
    cierre_crianza.monto_total = monto_total
    cierre_crianza.fecha_cierre = datos_liquidacion.fecha_cierre

    crianza.estado = EstadoCrianza.cerrada
    crianza.fecha_cierre = datos_liquidacion.fecha_cierre

    db.commit()
    db.refresh(cierre_crianza)
    return cierre_crianza
