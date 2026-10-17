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


def test_listar_usuarios_pendientes_de_activar(client, crear_usuario):
    admin = crear_usuario("admin@granjaelmoro.com.ar", "admin")
    # crear_usuario activa al granjero de una (ver conftest.py) — para
    # probar el filtro de pendientes hay que registrar sin pasar por ahí.
    client.post(
        "/auth/register",
        json={"nombre": "Pendiente", "email": "pendiente@granjaelmoro.com.ar", "password": "clave12345"},
    )

    resp = client.get("/usuarios?rol=granjero", headers=admin)
    assert resp.json() == []  # el filtro por defecto (activo=true) no lo trae

    resp = client.get("/usuarios?activo=false&rol=granjero", headers=admin)
    assert [u["email"] for u in resp.json()] == ["pendiente@granjaelmoro.com.ar"]
