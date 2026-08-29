"""Umbrales y lógica de app/services/alertas.py — ver docs/modelo-datos.md,
sección "Alertas", para la justificación de cada número.
"""

from datetime import date, time

import pytest

from app.models.crianza import Crianza
from app.models.crianza_galpon import CrianzaGalpon
from app.models.estandar import Estandar
from app.models.galpon import Galpon
from app.models.ingreso_aves import IngresoAves
from app.models.lectura_diaria_galpon import LecturaDiariaGalpon
from app.models.lectura_diaria_granja import LecturaDiariaGranja
from app.models.usuario import RolUsuario, Usuario
from app.services.alertas import evaluar_lectura_galpon, evaluar_lectura_granja


@pytest.fixture()
def escenario(db_session):
    """Un galpón con 10000 aves netas, ingresadas el 2024-01-01, y el
    estándar real de día 1 a 5 (mortandad acumulada esperada creciente,
    agua esperada creciente) — subconjunto de los valores sembrados en
    app/db/seed_estandares.py.
    """
    admin = Usuario(
        nombre="Admin", email="admin@test.com", password_hash="x", rol=RolUsuario.admin
    )
    granjero = Usuario(
        nombre="Granjero", email="granjero@test.com", password_hash="x", rol=RolUsuario.granjero
    )
    db_session.add_all([admin, granjero])
    db_session.flush()

    galpon = Galpon(nombre="Galpón 1", capacidad_maxima=24000)
    db_session.add(galpon)
    db_session.flush()

    crianza = Crianza(numero=1, fecha_inicio=date(2024, 1, 1), creado_por_id=admin.id)
    db_session.add(crianza)
    db_session.flush()

    cg = CrianzaGalpon(crianza_id=crianza.id, galpon_id=galpon.id, granjero_id=granjero.id)
    db_session.add(cg)
    db_session.flush()

    ingreso = IngresoAves(
        crianza_galpon_id=cg.id,
        fecha=date(2024, 1, 1),
        origen="Test",
        cantidad=10000,
        muertos_transporte=0,
        cantidad_neta=10000,
    )
    db_session.add(ingreso)

    # Estandar real (días 1-5) sembrado por app/db/seed_estandares.py.
    for dia, mortandad_frac, agua in [
        (1, 0.00029, 0.0083),
        (2, 0.00067, 0.0150),
        (3, 0.00246, 0.0225),
        (4, 0.00447, 0.0282),
        (5, 0.00622, 0.0318),
    ]:
        db_session.add(
            Estandar(dia_vida=dia, mortandad_acumulada_esperada=mortandad_frac, agua_litros_pollo_esperado=agua)
        )

    db_session.flush()
    return {"cg": cg, "crianza": crianza}


def _lectura_galpon(db_session, cg_id, fecha, mortandad, lectura_agua):
    lectura = LecturaDiariaGalpon(
        crianza_galpon_id=cg_id,
        fecha=fecha,
        mortandad=mortandad,
        lectura_agua=lectura_agua,
        cargado_por_id=1,
    )
    db_session.add(lectura)
    db_session.flush()
    return lectura


def test_mortandad_dentro_de_lo_esperado_no_dispara(db_session, escenario):
    cg = escenario["cg"]
    # día 1: estándar esperado = 0.00029*10000 = 2.9 muertos. 3 muertos está en línea.
    lectura = _lectura_galpon(db_session, cg.id, date(2024, 1, 2), mortandad=3, lectura_agua=100.0)
    alertas = evaluar_lectura_galpon(db_session, lectura)
    assert not [a for a in alertas if a.tipo.value == "mortandad"]


def test_mortandad_critica_dispara(db_session, escenario):
    cg = escenario["cg"]
    # día 1: esperado ~2.9. 10 muertos es >2x -> crítico.
    lectura = _lectura_galpon(db_session, cg.id, date(2024, 1, 2), mortandad=10, lectura_agua=100.0)
    alertas = evaluar_lectura_galpon(db_session, lectura)
    tipos = [a.tipo.value for a in alertas]
    assert "mortandad" in tipos
    assert any("duplica" in a.descripcion or "supera" in a.descripcion for a in alertas)


def test_agua_muy_baja_dispara(db_session, escenario):
    cg = escenario["cg"]
    _lectura_galpon(db_session, cg.id, date(2024, 1, 2), mortandad=3, lectura_agua=100.0)
    # día 2 esperado: 0.0150 L/ave. Consumo real bajísimo (posible bebedero tapado).
    lectura2 = _lectura_galpon(db_session, cg.id, date(2024, 1, 3), mortandad=2, lectura_agua=100.5)
    alertas = evaluar_lectura_galpon(db_session, lectura2)
    assert any(a.tipo.value == "agua" for a in alertas)
    assert any("bebederos" in a.descripcion for a in alertas)


def test_agua_normal_no_dispara(db_session, escenario):
    cg = escenario["cg"]
    _lectura_galpon(db_session, cg.id, date(2024, 1, 2), mortandad=3, lectura_agua=100.0)
    # consumo esperado día2 ~ 0.0150 L/ave * ~9995 aves vivas ~= 150 L -> +15 en el medidor (factor x10)
    lectura2 = _lectura_galpon(db_session, cg.id, date(2024, 1, 3), mortandad=2, lectura_agua=115.0)
    alertas = evaluar_lectura_galpon(db_session, lectura2)
    assert not [a for a in alertas if a.tipo.value == "agua"]


def test_granja_sin_historial_no_dispara(db_session, escenario):
    crianza = escenario["crianza"]
    lectura = LecturaDiariaGranja(
        crianza_id=crianza.id,
        fecha=date(2024, 1, 2),
        hora_desde=time(8, 0, 0),
        hora_hasta=time(8, 0, 0),
        lectura_gas=1000.0,
        lectura_electricidad_activa=500.0,
        lectura_electricidad_reactiva=100.0,
        cargado_por_id=1,
    )
    db_session.add(lectura)
    db_session.flush()
    assert evaluar_lectura_granja(db_session, lectura) == []


def test_granja_pico_de_gas_dispara(db_session, escenario):
    crianza = escenario["crianza"]
    base = {
        "crianza_id": crianza.id,
        "hora_desde": time(8, 0, 0),
        "hora_hasta": time(8, 0, 0),
        "cargado_por_id": 1,
    }
    lecturas_previas = [
        (date(2024, 1, 2), 1000.0),
        (date(2024, 1, 3), 1100.0),
        (date(2024, 1, 4), 1200.0),
    ]
    for fecha, gas in lecturas_previas:
        db_session.add(
            LecturaDiariaGranja(
                fecha=fecha, lectura_gas=gas, lectura_electricidad_activa=500.0,
                lectura_electricidad_reactiva=100.0, **base,
            )
        )
    db_session.flush()
    # promedio histórico de consumo diario de gas = 100. Hoy salta a 300 (3x).
    hoy = LecturaDiariaGranja(
        fecha=date(2024, 1, 5), lectura_gas=1500.0, lectura_electricidad_activa=500.0,
        lectura_electricidad_reactiva=100.0, **base,
    )
    db_session.add(hoy)
    db_session.flush()
    alertas = evaluar_lectura_granja(db_session, hoy)
    assert any(a.tipo.value == "gas" for a in alertas)
