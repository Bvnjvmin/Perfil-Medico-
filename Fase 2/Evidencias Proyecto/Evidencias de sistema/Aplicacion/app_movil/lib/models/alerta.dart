/// Aviso del sistema (HU 9 y HU 10): un recordatorio de una actividad próxima o una
/// alerta porque una actividad no fue confirmada. Coincide con `AlertaOut` del backend
/// (`GET /alertas`).
class Alerta {
  final String id;
  final String perfilId;
  final String actividadId;
  final String tipo; // 'recordatorio' | 'alerta'
  final int nivel; // 0 recordatorio; 1, 2, ... alertas escalonadas
  final String mensaje;
  final String creadaEn;
  final String? leidaEn;

  const Alerta({
    required this.id,
    required this.perfilId,
    required this.actividadId,
    required this.tipo,
    required this.nivel,
    required this.mensaje,
    required this.creadaEn,
    this.leidaEn,
  });

  bool get esAlerta => tipo == 'alerta';
  bool get estaLeida => leidaEn != null;

  factory Alerta.fromJson(Map<String, dynamic> json) {
    return Alerta(
      id: json['id'].toString(),
      perfilId: (json['perfil_id'] ?? '').toString(),
      actividadId: (json['actividad_id'] ?? '').toString(),
      tipo: (json['tipo'] ?? 'recordatorio').toString(),
      nivel: (json['nivel'] as num?)?.toInt() ?? 0,
      mensaje: (json['mensaje'] ?? '').toString(),
      creadaEn: (json['creada_en'] ?? '').toString(),
      leidaEn: json['leida_en']?.toString(),
    );
  }
}
