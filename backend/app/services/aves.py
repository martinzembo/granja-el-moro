"""Consultas sobre población de un CrianzaGalpon, compartidas entre
app/services/alertas.py, app/services/calculos.py y las validaciones de los
routers. Un solo lugar para "cuántas aves netas entraron / cuántas murieron
/ cuántas se retiraron", para no recalcularlo distinto en cada archivo.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models.ingreso_aves import IngresoAves
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.retiro_camion import RetiroCamion


def fecha_primer_ingreso(db: Session, crianza_galpon_id: int) -> date | None:
    ingresos = db.query(IngresoAves).filter(IngresoAves.crianza_galpon_id == crianza_galpon_id).all()
    if not ingresos:
        return None
    return min(i.fecha for i in ingresos)


def edad_dias(db: Session, crianza_galpon_id: int, fecha: date) -> int | None:
    """Edad simple (día calendario - primer ingreso), la que se usa para
    evaluar alertas día a día. No confundir con `edad_ponderada` de
    app/services/calculos.py, que promedia por partidas para el cierre."""
    fecha_ingreso = fecha_primer_ingreso(db, crianza_galpon_id)
    if fecha_ingreso is None:
        return None
    return (fecha - fecha_ingreso).days


def aves_netas_totales(db: Session, crianza_galpon_id: int) -> int:
    ingresos = db.query(IngresoAves).filter(IngresoAves.crianza_galpon_id == crianza_galpon_id).all()
    return sum(i.cantidad_neta for i in ingresos)


def mortandad_acumulada(db: Session, crianza_galpon_id: int, hasta_fecha: date | None = None) -> int:
    query = db.query(LecturaDiariaGalpon.mortandad).filter(
        LecturaDiariaGalpon.crianza_galpon_id == crianza_galpon_id
    )
    if hasta_fecha is not None:
        query = query.filter(LecturaDiariaGalpon.fecha <= hasta_fecha)
    return sum(m for (m,) in query.all())


def aves_retiradas(db: Session, crianza_galpon_id: int) -> int:
    filas = (
        db.query(RetiroCamion.cantidad_aves)
        .filter(RetiroCamion.crianza_galpon_id == crianza_galpon_id)
        .all()
    )
    return sum(c for (c,) in filas)


def aves_vivas_disponibles(db: Session, crianza_galpon_id: int) -> int:
    """Aves netas ingresadas, menos las que ya murieron o ya se retiraron a
    faena — lo que queda "en pie" en el galpón hoy."""
    return (
        aves_netas_totales(db, crianza_galpon_id)
        - mortandad_acumulada(db, crianza_galpon_id)
        - aves_retiradas(db, crianza_galpon_id)
    )
