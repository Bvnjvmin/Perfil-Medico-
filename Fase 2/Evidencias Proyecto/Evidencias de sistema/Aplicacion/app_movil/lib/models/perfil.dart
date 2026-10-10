/// Perfil de salud del titular.
///
/// Coincide con `PerfilOut` del backend (backend/app/schemas/perfil.py).
class Perfil {
  final String id;
  final String nombre;
  final String? rut;
  final String? grupoSanguineo;
  final DateTime? fechaNacimiento;

  Perfil({
    required this.id,
    required this.nombre,
    this.rut,
    this.grupoSanguineo,
    this.fechaNacimiento,
  });

  factory Perfil.fromJson(Map<String, dynamic> json) {
    final fecha = json['fecha_nacimiento'] as String?;
    return Perfil(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      rut: json['rut'] as String?,
      grupoSanguineo: json['grupo_sanguineo'] as String?,
      fechaNacimiento: fecha == null ? null : DateTime.parse(fecha),
    );
  }
}