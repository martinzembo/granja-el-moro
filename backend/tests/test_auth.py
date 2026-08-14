def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_and_login(client):
    register_payload = {
        "nombre": "Admin Test",
        "email": "admin@granjaelmoro.com.ar",
        "password": "supersegura123",
        "rol": "admin",
    }
    resp = client.post("/auth/register", json=register_payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == register_payload["email"]
    assert "password" not in body
    assert "password_hash" not in body

    resp = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == register_payload["email"]


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "nombre": "Otro",
            "email": "otro@granjaelmoro.com.ar",
            "password": "correcta123",
            "rol": "granjero",
        },
    )
    resp = client.post(
        "/auth/login", json={"email": "otro@granjaelmoro.com.ar", "password": "incorrecta"}
    )
    assert resp.status_code == 401


def test_galpones_requiere_admin_para_crear(client):
    # granjero se registra y loguea
    client.post(
        "/auth/register",
        json={
            "nombre": "Granjero",
            "email": "granjero@granjaelmoro.com.ar",
            "password": "clave1234",
            "rol": "granjero",
        },
    )
    login = client.post(
        "/auth/login", json={"email": "granjero@granjaelmoro.com.ar", "password": "clave1234"}
    )
    token = login.json()["access_token"]

    resp = client.post(
        "/galpones",
        json={"nombre": "Galpón 1", "capacidad_maxima": 24000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
