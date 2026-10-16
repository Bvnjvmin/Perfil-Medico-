import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/actividad.dart';
import '../models/alergia.dart';
import '../models/contacto_emergencia.dart';
import '../models/medicamento.dart';
import '../models/perfil.dart';
import '../models/rutina_cuidado.dart';
import '../models/usuario.dart';
import '../utils/hora.dart';

class ApiException implements Exception {
  final String mensaje;
  ApiException(this.mensaje);
  @override
  String toString() => mensaje;
}

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000';
  static const _headersJson = {'Content-Type': 'application/json'};

  // Respaldo en memoria SOLO para la agenda (el backend aún no tiene rutas de
  // actividades). Alergias y contactos ya existen en el backend: no se simulan.
  static final Set<String> _confirmadasRespaldo = {};
  static final Map<String, Actividad> _cacheActividades = {};

  // El backend elimina con /perfiles/{perfil_id}/.../{id}. Estos mapas recuerdan
  // a qué perfil pertenece cada registro para no cambiar la firma de eliminar*.
  static final Map<String, String> _perfilDeAlergia = {};
  static final Map<String, String> _perfilDeContacto = {};

  Future<Usuario> registrar({
    required String nombre,
    required String email,
    required String password,
  }) async {
    final respuesta = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: _headersJson,
      body: jsonEncode({
        'nombre': nombre,
        'email': email,
        'password': password,
      }),
    );

    if (respuesta.statusCode == 201) {
      return Usuario.fromJson(_decodificar(respuesta));
    }
    throw ApiException(_extraerDetalle(respuesta));
  }

  Future<String> login({required String email, required String password}) async {
    final respuesta = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );

    if (respuesta.statusCode == 200) {
      final datos = _decodificar(respuesta);
      return datos['access_token'] as String;
    }
    throw ApiException(_extraerDetalle(respuesta));
  }

  Future<Usuario> obtenerUsuarioActual(String token) async {
    final respuesta = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (respuesta.statusCode == 200) {
      return Usuario.fromJson(_decodificar(respuesta));
    }
    throw ApiException(_extraerDetalle(respuesta));
  }

  Map<String, String> _auth(String token, {bool json = false}) => {
        'Authorization': 'Bearer $token',
        if (json) 'Content-Type': 'application/json',
      };

  dynamic _decodificar(http.Response r) => jsonDecode(utf8.decode(r.bodyBytes));

  List<T> _lista<T>(http.Response r, T Function(Map<String, dynamic>) desde) {
    return (_decodificar(r) as List)
        .map((e) => desde(e as Map<String, dynamic>))
        .toList();
  }

  // --- Perfiles y Dependientes (HU 2 y HU 6) -------------------------------

  Future<List<Perfil>> listarPerfiles(String token) async {
    final r =
        await http.get(Uri.parse('$baseUrl/perfiles'), headers: _auth(token));
    if (r.statusCode == 200) return _lista(r, Perfil.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  Future<Perfil> crearPerfil(
    String token, {
    required String nombre,
    String? rut,
    String? grupoSanguineo,
    DateTime? fechaNacimiento,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'tipo': 'titular',
        'nombre': nombre,
        'rut': rut,
        'grupo_sanguineo': grupoSanguineo,
        'fecha_nacimiento':
            fechaNacimiento == null ? null : fechaParaApi(fechaNacimiento),
      }),
    );
    if (r.statusCode == 201) return Perfil.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  Future<Perfil> crearDependiente(
    String token, {
    required String nombre,
    required String subtipo,
    String? rut,
    String? grupoSanguineo,
    DateTime? fechaNacimiento,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'tipo': 'dependiente',
        'subtipo': subtipo,
        'nombre': nombre,
        'rut': rut,
        'grupo_sanguineo': grupoSanguineo,
        'fecha_nacimiento':
            fechaNacimiento == null ? null : fechaParaApi(fechaNacimiento),
      }),
    );
    if (r.statusCode == 201 || r.statusCode == 200) {
      return Perfil.fromJson(_decodificar(r));
    }
    throw ApiException(_extraerDetalle(r));
  }

  Future<Perfil> actualizarPerfil(
    String token,
    String perfilId, {
    required String nombre,
    String? subtipo,
    String? rut,
    String? grupoSanguineo,
    DateTime? fechaNacimiento,
  }) async {
    final r = await http.put(
      Uri.parse('$baseUrl/perfiles/$perfilId'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'nombre': nombre,
        if (subtipo != null) 'subtipo': subtipo,
        'rut': rut,
        'grupo_sanguineo': grupoSanguineo,
        'fecha_nacimiento':
            fechaNacimiento == null ? null : fechaParaApi(fechaNacimiento),
      }),
    );
    if (r.statusCode == 200) return Perfil.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  Future<void> eliminarPerfil(String token, String perfilId) async {
    final r = await http.delete(
      Uri.parse('$baseUrl/perfiles/$perfilId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) return;
    throw ApiException(_extraerDetalle(r));
  }

  // --- Medicamentos (HU 4 y M7) --------------------------------------------

  Future<List<Medicamento>> listarMedicamentos(
      String token, String perfilId) async {
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/medicamentos'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, Medicamento.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  Future<Medicamento> registrarMedicamento(
    String token,
    String perfilId, {
    required String nombre,
    required String dosis,
    required String frecuencia,
    String? horaInicio,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles/$perfilId/medicamentos'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'nombre': nombre,
        'dosis': dosis,
        'frecuencia': frecuencia,
        'hora_inicio': horaInicio,
      }),
    );
    if (r.statusCode == 201) return Medicamento.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  Future<Medicamento> actualizarMedicamento(
    String token,
    String medicamentoId, {
    required String nombre,
    required String dosis,
    required String frecuencia,
    String? horaInicio,
  }) async {
    final r = await http.put(
      Uri.parse('$baseUrl/medicamentos/$medicamentoId'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'nombre': nombre,
        'dosis': dosis,
        'frecuencia': frecuencia,
        'hora_inicio': horaInicio,
      }),
    );
    if (r.statusCode == 200) return Medicamento.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  Future<void> eliminarMedicamento(String token, String medicamentoId) async {
    final r = await http.delete(
      Uri.parse('$baseUrl/medicamentos/$medicamentoId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) return;
    throw ApiException(_extraerDetalle(r));
  }

  // --- Rutinas de cuidado (HU 4 y M7) --------------------------------------

  Future<List<RutinaCuidado>> listarRutinas(
      String token, String perfilId) async {
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/rutinas'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, RutinaCuidado.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  Future<RutinaCuidado> registrarRutina(
    String token,
    String perfilId, {
    required String tipo,
    String? descripcion,
    required String frecuencia,
    String? hora,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles/$perfilId/rutinas'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'tipo': tipo,
        'descripcion': descripcion,
        'frecuencia': frecuencia,
        'hora': hora,
      }),
    );
    if (r.statusCode == 201) return RutinaCuidado.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  Future<RutinaCuidado> actualizarRutina(
    String token,
    String rutinaId, {
    required String tipo,
    String? descripcion,
    required String frecuencia,
    String? hora,
  }) async {
    final r = await http.put(
      Uri.parse('$baseUrl/rutinas/$rutinaId'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'tipo': tipo,
        'descripcion': descripcion,
        'frecuencia': frecuencia,
        'hora': hora,
      }),
    );
    if (r.statusCode == 200) return RutinaCuidado.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  Future<void> eliminarRutina(String token, String rutinaId) async {
    final r = await http.delete(
      Uri.parse('$baseUrl/rutinas/$rutinaId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) return;
    throw ApiException(_extraerDetalle(r));
  }

  // --- Agenda de Actividades (M3 - Cierre HU 5) ----------------------------

  Future<List<Actividad>> listarActividades(
    String token,
    String perfilId,
    DateTime fecha,
  ) async {
    final fechaStr = fechaParaApi(fecha);
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/actividades?fecha=$fechaStr'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, Actividad.fromJson);

    if (r.statusCode == 404) {
      final meds = await listarMedicamentos(token, perfilId);
      final ruts = await listarRutinas(token, perfilId);
      final List<Actividad> generadas = [];

      for (final m in meds) {
        final idAct = 'med_${perfilId}_${m.id}_$fechaStr';
        final conf = _confirmadasRespaldo.contains(idAct);
        final act = Actividad(
          id: idAct,
          perfilId: perfilId,
          fecha: fechaStr,
          origenTipo: 'medicamento',
          origenId: m.id,
          titulo: m.nombre,
          detalle: '${m.dosis} • ${m.frecuencia}',
          hora: m.horaInicio ?? '08:00',
          estado: conf ? 'confirmada' : 'pendiente',
        );
        _cacheActividades[idAct] = act;
        generadas.add(act);
      }

      for (final rut in ruts) {
        final idAct = 'rut_${perfilId}_${rut.id}_$fechaStr';
        final conf = _confirmadasRespaldo.contains(idAct);
        final act = Actividad(
          id: idAct,
          perfilId: perfilId,
          fecha: fechaStr,
          origenTipo: 'rutina',
          origenId: rut.id,
          titulo: (rut.descripcion != null && rut.descripcion!.isNotEmpty)
              ? '${rut.tipo}: ${rut.descripcion}'
              : rut.tipo,
          detalle: rut.frecuencia,
          hora: rut.hora ?? '10:00',
          estado: conf ? 'confirmada' : 'pendiente',
        );
        _cacheActividades[idAct] = act;
        generadas.add(act);
      }

      generadas.sort((a, b) => a.hora.compareTo(b.hora));
      return generadas;
    }

    throw ApiException(_extraerDetalle(r));
  }

  Future<Actividad> confirmarActividad(String token, String actividadId) async {
    final r = await http.post(
      Uri.parse('$baseUrl/actividades/$actividadId/confirmar'),
      headers: _auth(token),
    );
    if (r.statusCode == 200 || r.statusCode == 201) {
      return Actividad.fromJson(_decodificar(r));
    }
    if (r.statusCode == 404) {
      _confirmadasRespaldo.add(actividadId);
      final previa = _cacheActividades[actividadId];
      final actualizada = Actividad(
        id: actividadId,
        perfilId: previa?.perfilId ?? '',
        fecha: previa?.fecha ?? fechaParaApi(DateTime.now()),
        origenTipo: previa?.origenTipo ?? 'medicamento',
        origenId: previa?.origenId ?? '1',
        titulo: previa?.titulo ?? '',
        detalle: previa?.detalle,
        hora: previa?.hora ?? '08:00',
        estado: 'confirmada',
        confirmadaEn: DateTime.now().toIso8601String(),
      );
      _cacheActividades[actividadId] = actualizada;
      return actualizada;
    }
    throw ApiException(_extraerDetalle(r));
  }

  Future<Actividad> desconfirmarActividad(
      String token, String actividadId) async {
    final r = await http.post(
      Uri.parse('$baseUrl/actividades/$actividadId/desconfirmar'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) {
      return Actividad.fromJson(_decodificar(r));
    }
    if (r.statusCode == 404) {
      _confirmadasRespaldo.remove(actividadId);
      final previa = _cacheActividades[actividadId];
      final actualizada = Actividad(
        id: actividadId,
        perfilId: previa?.perfilId ?? '',
        fecha: previa?.fecha ?? fechaParaApi(DateTime.now()),
        origenTipo: previa?.origenTipo ?? 'medicamento',
        origenId: previa?.origenId ?? '1',
        titulo: previa?.titulo ?? '',
        detalle: previa?.detalle,
        hora: previa?.hora ?? '08:00',
        estado: 'pendiente',
      );
      _cacheActividades[actividadId] = actualizada;
      return actualizada;
    }
    throw ApiException(_extraerDetalle(r));
  }

  // --- Alergias, Contactos y Cuidadores (M7 - HU 2 y HU 7) -----------------

  Future<List<Alergia>> listarAlergias(String token, String perfilId) async {
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/alergias'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) {
      final lista = _lista(r, Alergia.fromJson);
      for (final a in lista) {
        _perfilDeAlergia[a.id] = perfilId;
      }
      return lista;
    }
    throw ApiException(_extraerDetalle(r));
  }

  /// El backend solo guarda `sustancia` y `severidad` (ambas obligatorias).
  /// [reaccion] se mantiene en la firma por compatibilidad, pero no se envía.
  Future<Alergia> registrarAlergia(
    String token,
    String perfilId, {
    required String nombre,
    String? severidad,
    String? reaccion,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles/$perfilId/alergias'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'sustancia': nombre,
        'severidad': (severidad == null || severidad.isEmpty)
            ? 'leve'
            : severidad,
      }),
    );
    if (r.statusCode == 201 || r.statusCode == 200) {
      final alergia = Alergia.fromJson(_decodificar(r));
      _perfilDeAlergia[alergia.id] = perfilId;
      return alergia;
    }
    throw ApiException(_extraerDetalle(r));
  }

  Future<void> eliminarAlergia(
    String token,
    String alergiaId, {
    String? perfilId,
  }) async {
    final pid = perfilId ?? _perfilDeAlergia[alergiaId];
    if (pid == null) {
      throw ApiException(
          'No se pudo determinar el perfil de la alergia. Recarga la lista.');
    }
    final r = await http.delete(
      Uri.parse('$baseUrl/perfiles/$pid/alergias/$alergiaId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) {
      _perfilDeAlergia.remove(alergiaId);
      return;
    }
    throw ApiException(_extraerDetalle(r));
  }

  Future<List<ContactoEmergencia>> listarContactos(
      String token, String perfilId) async {
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/contactos-emergencia'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) {
      final lista = _lista(r, ContactoEmergencia.fromJson);
      for (final c in lista) {
        _perfilDeContacto[c.id] = perfilId;
      }
      return lista;
    }
    throw ApiException(_extraerDetalle(r));
  }

  /// [parentesco] se envía al backend como `relacion`.
  /// El teléfono debe tener entre 6 y 20 caracteres.
  Future<ContactoEmergencia> registrarContacto(
    String token,
    String perfilId, {
    required String nombre,
    required String telefono,
    String? parentesco,
    int prioridad = 1,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles/$perfilId/contactos-emergencia'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'nombre': nombre,
        'telefono': telefono,
        'relacion': (parentesco == null || parentesco.isEmpty)
            ? null
            : parentesco,
        'prioridad': prioridad,
      }),
    );
    if (r.statusCode == 201 || r.statusCode == 200) {
      final contacto = ContactoEmergencia.fromJson(_decodificar(r));
      _perfilDeContacto[contacto.id] = perfilId;
      return contacto;
    }
    throw ApiException(_extraerDetalle(r));
  }

  Future<void> eliminarContacto(
    String token,
    String contactoId, {
    String? perfilId,
  }) async {
    final pid = perfilId ?? _perfilDeContacto[contactoId];
    if (pid == null) {
      throw ApiException(
          'No se pudo determinar el perfil del contacto. Recarga la lista.');
    }
    final r = await http.delete(
      Uri.parse('$baseUrl/perfiles/$pid/contactos-emergencia/$contactoId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) {
      _perfilDeContacto.remove(contactoId);
      return;
    }
    throw ApiException(_extraerDetalle(r));
  }

  /// El backend aún no tiene la ruta de cuidadores. Antes un 404 se trataba
  /// como éxito y la app decía "compartido" sin guardar nada; ahora se avisa.
  Future<void> compartirPerfil(
    String token,
    String perfilId, {
    required String email,
    required String rol,
    required bool puedeConfirmar,
    required bool puedeEditarRutinas,
  }) async {
    final r = await http.post(
      Uri.parse('$baseUrl/perfiles/$perfilId/cuidadores'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'email': email,
        'rol': rol,
        'puede_confirmar': puedeConfirmar,
        'puede_editar_rutinas': puedeEditarRutinas,
      }),
    );
    if (r.statusCode == 201 || r.statusCode == 200) return;
    if (r.statusCode == 404) {
      throw ApiException(
          'Compartir perfil aún no está disponible en el servidor.');
    }
    throw ApiException(_extraerDetalle(r));
  }

  String _extraerDetalle(http.Response respuesta) {
    try {
      final cuerpo = _decodificar(respuesta);
      final detalle = cuerpo['detail'];
      if (detalle is List) {
        // 422 de FastAPI: [{loc: [...], msg: "...", type: "..."}]
        final mensajes = detalle
            .map((e) => e is Map ? (e['msg'] ?? '').toString() : e.toString())
            .where((m) => m.isNotEmpty)
            .toList();
        if (mensajes.isNotEmpty) return mensajes.join('\n');
      } else if (detalle != null) {
        return detalle.toString();
      }
      return 'Error inesperado (${respuesta.statusCode})';
    } catch (_) {
      return 'Error inesperado (${respuesta.statusCode})';
    }
  }
}
