import '../../core/api_client.dart';
import '../../core/date_utils.dart';
import '../../core/usuario.dart';
import 'admin_models.dart';

/// Llamadas a la API que usa el flujo del administrador.
class AdminApi {
  AdminApi(this._client);

  final ApiClient _client;

  Future<List<Crianza>> crianzas() async {
    final data = await _client.get('/crianzas') as List;
    return data.map((e) => Crianza.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Crianza> crearCrianza({required int numero, required DateTime fechaInicio}) async {
    final data = await _client.post('/crianzas', {
      'numero': numero,
      'fecha_inicio': formatoFecha(fechaInicio),
    });
    return Crianza.fromJson(data as Map<String, dynamic>);
  }

  Future<List<Galpon>> galpones() async {
    final data = await _client.get('/galpones') as List;
    return data.map((e) => Galpon.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Galpon> crearGalpon({required String nombre, required int capacidadMaxima}) async {
    final data = await _client.post('/galpones', {'nombre': nombre, 'capacidad_maxima': capacidadMaxima});
    return Galpon.fromJson(data as Map<String, dynamic>);
  }

  Future<List<Usuario>> granjeros() async {
    final data = await _client.get('/usuarios?rol=granjero') as List;
    return data.map((e) => Usuario.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<CrianzaGalpon>> galponesDeCrianza(int crianzaId) async {
    final data = await _client.get('/crianzas/$crianzaId/galpones') as List;
    return data.map((e) => CrianzaGalpon.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> asignarGalpon({required int crianzaId, required int galponId, required int granjeroId}) {
    return _client.post('/crianzas/$crianzaId/galpones', {
      'galpon_id': galponId,
      'granjero_id': granjeroId,
    });
  }

  Future<List<IngresoAves>> ingresos(int crianzaId, int cgId) async {
    final data = await _client.get('/crianzas/$crianzaId/galpones/$cgId/ingresos') as List;
    return data.map((e) => IngresoAves.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> registrarIngreso({
    required int crianzaId,
    required int cgId,
    required DateTime fecha,
    required String origen,
    required int cantidad,
    required int muertosTransporte,
  }) {
    return _client.post('/crianzas/$crianzaId/galpones/$cgId/ingresos', {
      'fecha': formatoFecha(fecha),
      'origen': origen,
      'cantidad': cantidad,
      'muertos_transporte': muertosTransporte,
    });
  }

  Future<List<Alerta>> alertas(int crianzaId, {bool? resuelta}) async {
    final query = resuelta == null ? '' : '?resuelta=$resuelta';
    final data = await _client.get('/crianzas/$crianzaId/alertas$query') as List;
    return data.map((e) => Alerta.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> resolverAlerta(int crianzaId, int alertaId) {
    return _client.patch('/crianzas/$crianzaId/alertas/$alertaId/resolver');
  }
}
