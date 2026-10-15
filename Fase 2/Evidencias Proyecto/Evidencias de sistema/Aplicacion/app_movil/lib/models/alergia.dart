class Alergia {
  final String id;
  final String perfilId;
  final String nombre;
  final String? severidad;
  final String? reaccion;

  const Alergia({
    required this.id,
    this.perfilId = '',
    required this.nombre,
    this.severidad,
    this.reaccion,
  });

  /// El backend devuelve `sustancia`; se aceptan `nombre`/`alergeno` por compatibilidad.
  factory Alergia.fromJson(Map<String, dynamic> json) {
    return Alergia(
      id: json['id'].toString(),
      perfilId: (json['perfil_id'] ?? '').toString(),
      nombre: (json['sustancia'] ?? json['nombre'] ?? json['alergeno'] ?? '')
          .toString(),
      severidad: json['severidad']?.toString(),
      reaccion: (json['reaccion'] ?? json['notas'])?.toString(),
    );
  }
}