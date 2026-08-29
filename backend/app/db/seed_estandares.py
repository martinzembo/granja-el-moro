"""Siembra la tabla `estandares` con la curva real de mortandad y agua
esperadas por día de vida, extraída de docs/crianza92.xls (hojas Mort y
Agua, columnas STD/TEÓRICO — ver docs/modelo-datos.md, sección "Alertas").

Es la única crianza real completa que tenemos, así que es la mejor
referencia disponible hoy — mejor que inventar una curva genérica. Cuando
haya más crianzas cerradas, conviene recalcular esto con el promedio de
varias en vez de una sola.

Uso:
    python -m app.db.seed_estandares
"""

from app.db.session import SessionLocal
from app.models.estandar import Estandar

AVES_INICIALES_REFERENCIA = 119798  # total de la crianza 92, para normalizar mortandad a fracción

# (día_vida, mortandad_acumulada_esperada [cantidad absoluta en la crianza real], agua_litros_pollo_esperado)
# Mortandad: hoja "Mort", columna STD -> Acum. Agua: hoja "Agua", columna TEÓRICO,
# suavizada con media móvil de 3 días para no heredar el ruido día a día del
# Excel real como si fuera parte del estándar (la mortandad acumulada no
# necesita suavizado: al ser acumulada ya absorbe el ruido diario).
_MORTANDAD_ACUM_ABSOLUTA = {
    1: 35, 2: 80, 3: 295, 4: 535, 5: 745, 6: 885, 7: 1010, 8: 1120, 9: 1220,
    10: 1295, 11: 1365, 12: 1425, 13: 1475, 14: 1520, 15: 1575, 16: 1630,
    17: 1680, 18: 1735, 19: 1800, 20: 1845, 21: 1890, 22: 1930, 23: 1975,
    24: 2020, 25: 2075, 26: 2125, 27: 2170, 28: 2220, 29: 2270, 30: 2320,
    31: 2380, 32: 2435, 33: 2495, 34: 2570, 35: 2635, 36: 2720, 37: 2835,
    38: 2985, 39: 3150, 40: 3325, 41: 3495, 42: 3680, 43: 3875, 44: 4085,
    45: 4315, 46: 4520, 47: 4760, 48: 5000, 49: 5100, 50: 5204, 51: 5314,
}

_AGUA_TEORICA_LTS_POLLO_CRUDA = {
    1: 0.00204081632653061, 2: 0.0145803553195834, 3: 0.0282744793158476,
    4: 0.024542054019049415, 5: 0.031651806564146595, 6: 0.03928937327935532,
    7: 0.05220121589035783, 8: 0.059348777660519825, 9: 0.07071309342308266,
    10: 0.07669580624347501, 11: 0.08664121162700741, 12: 0.11021201512872068,
    13: 0.10818013645099643, 14: 0.11682122774058099, 15: 0.12429339135090901,
    16: 0.13032727709309225, 17: 0.13469706789915448, 18: 0.15898502633949757,
    19: 0.15993331391879284, 20: 0.17415644370089206, 21: 0.20092113441914283,
    22: 0.20701251619351974, 23: 0.2243787045566554, 24: 0.2375819295670299,
    25: 0.25777144197062335, 26: 0.27003448560375914, 27: 0.28617500533857015,
    28: 0.29270511422297185, 29: 0.2931625509573549, 30: 0.3205286976528329,
    31: 0.30645082432048587, 32: 0.3123427179888673, 33: 0.3067184135455654,
    34: 0.30414854607647446, 35: 0.344629234325855, 36: 0.2916313254347602,
    37: 0.3322189638879993, 38: 0.32229672831864875, 39: 0.318489534602181,
    40: 0.3321517445081221, 41: 0.29715266302830495, 42: 0.31076516266865706,
    43: 0.34520164965992406, 44: 0.34050642946255705, 45: 0.3380068614395545,
    46: 0.3789892401071147, 47: 0.408421156313392, 48: 0.3519608717406174,
    49: 0.41134985236846744, 50: 0.408421156313392,
}


def _suavizar_media_movil_3(valores: dict[int, float]) -> dict[int, float]:
    dias = sorted(valores)
    suavizado = {}
    for d in dias:
        vecinos = [valores[x] for x in (d - 1, d, d + 1) if x in valores]
        suavizado[d] = sum(vecinos) / len(vecinos)
    return suavizado


def generar_estandares() -> list[dict]:
    agua_suavizada = _suavizar_media_movil_3(_AGUA_TEORICA_LTS_POLLO_CRUDA)
    dias = sorted(_MORTANDAD_ACUM_ABSOLUTA)
    return [
        {
            "dia_vida": d,
            "mortandad_acumulada_esperada": _MORTANDAD_ACUM_ABSOLUTA[d] / AVES_INICIALES_REFERENCIA,
            "agua_litros_pollo_esperado": agua_suavizada.get(d, agua_suavizada[max(agua_suavizada)]),
        }
        for d in dias
    ]


def seed() -> None:
    db = SessionLocal()
    try:
        for fila in generar_estandares():
            existente = (
                db.query(Estandar).filter(Estandar.dia_vida == fila["dia_vida"]).first()
            )
            if existente:
                existente.mortandad_acumulada_esperada = fila["mortandad_acumulada_esperada"]
                existente.agua_litros_pollo_esperado = fila["agua_litros_pollo_esperado"]
            else:
                db.add(Estandar(**fila))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print(f"Sembrados {len(_MORTANDAD_ACUM_ABSOLUTA)} días de estándar.")
