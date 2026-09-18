"""GET /crianzas/{id}/resumen — los números "en vivo" que el administrador
pidió ver además de las alertas (ver app/services/resumen.py). No cubre
índice de crecimiento/conversión/IE a propósito: esos requieren peso, que
acá no se conoce hasta el retiro a faena.
"""

from datetime import date

from app.models.crianza import Crianza
from app.models.estandar import Estandar
from app.services.resumen import resumen_crianza


def _armar_crianza_con_datos(client, crear_usuario, db_session):
    admin = crear_usuario("admin@granjaelmoro.com.ar", "admin")
    granjero = crear_usuario("granjero@granjaelmoro.com.ar", "granjero")
    granjero_id = client.get("/auth/me", headers=granjero).json()["id"]

    galpon_id = client.post(
        "/galpones", json={"nombre": "Galpón 1", "capacidad_maxima": 24000}, headers=admin
    ).json()["id"]
    crianza_id = client.post(
        "/crianzas", json={"numero": 1, "fecha_inicio": "2024-01-01"}, headers=admin
    ).json()["id"]
    cg_id = client.post(
        f"/crianzas/{crianza_id}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": granjero_id},
        headers=admin,
    ).json()["id"]

    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Las Violetas", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )

    # Estandar real de días 0 y 1 (fracciones chicas, alcanza para el test).
    db_session.add_all(
        [
            Estandar(dia_vida=0, mortandad_acumulada_esperada=0.002, agua_litros_pollo_esperado=0.02),
            Estandar(dia_vida=1, mortandad_acumulada_esperada=0.004, agua_litros_pollo_esperado=0.03),
        ]
    )
    db_session.commit()

    # Día 0: mortandad 2, lectura de agua inicial.
    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
        json={"fecha": "2024-01-01", "mortandad": 2, "lectura_agua": 100},
        headers=granjero,
    )
    # Día 1: mortandad 1, consumió (110-100)*10 = 100 litros.
    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
        json={"fecha": "2024-01-02", "mortandad": 1, "lectura_agua": 110},
        headers=granjero,
    )

    client.post(
        f"/crianzas/{crianza_id}/lecturas-granja",
        json={
            "fecha": "2024-01-01",
            "hora_desde": "08:00:00",
            "hora_hasta": "08:05:00",
            "lectura_gas": 50,
            "lectura_electricidad_activa": 200,
            "lectura_electricidad_reactiva": 20,
        },
        headers=granjero,
    )
    client.post(
        f"/crianzas/{crianza_id}/lecturas-granja",
        json={
            "fecha": "2024-01-02",
            "hora_desde": "08:00:00",
            "hora_hasta": "08:05:00",
            "lectura_gas": 65,
            "lectura_electricidad_activa": 230,
            "lectura_electricidad_reactiva": 25,
        },
        headers=granjero,
    )

    client.post(
        f"/crianzas/{crianza_id}/entregas",
        json={"fecha": "2024-01-01", "tipo_insumo": "alimento", "kilos": 500, "remito": "0001-00001234"},
        headers=admin,
    )

    return admin, granjero, crianza_id, cg_id


def test_resumen_crianza_numeros_reales(client, crear_usuario, db_session):
    admin, _granjero, crianza_id, cg_id = _armar_crianza_con_datos(client, crear_usuario, db_session)

    resp = client.get(f"/crianzas/{crianza_id}/resumen", headers=admin)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["crianza_id"] == crianza_id
    assert body["alimento_entregado_kg"] == 500.0

    assert len(body["galpones"]) == 1
    galpon = body["galpones"][0]
    assert galpon["crianza_galpon_id"] == cg_id
    assert galpon["galpon_nombre"] == "Galpón 1"
    assert galpon["aves_netas"] == 1000
    assert galpon["mortandad_acumulada"] == 3  # 2 + 1
    assert galpon["aves_vivas"] == 997
    assert galpon["mortandad_pct"] == 0.003
    # Consumo de hoy (día 1): (110-100)*10 = 100 litros -> /997 aves vivas.
    assert galpon["agua_acumulada_litros"] == 100.0
    assert abs(galpon["agua_litros_pollo_hoy"] - (100 / 997)) < 1e-9
    # La comparación contra Estandar usa la fecha REAL de hoy para calcular
    # la edad (a propósito, ver resumen_crianza) — con datos de 2024 eso cae
    # muy lejos de los días 0-1 sembrados, así que acá da None. Se prueba
    # con una fecha fija en test_resumen_compara_contra_estandar_por_edad.
    assert galpon["agua_esperada_litros_pollo_hoy"] is None

    granja = body["granja"]
    assert granja["fecha"] == "2024-01-02"
    assert granja["consumo_gas_hoy"] == 15.0  # 65 - 50
    assert granja["consumo_electricidad_activa_hoy"] == 30.0  # 230 - 200
    assert granja["consumo_electricidad_reactiva_hoy"] == 5.0  # 25 - 20
    # Todavía no hay suficiente historial para un promedio de 3 días.
    assert granja["promedio_gas_3_dias"] is None


def test_resumen_compara_contra_estandar_por_edad(client, crear_usuario, db_session):
    """La edad para comparar contra `Estandar` es la real de hoy (un hecho
    de calendario, no depende de si ya se cargó el dato del día) — se
    prueba pasándole una fecha fija al servicio en vez de a la fecha real
    de cuando corre el test."""
    _admin, _granjero, crianza_id, _cg_id = _armar_crianza_con_datos(client, crear_usuario, db_session)
    crianza = db_session.get(Crianza, crianza_id)

    resumen = resumen_crianza(db_session, crianza, hoy=date(2024, 1, 2))  # día 1 de vida
    galpon = resumen["galpones"][0]
    assert galpon["edad_dias"] == 1
    assert galpon["mortandad_esperada_pct"] == 0.004
    assert galpon["agua_esperada_litros_pollo_hoy"] == 0.03


def test_resumen_crianza_sin_datos_no_rompe(client, crear_usuario):
    admin = crear_usuario("admin2@granjaelmoro.com.ar", "admin")
    crianza_id = client.post(
        "/crianzas", json={"numero": 2, "fecha_inicio": "2024-01-01"}, headers=admin
    ).json()["id"]

    resp = client.get(f"/crianzas/{crianza_id}/resumen", headers=admin)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["alimento_entregado_kg"] == 0.0
    assert body["galpones"] == []
    assert body["granja"]["fecha"] is None


def test_resumen_crianza_inexistente_da_404(client, crear_usuario):
    admin = crear_usuario("admin3@granjaelmoro.com.ar", "admin")
    resp = client.get("/crianzas/9999/resumen", headers=admin)
    assert resp.status_code == 404
