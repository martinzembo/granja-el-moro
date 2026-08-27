# Modelo de datos

Reemplaza el borrador inicial. Está basado en dos fuentes reales de la
granja, no en supuestos: la planilla en papel de MIRALEJOS S.A.C.I.F.I. y A.,
los mensajes diarios reales que manda el granjero por WhatsApp (mortandad por
galpón, lecturas de medidores de agua/gas/luz, remito de alimento), y el
Excel `docs/crianza92.xls` que arma hoy el administrador a mano con esos
datos. Las fórmulas de esta sección están verificadas contra los números
reales de ese Excel, no inventadas.

## Idea central: granularidad mixta

No todo se carga por galpón ni todo se carga diario. Hay tres niveles:

1. **Por galpón, diario**: mortandad, lectura de agua (cada galpón tiene su
   propio caudalímetro).
2. **Por granja completa, diario**: gas y electricidad (hay un solo medidor
   de cada uno para toda la granja, no por galpón).
3. **Por evento, a nivel de crianza completa**: entrega de alimento/cáscara
   (remito del proveedor, no diario), y retiro de aves a faena (remito por
   camión).

Esto reemplaza el diseño inicial de `RegistroDiario`, que asumía todo como
una lectura diaria uniforme por galpón.

## Entidades

### Usuario, Galpon
Sin cambios respecto al borrador inicial.

### Crianza
Un ciclo productivo completo. Se le agrega `numero` porque así es como la
granja ya las identifica (ej. "crianza92").

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| numero | int, único | correlativo de la granja |
| fecha_inicio | date | |
| fecha_cierre | date, nullable | |
| estado | enum(en_curso, cerrada) | |
| creado_por_id | FK Usuario | |

### CrianzaGalpon
Qué galpón participa de la crianza y quién es el granjero responsable. Ya no
tiene `aves_iniciales` ni `peso_inicial_promedio` directo: un galpón puede
recibir pollitos de **varios orígenes en fechas distintas** (ver
`IngresoAves`), y el total sale de sumarlos.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_id | FK Crianza | |
| galpon_id | FK Galpon | |
| granjero_id | FK Usuario | responsable de la carga diaria de ese galpón |

### IngresoAves
Cada partida de pollitos BB que entra a un galpón. En la crianza real vista,
el Galpón 1 recibió 3 partidas de origen distinto en 2 fechas distintas.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_galpon_id | FK CrianzaGalpon | |
| fecha | date | también define el "día 0" de edad de ese galpón — ver más abajo |
| origen | string | línea genética / granja de reproductoras (ej. "Las Violetas", "HC", "SM3") |
| cantidad | int | pollitos despachados |
| muertos_transporte | int | faltantes/muertos en el traslado |
| cantidad_neta | int | `cantidad - muertos_transporte` |

**Edad de un galpón**: `fecha_actual - fecha del primer IngresoAves de ese
galpón`. Cada galpón tiene su propio reloj de edad (en la crianza real, el
Galpón 1 empezó 2 días antes que el resto) — los estándares de mortandad y
agua se comparan contra esta edad, no contra la fecha de la crianza en
general.

### Estandar
Valores esperados por día de vida, usados para alertas (Semana 3). Antes
tenía también `peso_esperado` y `consumo_alimento_esperado`, que eran
supuestos sin confirmar — se sacan porque el Excel real no los usa así. Lo
que sí confirmé, en las columnas STD/TEÓRICO del Excel:

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| dia_vida | int | |
| mortandad_acumulada_esperada | int | cantidad acumulada esperada de muertos, por galpón, a esa edad |
| agua_litros_pollo_esperado | decimal | litros por ave esperados a esa edad |

Por ahora es una única tabla global (no distingue por línea genética/raza).
El Excel menciona "Pollo Cobb" como referencia — si en el futuro se maneja
más de una línea genética con curvas distintas, esta tabla necesita un
`linea_genetica_id`. Lo dejo anotado, no lo modelo todavía (no hay caso real
que lo requiera hoy).

### LecturaDiariaGalpon
Lo que manda el granjero todos los días, por galpón. Reemplaza al
`RegistroDiario` original.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_galpon_id | FK CrianzaGalpon | |
| fecha | date | |
| mortandad | int | muertos ese día (dato directo, no acumulado) |
| lectura_agua | decimal | **lectura cruda del caudalímetro**, no el consumo — ver cálculo abajo |
| cargado_por_id | FK Usuario | |
| creado_en | datetime | |

**Cálculo de consumo de agua** (verificado exacto contra el Excel):
```
consumo_litros_del_dia = (lectura_agua_hoy - lectura_agua_ayer) × 10
litros_por_pollo = consumo_litros_del_dia / aves_vivas
```
El factor `×10` es del caudalímetro instalado (cuenta de a 10 litros por
pulso). Esto se calcula en la capa de negocio al procesar la carga, no se
guarda ya calculado — se necesita la lectura del día anterior para derivarlo.

### LecturaDiariaGranja
Gas y electricidad: un solo medidor de cada uno para toda la granja (no por
galpón), reportado en una ventana horaria fija (ej. 08:00 a 08:00 del día
siguiente).

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_id | FK Crianza | |
| fecha | date | |
| hora_desde | time | ej. 08:00 |
| hora_hasta | time | ej. 08:00 (día siguiente) |
| lectura_gas | decimal | m³, lectura cruda acumulada del medidor |
| lectura_electricidad_activa | decimal | kWh, lectura cruda acumulada |
| lectura_electricidad_reactiva | decimal | kvarh, lectura cruda acumulada |
| cargado_por_id | FK Usuario | |
| creado_en | datetime | |

