"""Guardas de integridad de app/api/validaciones.py y las reglas propias de
cada router (capacidad de galpón, aves vivas disponibles, permisos de
insumos/retiros). Complementa a test_crianza_flujo.py, que cubre el camino
feliz completo.
"""

from datetime import date, timedelta


def _registrar_y_loguear(client, email, rol, password="clave1234"):
    client.post(
        "/auth/register",
        json={"nombre": email, "email": email, "password": password, "rol": rol},
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _armar_crianza_con_galpon(client, admin, fecha_inicio="2024-01-01"):
    granjero_id = client.get(
        "/auth/me", headers=_registrar_y_loguear(client, "granjero@granjaelmoro.com.ar", "granjero")
    ).json()["id"]
    galpon_id = client.post(
        "/galpones", json={"nombre": "Galpón 1", "capacidad_maxima": 20000}, headers=admin
    ).json()["id"]
    crianza_id = client.post(
        "/crianzas", json={"numero": 1, "fecha_inicio": fecha_inicio}, headers=admin
    ).json()["id"]
    cg_id = client.post(
        f"/crianzas/{crianza_id}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": granjero_id},
        headers=admin,
    ).json()["id"]
    return crianza_id, galpon_id, cg_id


def test_no_se_puede_asignar_el_mismo_galpon_dos_veces(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, galpon_id, _ = _armar_crianza_con_galpon(client, admin)

    otro_granjero_id = client.get(
        "/auth/me", headers=_registrar_y_loguear(client, "granjero2@granjaelmoro.com.ar", "granjero")
    ).json()["id"]
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": otro_granjero_id},
        headers=admin,
    )
    assert resp.status_code == 400


def test_no_se_puede_asignar_galpon_ya_en_uso_en_otra_crianza_en_curso(client):
    """Un galpón físico no puede estar corriendo dos crianzas a la vez,
    aunque sean crianzas distintas."""
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza1_id, galpon_id, cg1_id = _armar_crianza_con_galpon(client, admin)

    granjero2_id = client.get(
        "/auth/me", headers=_registrar_y_loguear(client, "granjero2@granjaelmoro.com.ar", "granjero")
    ).json()["id"]
    crianza2_id = client.post(
        "/crianzas", json={"numero": 2, "fecha_inicio": "2024-01-01"}, headers=admin
    ).json()["id"]

    resp = client.post(
        f"/crianzas/{crianza2_id}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": granjero2_id},
        headers=admin,
    )
    assert resp.status_code == 400
    assert "en curso" in resp.text

    # Si la primera crianza se cierra, el galpón queda libre para la segunda.
    client.post(
        f"/crianzas/{crianza1_id}/galpones/{cg1_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )
    client.post(
        f"/crianzas/{crianza1_id}/galpones/{cg1_id}/retiros",
        json={"fecha": "2024-01-10", "remito": "1", "transportista": "X", "cantidad_aves": 1000, "peso_neto": 3000},
        headers=admin,
    )
    client.post(
        f"/crianzas/{crianza1_id}/entregas",
        json={"tipo_insumo": "alimento", "fecha": "2024-01-05", "remito": "1", "kilos": 2000},
        headers=admin,
    )
    cierre = client.post(
        f"/crianzas/{crianza1_id}/cierre",
        json={"fecha_cierre": "2024-01-10", "indice_tabla": 100, "premios": 0, "gas_ajuste": 0, "ajuste": 0},
        headers=admin,
    )
    assert cierre.status_code == 201, cierre.text

    resp = client.post(
        f"/crianzas/{crianza2_id}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": granjero2_id},
        headers=admin,
    )
    assert resp.status_code == 201, resp.text


def test_ingreso_no_puede_superar_capacidad_del_galpon(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin)

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 25000, "muertos_transporte": 0},
        headers=admin,
    )
    assert resp.status_code == 400
    assert "capacidad" in resp.text


def test_muertos_transporte_no_puede_superar_cantidad(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin)

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 1000, "muertos_transporte": 1001},
        headers=admin,
    )
    assert resp.status_code == 400


def test_ingreso_no_puede_ser_anterior_al_inicio_de_la_crianza(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin, fecha_inicio="2024-01-10")

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )
    assert resp.status_code == 400


