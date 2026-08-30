enum RolUsuario { admin, granjero }

RolUsuario rolDesdeString(String valor) {
  return valor == 'admin' ? RolUsuario.admin : RolUsuario.granjero;
}

/// Espejo de `UsuarioOut` del backend (app/schemas/usuario.py).
class Usuario {
  Usuario({required this.id, required this.nombre, required this.email, required this.rol});

  final int id;
  final String nombre;
  final String email;
  final RolUsuario rol;

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'] as int,
      nombre: json['nombre'] as String,
      email: json['email'] as String,
      rol: rolDesdeString(json['rol'] as String),
    );
  }
}
