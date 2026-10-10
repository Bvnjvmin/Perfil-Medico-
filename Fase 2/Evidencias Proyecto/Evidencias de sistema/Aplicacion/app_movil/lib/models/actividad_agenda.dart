import 'medicamento.dart';
import 'rutina_cuidado.dart';

enum TipoActividad { medicamento, rutina }

/// Una fila de la agenda diaria: puede venir de un medicamento o de una
/// rutina de cuidado (HU 4). Es solo una vista; no existe tabla en el backend.
class ActividadAgenda {
  /// Identificador estable ("med:<id>" o "rut:<id>") para guardar la confirmación.
  final String clave;
  final TipoActividad tipo;
  final String titulo;
  final String detalle;
  final String? hora;

  const ActividadAgenda({
    required this.clave,
    required this.tipo,
    required this.titulo,
    required this.detalle,
    this.hora,
  });
}

/// Une medicamentos y rutinas activos en una sola lista ordenada por hora
/// (las que no tienen hora van al final, ordenadas por nombre).
List<ActividadAgenda> construirAgenda(
  List<Medicamento> medicamentos,
  List<RutinaCuidado> rutinas,
) {
  final items = <ActividadAgenda>[
    for (final m in medicamentos.where((m) => m.activo))
      ActividadAgenda(
        clave: 'med:${m.id}',
        tipo: TipoActividad.medicamento,
        titulo: m.nombre,
        detalle: '${m.dosis} · ${m.frecuencia}',
        hora: m.horaInicio,
      ),
    for (final r in rutinas.where((r) => r.activo))
      ActividadAgenda(
        clave: 'rut:${r.id}',
        tipo: TipoActividad.rutina,
        titulo: r.titulo,
        detalle: '${r.tipoLegible} · ${r.frecuencia}',
        hora: r.hora,
      ),
  ];

  items.sort((a, b) {
    final ha = a.hora;
    final hb = b.hora;
    if (ha == null && hb == null) return a.titulo.compareTo(b.titulo);
    if (ha == null) return 1;
    if (hb == null) return -1;
    final c = ha.compareTo(hb);
    return c != 0 ? c : a.titulo.compareTo(b.titulo);
  });
  return items;
}