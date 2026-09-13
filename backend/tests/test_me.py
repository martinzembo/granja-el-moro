def test_mis_asignaciones(client, crear_usuario):
    admin = crear_usuario("admin@granjaelmoro.com.ar", "admin")
    granjero = crear_usuario("granjero@granjaelmoro.com.ar", "granjero")
    otro_granjero = crear_usuario("otro@granjaelmoro.com.ar", "granjero")

    granjero_id = client.get("/auth/me", headers=granjero).json()["id"]
    galpon_id = client.post(
        "/galpones", json={"nombre": "Galpón 1", "capacidad_maxima": 20000}, headers=admin
    ).json()["id"]
    crianza = client.post(
        "/crianzas", json={"numero": 1, "fecha_inicio": "2024-01-01"}, headers=admin
    ).json()
    client.post(
        f"/crianzas/{crianza['id']}/galpones",
        json={"galpon_id": galpon_id, "granjero_id": granjero_id},
        headers=admin,
    )

    resp = client.get("/me/asignaciones", headers=granjero)
    assert resp.status_code == 200
    asignaciones = resp.json()
    assert len(asignaciones) == 1
    assert asignaciones[0]["crianza_numero"] == 1
    assert asignaciones[0]["galpon_nombre"] == "Galpón 1"
    assert asignaciones[0]["crianza_estado"] == "en_curso"

    resp_otro = client.get("/me/asignaciones", headers=otro_granjero)
    assert resp_otro.status_code == 200
    assert resp_otro.json() == []
