# Plan de desarrollo — Sistema Granja "El Moro"

Rango realista: 6-10 semanas. Se toma 8 como base ajustable. El objetivo de este
plan no es cumplir un cronograma estricto (el tiempo real no importa), sino
tener claro **el orden de construcción**: qué depende de qué, y por dónde
arrancar en cada momento.

Referencia: [propuesta.md](propuesta.md) — fundamentación, objetivos y alcance
del proyecto. Etapas 4.3 de la propuesta se corresponden con las semanas de
este plan.

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

## Semana 4-5: App Flutter (trabajadores/granjeros)

- Setup del proyecto, navegación, conexión a la API
- Pantallas de carga de datos diarios (lo que hoy hacen por WhatsApp)
- Manejo de estado, offline-first si aplica (importante en zona rural con
  conectividad débil)
- **A evaluar**: carga de lecturas de medidor (agua/gas/luz) por foto, con
  OCR para leer el número automáticamente y reducir error humano. Ver nota
  de factibilidad más abajo — no es bloqueante para el resto de la etapa.

**Hito:** un trabajador puede loguearse y cargar datos reales desde el celular.

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

## Semana 6-7: Panel web React (admin)

- Dashboard con métricas (producción, stock, alertas)
- Vistas de gestión (usuarios, reportes, históricos)
- Conexión a la misma API

**Hito:** el admin ve en tiempo real lo que cargan los trabajadores.

## Semana 8: Integración final + pulido

- Testing end-to-end (flujo completo: trabajador carga → admin ve → reporte
  se genera)
- Corrección de bugs de integración
- Documentación mínima para la defensa/entrega

**Hito:** sistema funcionando de punta a punta, demo lista.
