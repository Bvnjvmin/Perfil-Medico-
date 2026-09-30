/// Representa al usuario autenticado (titular o cuidador).
///
/// Coincide a propósito con el esquema `UsuarioOut` del backend
/// (backend/app/schemas/usuario.py): mismos campos, mismo orden de ideas.
/// Nunca incluye la contraseña porque el backend tampoco la devuelve.
class Usuario {
  final String id;
  final String nombre;
  final String email;
  final String rol; // "titular" | "cuidador"
  final DateTime creadoEn;

  Usuario({
    required this.id,
    required this.nombre,
    required this.email,
    required this.rol,
    required this.creadoEn,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      email: json['email'] as String,
      rol: json['rol'] as String,
      creadoEn: DateTime.parse(json['creado_en'] as String),
    );
  }
}
