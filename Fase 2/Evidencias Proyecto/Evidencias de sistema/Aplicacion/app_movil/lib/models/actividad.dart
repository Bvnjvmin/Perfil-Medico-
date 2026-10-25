class Actividad {
  final String id;
  final String perfilId;
  final String fecha;
  final String origenTipo; // 'medicamento' | 'rutina'
  final String origenId;
  final String titulo;
  final String? detalle;
  final String hora;
  final String estado; // 'pendiente' | 'confirmada' | 'vencida' | 'omitida'
  final String? confirmadaEn;
  final String? confirmadaPorId;

  const Actividad({
    required this.id,
    required this.perfilId,
    required this.fecha,
    required this.origenTipo,
    required this.origenId,
    required this.titulo,
    this.detalle,
    required this.hora,
    required this.estado,
    this.confirmadaEn,
    this.confirmadaPorId,
  });

  bool get estaConfirmada => estado.toLowerCase() == 'confirmada';

  /// Pasó el día sin confirmarse (la marca el backend a la medianoche).
  bool get estaVencida => estado.toLowerCase() == 'vencida';

  factory Actividad.fromJson(Map<String, dynamic> json) {
    return Actividad(
      id: json['id'].toString(),
      perfilId: (json['perfil_id'] ?? '').toString(),
      fecha: (json['fecha'] ?? '').toString(),
      origenTipo: (json['origen_tipo'] ?? '').toString(),
      origenId: (json['origen_id'] ?? '').toString(),
      titulo: (json['titulo'] ?? '').toString(),
      detalle: json['detalle']?.toString(),
      hora: (json['hora'] ?? '').toString(),
      estado: (json['estado'] ?? 'pendiente').toString(),
      confirmadaEn: json['confirmada_en']?.toString(),
      confirmadaPorId: json['confirmada_por_id']?.toString(),
    );
  }

  Actividad copyWith({
    String? estado,
    String? confirmadaEn,
    String? confirmadaPorId,
  }) {
    return Actividad(
      id: id,
      perfilId: perfilId,
      fecha: fecha,
      origenTipo: origenTipo,
      origenId: origenId,
      titulo: titulo,
      detalle: detalle,
      hora: hora,
      estado: estado ?? this.estado,
      confirmadaEn: confirmadaEn ?? this.confirmadaEn,
      confirmadaPorId: confirmadaPorId ?? this.confirmadaPorId,
    );
  }
}
