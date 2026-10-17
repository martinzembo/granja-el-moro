# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Convenciones de git

**No agregar líneas de atribución a Claude en los commits** (nada de
`Co-Authored-By: Claude...` ni menciones similares) — pedido explícito del
cliente, que además hizo reescribir el historial existente para sacar las
que ya estaban. Esto vale para todo commit hecho en este repo, sin
excepción.

## Project

Sistema de gestión de crianzas avícolas para Granja "El Moro" (Lobos, Buenos
Aires). Reemplaza un flujo manual de WhatsApp + planillas: carga diaria del
granjero desde una app Android y administración desde un panel web, sobre
una API común. Contexto completo del negocio, objetivos y alcance original
en [docs/propuesta.md](docs/propuesta.md). El alcance se ajustó dos veces
sobre esa propuesta original — primero a una sola app Android para los dos
roles, después (corrección del docente de la cátedra que evalúa el
proyecto, viendo capturas de la app) de vuelta a panel web para el admin +
app Android solo para el granjero, que es como quedó. Ver
[docs/plan.md](docs/plan.md) sección "Ajuste de alcance" para el detalle de
ambos cambios.

Plan de desarrollo (orden de construcción por etapas, no un cronograma
estricto) en [docs/plan.md](docs/plan.md). Modelo de datos en
[docs/modelo-datos.md](docs/modelo-datos.md) — está basado en datos reales de
una crianza real de la granja (mensajes de WhatsApp del granjero + el Excel
`docs/crianza92.xls` que arma el administrador), no en supuestos. Las
fórmulas de cierre (índice de crecimiento, conversión, índice de eficiencia)
están verificadas exactas contra esos números reales.

## Repo layout (monorepo)

- `backend/` — API REST (FastAPI + PostgreSQL + Alembic). En desarrollo activo.
- `mobile/` — app Flutter/Android, **solo para el rol granjero** (carga
  diaria: mortandad, agua, gas/electricidad, entregas de alimento). El
  flujo de admin que tenía antes (`features/admin/`) sigue en el repo pero
  ya no está enganchado desde `app.dart` — ver sección Mobile más abajo.
- `web/` — panel React para el administrador (crianzas, galpones, alertas,
  resumen, cierre, cuentas pendientes de activar). Reemplaza al admin
  móvil — ver sección Web más abajo y [docs/plan.md](docs/plan.md), sección
  "Ajuste de alcance".
- `docs/` — propuesta de proyecto original, plan (con los ajustes de alcance
  reales) y modelo de datos.

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

python -m app.db.seed_estandares                  # siembra/actualiza la tabla estandares (mortandad/agua por día de vida)
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
  agregarla. Las excepciones son `app/services/calculos.py` (el cierre de
  crianza — índice de crecimiento, conversión, índice de eficiencia,
  liquidación — verificado contra datos reales) y `app/services/alertas.py`
  (umbrales de mortandad/agua/gas/electricidad, corren automáticamente al
  cargar cada lectura desde `routers/lecturas.py`). Ambos son lógica de
  negocio no trivial, así que viven en módulos aparte en vez de inline en el
  router. Si otro endpoint empieza a acumular ese tipo de lógica, el mismo
  criterio aplica: va en `app/services/`, no inline.
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

