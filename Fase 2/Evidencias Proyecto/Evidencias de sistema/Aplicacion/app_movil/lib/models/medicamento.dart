/// Medicamento de un perfil. Coincide con `MedicamentoOut` del backend.
class Medicamento {
  final String id;
  final String perfilId;
  final String nombre;
  final String dosis;
  final String frecuencia;

  /// Hora en formato "HH:MM:SS" tal como la entrega el backend (puede ser null).
  final String? horaInicio;
  final bool activo;

  Medicamento({
    required this.id,
    required this.perfilId,
    required this.nombre,
    required this.dosis,
    required this.frecuencia,
    this.horaInicio,
    required this.activo,
  });

  factory Medicamento.fromJson(Map<String, dynamic> json) {
    return Medicamento(
      id: json['id'] as String,
      perfilId: json['perfil_id'] as String,
      nombre: json['nombre'] as String,
      dosis: json['dosis'] as String,
      frecuencia: json['frecuencia'] as String,
      horaInicio: json['hora_inicio'] as String?,
      activo: json['activo'] as bool? ?? true,
    );
  }
}
