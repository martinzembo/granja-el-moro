import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'api_client.dart';
import 'usuario.dart';

enum EstadoAuth { cargando, autenticado, noAutenticado }

/// Sesión del usuario logueado. Guarda el JWT en almacenamiento seguro del
/// celular para no pedir login cada vez que se abre la app.
class AuthService extends ChangeNotifier {
  static const _storage = FlutterSecureStorage();
  static const _claveToken = 'token';

  EstadoAuth estado = EstadoAuth.cargando;
  String? _token;
  Usuario? usuario;

  String? get token => _token;

  /// Se llama una vez al arrancar la app: si hay un token guardado y sigue
  /// siendo válido, entra directo sin pedir login de nuevo.
  Future<void> intentarSesionGuardada() async {
    final tokenGuardado = await _storage.read(key: _claveToken);
    if (tokenGuardado == null) {
      estado = EstadoAuth.noAutenticado;
      notifyListeners();
      return;
    }
    try {
      final data = await ApiClient(token: tokenGuardado).get('/auth/me');
      _token = tokenGuardado;
      usuario = Usuario.fromJson(data as Map<String, dynamic>);
      estado = EstadoAuth.autenticado;
    } catch (_) {
      // token vencido o inválido — se descarta, vuelve a pedir login
      await _storage.delete(key: _claveToken);
      estado = EstadoAuth.noAutenticado;
    }
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    final data = await ApiClient().post(
      '/auth/login',
      {'email': email, 'password': password},
      auth: false,
    );
    final token = data['access_token'] as String;
    final me = await ApiClient(token: token).get('/auth/me');

    await _storage.write(key: _claveToken, value: token);
    _token = token;
    usuario = Usuario.fromJson(me as Map<String, dynamic>);
    estado = EstadoAuth.autenticado;
    notifyListeners();
  }

  /// Registro público: siempre crea un granjero (el backend ni siquiera
  /// acepta elegir otro rol acá, ver docs/modelo-datos.md). Pedido del
  /// docente de la cátedra: la cuenta queda inactiva hasta que un admin la
  /// habilite (ver AdminHomeScreen > "Cuentas pendientes"), así que NO
  /// inicia sesión automáticamente — antes sí lo hacía, pero ahora el
  /// login fallaría con 403 justo después de crearla.
  Future<void> registrarGranjero(String nombre, String email, String password) async {
    await ApiClient().post(
      '/auth/register',
      {'nombre': nombre, 'email': email, 'password': password},
      auth: false,
    );
  }

  Future<void> logout() async {
    await _storage.delete(key: _claveToken);
    _token = null;
    usuario = null;
    estado = EstadoAuth.noAutenticado;
    notifyListeners();
  }

  ApiClient get api => ApiClient(token: _token);
}
