"""Las fórmulas de app/services/calculos.py están verificadas contra los
números reales de docs/crianza92.xls (Galpón 1 de esa crianza). Estos tests
fijan esa verificación como regresión: si alguien las toca sin querer, se
rompen acá antes que en producción.
"""

from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app.services.calculos import conversion, edad_ponderada, indice_crecimiento, indice_eficiencia


def _ingreso(cantidad_neta, fecha):
    return SimpleNamespace(cantidad_neta=cantidad_neta, fecha=fecha)


def test_edad_ponderada_con_origenes_mixtos():
    # Galpón 1 real: dos partidas ingresadas el mismo día (10487 + 5231 aves)
    # y una tercera dos días después (5828 aves), retiradas 49/47 días después.
    fecha_1 = date(2024, 1, 1)
    fecha_2 = date(2024, 1, 3)
    fecha_retiro = fecha_1 + timedelta(days=49)

    ingresos = [
        _ingreso(10487, fecha_1),
        _ingreso(5231, fecha_1),
        _ingreso(5828, fecha_2),
    ]

    assert edad_ponderada(ingresos, fecha_retiro) == pytest.approx(48.45901791515644, rel=1e-9)


def test_indice_crecimiento():
    assert indice_crecimiento(3.104, 48.45901791515644) == pytest.approx(64.05412518748481, rel=1e-6)


def test_conversion():
    # Los dos números vienen de agregaciones distintas dentro del mismo Excel
    # (hoja Alimento vs hoja Retiro), por eso la tolerancia es un poco más
    # laxa que en los otros tests — hay un residuo de redondeo real, de ~0.01%.
    assert conversion(106959.5198, 58940.0) == pytest.approx(1.8149482873164273, rel=2e-4)


def test_indice_eficiencia():
    mortandad_pct = 0.11881555741204863
    ie = indice_eficiencia(
        mortandad_pct=mortandad_pct,
        peso_promedio_kg=3.104,
        edad_dias=48.45901791515644,
        conversion_=1.8149482873164273,
    )
    assert ie == pytest.approx(311.0, rel=1e-2)