**El rol admin no se autoregistra.** `POST /auth/register` es público (la
app lo usa para "Crear cuenta") y usa `RegistroCreate`
(`app/schemas/usuario.py`), que a propósito no tiene campo `rol` —
`model_config = ConfigDict(extra="forbid")` hace que colar un `rol` en el
body devuelva 422 en vez de ignorarlo en silencio. El registro público
siempre crea un granjero, pero **inactivo** (`activo=False`) — pedido del
docente de la cátedra: antes se activaba solo, pero eso permitía que
cualquiera con el link de la app quedara cargado como granjero sin que el
administrador se enterara. Un admin lo tiene que habilitar a mano con
`PATCH /usuarios/{id}/activar` (`app/api/routers/usuarios.py`) — hasta
entonces, `POST /auth/login` devuelve 403. `GET /usuarios?activo=false`
lista las cuentas pendientes (el filtro por defecto de ese endpoint sigue
siendo `activo=true`, para no romper el selector de granjero al asignar un
galpón). En la app, `UsuariosPendientesScreen` (entrada desde un ícono con
badge en `AdminHomeScreen`) es la pantalla para aprobarlas; el registro ya
no hace login automático después de crear la cuenta, porque fallaría con
403 justo después. La única forma de dar de alta un admin directamente
activo es `python -m app.db.crear_admin --nombre "..." --email ... --password ...`
(corre directo contra la base, sin pasar por HTTP — ver ese archivo). Otras
reglas de `RegistroCreate`/`UsuarioCreate`/`LoginRequest`: contraseña mínimo
8 caracteres, email **case-sensitive** a propósito (decisión explícita del
cliente pese a la recomendación en contra — "Juan@x.com" y "juan@x.com" son
cuentas distintas, tanto al registrarse como al loguearse; solo se recorta
espacios). La app fuerza `textCapitalization: TextCapitalization.none` en el
campo de email para mitigar que el teclado le meta una mayúscula sola.

### Testing

`tests/conftest.py` levanta una base SQLite en memoria y sobreescribe la
dependency `get_db` de la app — los tests no requieren Postgres. Cada test
recibe una base limpia (`create_all`/`drop_all` por fixture). Dos fixtures:
`client` (TestClient completo, para tests de endpoints — patrón en
`tests/test_auth.py`) y `db_session` (sesión directa contra la misma base,
para tests de servicios que arman sus propios modelos sin pasar por la API —
patrón en `tests/test_alertas.py`). `tests/test_calculos.py` fija las
fórmulas de cierre como regresión contra números reales verificados; si las
tocás sin querer, se rompen ahí antes que en producción. `tests/test_validaciones.py`
cubre las guardas de integridad (crianza cerrada, capacidad de galpón, aves
vivas disponibles, fechas) — al agregar una guarda nueva en un router, sumar
el caso ahí también.

### Granularidad de la carga de datos (importante)

No todo se carga por galpón ni todo diario — ver
[docs/modelo-datos.md](docs/modelo-datos.md) para el detalle completo, pero
en resumen: mortandad y agua son **por galpón, diarias** (`LecturaDiariaGalpon`,
agua como lectura cruda de caudalímetro, no consumo ya calculado); gas y
electricidad son **de toda la granja, diarias** (`LecturaDiariaGranja`, un
solo medidor de cada uno); alimento y cáscara son **por evento** (remito,
`EntregaInsumo`, no diario, no por galpón). Un galpón puede tener varias
partidas de ingreso de aves con fechas/orígenes distintos (`IngresoAves`).
Ojo que "edad de un galpón" se calcula distinto en dos lugares por razones
distintas: para las alertas y validaciones del día a día (`edad_dias` en
`app/services/aves.py`) es `fecha - fecha del primer IngresoAves` (entero,
simple, es como lo hace el Excel real mientras la crianza está en curso);
para el cierre final (`edad_ponderada` en `app/services/calculos.py`) es un
promedio ponderado por cantidad de aves de cada partida (fraccionario) —
verificado exacto contra el Excel real. No usar uno en el lugar del otro.
`app/services/aves.py` también tiene `aves_netas_totales`, `mortandad_acumulada`
y `aves_vivas_disponibles` — consultas chicas que se repiten entre alertas,
cierre y las validaciones de los routers; están ahí para no recalcularlas
distinto en cada lugar.

### Alertas

`app/services/alertas.py` corre automáticamente al cargar cada lectura
(`routers/lecturas.py` llama a `evaluar_lectura_galpon`/`evaluar_lectura_granja`
después de un `db.flush()`, para tener el `id` de la lectura antes de linkear
la `Alerta`). Mortandad y agua se comparan contra `Estandar` por edad
(umbrales: 1.5×/2× acumulado, 3× pico diario, ±30% agua — justificados en
docs/modelo-datos.md sección "Alertas"). Gas y electricidad **no** usan
`Estandar` — no hay curva por edad confiable con una sola crianza de
referencia y clima como variable no controlada, así que se comparan contra
el promedio móvil de los últimos 3 días de la misma crianza (±40%). Los
umbrales son constantes al principio del archivo, pensados para ajustarse
con la experiencia de más crianzas reales, no para quedar fijos.

