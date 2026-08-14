from fastapi import FastAPI

from app.api.routers import auth, crianzas, galpones

app = FastAPI(title="Granja El Moro API")

app.include_router(auth.router)
app.include_router(galpones.router)
app.include_router(crianzas.router)


@app.get("/health")
def health():
    return {"status": "ok"}
