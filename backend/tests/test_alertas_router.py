"""Tests de los endpoints HTTP de alertas — complementa a test_alertas.py,
que prueba app/services/alertas.py directo contra el modelo, sin pasar por
la API.
"""


def _registrar_y_loguear(client, email, rol, password="clave1234"):
    client.post(
        "/auth/register",
        json={"nombre": email, "email": email, "password": password, "rol": rol},
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _armar_dos_crianzas_con_mortandad_critica(client):
    """Dos crianzas con un galpón cada una; a la crianza 1 le carga una
    mortandad muy por encima del estándar (dispara alerta), a la crianza 2
    no le carga nada — sirve para probar que el scope por crianza funciona.
    """
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    granjero = _registrar_y_loguear(client, "granjero@granjaelmoro.com.ar", "granjero")
    granjero_id = client.get("/auth/me", headers=granjero).json()["id"]

    ids = {}
    for numero in (1, 2):
        galpon_id = client.post(
            "/galpones", json={"nombre": f"Galpon {numero}", "capacidad_maxima": 20000}, headers=admin
        ).json()["id"]
        crianza_id = client.post(
            "/crianzas", json={"numero": numero, "fecha_inicio": "2024-01-01"}, headers=admin
        ).json()["id"]
        cg_id = client.post(
            f"/crianzas/{crianza_id}/galpones",
            json={"galpon_id": galpon_id, "granjero_id": granjero_id},
            headers=admin,
        ).json()["id"]
        client.post(
            f"/crianzas/{crianza_id}/galpones/{cg_id}/ingresos",
            json={"fecha": "2024-01-01", "origen": "Test", "cantidad": 10000, "muertos_transporte": 0},
            headers=admin,
        )
        ids[numero] = {"crianza_id": crianza_id, "cg_id": cg_id}

    # Mortandad crítica solo en la crianza 1 (día 1, sin Estandar sembrado
    # no dispara nada — así que primero sembramos un Estandar mínimo).
    return admin, granjero, ids


def test_listar_alertas_scope_por_crianza(client, db_session):

    from app.models.estandar import Estandar

    db_session.add(Estandar(dia_vida=0, mortandad_acumulada_esperada=0.001, agua_litros_pollo_esperado=0.01))
    db_session.commit()

    admin, granjero, ids = _armar_dos_crianzas_con_mortandad_critica(client)

    # Mortandad muy alta en crianza 1, día 0 (misma fecha del ingreso).
    resp = client.post(
        f"/crianzas/{ids[1]['crianza_id']}/galpones/{ids[1]['cg_id']}/lecturas",
        json={"fecha": "2024-01-01", "mortandad": 500, "lectura_agua": 100.0},
        headers=granjero,
    )
    assert resp.status_code == 201, resp.text

    alertas_crianza_1 = client.get(f"/crianzas/{ids[1]['crianza_id']}/alertas", headers=admin).json()
    assert len(alertas_crianza_1) >= 1
    assert all(a["tipo"] == "mortandad" for a in alertas_crianza_1)

    # La crianza 2 no tiene ninguna alerta — no se filtró mal el scope.
    alertas_crianza_2 = client.get(f"/crianzas/{ids[2]['crianza_id']}/alertas", headers=admin).json()
    assert alertas_crianza_2 == []


def test_resolver_alerta_de_otra_crianza_da_404(client, db_session):
    """Regresión del bug: resolver_alerta no chequeaba que la alerta
    perteneciera a la crianza del path — antes esto devolvía 200."""

    from app.models.estandar import Estandar

    db_session.add(Estandar(dia_vida=0, mortandad_acumulada_esperada=0.001, agua_litros_pollo_esperado=0.01))
    db_session.commit()

    admin, granjero, ids = _armar_dos_crianzas_con_mortandad_critica(client)

    client.post(
        f"/crianzas/{ids[1]['crianza_id']}/galpones/{ids[1]['cg_id']}/lecturas",
        json={"fecha": "2024-01-01", "mortandad": 500, "lectura_agua": 100.0},
        headers=granjero,
    )
    alerta_id = client.get(f"/crianzas/{ids[1]['crianza_id']}/alertas", headers=admin).json()[0]["id"]

    # Intentar resolverla "a través" de la crianza 2 -> no le pertenece.
    resp = client.patch(f"/crianzas/{ids[2]['crianza_id']}/alertas/{alerta_id}/resolver", headers=admin)
    assert resp.status_code == 404

    # Por la crianza correcta sí funciona.
    resp = client.patch(f"/crianzas/{ids[1]['crianza_id']}/alertas/{alerta_id}/resolver", headers=admin)
    assert resp.status_code == 200
    assert resp.json()["resuelta"] is True


def test_resolver_alerta_requiere_admin(client, db_session):
    from app.models.estandar import Estandar

    db_session.add(Estandar(dia_vida=0, mortandad_acumulada_esperada=0.001, agua_litros_pollo_esperado=0.01))
    db_session.commit()

    admin, granjero, ids = _armar_dos_crianzas_con_mortandad_critica(client)
    client.post(
        f"/crianzas/{ids[1]['crianza_id']}/galpones/{ids[1]['cg_id']}/lecturas",
        json={"fecha": "2024-01-01", "mortandad": 500, "lectura_agua": 100.0},
        headers=granjero,
    )
    alerta_id = client.get(f"/crianzas/{ids[1]['crianza_id']}/alertas", headers=admin).json()[0]["id"]

    resp = client.patch(f"/crianzas/{ids[1]['crianza_id']}/alertas/{alerta_id}/resolver", headers=granjero)
    assert resp.status_code == 403


def test_filtro_resuelta(client, db_session):
    from app.models.estandar import Estandar

    db_session.add(Estandar(dia_vida=0, mortandad_acumulada_esperada=0.001, agua_litros_pollo_esperado=0.01))
    db_session.commit()

    admin, granjero, ids = _armar_dos_crianzas_con_mortandad_critica(client)
    client.post(
        f"/crianzas/{ids[1]['crianza_id']}/galpones/{ids[1]['cg_id']}/lecturas",
        json={"fecha": "2024-01-01", "mortandad": 500, "lectura_agua": 100.0},
        headers=granjero,
    )
    # Con mortandad=500 disparan dos alertas (pico diario + acumulado
    # crítico) — se resuelven todas para poder afirmar sin_resolver == [].
    disparadas = client.get(f"/crianzas/{ids[1]['crianza_id']}/alertas", headers=admin).json()
    assert len(disparadas) == 2
    for alerta in disparadas:
        client.patch(f"/crianzas/{ids[1]['crianza_id']}/alertas/{alerta['id']}/resolver", headers=admin)

    sin_resolver = client.get(f"/crianzas/{ids[1]['crianza_id']}/alertas?resuelta=false", headers=admin).json()
    resueltas = client.get(f"/crianzas/{ids[1]['crianza_id']}/alertas?resuelta=true", headers=admin).json()
    assert sin_resolver == []
    assert len(resueltas) == 2
