import '../../core/usuario.dart';

class Crianza {
  Crianza({
    required this.id,
    required this.numero,
    required this.fechaInicio,
    required this.estado,
  });

  final int id;
  final int numero;
  final DateTime fechaInicio;
  final String estado;

  bool get enCurso => estado == 'en_curso';

  factory Crianza.fromJson(Map<String, dynamic> json) {
    return Crianza(
      id: json['id'] as int,
      numero: json['numero'] as int,
      fechaInicio: DateTime.parse(json['fecha_inicio'] as String),
      estado: json['estado'] as String,
    );
  }
}

class Galpon {
  Galpon({required this.id, required this.nombre, required this.capacidadMaxima});

  final int id;
  final String nombre;
  final int capacidadMaxima;

  factory Galpon.fromJson(Map<String, dynamic> json) {
    return Galpon(
      id: json['id'] as int,
      nombre: json['nombre'] as String,
      capacidadMaxima: json['capacidad_maxima'] as int,
    );
  }
}

/// Espejo de `CrianzaGalponOut` — ya viene con los nombres resueltos desde
/// el backend (ver app/api/routers/crianzas.py `_cg_out`).
class CrianzaGalpon {
  CrianzaGalpon({
    required this.id,
    required this.crianzaId,
    required this.galponId,
    required this.galponNombre,
    required this.granjeroId,
    required this.granjeroNombre,
  });

  final int id;
  final int crianzaId;
  final int galponId;
  final String galponNombre;
  final int granjeroId;
  final String granjeroNombre;

  factory CrianzaGalpon.fromJson(Map<String, dynamic> json) {
    return CrianzaGalpon(
      id: json['id'] as int,
      crianzaId: json['crianza_id'] as int,
      galponId: json['galpon_id'] as int,
      galponNombre: json['galpon_nombre'] as String,
      granjeroId: json['granjero_id'] as int,
      granjeroNombre: json['granjero_nombre'] as String,
    );
  }
}

class IngresoAves {
  IngresoAves({
    required this.fecha,
    required this.origen,
    required this.cantidad,
    required this.muertosTransporte,
    required this.cantidadNeta,
  });

  final DateTime fecha;
  final String origen;
  final int cantidad;
  final int muertosTransporte;
  final int cantidadNeta;

  factory IngresoAves.fromJson(Map<String, dynamic> json) {
    return IngresoAves(
      fecha: DateTime.parse(json['fecha'] as String),
      origen: json['origen'] as String,
      cantidad: json['cantidad'] as int,
      muertosTransporte: json['muertos_transporte'] as int,
      cantidadNeta: json['cantidad_neta'] as int,
    );
  }
}

class Alerta {
  Alerta({required this.id, required this.tipo, required this.descripcion, required this.fecha, required this.resuelta});

  final int id;
  final String tipo;
  final String descripcion;
  final DateTime fecha;
  final bool resuelta;

  factory Alerta.fromJson(Map<String, dynamic> json) {
    return Alerta(
      id: json['id'] as int,
      tipo: json['tipo'] as String,
      descripcion: json['descripcion'] as String,
      fecha: DateTime.parse(json['fecha'] as String),
      resuelta: json['resuelta'] as bool,
    );
  }
}

class RetiroCamion {
  RetiroCamion({
    required this.fecha,
    required this.remito,
    required this.transportista,
    required this.cantidadAves,
    required this.pesoNeto,
  });

  final DateTime fecha;
  final String remito;
  final String transportista;
  final int cantidadAves;
  final double pesoNeto;

  factory RetiroCamion.fromJson(Map<String, dynamic> json) {
    return RetiroCamion(
      fecha: DateTime.parse(json['fecha'] as String),
      remito: json['remito'] as String,
      transportista: json['transportista'] as String,
      cantidadAves: json['cantidad_aves'] as int,
      pesoNeto: (json['peso_neto'] as num).toDouble(),
    );
  }
}

class EntregaInsumo {
  EntregaInsumo({
    required this.tipoInsumo,
    required this.fecha,
    required this.remito,
    required this.kilos,
  });

  final String tipoInsumo;
  final DateTime fecha;
  final String remito;
  final double kilos;

  factory EntregaInsumo.fromJson(Map<String, dynamic> json) {
    return EntregaInsumo(
      tipoInsumo: json['tipo_insumo'] as String,
      fecha: DateTime.parse(json['fecha'] as String),
      remito: json['remito'] as String,
      kilos: (json['kilos'] as num).toDouble(),
    );
  }
}

/// Espejo de `CierreCrianzaOut` — la liquidación final de la crianza.
class CierreCrianza {
  CierreCrianza({
    required this.totalAvesEntregadas,
    required this.pesoTotal,
    required this.iePromedio,
    required this.indiceTabla,
    required this.premios,
    required this.gasAjuste,
    required this.ajuste,
    required this.precioXPollo,
    required this.montoTotal,
    required this.fechaCierre,
  });

  final int totalAvesEntregadas;
  final double pesoTotal;
  final double iePromedio;
  final double indiceTabla;
  final double premios;
  final double gasAjuste;
  final double ajuste;
  final double precioXPollo;
  final double montoTotal;
  final DateTime fechaCierre;

