/// Representa al usuario autenticado.
///
/// Coincide a propósito con el esquema `UsuarioOut` del backend
/// (backend/app/schemas/usuario.py): mismos campos, mismo orden de ideas.
/// Nunca incluye la contraseña porque el backend tampoco la devuelve.
///
/// Nota: el campo `rol` se eliminó (Sprint 2) — la gestión de permisos
/// (titular/cuidador) sobre los perfiles clínicos se maneja mediante
/// tablas intermedias a partir del Sprint 3.
class Usuario {
  final String id;
  final String nombre;
  final String email;
  final DateTime creadoEn;

  Usuario({
    required this.id,
    required this.nombre,
    required this.email,
    required this.creadoEn,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      email: json['email'] as String,
      creadoEn: DateTime.parse(json['creado_en'] as String),
    );
  }
}