### Resumen (dashboard)

El administrador pidió ver los números reales de una crianza en curso, no
solo enterarse cuando algo se desvía — `GET /crianzas/{id}/resumen`
(`app/services/resumen.py`) da edad, mortandad, agua acumulada y
alimento/gas/electricidad, reusando los mismos cálculos y umbrales de
comparación que `app/services/alertas.py` (mismo `Estandar` por edad para
mortandad/agua, mismo promedio móvil de 3 días para gas/electricidad) — a
propósito no hay un segundo criterio de "cuánto se esperaba" en el sistema.
No incluye índice de crecimiento/conversión/IE: esos necesitan peso, y acá
no se pesa a las aves hasta que salen a faena (`RetiroCamion`) — eso se
calcula recién al cierre, ver `app/services/calculos.py`. La edad para
comparar contra `Estandar` usa la fecha real de hoy (un hecho de calendario,
no depende de si ya se cargó el dato del día) — `resumen_crianza` acepta un
`hoy` opcional solo para poder testear eso de forma determinística.
Pantalla mobile: `ResumenScreen`, entrada desde `CrianzaDetailScreen`.

### Validaciones

`app/api/validaciones.py` tiene las guardas de integridad que se repiten
entre routers (`requiere_crianza_en_curso`, `requiere_fecha_no_futura`,
`requiere_fecha_no_anterior`) — levantan `HTTPException` directo, por eso
viven en `app/api/` y no en `app/services/` (son chequeos triviales de
integridad de datos, no cálculos de negocio). Reglas que sí son específicas
de un router quedan inline ahí (ej. capacidad máxima del galpón al cargar un
`IngresoAves` en `routers/crianzas.py`, o que un `RetiroCamion` no supere
`aves_vivas_disponibles` en `routers/retiros.py`). Una vez que una crianza
pasa a `cerrada`, ningún endpoint de carga (ingresos, lecturas, entregas,
retiros) acepta escrituras nuevas para esa crianza — ver
`tests/test_validaciones.py` para el catálogo completo de lo que se
rechaza y por qué.

### Pendiente / decisiones abiertas

Ver la sección final de [docs/modelo-datos.md](docs/modelo-datos.md). Lo más
relevante: el reparto de alimento consumido por galpón es una aproximación
(proporcional a aves×días, igual criterio que usa el Excel de la granja pero
no idéntico bit a bit), la tabla real de precio de liquidación
(`indice_tabla` en `CierreCrianza`) es un dato de entrada manual — el
administrador confirmó que ese cálculo lo hace la integradora con su propia
fórmula interna, no se modela acá — y los umbrales de `app/services/alertas.py`
están calibrados con una sola crianza real: van a necesitar ajuste (sobre
todo gas/electricidad, que dependen de clima/temporada) a medida que se
acumule historial de más crianzas.

## Mobile

Proyecto Flutter, un solo APK. Originalmente era para los dos roles
(granjero y admin, Semana 4-7 del plan), pero tras la corrección del
docente (ver sección Project) **el admin móvil quedó reemplazado por el
panel web** — `features/admin/` sigue en el repo (código probado, por si
hace falta retomarlo) pero ya no está enganchado desde `app.dart`: un admin
que loguea en la app ve `AdminEnWebScreen` (`features/admin/admin_en_web_screen.dart`),
un aviso con botón de cerrar sesión en vez del flujo completo que tenía
antes. La app en uso real es, en la práctica, solo para el granjero.

### Entorno (esta máquina)

No usa un instalador estándar (no hay paquete de Flutter en winget) — quedó
así:

- Flutter SDK: clonado en `C:\src\flutter` (rama `stable`, no vive dentro
  del repo). Agregado al PATH de usuario.
