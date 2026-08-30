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

/// Reexporta Usuario/RolUsuario para no repetir el import en cada pantalla
/// de admin que necesita elegir un granjero.
typedef Granjero = Usuario;
