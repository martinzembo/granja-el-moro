/// A qué galpón/crianza está asignado el granjero — espejo de
/// `AsignacionOut` (backend app/schemas/asignacion.py).
class Asignacion {
  Asignacion({
    required this.crianzaGalponId,
    required this.crianzaId,
    required this.crianzaNumero,
    required this.crianzaEstado,
    required this.galponId,
    required this.galponNombre,
  });

  final int crianzaGalponId;
  final int crianzaId;
  final int crianzaNumero;
  final String crianzaEstado;
  final int galponId;
  final String galponNombre;

  bool get enCurso => crianzaEstado == 'en_curso';

  factory Asignacion.fromJson(Map<String, dynamic> json) {
    return Asignacion(
      crianzaGalponId: json['crianza_galpon_id'] as int,
      crianzaId: json['crianza_id'] as int,
      crianzaNumero: json['crianza_numero'] as int,
      crianzaEstado: json['crianza_estado'] as String,
      galponId: json['galpon_id'] as int,
      galponNombre: json['galpon_nombre'] as String,
    );
  }
}

/// Espejo de `LecturaDiariaGalponOut`.
class LecturaGalpon {
  LecturaGalpon({required this.fecha, required this.mortandad, required this.lecturaAgua});

  final DateTime fecha;
  final int mortandad;
  final double lecturaAgua;

  factory LecturaGalpon.fromJson(Map<String, dynamic> json) {
    return LecturaGalpon(
      fecha: DateTime.parse(json['fecha'] as String),
      mortandad: json['mortandad'] as int,
      lecturaAgua: (json['lectura_agua'] as num).toDouble(),
    );
  }
}

/// Espejo de `LecturaDiariaGranjaOut`.
class LecturaGranja {
  LecturaGranja({
    required this.fecha,
    required this.lecturaGas,
    required this.lecturaElectricidadActiva,
    required this.lecturaElectricidadReactiva,
  });

  final DateTime fecha;
  final double lecturaGas;
  final double lecturaElectricidadActiva;
  final double lecturaElectricidadReactiva;

  factory LecturaGranja.fromJson(Map<String, dynamic> json) {
    return LecturaGranja(
      fecha: DateTime.parse(json['fecha'] as String),
      lecturaGas: (json['lectura_gas'] as num).toDouble(),
      lecturaElectricidadActiva: (json['lectura_electricidad_activa'] as num).toDouble(),
      lecturaElectricidadReactiva: (json['lectura_electricidad_reactiva'] as num).toDouble(),
    );
  }
}
