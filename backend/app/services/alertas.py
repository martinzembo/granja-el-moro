"""Evaluación de alertas por desvío contra `Estandar` (mortandad y agua, por
galpón) o contra el propio historial reciente (gas y electricidad, de toda
la granja — no hay un estándar por edad confiable para eso, ver
docs/modelo-datos.md sección "Alertas").

Se llama una vez por cada lectura nueva, desde app/api/routers/lecturas.py.
No va inline en el router por la misma razón que app/services/calculos.py:
es lógica de negocio no trivial.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models.alerta import Alerta, TipoAlerta
from app.models.estandar import Estandar
from app.models.ingreso_aves import IngresoAves
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.lectura_diaria_granja import LecturaDiariaGranja

# Umbrales — justificados en docs/modelo-datos.md, sección "Alertas".
MORTANDAD_ATENCION = 1.5  # acumulado 50% por encima del estándar
MORTANDAD_CRITICO = 2.0  # acumulado 100% por encima del estándar
MORTANDAD_PICO_DIARIO = 3.0  # un solo día dispara aunque el acumulado venga bien
AGUA_BAJO = 0.7  # 30% por debajo del estándar (riesgo: bebederos tapados)
AGUA_ALTO = 1.3  # 30% por encima del estándar (riesgo: pérdida o estrés calórico)
GRANJA_TOLERANCIA = 0.4  # ±40% contra el promedio móvil de gas/electricidad
GRANJA_VENTANA_DIAS = 3
FACTOR_CAUDALIMETRO = 10  # ver docs/modelo-datos.md, cálculo de consumo de agua


def _edad_dias(db: Session, crianza_galpon_id: int, fecha: date) -> int | None:
    ingresos = (
        db.query(IngresoAves).filter(IngresoAves.crianza_galpon_id == crianza_galpon_id).all()
    )
    if not ingresos:
        return None
    fecha_ingreso = min(i.fecha for i in ingresos)
    return (fecha - fecha_ingreso).days


def _aves_netas_totales(db: Session, crianza_galpon_id: int) -> int:
    ingresos = (
        db.query(IngresoAves).filter(IngresoAves.crianza_galpon_id == crianza_galpon_id).all()
    )
    return sum(i.cantidad_neta for i in ingresos)


def _mortandad_acumulada(db: Session, crianza_galpon_id: int, hasta_fecha: date) -> int:
    filas = (
        db.query(LecturaDiariaGalpon.mortandad)
        .filter(
            LecturaDiariaGalpon.crianza_galpon_id == crianza_galpon_id,
            LecturaDiariaGalpon.fecha <= hasta_fecha,
        )
        .all()
    )
    return sum(m for (m,) in filas)


def _chequear_mortandad(
    db: Session, lectura: LecturaDiariaGalpon, edad: int, aves_netas: int
) -> list[Alerta]:
    estandar_hoy = db.query(Estandar).filter(Estandar.dia_vida == edad).first()
    if not estandar_hoy or not aves_netas:
        return []

    mortandad_acum = _mortandad_acumulada(db, lectura.crianza_galpon_id, lectura.fecha)
    esperado_acum = float(estandar_hoy.mortandad_acumulada_esperada) * aves_netas
    alertas = []

    if esperado_acum > 0:
        ratio = mortandad_acum / esperado_acum
        if ratio >= MORTANDAD_CRITICO:
            alertas.append(
                (
                    TipoAlerta.mortandad,
                    f"Mortandad acumulada ({mortandad_acum}) duplica o supera el estándar "
                    f"esperado (~{esperado_acum:.0f}) para día {edad} de vida — revisar galpón urgente.",
                )
            )
        elif ratio >= MORTANDAD_ATENCION:
            alertas.append(
                (
                    TipoAlerta.mortandad,
                    f"Mortandad acumulada ({mortandad_acum}) supera en 50% el estándar "
                    f"esperado (~{esperado_acum:.0f}) para día {edad} de vida.",
                )
            )

    # Pico puntual: un día con muchas más muertes que las esperadas para esa
    # edad dispara aunque el acumulado todavía esté dentro de lo normal — es
    # la señal temprana de un brote que menciona la propuesta del proyecto.
    estandar_ayer = db.query(Estandar).filter(Estandar.dia_vida == edad - 1).first()
    frac_ayer = float(estandar_ayer.mortandad_acumulada_esperada) if estandar_ayer else 0.0
    incremento_esperado = (float(estandar_hoy.mortandad_acumulada_esperada) - frac_ayer) * aves_netas
    if incremento_esperado > 0 and lectura.mortandad >= incremento_esperado * MORTANDAD_PICO_DIARIO:
        alertas.append(
            (
                TipoAlerta.mortandad,
                f"Mortandad del día ({lectura.mortandad}) es {lectura.mortandad / incremento_esperado:.1f}x "
                f"lo esperado para día {edad} de vida (~{incremento_esperado:.0f}) — posible brote.",
            )
        )

    return alertas


def _chequear_agua(
    db: Session, lectura: LecturaDiariaGalpon, edad: int, aves_netas: int
) -> list[Alerta]:
    estandar = db.query(Estandar).filter(Estandar.dia_vida == edad).first()
    if not estandar:
        return []

    anterior = (
        db.query(LecturaDiariaGalpon)
        .filter(
            LecturaDiariaGalpon.crianza_galpon_id == lectura.crianza_galpon_id,
            LecturaDiariaGalpon.fecha < lectura.fecha,
        )
        .order_by(LecturaDiariaGalpon.fecha.desc())
        .first()
    )
    if not anterior:
        return []  # sin lectura previa no se puede derivar el consumo del día

    consumo_litros = (float(lectura.lectura_agua) - float(anterior.lectura_agua)) * FACTOR_CAUDALIMETRO
    if consumo_litros < 0:
        return []  # lectura inconsistente (¿medidor cambiado?), no evaluar

    mortandad_acum = _mortandad_acumulada(db, lectura.crianza_galpon_id, lectura.fecha)
    aves_vivas = aves_netas - mortandad_acum
    esperado = float(estandar.agua_litros_pollo_esperado)
    if aves_vivas <= 0 or esperado <= 0:
        return []

    litros_pollo = consumo_litros / aves_vivas
    ratio = litros_pollo / esperado

    if ratio <= AGUA_BAJO:
        return [
            (
                TipoAlerta.agua,
                f"Consumo de agua ({litros_pollo:.3f} L/ave) es {(1 - ratio) * 100:.0f}% menor al "
                f"esperado (~{esperado:.3f} L/ave) para día {edad} de vida — revisar bebederos.",
            )
        ]
    if ratio >= AGUA_ALTO:
        return [
            (
                TipoAlerta.agua,
                f"Consumo de agua ({litros_pollo:.3f} L/ave) es {(ratio - 1) * 100:.0f}% mayor al "
                f"esperado (~{esperado:.3f} L/ave) para día {edad} de vida — revisar pérdidas o estrés calórico.",
            )
        ]
    return []


def evaluar_lectura_galpon(db: Session, lectura: LecturaDiariaGalpon) -> list[Alerta]:
    """Corre los chequeos de mortandad y agua para una lectura recién
    cargada, persiste las alertas que disparen y las devuelve."""
    edad = _edad_dias(db, lectura.crianza_galpon_id, lectura.fecha)
    if edad is None:
        return []
    aves_netas = _aves_netas_totales(db, lectura.crianza_galpon_id)

    disparadas = _chequear_mortandad(db, lectura, edad, aves_netas) + _chequear_agua(
        db, lectura, edad, aves_netas
    )

    alertas = []
    for tipo, descripcion in disparadas:
        alerta = Alerta(lectura_diaria_galpon_id=lectura.id, tipo=tipo, descripcion=descripcion)
        db.add(alerta)
        alertas.append(alerta)
    return alertas


def _chequear_desvio_granja(
    lectura: LecturaDiariaGranja, tipo: TipoAlerta, etiqueta: str, deltas: list[float]
) -> list[tuple[TipoAlerta, str]]:
    if len(deltas) < 2:
        return []
    hoy = deltas[-1]
    historicos = deltas[:-1][-GRANJA_VENTANA_DIAS:]
    if not historicos or hoy < 0:
        return []
    promedio = sum(historicos) / len(historicos)
    if promedio <= 0:
        return []
    ratio = hoy / promedio
    if ratio >= 1 + GRANJA_TOLERANCIA or ratio <= 1 - GRANJA_TOLERANCIA:
        return [
            (
                tipo,
                f"Consumo de {etiqueta} de hoy ({hoy:.1f}) se desvía "
                f"{abs(ratio - 1) * 100:.0f}% del promedio de los últimos {len(historicos)} días "
                f"({promedio:.1f}).",
            )
        ]
    return []


def evaluar_lectura_granja(db: Session, lectura: LecturaDiariaGranja) -> list[Alerta]:
    """Gas y electricidad no tienen un estándar por edad confiable (dependen
    mucho del clima/temporada, y solo tenemos una crianza real de referencia)
    — se comparan contra el promedio móvil de los últimos días de la misma
    crianza en vez de una curva fija."""
    historial = (
        db.query(LecturaDiariaGranja)
        .filter(
            LecturaDiariaGranja.crianza_id == lectura.crianza_id,
            LecturaDiariaGranja.fecha <= lectura.fecha,
        )
        .order_by(LecturaDiariaGranja.fecha)
        .all()
    )
    if len(historial) < 2:
        return []

    deltas_gas = [
        float(b.lectura_gas) - float(a.lectura_gas) for a, b in zip(historial, historial[1:])
    ]
    deltas_activa = [
        float(b.lectura_electricidad_activa) - float(a.lectura_electricidad_activa)
        for a, b in zip(historial, historial[1:])
    ]
    deltas_reactiva = [
        float(b.lectura_electricidad_reactiva) - float(a.lectura_electricidad_reactiva)
        for a, b in zip(historial, historial[1:])
    ]

    disparadas = (
        _chequear_desvio_granja(lectura, TipoAlerta.gas, "gas (m³)", deltas_gas)
        + _chequear_desvio_granja(lectura, TipoAlerta.electricidad, "electricidad activa (kWh)", deltas_activa)
        + _chequear_desvio_granja(lectura, TipoAlerta.electricidad, "electricidad reactiva (kvarh)", deltas_reactiva)
    )

    alertas = []
    for tipo, descripcion in disparadas:
        alerta = Alerta(lectura_diaria_granja_id=lectura.id, tipo=tipo, descripcion=descripcion)
        db.add(alerta)
        alertas.append(alerta)
    return alertas
