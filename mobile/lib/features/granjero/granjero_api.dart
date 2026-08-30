import '../../core/api_client.dart';
import '../../core/date_utils.dart';
import 'granjero_models.dart';

/// Llamadas a la API que usa el flujo del granjero. Envuelve [ApiClient]
/// con los endpoints puntuales, para no repetir rutas/parseo en las
/// pantallas.
class GranjeroApi {
  GranjeroApi(this._client);

  final ApiClient _client;

  Future<List<Asignacion>> misAsignaciones() async {
    final data = await _client.get('/me/asignaciones') as List;
    return data.map((e) => Asignacion.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<LecturaGalpon>> lecturasGalpon(int crianzaId, int cgId) async {
    final data = await _client.get('/crianzas/$crianzaId/galpones/$cgId/lecturas') as List;
    return data.map((e) => LecturaGalpon.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> cargarLecturaGalpon({
    required int crianzaId,
    required int cgId,
    required DateTime fecha,
    required int mortandad,
    required double lecturaAgua,
  }) {
    return _client.post('/crianzas/$crianzaId/galpones/$cgId/lecturas', {
      'fecha': formatoFecha(fecha),
      'mortandad': mortandad,
      'lectura_agua': lecturaAgua,
    });
  }

  Future<List<LecturaGranja>> lecturasGranja(int crianzaId) async {
    final data = await _client.get('/crianzas/$crianzaId/lecturas-granja') as List;
    return data.map((e) => LecturaGranja.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// La ventana horaria es siempre 08:00 a 08:00 del día siguiente en la
  /// granja real (ver docs/modelo-datos.md) — no se le pide al granjero
  /// que la cargue, se fija acá.
  Future<void> cargarLecturaGranja({
    required int crianzaId,
    required DateTime fecha,
    required double lecturaGas,
    required double lecturaElectricidadActiva,
    required double lecturaElectricidadReactiva,
  }) {
    return _client.post('/crianzas/$crianzaId/lecturas-granja', {
      'fecha': formatoFecha(fecha),
      'hora_desde': '08:00:00',
      'hora_hasta': '08:00:00',
      'lectura_gas': lecturaGas,
      'lectura_electricidad_activa': lecturaElectricidadActiva,
      'lectura_electricidad_reactiva': lecturaElectricidadReactiva,
    });
  }
}
