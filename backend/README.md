# Backend — Granja El Moro

API REST en FastAPI + PostgreSQL + Alembic. Ver [../docs/modelo-datos.md](../docs/modelo-datos.md)
para el modelo de datos y [../docs/plan.md](../docs/plan.md) para el plan de desarrollo.

## Setup local

Requiere Python 3.11+ y PostgreSQL corriendo localmente (o accesible por red).

```bash
cd backend
python -m venv venv
./venv/Scripts/activate       # Windows (PowerShell: .\venv\Scripts\Activate.ps1)
pip install -r requirements.txt

cp .env.example .env          # completar DATABASE_URL y SECRET_KEY
# generar SECRET_KEY con: python -c "import secrets; print(secrets.token_hex(32))"
```

Crear la base en Postgres (nombre según `DATABASE_URL`, por defecto `elmoro`):

```sql
CREATE DATABASE elmoro;
```

Aplicar migraciones:

```bash
alembic upgrade head
```

## Correr el servidor

```bash
uvicorn app.main:app --reload
```

Docs interactivas (Swagger) en `http://127.0.0.1:8000/docs`.

## Tests

Los tests corren contra SQLite en memoria (no requieren Postgres levantado):

```bash
pytest
```

## Migraciones (Alembic)

Después de modificar un modelo en `app/models/`:

```bash
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

Siempre revisar el archivo de migración generado antes de aplicarlo — el
autogenerate no detecta todo (renombres de columnas, algunos cambios de tipo).
