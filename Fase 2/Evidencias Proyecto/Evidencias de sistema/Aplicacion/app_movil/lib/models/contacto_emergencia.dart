class ContactoEmergencia {
  final String id;
  final String perfilId;
  final String nombre;
  final String telefono;
  final String? parentesco;
  final int prioridad;

  const ContactoEmergencia({
    required this.id,
    this.perfilId = '',
    required this.nombre,
    required this.telefono,
    this.parentesco,
    this.prioridad = 1,
  });

  /// El backend devuelve `relacion`; se acepta `parentesco` por compatibilidad.
  factory ContactoEmergencia.fromJson(Map<String, dynamic> json) {
    return ContactoEmergencia(
      id: json['id'].toString(),
      perfilId: (json['perfil_id'] ?? '').toString(),
      nombre: (json['nombre'] ?? '').toString(),
      telefono: (json['telefono'] ?? '').toString(),
      parentesco: (json['relacion'] ?? json['parentesco'])?.toString(),
      prioridad: int.tryParse((json['prioridad'] ?? 1).toString()) ?? 1,
    );
  }
}