  factory CierreCrianza.fromJson(Map<String, dynamic> json) {
    return CierreCrianza(
      totalAvesEntregadas: json['total_aves_entregadas'] as int,
      pesoTotal: (json['peso_total'] as num).toDouble(),
      iePromedio: (json['ie_promedio'] as num).toDouble(),
      indiceTabla: (json['indice_tabla'] as num).toDouble(),
      premios: (json['premios'] as num).toDouble(),
      gasAjuste: (json['gas_ajuste'] as num).toDouble(),
      ajuste: (json['ajuste'] as num).toDouble(),
      precioXPollo: (json['precio_x_pollo'] as num).toDouble(),
      montoTotal: (json['monto_total'] as num).toDouble(),
      fechaCierre: DateTime.parse(json['fecha_cierre'] as String),
    );
  }
}

/// Espejo de `ResumenGalponOut` — los números "en vivo" de un galpón (ver
/// app/services/resumen.py). A propósito no trae índice de crecimiento ni
/// conversión: eso necesita peso, que no se conoce hasta el retiro a faena.
class ResumenGalpon {
  ResumenGalpon({
    required this.galponNombre,
    required this.granjeroNombre,
    required this.edadDias,
    required this.avesNetas,
    required this.avesVivas,
    required this.mortandadAcumulada,
    required this.mortandadPct,
    required this.mortandadEsperadaPct,
    required this.aguaAcumuladaLitros,
    required this.aguaLitrosPolloHoy,
    required this.aguaEsperadaLitrosPolloHoy,
  });

  final String galponNombre;
  final String granjeroNombre;
  final int? edadDias;
  final int avesNetas;
  final int avesVivas;
  final int mortandadAcumulada;
  final double mortandadPct;
  final double? mortandadEsperadaPct;
  final double aguaAcumuladaLitros;
  final double? aguaLitrosPolloHoy;
  final double? aguaEsperadaLitrosPolloHoy;

  factory ResumenGalpon.fromJson(Map<String, dynamic> json) {
    double? asDouble(dynamic v) => v == null ? null : (v as num).toDouble();
    return ResumenGalpon(
      galponNombre: json['galpon_nombre'] as String,
      granjeroNombre: json['granjero_nombre'] as String,
      edadDias: json['edad_dias'] as int?,
      avesNetas: json['aves_netas'] as int,
      avesVivas: json['aves_vivas'] as int,
      mortandadAcumulada: json['mortandad_acumulada'] as int,
      mortandadPct: (json['mortandad_pct'] as num).toDouble(),
      mortandadEsperadaPct: asDouble(json['mortandad_esperada_pct']),
      aguaAcumuladaLitros: (json['agua_acumulada_litros'] as num).toDouble(),
      aguaLitrosPolloHoy: asDouble(json['agua_litros_pollo_hoy']),
      aguaEsperadaLitrosPolloHoy: asDouble(json['agua_esperada_litros_pollo_hoy']),
    );
  }
}

/// Espejo de `ResumenGranjaOut` — gas/electricidad de toda la granja, mismo
/// criterio de comparación (promedio móvil de 3 días) que las alertas.
class ResumenGranja {
  ResumenGranja({
    required this.fecha,
    required this.consumoGasHoy,
    required this.promedioGas3Dias,
    required this.consumoElectricidadActivaHoy,
    required this.promedioElectricidadActiva3Dias,
    required this.consumoElectricidadReactivaHoy,
    required this.promedioElectricidadReactiva3Dias,
  });

  final DateTime? fecha;
  final double? consumoGasHoy;
  final double? promedioGas3Dias;
  final double? consumoElectricidadActivaHoy;
  final double? promedioElectricidadActiva3Dias;
  final double? consumoElectricidadReactivaHoy;
  final double? promedioElectricidadReactiva3Dias;

  factory ResumenGranja.fromJson(Map<String, dynamic> json) {
    double? asDouble(dynamic v) => v == null ? null : (v as num).toDouble();
    return ResumenGranja(
      fecha: json['fecha'] == null ? null : DateTime.parse(json['fecha'] as String),
      consumoGasHoy: asDouble(json['consumo_gas_hoy']),
      promedioGas3Dias: asDouble(json['promedio_gas_3_dias']),
      consumoElectricidadActivaHoy: asDouble(json['consumo_electricidad_activa_hoy']),
      promedioElectricidadActiva3Dias: asDouble(json['promedio_electricidad_activa_3_dias']),
      consumoElectricidadReactivaHoy: asDouble(json['consumo_electricidad_reactiva_hoy']),
      promedioElectricidadReactiva3Dias: asDouble(json['promedio_electricidad_reactiva_3_dias']),
    );
  }
}

/// Espejo de `ResumenCrianzaOut` — el "dashboard" que pidió el
/// administrador: los mismos números que hoy arma a mano mirando el Excel.
class ResumenCrianza {
  ResumenCrianza({required this.alimentoEntregadoKg, required this.granja, required this.galpones});

  final double alimentoEntregadoKg;
  final ResumenGranja granja;
  final List<ResumenGalpon> galpones;

  factory ResumenCrianza.fromJson(Map<String, dynamic> json) {
    return ResumenCrianza(
      alimentoEntregadoKg: (json['alimento_entregado_kg'] as num).toDouble(),
      granja: ResumenGranja.fromJson(json['granja'] as Map<String, dynamic>),
      galpones: (json['galpones'] as List)
          .map((e) => ResumenGalpon.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// Reexporta Usuario/RolUsuario para no repetir el import en cada pantalla
/// de admin que necesita elegir un granjero.
typedef Granjero = Usuario;
