/// Rutina de cuidado (alimentación, hidratación, vitaminas...).
/// Coincide con `RutinaCuidadoOut` del backend.
class RutinaCuidado {
  final String id;
  final String perfilId;
  final String tipo;
  final String? descripcion;
  final String frecuencia;

  /// Hora en formato "HH:MM:SS" tal como la entrega el backend (puede ser null).
  final String? hora;
  final bool activo;

  RutinaCuidado({
    required this.id,
    required this.perfilId,
    required this.tipo,
    this.descripcion,
    required this.frecuencia,
    this.hora,
    required this.activo,
  });

  factory RutinaCuidado.fromJson(Map<String, dynamic> json) {
    return RutinaCuidado(
      id: json['id'] as String,
      perfilId: json['perfil_id'] as String,
      tipo: json['tipo'] as String,
      descripcion: json['descripcion'] as String?,
      frecuencia: json['frecuencia'] as String,
      hora: json['hora'] as String?,
      activo: json['activo'] as bool? ?? true,
    );
  }

  /// Nombre del tipo listo para mostrar ("alimentacion" -> "Alimentación").
  String get tipoLegible {
    switch (tipo) {
      case 'alimentacion':
        return 'Alimentación';
      case 'hidratacion':
        return 'Hidratación';
      case 'vitaminas':
        return 'Vitaminas';
      default:
        if (tipo.isEmpty) return tipo;
        return tipo[0].toUpperCase() + tipo.substring(1);
    }
  }

  /// Título para la agenda: la descripción si existe, si no el tipo.
  String get titulo {
    final d = descripcion;
    return (d != null && d.trim().isNotEmpty) ? d.trim() : tipoLegible;
  }
}