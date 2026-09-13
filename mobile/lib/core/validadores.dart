/// Validadores de formulario compartidos entre login y registro.
final _emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

String? validarEmail(String? v) {
  if (v == null || v.trim().isEmpty) return 'Ingresá tu email';
  if (!_emailRegex.hasMatch(v.trim())) return 'Ese email no parece válido';
  return null;
}
