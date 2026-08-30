from fastapi import FastAPI

from app.api.routers import alertas, auth, cierre, crianzas, galpones, insumos, lecturas, me, retiros, usuarios

app = FastAPI(title="Granja El Moro API")

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