def test_ingreso_no_puede_ser_en_el_futuro(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    manana = (date.today() + timedelta(days=1)).isoformat()
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin, fecha_inicio="2024-01-01")

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": manana, "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )
    assert resp.status_code == 400


def test_lectura_no_puede_ser_anterior_al_ingreso_de_aves(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin)

    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-05", "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )
    # El admin puede cargar lecturas también (no solo el granjero asignado).
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
        json={"fecha": "2024-01-01", "mortandad": 0, "lectura_agua": 0},
        headers=admin,
    )
    assert resp.status_code == 400


def test_no_se_puede_cargar_datos_en_crianza_cerrada(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin)

    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )
    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/retiros",
        json={"fecha": "2024-01-10", "remito": "1", "transportista": "X", "cantidad_aves": 1000, "peso_neto": 3000},
        headers=admin,
    )
    client.post(
        f"/crianzas/{crianza_id}/entregas",
        json={"tipo_insumo": "alimento", "fecha": "2024-01-05", "remito": "1", "kilos": 2000},
        headers=admin,
    )
    cierre = client.post(
        f"/crianzas/{crianza_id}/cierre",
        json={"fecha_cierre": "2024-01-10", "indice_tabla": 100, "premios": 0, "gas_ajuste": 0, "ajuste": 0},
        headers=admin,
    )
    assert cierre.status_code == 201, cierre.text

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
        json={"fecha": "2024-01-11", "mortandad": 1, "lectura_agua": 10},
        headers=admin,
    )
    assert resp.status_code == 400

    resp = client.post(
        f"/crianzas/{crianza_id}/entregas",
        json={"tipo_insumo": "alimento", "fecha": "2024-01-11", "remito": "1", "kilos": 100},
        headers=admin,
    )
    assert resp.status_code == 400


def test_retiro_no_puede_superar_aves_vivas_disponibles(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin)

    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/retiros",
        json={"fecha": "2024-01-10", "remito": "1", "transportista": "X", "cantidad_aves": 1001, "peso_neto": 3000},
        headers=admin,
    )
    assert resp.status_code == 400
    assert "aves vivas disponibles" in resp.text


def test_insumos_requiere_admin(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    granjero = _registrar_y_loguear(client, "granjero4@granjaelmoro.com.ar", "granjero")
    crianza_id = client.post(
        "/crianzas", json={"numero": 1, "fecha_inicio": "2024-01-01"}, headers=admin
    ).json()["id"]

    resp = client.post(
        f"/crianzas/{crianza_id}/entregas",
        json={"tipo_insumo": "alimento", "fecha": "2024-01-01", "remito": "1", "kilos": 100},
        headers=granjero,
    )
    assert resp.status_code == 403

    resp = client.post(
        f"/crianzas/{crianza_id}/entregas",
        json={"tipo_insumo": "alimento", "fecha": "2024-01-01", "remito": "1", "kilos": 100},
        headers=admin,
    )
    assert resp.status_code == 201

    resp = client.get(f"/crianzas/{crianza_id}/entregas", headers=granjero)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_retiros_requiere_admin(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    granjero = _registrar_y_loguear(client, "granjero5@granjaelmoro.com.ar", "granjero")
    crianza_id, _, cg_id = _armar_crianza_con_galpon(client, admin)
    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 1000, "muertos_transporte": 0},
        headers=admin,
    )

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/retiros",
        json={"fecha": "2024-01-10", "remito": "1", "transportista": "X", "cantidad_aves": 500, "peso_neto": 1500},
        headers=granjero,
    )
    assert resp.status_code == 403

    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/retiros",
        json={"fecha": "2024-01-10", "remito": "1", "transportista": "X", "cantidad_aves": 500, "peso_neto": 1500},
        headers=admin,
    )
    assert resp.status_code == 201

    resp = client.get(f"/crianzas/{crianza_id}/galpones/{cg_id}/retiros", headers=granjero)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_cierre_antes_de_cerrar_da_404(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    crianza_id, _, _ = _armar_crianza_con_galpon(client, admin)

    resp = client.get(f"/crianzas/{crianza_id}/cierre", headers=admin)
    assert resp.status_code == 404

    resp = client.get(f"/crianzas/{crianza_id}/cierre/galpones", headers=admin)
    assert resp.status_code == 200
    assert resp.json() == []