- Android SDK: solo las command-line tools (sin Android Studio), en
  `C:\Android\sdk`. `ANDROID_HOME`/`ANDROID_SDK_ROOT` apuntan ahí.
- Sin emulador — se prueba contra un celular Android real por USB (con
  "depuración USB" habilitada en el teléfono).
- Si una terminal nueva no encuentra `flutter`/`adb`: las variables son a
  nivel de usuario de Windows, así que una terminal que ya estaba abierta
  antes de instalar esto no las hereda — hay que abrir una nueva.

### Comandos

```bash
cd mobile

flutter doctor                    # verifica el toolchain completo
adb devices                       # confirma que el celular está conectado (debe decir "device", no "unauthorized")

flutter run                       # instala y corre en el celular conectado, con hot reload
flutter build apk --debug         # compila sin correr (valida que el build funciona)

adb reverse tcp:8000 tcp:8000     # con el celular por USB, así "localhost:8000" en la app
                                   # apunta al backend corriendo en esta PC (ver backend/README.md)
```

Cuando el proyecto tenga más estructura que el scaffold de `flutter create`
(cliente HTTP, manejo de estado, navegación por rol), documentar acá esas
decisiones siguiendo el mismo formato que la sección de Backend.

## Web

Panel del administrador — React + Vite, sin TypeScript (mismo criterio
pragmático que el resto del proyecto: sin capas extra que este tamaño de
proyecto no necesita). Reemplaza al admin móvil (ver sección Mobile) — es
la única forma de administrar crianzas/galpones/alertas/cierre/cuentas
pendientes.

### Arquitectura

Espejo deliberado de `mobile/lib/features/admin/`, mismo recorte de
archivos para no tener dos formas distintas de organizar lo mismo:

- `src/core/apiClient.js` — wrapper sobre `fetch`, mismo criterio que
  `mobile/lib/core/api_client.dart` (decodifica los errores de FastAPI a
  `ApiException`, con el mismo mensaje en español que ya manda el backend).
- `src/core/config.js` — la URL del backend se arma a partir del host
  desde el que se abrió el panel (`window.location.hostname`), no se
  hardcodea `localhost` — así sirve igual si el panel se abre en la compu
  que corre el backend o desde otro dispositivo de la red de la granja
  apuntando a la IP de esa compu.
- `src/core/AuthContext.jsx` — sesión del admin (token en `localStorage`),
  espejo de `AuthService` en mobile. A propósito rechaza un login que no
  sea de un usuario `admin` — el panel web no es para granjeros. Pedido
  explícito del cliente, medida de seguridad: ir atrás/adelante con los
  botones del navegador fuerza logout en vez de dejar ver el panel sin
  loguearse de nuevo. Dos chequeos porque el navegador puede volver a esa
  página de dos formas distintas: restaurando una versión "congelada" sin
  re-ejecutar JS (bfcache — se detecta con el evento `pageshow` y
  `event.persisted`) o haciendo una recarga completa (se detecta con
  `performance.getEntriesByType('navigation')[0].type === 'back_forward'`,
  la Navigation Timing API). Sin el segundo chequeo, un navegador que no
  use bfcache dejaría pasar la recarga completa con el token todavía
  válido, sin pedir login de nuevo.
- `src/features/admin/adminApi.js` — mismos endpoints que
  `mobile/lib/features/admin/admin_api.dart`, 1:1.
- `src/features/admin/*Screen.jsx` — una pantalla por archivo, mismo
  recorte que las pantallas de mobile (`CrianzaDetailScreen`,
  `GalponDetailScreen`, `ResumenScreen`, `AlertasScreen`, `CierreFormScreen`,
  `UsuariosPendientesScreen`, formularios de ingreso/retiro/entrega/alta).

### Comandos

```bash
cd web
npm install        # primera vez
npm run dev         # servidor de desarrollo (http://localhost:5173)
npm run build        # build de producción a dist/
npm run lint          # oxlint
```

Necesita el backend corriendo (`uvicorn app.main:app`, ver backend/README.md)
en el mismo host, puerto 8000.
