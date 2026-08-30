"""Test de integración del flujo completo: alta de crianza, ingreso de aves,
carga diaria (galpón y granja), entrega de insumos, retiro a faena y cierre.
Sigue el mismo circuito real que reemplaza al WhatsApp + Excel de la granja.
"""


def _registrar_y_loguear(client, email, rol, password="clave1234"):
    client.post(
        "/auth/register",
        json={"nombre": email, "email": email, "password": password, "rol": rol},
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_flujo_completo_hasta_el_cierre(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    granjero = _registrar_y_loguear(client, "granjero@granjaelmoro.com.ar", "granjero")
    otro_granjero = _registrar_y_loguear(client, "otro@granjaelmoro.com.ar", "granjero")

    granjero_id = client.get("/auth/me", headers=granjero).json()["id"]

    galpon_id = client.post(
        "/galpones", json={"nombre": "Galpón 1", "capacidad_maxima": 24000}, headers=admin
    ).json()["id"]

    crianza = client.post(
        "/crianzas", json={"numero": 92, "fecha_inicio": "2024-01-01"}, headers=admin
    ).json()
    crianza_id = crianza["id"]

    cg = client.post(
        f"/crianzas/{crianza_id}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": granjero_id},
        headers=admin,
    ).json()
    cg_id = cg["id"]
    # La app admin necesita los nombres resueltos, no solo los ids (ver
    # app/api/routers/crianzas.py `_cg_out`).
    assert cg["galpon_nombre"] == "Galpón 1"
    assert cg["granjero_nombre"] == "granjero@granjaelmoro.com.ar"

    listado = client.get(f"/crianzas/{crianza_id}/galpones", headers=admin).json()
    assert listado[0]["galpon_nombre"] == "Galpón 1"
    assert listado[0]["granjero_nombre"] == "granjero@granjaelmoro.com.ar"

    # Dos partidas de origen distinto el mismo día -> igual que el caso real.
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "Las Violetas", "cantidad": 10500, "muertos_transporte": 13},
        headers=admin,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["cantidad_neta"] == 10487

    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-01", "origen": "HC", "cantidad": 5238, "muertos_transporte": 7},
        headers=admin,
    )
    client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
        json={"fecha": "2024-01-03", "origen": "Las Violetas", "cantidad": 5850, "muertos_transporte": 22},
        headers=admin,
    )
    # Total neto del galpón: 10487 + 5231 + 5828 = 21546 (igual que el galpón 1 real).

    # El granjero asignado puede cargar la lectura diaria de su galpón...
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
        json={"fecha": "2024-01-02", "mortandad": 128, "lectura_agua": 1777013.0},
        headers=granjero,
    )
    assert resp.status_code == 201, resp.text

    # ...pero otro granjero no asignado a ese galpón, no.
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/lecturas",
        json={"fecha": "2024-01-03", "mortandad": 50, "lectura_agua": 1777015.0},
        headers=otro_granjero,
    )
    assert resp.status_code == 403

    # Gas y electricidad son de toda la granja, cualquier granjero asignado
    # a la crianza puede cargarlos.
    resp = client.post(
        f"/crianzas/{crianza_id}/lecturas-granja",
        json={
            "fecha": "2024-01-02",
            "hora_desde": "08:00:00",
            "hora_hasta": "08:00:00",
            "lectura_gas": 572768.0,
            "lectura_electricidad_activa": 123433.0,
            "lectura_electricidad_reactiva": 93795.0,
        },
        headers=granjero,
    )
    assert resp.status_code == 201, resp.text

    # El alimento lo carga el administrador, por remito.
    resp = client.post(
        f"/crianzas/{crianza_id}/entregas",
        json={
            "tipo_insumo": "alimento",
            "fecha": "2024-01-16",
            "remito": "235529",
            "tipo_alimento": 1,
            "kilos": 106959.52,
        },
        headers=admin,
    )
    assert resp.status_code == 201, resp.text

    # Retiro a faena.
    resp = client.post(
        f"/crianzas/{crianza_id}/galpones/{cg_id}/retiros",
        json={
            "fecha": "2024-02-19",
            "remito": "38566",
            "transportista": "LEONARDO",
            "cantidad_aves": 18986,
            "peso_neto": 58940.0,
        },
        headers=admin,
    )
    assert resp.status_code == 201, resp.text

    # Cierre: el admin carga los componentes de la liquidación (valor de
    # entrada manual, no calculado por el sistema).
    resp = client.post(
        f"/crianzas/{crianza_id}/cierre",
        json={
            "fecha_cierre": "2024-02-19",
            "indice_tabla": 534.96,
            "premios": 0,
            "gas_ajuste": 18.98,
            "ajuste": 296.06,
        },
        headers=admin,
    )
    assert resp.status_code == 201, resp.text
    cierre = resp.json()
    assert cierre["total_aves_entregadas"] == 18986
    assert cierre["peso_total"] == 58940.0
    assert cierre["precio_x_pollo"] == 850.0
    assert cierre["monto_total"] == 850.0 * 18986

    # No se puede cerrar dos veces.
    resp = client.post(
        f"/crianzas/{crianza_id}/cierre",
        json={"fecha_cierre": "2024-02-19", "indice_tabla": 1, "premios": 0, "gas_ajuste": 0, "ajuste": 0},
        headers=admin,
    )
    assert resp.status_code == 400
