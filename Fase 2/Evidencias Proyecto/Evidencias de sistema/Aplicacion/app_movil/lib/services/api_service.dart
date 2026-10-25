import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/actividad.dart';
import '../models/alerta.dart';
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

/// Peticiones HTTP con tiempo límite y mensajes claros cuando no hay conexión
/// (acción del Sprint 3: timeouts y manejo de errores de red).
class _Http {
  static const _limite = Duration(seconds: 15);

  static Future<http.Response> _enviar(
      Future<http.Response> Function() peticion) async {
    try {
      return await peticion().timeout(_limite);
    } on TimeoutException {
      throw ApiException(
          'El servidor tardó demasiado en responder. Revisa tu conexión e inténtalo de nuevo.');
    } on SocketException {
      throw ApiException(
          'No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.');
    } on http.ClientException {
      throw ApiException(
          'No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.');
    }
  }

  static Future<http.Response> get(Uri url, {Map<String, String>? headers}) =>
      _enviar(() => http.get(url, headers: headers));

  static Future<http.Response> post(Uri url,
          {Map<String, String>? headers, Object? body}) =>
      _enviar(() => http.post(url, headers: headers, body: body));

  static Future<http.Response> put(Uri url,
          {Map<String, String>? headers, Object? body}) =>
      _enviar(() => http.put(url, headers: headers, body: body));

