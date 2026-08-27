from fastapi import FastAPI

from app.api.routers import auth, cierre, crianzas, galpones, insumos, lecturas, retiros

app = FastAPI(title="Granja El Moro API")

app.include_router(auth.router)
app.include_router(galpones.router)
app.include_router(crianzas.router)
app.include_router(lecturas.router)
app.include_router(insumos.router)
app.include_router(retiros.router)
app.include_router(cierre.router)


@app.get("/health")
def health():
    return {"status": "ok"}
