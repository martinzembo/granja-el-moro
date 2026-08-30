def _registrar_y_loguear(client, email, rol, password="clave1234"):
    client.post(
        "/auth/register",
        json={"nombre": email, "email": email, "password": password, "rol": rol},
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_listar_usuarios_requiere_admin(client):
    granjero = _registrar_y_loguear(client, "granjero@granjaelmoro.com.ar", "granjero")
    resp = client.get("/usuarios", headers=granjero)
    assert resp.status_code == 403


def test_listar_usuarios_filtrado_por_rol(client):
    admin = _registrar_y_loguear(client, "admin@granjaelmoro.com.ar", "admin")
    _registrar_y_loguear(client, "granjero1@granjaelmoro.com.ar", "granjero")
    _registrar_y_loguear(client, "granjero2@granjaelmoro.com.ar", "granjero")

    resp = client.get("/usuarios?rol=granjero", headers=admin)
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert emails == {"granjero1@granjaelmoro.com.ar", "granjero2@granjaelmoro.com.ar"}

    resp = client.get("/usuarios?rol=admin", headers=admin)
    assert [u["email"] for u in resp.json()] == ["admin@granjaelmoro.com.ar"]
