# Plan de desarrollo — Sistema Granja "El Moro"

Rango realista: 6-10 semanas. Se toma 8 como base ajustable. El objetivo de este
plan no es cumplir un cronograma estricto (el tiempo real no importa), sino
tener claro **el orden de construcción**: qué depende de qué, y por dónde
arrancar en cada momento.

Referencia: [propuesta.md](propuesta.md) — fundamentación, objetivos y alcance
del proyecto. Etapas 4.3 de la propuesta se corresponden con las semanas de
este plan.

**Ajuste de alcance (post-Semana 3):** la propuesta original describía dos
clientes separados — app móvil para granjeros y panel web (React) para el
administrador. En la práctica, lo que el cliente quiere es **una sola app
Android** para los dos roles (granjeros y administradores), no un panel web
aparte. El panel web queda pospuesto — se evalúa más adelante si hace falta
(ej. para ver reportes en una pantalla más grande), pero no es el alcance
actual. Las Semanas 4-7 de abajo reflejan este ajuste, no el documento
original.

## Semana 1-2: Backend base + BD

- Modelado de datos completo (usuarios, galpones, crianzas, registros diarios
  de producción, alertas, tabla de liquidación — ver [modelo-datos.md](modelo-datos.md))
- Setup FastAPI + PostgreSQL + migraciones (Alembic)
- Auth (JWT, roles: admin/trabajador)
- CRUD de entidades principales

**Hito:** API funcionando con Swagger/docs, se puede crear/leer/actualizar
datos vía Postman.

## Semana 3: Backend — lógica de negocio

- Endpoints específicos del dominio (registro diario de producción, control
  de stock/alimento, alertas)
- Validaciones y reglas de negocio
- Tests básicos de los endpoints críticos

**Hito:** backend "completo" en funcionalidad core, listo para consumir.

## Semana 4-5: App Android (Flutter) — rol granjero

Un solo proyecto Flutter para toda la app (ver Semana 6-7) — acá se arranca
por el flujo del granjero, que es el que reemplaza directamente el WhatsApp
actual.

- Setup del proyecto, navegación, conexión a la API
- Login y ruteo por rol: después de loguearse, un granjero entra directo a
  su flujo (nunca ve pantallas de administrador — ver nota de arquitectura
  más abajo)
- Pantallas de carga de datos diarios (lo que hoy hacen por WhatsApp):
  mortandad y lectura de agua por galpón, lectura de gas/electricidad de la
  granja, entrega de alimento por remito
- Manejo de estado, offline-first si aplica (importante en zona rural con
  conectividad débil)
- **A evaluar**: carga de lecturas de medidor (agua/gas/luz) por foto, con
  OCR para leer el número automáticamente y reducir error humano. Ver nota
  de factibilidad más abajo — no es bloqueante para el resto de la etapa.

**Hito:** un granjero puede loguearse y cargar datos reales desde el celular.

### Nota de arquitectura: una app, dos flujos separados

Es un solo proyecto/repo Flutter (un solo APK), pero **admin y granjero no
comparten pantallas**: después del login, cada rol entra a una navegación
completamente distinta armada para su tarea — el granjero nunca ve un tab
de "administrador" oculto, ni viceversa. Esto es más simple de mantener
enfocado que una navegación única con tabs condicionales por rol, y evita
que un granjero se encuentre por error con una pantalla que no entiende.

### Nota: OCR de medidores (foto → número)

Idea del administrador: que el granjero saque una foto del medidor (como las
que ya mandó por WhatsApp) y la app lea el número sola. Es viable, pero con
matices:

- **Enfoque recomendado**: OCR asistido, no automático a ciegas. La app
  sugiere un valor leído de la foto, pero el granjero lo confirma o corrige
  antes de guardar — un error de OCR en una lectura de medidor se arrastra
  al cálculo de consumo del día siguiente (resta contra la lectura anterior),
  así que conviene un humano en el loop, al menos al principio.
- **Dónde correrlo**: mejor en el dispositivo (ML Kit de Google, gratis,
  funciona sin conexión) que contra un servicio en la nube — la propuesta ya
  marca la conectividad rural como riesgo, y esto no debería depender de
  tener señal en el momento de la carga.
- **Dificultad real**: los medidores de agua tienen rueditas mecánicas (fáciles
  para OCR) pero el de gas y los de luz son de dígitos con fondos/reflejos
  variables (fotos con mala luz, vidrio sucio) — la precisión no va a ser
  perfecta, de ahí lo de confirmar antes de guardar.
- Se puede dejar para una segunda vuelta de la app móvil (no imprescindible
  para el primer prototipo funcional) y decidir en base a cómo reacciona el
  granjero probando la carga manual primero.

## Semana 6-7: App Android (Flutter) — rol administrador

Mismo proyecto de la Semana 4-5, segundo flujo de navegación (el del admin).

- ABM de galpones y crianzas (alta de crianza, asignar galpones/granjeros,
  registrar ingresos de aves) desde el celular
- Dashboard de estado por galpón, comparando contra `Estandar`
- Alertas: listado de `GET /crianzas/{id}/alertas`, marcar resueltas
- Cierre de crianza: carga de retiros, entrega de alimento, y el formulario
  final de liquidación (`indice_tabla`/premios/ajustes que provee la
  integradora)
- Historial de crianzas cerradas

**Hito:** el administrador ve en tiempo real lo que cargan los granjeros y
puede cerrar una crianza completa desde el celular.

## Semana 8: Integración final + pulido

- Testing end-to-end (flujo completo: granjero carga → administrador ve y
  recibe alertas → cierre de crianza genera la liquidación)
- Corrección de bugs de integración
- Documentación mínima para la defensa/entrega

**Hito:** sistema funcionando de punta a punta, demo lista.

## Pospuesto (no es alcance actual)

- **Panel web (React) para el administrador**: la propuesta original lo
  incluía como tercer componente. Se pospone — se evalúa más adelante si
  hace falta (ej. reportes en pantalla grande), pero la app Android ya
  cubre el rol de administrador.
