# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Sistema de gestión de crianzas avícolas para Granja "El Moro" (Lobos, Buenos
Aires). Reemplaza un flujo manual de WhatsApp + planillas por una app móvil
(carga diaria de granjeros) + panel web (monitoreo del administrador) sobre
una API común. Contexto completo del negocio, objetivos y alcance en
[docs/propuesta.md](docs/propuesta.md).

Plan de desarrollo (orden de construcción por etapas, no un cronograma
estricto) en [docs/plan.md](docs/plan.md). Modelo de datos, incluyendo
supuestos pendientes de validar con la granja (unidades de medida, estructura
real de la tabla de liquidación), en [docs/modelo-datos.md](docs/modelo-datos.md).

## Repo layout (monorepo)

- `backend/` — API REST (FastAPI + PostgreSQL + Alembic). En desarrollo activo.
- `mobile/` — app Flutter para granjeros (carga diaria). Aún no iniciada.
- `web/` — panel React para el administrador. Aún no iniciada.
- `docs/` — propuesta de proyecto, plan y modelo de datos.

## Backend

### Comandos

```bash
cd backend
python -m venv venv && ./venv/Scripts/activate   # ya creado; recrear si falta
pip install -r requirements.txt

uvicorn app.main:app --reload                     # correr servidor (docs en /docs)
pytest                                            # test suite completo (SQLite en memoria, no requiere Postgres)
pytest tests/test_auth.py::test_register_and_login  # un test puntual

alembic revision --autogenerate -m "descripción"  # nueva migración tras cambiar un modelo
alembic upgrade head                              # aplicar migraciones (requiere Postgres corriendo)
```

Setup completo (incluyendo `.env`) en [backend/README.md](backend/README.md).

### Arquitectura

Capas, de afuera hacia adentro:

- `app/main.py` — arma la app FastAPI e incluye los routers.
- `app/api/routers/*.py` — un router por recurso (`auth`, `galpones`,
  `crianzas`, ...). Los endpoints son delgados: validan con el schema de
  Pydantic, hacen la operación de SQLAlchemy directo contra la sesión, devuelven.
  No hay capa de repositorio/service intermedia — para este tamaño de proyecto
  se decidió no agregarla; si un endpoint empieza a acumular lógica de negocio
  no trivial (ver Semana 3 del plan: alertas, índices de conversión/crecimiento),
  esa lógica va en un módulo aparte, no inline en el router.
- `app/api/deps.py` — dependencias de FastAPI compartidas: `get_current_user`
  decodifica el JWT contra la tabla `usuarios`; `require_role(*roles)` es una
  factory que devuelve una dependency para restringir un endpoint a roles
  puntuales (ej. `Depends(require_role(RolUsuario.admin))`).
- `app/schemas/*.py` — modelos Pydantic de entrada/salida de la API. Nunca se
  devuelve un modelo de SQLAlchemy directo; siempre pasa por un `*Out` con
  `from_attributes=True`.
- `app/models/*.py` — modelos SQLAlchemy 2.0 (`Mapped`/`mapped_column`),
  todos heredando de `Base` (`app/db/session.py`). `app/models/__init__.py`
  los importa todos: es el punto que Alembic usa (vía `alembic/env.py`) para
  ver el metadata completo al autogenerar migraciones — un modelo nuevo que no
  se agregue ahí no aparece en las migraciones.
- `app/core/config.py` — `Settings` (pydantic-settings) lee `.env`. Cualquier
  variable de entorno nueva se declara acá, no se lee con `os.environ` suelto.
- `app/core/security.py` — hashing de passwords con `bcrypt` directo (no
  `passlib`: es incompatible con versiones recientes de `bcrypt`, ver historial
  de commits) y creación/decodificación de JWT.

### Auth y roles

Dos roles: `admin` y `granjero` (`RolUsuario` en `app/models/usuario.py`). El
JWT lleva `sub` (id de usuario) y `rol`. Un endpoint que requiere estar
logueado usa `Depends(get_current_user)`; uno restringido a un rol usa
`Depends(require_role(RolUsuario.admin))`. El patrón para nuevos routers está
en `app/api/routers/galpones.py` (CRUD completo con lectura abierta a
cualquier usuario autenticado y escritura restringida a admin).

### Testing

`tests/conftest.py` levanta una base SQLite en memoria y sobreescribe la
dependency `get_db` de la app — los tests no requieren Postgres. Cada test
recibe una base limpia (`create_all`/`drop_all` por fixture). Al agregar un
router nuevo, seguir el patrón de `tests/test_auth.py` (fixture `client`).

### Pendiente / decisiones abiertas

Ver la sección final de [docs/modelo-datos.md](docs/modelo-datos.md) — hay
varios campos del modelo (unidades de agua/gas/electricidad, frecuencia de
pesaje, estructura de la tabla de liquidación de doble entrada) marcados
`[CONFIRMAR]` porque se derivaron de la propuesta sin validar con la granja.
No asumir que esos valores son definitivos al construir sobre ellos.

## Mobile y Web

Todavía no iniciados (Semana 4-5 y 6-7 del plan, respectivamente). Cuando
arranquen, documentar acá su estructura y comandos siguiendo el mismo formato
que la sección de Backend.
