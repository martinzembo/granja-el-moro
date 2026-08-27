# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Sistema de gestión de crianzas avícolas para Granja "El Moro" (Lobos, Buenos
Aires). Reemplaza un flujo manual de WhatsApp + planillas por una app móvil
(carga diaria de granjeros) + panel web (monitoreo del administrador) sobre
una API común. Contexto completo del negocio, objetivos y alcance en
[docs/propuesta.md](docs/propuesta.md).

Plan de desarrollo (orden de construcción por etapas, no un cronograma
estricto) en [docs/plan.md](docs/plan.md). Modelo de datos en
[docs/modelo-datos.md](docs/modelo-datos.md) — está basado en datos reales de
una crianza real de la granja (mensajes de WhatsApp del granjero + el Excel
`docs/crianza92.xls` que arma el administrador), no en supuestos. Las
fórmulas de cierre (índice de crecimiento, conversión, índice de eficiencia)
están verificadas exactas contra esos números reales.

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
  `crianzas`, `lecturas`, `insumos`, `retiros`, `cierre`). Los endpoints son
  delgados: validan con el schema de Pydantic, hacen la operación de
  SQLAlchemy directo contra la sesión, devuelven. No hay capa de
  repositorio/service genérica — para este tamaño de proyecto se decidió no
  agregarla. La única excepción es `app/services/calculos.py`: el cierre de
  crianza (índice de crecimiento, conversión, índice de eficiencia,
  liquidación) es lógica de negocio no trivial y verificada contra datos
  reales, así que vive en un módulo aparte en vez de inline en
  `routers/cierre.py`. Si otro endpoint empieza a acumular ese tipo de
  lógica (ver Semana 3 del plan: alertas por desvío de `Estandar`), va en
  `app/services/` también, no inline en el router.
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

### Granularidad de la carga de datos (importante)

No todo se carga por galpón ni todo diario — ver
[docs/modelo-datos.md](docs/modelo-datos.md) para el detalle completo, pero
en resumen: mortandad y agua son **por galpón, diarias** (`LecturaDiariaGalpon`,
agua como lectura cruda de caudalímetro, no consumo ya calculado); gas y
electricidad son **de toda la granja, diarias** (`LecturaDiariaGranja`, un
solo medidor de cada uno); alimento y cáscara son **por evento** (remito,
`EntregaInsumo`, no diario, no por galpón). Un galpón puede tener varias
partidas de ingreso de aves con fechas/orígenes distintos (`IngresoAves`) —
la edad de un galpón para comparar contra `Estandar` es un promedio
ponderado por esas partidas (`edad_ponderada` en `app/services/calculos.py`),
no una resta simple de fechas.

### Pendiente / decisiones abiertas

Ver la sección final de [docs/modelo-datos.md](docs/modelo-datos.md). Lo más
relevante: el reparto de alimento consumido por galpón es una aproximación
(proporcional a aves×días, igual criterio que usa el Excel de la granja pero
no idéntico bit a bit), y la tabla real de precio de liquidación
(`indice_tabla` en `CierreCrianza`) es un dato de entrada manual — el
administrador confirmó que ese cálculo lo hace la integradora con su propia
fórmula interna, no se modela acá.

## Mobile y Web

Todavía no iniciados (Semana 4-5 y 6-7 del plan, respectivamente). Cuando
arranquen, documentar acá su estructura y comandos siguiendo el mismo formato
que la sección de Backend.
