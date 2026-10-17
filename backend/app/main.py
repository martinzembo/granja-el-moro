from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import alertas, auth, cierre, crianzas, galpones, insumos, lecturas, me, retiros, usuarios

app = FastAPI(title="Granja El Moro API")

# El panel web (web/) corre en el navegador, a diferencia de la app móvil
# — sin esto, el navegador bloquea los pedidos a este backend por CORS
# (ver CLAUDE.md, sección Web). Se permite cualquier origen porque la
# IP/puerto desde donde se sirve el panel puede variar (dev, LAN de la
# granja, etc. — ver web/src/core/config.js) y la auth es por Bearer token
# en el header, no por cookies, así que un origen abierto acá no habilita
# CSRF.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(galpones.router)
app.include_router(crianzas.router)
app.include_router(lecturas.router)
app.include_router(insumos.router)
app.include_router(retiros.router)
app.include_router(cierre.router)
app.include_router(alertas.router)
app.include_router(me.router)


@app.get("/health")
def health():
    return {"status": "ok"}
