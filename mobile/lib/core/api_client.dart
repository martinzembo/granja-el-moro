import 'dart:convert';

import 'package:http/http.dart' as http;

import 'config.dart';

/// Excepción con el mensaje que ya viene armado en español desde el backend
/// (FastAPI devuelve `{"detail": "..."}` en los errores) — se puede mostrar
/// directo en un SnackBar sin traducir nada.
class ApiException implements Exception {
  ApiException(this.statusCode, this.message);

  final int statusCode;
  final String message;

  @override
  String toString() => message;
}

/// Wrapper fino sobre `http` para hablar con el backend. Adjunta el token
/// JWT cuando se pide (`auth: true`, default) y decodifica los errores de
/// FastAPI a [ApiException].
class ApiClient {
  ApiClient({this.token});

  final String? token;

  Map<String, String> _headers({bool auth = true}) {
    final headers = {'Content-Type': 'application/json'};
    if (auth && token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Uri _uri(String path) => Uri.parse('$apiBaseUrl$path');

  dynamic _procesar(http.Response resp) {
    if (resp.statusCode >= 200 && resp.statusCode < 300) {
      if (resp.body.isEmpty) return null;
      return jsonDecode(utf8.decode(resp.bodyBytes));
    }
    String mensaje = 'Error inesperado (${resp.statusCode})';
    try {
      final data = jsonDecode(utf8.decode(resp.bodyBytes));
      if (data is Map && data['detail'] != null) {
        mensaje = data['detail'].toString();
      }
    } catch (_) {
      // el body no era JSON, nos quedamos con el mensaje genérico
    }
    throw ApiException(resp.statusCode, mensaje);
  }

  Future<dynamic> get(String path, {bool auth = true}) async {
    final resp = await http.get(_uri(path), headers: _headers(auth: auth));
    return _procesar(resp);
  }

  Future<dynamic> post(String path, Map<String, dynamic> body, {bool auth = true}) async {
    final resp = await http.post(_uri(path), headers: _headers(auth: auth), body: jsonEncode(body));
    return _procesar(resp);
  }

  Future<dynamic> patch(String path, {Map<String, dynamic>? body, bool auth = true}) async {
    final resp = await http.patch(
      _uri(path),
      headers: _headers(auth: auth),
      body: body != null ? jsonEncode(body) : null,
    );
    return _procesar(resp);
  }
}
