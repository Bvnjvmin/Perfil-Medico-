/// Permisos del usuario autenticado sobre el perfil (HU 7).
class AccesoPerfil {
  final String rol; // 'titular', 'cuidador', 'lectura'
  final bool puedeConfirmar;
  final bool puedeEditarRutinas;

  const AccesoPerfil({
    required this.rol,
    required this.puedeConfirmar,
    required this.puedeEditarRutinas,
  });

  factory AccesoPerfil.fromJson(Map<String, dynamic> json) {
    final rol = (json['rol'] ?? 'lectura').toString();
    final esLectura = rol == 'lectura';
    return AccesoPerfil(
      rol: rol,
      puedeConfirmar:
          esLectura ? false : (json['puede_confirmar'] as bool? ?? true),
      puedeEditarRutinas:
          esLectura ? false : (json['puede_editar_rutinas'] as bool? ?? true),
    );
  }
}

/// Perfil de salud (titular o dependiente).
/// Coincide con `PerfilOut` del backend (backend/app/schemas/perfil.py).
class Perfil {
  final String id;
  final String nombre;
  final String tipo; // 'titular' | 'dependiente'
  final String? subtipo; // 'Adulto mayor' | 'Niño' | null
  final String? rut;
  final String? grupoSanguineo;
  final DateTime? fechaNacimiento;
  final bool activo;
  final AccesoPerfil? miAcceso;

  Perfil({
    required this.id,
    required this.nombre,
    this.tipo = 'titular',
    this.subtipo,
    this.rut,
    this.grupoSanguineo,
    this.fechaNacimiento,
    this.activo = true,
    this.miAcceso,
  });

  bool get esTitular => tipo.toLowerCase() == 'titular';
  bool get esDependiente => tipo.toLowerCase() == 'dependiente';

  /// Reglas de permisos (M4 - HU 7):
  /// Si el backend aún no envía `mi_acceso`, por defecto el titular tiene control total.
  bool get esSoloLectura => miAcceso?.rol == 'lectura';
  bool get puedeConfirmar =>
      esSoloLectura ? false : (miAcceso?.puedeConfirmar ?? true);
  bool get puedeEditarRutinas =>
      esSoloLectura ? false : (miAcceso?.puedeEditarRutinas ?? true);
  bool get esPropio =>
      miAcceso == null ||
      miAcceso!.rol == 'titular' ||
      miAcceso!.rol == 'propietario';

  factory Perfil.fromJson(Map<String, dynamic> json) {
    final fecha = json['fecha_nacimiento'] as String?;
    return Perfil(
      id: json['id'].toString(),
      nombre: (json['nombre'] ?? '').toString(),
      tipo: (json['tipo'] ?? 'titular').toString(),
      subtipo: json['subtipo'] as String?,
      rut: json['rut'] as String?,
      grupoSanguineo: json['grupo_sanguineo'] as String?,
      fechaNacimiento:
          (fecha == null || fecha.isEmpty) ? null : DateTime.parse(fecha),
      activo: json['activo'] as bool? ?? true,
      miAcceso: json['mi_acceso'] is Map<String, dynamic>
          ? AccesoPerfil.fromJson(json['mi_acceso'] as Map<String, dynamic>)
          : null,
    );
  }
}
