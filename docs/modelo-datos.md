# Modelo de datos — borrador inicial

Derivado de [propuesta.md](propuesta.md). Es un punto de partida para arrancar
el backend en la Semana 1-2 — se ajusta a medida que se valida con el negocio
real. Los puntos marcados **[CONFIRMAR]** son supuestos que hice para poder
avanzar y que conviene revisar con la granja antes de cerrar el modelo.

## Entidades

### Usuario
Administrador o granjero/trabajador.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | string | |
| email | string, único | login |
| password_hash | string | |
| rol | enum(admin, granjero) | |
| activo | bool | |
| creado_en | datetime | |

### Galpon
Unidad física de alojamiento de aves.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | string | ej. "Galpón 1" |
| capacidad_maxima | int | aves. Propuesta: hasta 119.000 aves entre 5 galpones |

### Crianza
Un ciclo productivo completo (alta → seguimiento → cierre), según etapa 2 de
la metodología.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| fecha_inicio | date | |
| fecha_cierre | date, nullable | null mientras está en curso |
| estado | enum(en_curso, cerrada) | |
| creado_por | FK Usuario | admin que la dio de alta |

### CrianzaGalpon
Tabla intermedia: qué galpones participan de una crianza, con qué granjero
responsable y cuántas aves arrancaron.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_id | FK Crianza | |
| galpon_id | FK Galpon | |
| granjero_id | FK Usuario | responsable de la carga diaria |
| aves_iniciales | int | cantidad de pollitos BB alojados |
| peso_inicial_promedio | decimal | gramos **[CONFIRMAR]** — ¿se pesa al ingreso? |

### RegistroDiario
El corazón operativo: reemplaza el mensaje de WhatsApp diario. Un registro
por galpón por día.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_galpon_id | FK CrianzaGalpon | |
| fecha | date | |
| dia_de_crianza | int | calculado o cargado, para comparar contra estándares |
| mortandad | int | aves muertas ese día |
| consumo_agua | decimal | litros **[CONFIRMAR unidad]** |
| consumo_alimento | decimal | kg |
| consumo_gas | decimal | **[CONFIRMAR unidad — m³, kg, %]** |
| consumo_electricidad | decimal | kWh **[CONFIRMAR]** |
| peso_promedio_semanal | decimal | gramos, **[CONFIRMAR]** cada cuánto se pesa (¿diario? ¿semanal?) |
| cargado_por | FK Usuario | granjero que lo ingresó |
| creado_en | datetime | |

### Estandar
Valores esperados por día de crianza, usados para detectar desvíos y generar
alertas. **[CONFIRMAR]** si es una tabla fija por raza/línea genética o si se
carga por crianza.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| dia_de_crianza | int | |
| mortandad_max_esperada | decimal | % o cantidad |
| consumo_agua_esperado | decimal | |
| consumo_alimento_esperado | decimal | |
| peso_esperado | decimal | gramos |

### Alerta
Generada automáticamente cuando un `RegistroDiario` se desvía de `Estandar`.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| registro_diario_id | FK RegistroDiario | |
| tipo | enum(mortandad, agua, alimento, peso, ...) | |
| descripcion | string | |
| fecha | datetime | |
| resuelta | bool | |

### TablaLiquidacion
La tabla de doble entrada que fija el precio por pollo según los índices de
cierre. **[CONFIRMAR]** — es la pieza de lógica de negocio más específica del
contrato con la integradora; necesito ver la tabla real (ejes, rangos,
valores) para modelarla bien. Por ahora se asume:

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| indice_conversion_min / max | decimal | eje X: kg alimento / kg peso |
| indice_crecimiento_min / max | decimal | eje Y: gramos/día |
| precio_por_kg | decimal | valor resultante |
| vigente_desde | date | por si cambia el contrato con la integradora |

### CierreCrianza (Liquidación)
Resultado del cierre de una `Crianza`.

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| crianza_id | FK Crianza, único | |
| total_aves_entregadas | int | |
| peso_total_kg | decimal | |
| indice_crecimiento | decimal | calculado |
| indice_conversion | decimal | calculado |
| precio_por_kg_resultante | decimal | de `TablaLiquidacion` |
| monto_total | decimal | |
| fecha_cierre | date | |

## Relaciones (resumen)

```
Usuario 1---N CrianzaGalpon (como granjero)
Galpon  1---N CrianzaGalpon
Crianza 1---N CrianzaGalpon
CrianzaGalpon 1---N RegistroDiario
RegistroDiario 1---N Alerta
Crianza 1---1 CierreCrianza
TablaLiquidacion (independiente, consultada al cerrar)
Estandar (independiente, consultada por día de crianza)
```

## Pendiente de validar con la granja

1. Estructura real de la tabla de doble entrada de liquidación (ejes y rangos exactos).
2. Unidades de medida de agua, gas y electricidad tal como las reportan hoy por WhatsApp.
3. Frecuencia real de pesaje (¿diario, semanal?) y si el peso se carga por ave muestreada o promedio de galpón.
4. Si los "estándares" son fijos por línea genética de pollo o se cargan manualmente por crianza.