El consumo del día sale de restar la lectura anterior, igual que el agua
(sin el factor ×10 en este caso).

### EntregaInsumo
Alimento y cáscara de girasol/arroz se registran por remito, no diario, a
nivel de toda la crianza (no por galpón — llega un camión para toda la
granja). Lo carga el administrador, no el granjero.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_id | FK Crianza | |
| tipo_insumo | enum(alimento, cascara) | |
| fecha | date | |
| remito | string | |
| tipo_alimento | int, nullable | etapa del alimento (1=iniciador, 2, 3, 4...), solo aplica si tipo_insumo=alimento |
| kilos | decimal | |
| cargado_por_id | FK Usuario | |

### RetiroCamion
Cada camión que retira aves de un galpón para faena. Puede haber varios por
galpón en los días de retiro.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_galpon_id | FK CrianzaGalpon | |
| fecha | date | |
| remito | string | |
| transportista | string | |
| hora_salida | time, nullable | |
| cantidad_aves | int | |
| peso_bruto | decimal, nullable | kg, camión cargado |
| peso_tara | decimal, nullable | kg, camión vacío |
| peso_neto | decimal | kg, peso de las aves |
| cargado_por_id | FK Usuario | |

### CierreGalpon
Resultado por galpón al cerrar la crianza. Fórmulas verificadas exactas
contra el Excel real:

| Campo | Tipo | Fórmula |
|---|---|---|
| id | PK | |
| crianza_galpon_id | FK CrianzaGalpon, único | |
| edad_dias | int | edad del galpón al momento del retiro |
| peso_promedio | decimal (kg) | `peso_neto total de RetiroCamion / cantidad_aves total` |
| alimento_consumido | decimal (kg) | alimento del `EntregaInsumo` de la crianza, prorrateado por población viva del galpón (estimado, no medido por galpón — así lo hace hoy la granja) |
| indice_crecimiento | decimal (g/día) | `(peso_promedio × 1000) / edad_dias` |
| conversion | decimal | `alimento_consumido / peso_producido_total_kg` |
| mortandad_pct | decimal | mortandad acumulada / aves netas ingresadas |
| indice_eficiencia | decimal | `(viabilidad% × peso_promedio_kg) / (edad_dias × conversion) × 100` — es el IEP/EPEF estándar de la industria avícola |

### CierreCrianza (liquidación)
Total de la crianza. El administrador confirmó que el cálculo de
`indice_tabla` es un valor que la integradora (MIRALEJOS) determina con su
propia fórmula interna — **no lo calculamos nosotros**, se carga manual al
cerrar. Lo que sí verificamos exacto contra el Excel real es cómo se
combinan esos componentes:

```
precio_x_pollo = indice_tabla + premios + gas_ajuste + ajuste
```
(Ejemplo real: 534.96 + 0 + 18.98 + 296.06 = 850.0 ✓)

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_id | FK Crianza, único | |
| total_aves_entregadas | int | |
| peso_total | decimal (kg) | |
| ie_promedio | decimal | promedio ponderado de `CierreGalpon.indice_eficiencia` |
| indice_tabla | decimal | **valor de entrada manual**, provisto por la integradora |
| premios | decimal | valor de entrada manual |
| gas_ajuste | decimal | valor de entrada manual |
| ajuste | decimal | valor de entrada manual |
| precio_x_pollo | decimal | = suma de los 4 anteriores (validado en el endpoint, no recalculado por fórmula propia) |
| monto_total | decimal | `precio_x_pollo × total_aves_entregadas` |
| fecha_cierre | date | |

### Alerta
Sin cambios de concepto respecto al borrador inicial, salvo que ahora
referencia `LecturaDiariaGalpon` (mortandad/agua) o `LecturaDiariaGranja`
(gas/electricidad) según el tipo. La definición de los umbrales por edad
queda para Semana 3, como ya se había marcado.

## Qué se saca del alcance (por ahora)

- **Costeo detallado de gas/luz** (tarifas, impuestos, IIBB, etc. — hoja
  `Consumos` del Excel): es contabilidad del costo operativo de la granja,
  no algo que el granjero cargue ni que el admin necesite ver en tiempo real
  para monitorear una crianza. Se guarda la lectura cruda (`LecturaDiariaGranja`)
  y el costeo en pesos queda fuera del sistema por ahora.
- **Proyección de días de alimento restante** (hoja `Alimento` del Excel):
  es un reporte derivado, no un dato a cargar. Candidato para Semana 7
  (reportes), no para el modelo de datos base.
- **Tabla de doble entrada real de `indice_tabla`**: confirmado con el
  administrador que no se modela — es un cálculo interno de la integradora,
  se carga como dato manual en `CierreCrianza`.

## Pendiente de validar con la granja

1. El factor `×10` del caudalímetro de agua — confirmar si es igual en los
   5 galpones o varía por medidor instalado.
2. Si `Estandar` alguna vez necesita distinguir por línea genética (hoy es
   una sola tabla global).
3. Estructura exacta del reparto de alimento por galpón cuando se calculan
   `CierreGalpon.alimento_consumido` (hoy es una estimación proporcional a
   población viva, igual que hace el Excel — no es una medición real).
