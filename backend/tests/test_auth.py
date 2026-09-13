def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_and_login(client):
    register_payload = {
        "nombre": "Granjero Test",
        "email": "granjero@granjaelmoro.com.ar",
        "password": "supersegura123",
    }
    resp = client.post("/auth/register", json=register_payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == register_payload["email"]
    assert body["rol"] == "granjero"
    assert body["activo"] is True
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


def test_registro_publico_no_puede_elegir_rol(client):
    """RegistroCreate usa extra="forbid" — un `rol` colado en el body
    devuelve 422, no se ignora en silencio ni crea un admin."""
    resp = client.post(
        "/auth/register",
        json={
            "nombre": "Intento Admin",
            "email": "intento@granjaelmoro.com.ar",
            "password": "clave12345",
            "rol": "admin",
        },
    )
    assert resp.status_code == 422


def test_registro_publico_rechaza_password_corta(client):
    resp = client.post(
        "/auth/register",
        json={"nombre": "Corto", "email": "corto@granjaelmoro.com.ar", "password": "1234567"},
    )
    assert resp.status_code == 422


def test_registro_rechaza_email_duplicado_exacto(client):
    client.post(
        "/auth/register",
        json={"nombre": "Uno", "email": "duplicado@granjaelmoro.com.ar", "password": "clave12345"},
    )
    resp = client.post(
        "/auth/register",
        json={"nombre": "Dos", "email": "duplicado@granjaelmoro.com.ar", "password": "otraclave123"},
    )
    assert resp.status_code == 400
    assert "ya está registrado" in resp.text


def test_email_es_case_sensitive(client):
    """Decisión explícita del cliente: "Casing@x.com" y "casing@x.com" son
    cuentas distintas — no se normaliza a minúsculas ni al registrarse ni al
    loguearse (ver app/schemas/usuario.py, _normalizar_email)."""
    client.post(
        "/auth/register",
        json={"nombre": "Casing", "email": "Casing@granjaelmoro.com.ar", "password": "clave12345"},
    )
    # Mismo email pero en minúsculas -> no es la misma cuenta, se puede
    # registrar de nuevo sin chocar con "ya está registrado".
    resp = client.post(
        "/auth/register",
        json={"nombre": "Otro Casing", "email": "casing@granjaelmoro.com.ar", "password": "clave12345"},
    )
    assert resp.status_code == 201, resp.text

    # Loguearse con una capitalización distinta a la registrada falla.
    resp = client.post(
        "/auth/login", json={"email": "CASING@granjaelmoro.com.ar", "password": "clave12345"}
    )
    assert resp.status_code == 401

    # Con la capitalización exacta funciona.
    resp = client.post(
        "/auth/login", json={"email": "Casing@granjaelmoro.com.ar", "password": "clave12345"}
    )
    assert resp.status_code == 200, resp.text


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "nombre": "Otro",
            "email": "otro@granjaelmoro.com.ar",
            "password": "correcta123",
        },
    )
    resp = client.post(
        "/auth/login", json={"email": "otro@granjaelmoro.com.ar", "password": "incorrecta"}
    )
    assert resp.status_code == 401


def test_galpones_requiere_admin_para_crear(client, crear_usuario):
    granjero = crear_usuario("granjero@granjaelmoro.com.ar", "granjero")

    resp = client.post(
        "/galpones",
        json={"nombre": "Galpón 1", "capacidad_maxima": 24000},
        headers=granjero,
    )
    assert resp.status_code == 403


def test_admin_no_se_crea_por_http_pero_si_por_el_script(client, db_session):
    from app.db.crear_admin import crear_admin

    admin = crear_admin(db_session, "Admin Real", "admin@granjaelmoro.com.ar", "clave12345")
    assert admin.rol.value == "admin"

    resp = client.post(
        "/auth/login", json={"email": "admin@granjaelmoro.com.ar", "password": "clave12345"}
    )
    assert resp.status_code == 200, resp.text
