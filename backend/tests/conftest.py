import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app

# Tests corren contra SQLite en memoria: no requieren Postgres levantado.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Sesión directa contra la misma base SQLite en memoria, para tests que
    trabajan con modelos sin pasar por la API (ej. tests de servicios)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def crear_usuario(client, db_session):
    """Da de alta un usuario y devuelve el header de Authorization ya
    logueado. Los granjeros se dan de alta por el registro público
    (`POST /auth/register`, ya no acepta `rol`: siempre crea granjero); los
    admin se crean directo en la base con app/db/crear_admin.py, igual que
    en producción — no existe ningún endpoint que cree un admin.
    """

    def _crear(email: str, rol: str, password: str = "clave1234", nombre: str | None = None):
        nombre = nombre or email
        if rol == "admin":
            from app.db.crear_admin import crear_admin

            crear_admin(db_session, nombre, email, password)
        else:
            client.post(
                "/auth/register",
                json={"nombre": nombre, "email": email, "password": password},
            )
        login = client.post("/auth/login", json={"email": email, "password": password})
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _crear
