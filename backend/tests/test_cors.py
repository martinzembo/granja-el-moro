"""El panel web (web/) corre en el navegador, a diferencia de la app
móvil — sin CORS habilitado, el navegador bloquea los pedidos con
"Failed to fetch" antes de que lleguen a FastAPI (ver app/main.py)."""


def test_responde_con_header_cors_para_cualquier_origen(client):
    resp = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "*"