  static Future<http.Response> delete(Uri url,
          {Map<String, String>? headers, Object? body}) =>
      _enviar(() => http.delete(url, headers: headers, body: body));
}

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000';
  static const _headersJson = {'Content-Type': 'application/json'};

  // El backend elimina con /perfiles/{perfil_id}/.../{id}. Estos mapas recuerdan
  // a qué perfil pertenece cada registro para no cambiar la firma de eliminar*.
  static final Map<String, String> _perfilDeAlergia = {};
  static final Map<String, String> _perfilDeContacto = {};

  Future<Usuario> registrar({
    required String nombre,
    required String email,
    required String password,
  }) async {
    final respuesta = await _Http.post(
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
    final respuesta = await _Http.post(
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
    final respuesta = await _Http.get(
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

  /// La app muestra "Adulto mayor" / "Niño"; el backend solo acepta
  /// 'adulto_mayor' o 'nino'.
  String _subtipoParaApi(String s) {
    final t = s.trim().toLowerCase();
    if (t.startsWith('ni')) return 'nino';
    return 'adulto_mayor';
  }

  dynamic _decodificar(http.Response r) => jsonDecode(utf8.decode(r.bodyBytes));

  List<T> _lista<T>(http.Response r, T Function(Map<String, dynamic>) desde) {
    return (_decodificar(r) as List)
        .map((e) => desde(e as Map<String, dynamic>))
        .toList();
  }

  // --- Perfiles y Dependientes (HU 2 y HU 6) -------------------------------

  Future<List<Perfil>> listarPerfiles(String token) async {
    final r =
        await _Http.get(Uri.parse('$baseUrl/perfiles'), headers: _auth(token));
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
    final r = await _Http.post(
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
    final r = await _Http.post(
      Uri.parse('$baseUrl/perfiles'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'tipo': 'dependiente',
        'subtipo': _subtipoParaApi(subtipo),
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
    final r = await _Http.put(
      Uri.parse('$baseUrl/perfiles/$perfilId'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'nombre': nombre,
        if (subtipo != null) 'subtipo': _subtipoParaApi(subtipo),
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
    final r = await _Http.delete(
      Uri.parse('$baseUrl/perfiles/$perfilId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) return;
    throw ApiException(_extraerDetalle(r));
  }

  // --- Medicamentos (HU 4 y M7) --------------------------------------------

  Future<List<Medicamento>> listarMedicamentos(
      String token, String perfilId) async {
    final r = await _Http.get(
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
    final r = await _Http.post(
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
    final r = await _Http.put(
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
    final r = await _Http.delete(
      Uri.parse('$baseUrl/medicamentos/$medicamentoId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) return;
    throw ApiException(_extraerDetalle(r));
  }

  // --- Rutinas de cuidado (HU 4 y M7) --------------------------------------

  Future<List<RutinaCuidado>> listarRutinas(
      String token, String perfilId) async {
    final r = await _Http.get(
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
    final r = await _Http.post(
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
    final r = await _Http.put(
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
    final r = await _Http.delete(
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
    final r = await _Http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/actividades?fecha=$fechaStr'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, Actividad.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  Future<Actividad> confirmarActividad(String token, String actividadId) async {
    final r = await _Http.post(
      Uri.parse('$baseUrl/actividades/$actividadId/confirmar'),
      headers: _auth(token),
    );
    if (r.statusCode == 200 || r.statusCode == 201) {
      return Actividad.fromJson(_decodificar(r));
    }
    throw ApiException(_extraerDetalle(r));
  }

  Future<Actividad> desconfirmarActividad(
      String token, String actividadId) async {
    final r = await _Http.post(
      Uri.parse('$baseUrl/actividades/$actividadId/desconfirmar'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return Actividad.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  // --- Panel (HU 8) --------------------------------------------------------

  /// GET /panel?fecha=: una sola llamada con el avance del día de cada perfil
  /// propio o compartido. Devuelve los elementos tal como los envía el backend
  /// (`perfil`, `mi_acceso`, `total`, `confirmadas`, `pendientes`).
  Future<List<Map<String, dynamic>>> obtenerPanel(
      String token, DateTime fecha) async {
    final r = await _Http.get(
      Uri.parse('$baseUrl/panel?fecha=${fechaParaApi(fecha)}'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) {
      return (_decodificar(r) as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    }
    throw ApiException(_extraerDetalle(r));
  }

  // --- Recordatorios y alertas (HU 9 y HU 10) ------------------------------

  /// GET /alertas: avisos del usuario, los más nuevos primero.
  Future<List<Alerta>> listarAlertas(String token,
      {bool soloNoLeidas = false}) async {
    final r = await _Http.get(
      Uri.parse('$baseUrl/alertas?solo_no_leidas=$soloNoLeidas'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, Alerta.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  /// POST /alertas/{id}/leida.
  Future<Alerta> marcarAlertaLeida(String token, String alertaId) async {
    final r = await _Http.post(
      Uri.parse('$baseUrl/alertas/$alertaId/leida'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return Alerta.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  // --- Alergias, Contactos y Cuidadores (M7 - HU 2 y HU 7) -----------------

  Future<List<Alergia>> listarAlergias(String token, String perfilId) async {
    final r = await _Http.get(
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
    final r = await _Http.post(
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
    final r = await _Http.delete(
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
    final r = await _Http.get(
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
    final r = await _Http.post(
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
    final r = await _Http.delete(
      Uri.parse('$baseUrl/perfiles/$pid/contactos-emergencia/$contactoId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204 || r.statusCode == 200) {
      _perfilDeContacto.remove(contactoId);
      return;
    }
    throw ApiException(_extraerDetalle(r));
  }

  /// POST /perfiles/{id}/cuidadores. El backend espera `rol_vinculo`
  /// ('cuidador' | 'lectura') y responde 404 "No existe una cuenta con ese
  /// correo" si el invitado no se ha registrado: ese mensaje se muestra tal cual.
  Future<void> compartirPerfil(
    String token,
    String perfilId, {
    required String email,
    required String rol,
    required bool puedeConfirmar,
    required bool puedeEditarRutinas,
  }) async {
    final r = await _Http.post(
      Uri.parse('$baseUrl/perfiles/$perfilId/cuidadores'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'email': email,
        'rol_vinculo': rol,
        'puede_confirmar': puedeConfirmar,
        'puede_editar_rutinas': puedeEditarRutinas,
      }),
    );
    if (r.statusCode == 201 || r.statusCode == 200) return;
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
