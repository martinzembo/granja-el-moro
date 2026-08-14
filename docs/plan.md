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

**Hito:** un trabajador puede loguearse y cargar datos reales desde el celular.

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
