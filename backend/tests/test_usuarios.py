def test_listar_usuarios_requiere_admin(client, crear_usuario):
    granjero = crear_usuario("granjero@granjaelmoro.com.ar", "granjero")
    resp = client.get("/usuarios", headers=granjero)
    assert resp.status_code == 403


def test_listar_usuarios_filtrado_por_rol(client, crear_usuario):
    admin = crear_usuario("admin@granjaelmoro.com.ar", "admin")
    crear_usuario("granjero1@granjaelmoro.com.ar", "granjero")
    crear_usuario("granjero2@granjaelmoro.com.ar", "granjero")

    resp = client.get("/usuarios?rol=granjero", headers=admin)
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert emails == {"granjero1@granjaelmoro.com.ar", "granjero2@granjaelmoro.com.ar"}

    resp = client.get("/usuarios?rol=admin", headers=admin)
    assert [u["email"] for u in resp.json()] == ["admin@granjaelmoro.com.ar"]
