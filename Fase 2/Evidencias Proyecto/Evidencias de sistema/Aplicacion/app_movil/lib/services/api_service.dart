import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/medicamento.dart';
import '../models/perfil.dart';
import '../models/rutina_cuidado.dart';
import '../models/usuario.dart';
import '../utils/hora.dart';

/// Error de la API con el mensaje que devuelve el backend (campo "detail"
/// de FastAPI), para poder mostrarlo directo en la UI.
class ApiException implements Exception {
  final String mensaje;
  ApiException(this.mensaje);
  @override
  String toString() => mensaje;
}

class ApiService {
  /// URL base según dónde corre la app — cambiar según el entorno de prueba:
  /// - Emulador Android            -> 10.0.2.2 (así ve el "localhost" del host)
  /// - Simulador iOS / Flutter Web -> localhost
  /// - Celular físico              -> IP del computador en la red local (ej. 192.168.1.X)
  static const String baseUrl = 'http://10.0.2.2:8000';

  static const _headersJson = {'Content-Type': 'application/json'};

  /// POST /auth/register — crea un usuario nuevo.
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
      return Usuario.fromJson(jsonDecode(respuesta.body));
    }
    throw ApiException(_extraerDetalle(respuesta));
  }

  /// POST /auth/login — el backend usa el formulario estándar OAuth2, NO
  /// JSON: el body va como application/x-www-form-urlencoded, con el correo
  /// en el campo "username" (así lo exige OAuth2PasswordRequestForm).
  Future<String> login({required String email, required String password}) async {
    final respuesta = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );

    if (respuesta.statusCode == 200) {
      final datos = jsonDecode(respuesta.body);
      return datos['access_token'] as String;
    }
    throw ApiException(_extraerDetalle(respuesta));
  }

  /// GET /auth/me — endpoint protegido; requiere "Authorization: Bearer <token>".
  Future<Usuario> obtenerUsuarioActual(String token) async {
    final respuesta = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (respuesta.statusCode == 200) {
      return Usuario.fromJson(jsonDecode(respuesta.body));
    }
    throw ApiException(_extraerDetalle(respuesta));
  }

  // --- Helpers para endpoints protegidos -----------------------------------

  Map<String, String> _auth(String token, {bool json = false}) => {
        'Authorization': 'Bearer $token',
        if (json) 'Content-Type': 'application/json',
      };

  /// Decodifica siempre como UTF-8 para no romper tildes y eñes.
  dynamic _decodificar(http.Response r) => jsonDecode(utf8.decode(r.bodyBytes));

  List<T> _lista<T>(http.Response r, T Function(Map<String, dynamic>) desde) {
    return (_decodificar(r) as List)
        .map((e) => desde(e as Map<String, dynamic>))
        .toList();
  }

  // --- Perfil de salud (HU 2) ----------------------------------------------

  /// GET /perfiles — perfiles del titular autenticado.
  Future<List<Perfil>> listarPerfiles(String token) async {
    final r = await http.get(Uri.parse('$baseUrl/perfiles'), headers: _auth(token));
    if (r.statusCode == 200) return _lista(r, Perfil.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  /// POST /perfiles — crea el perfil de salud del titular.
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

  /// PUT /perfiles/{id} — actualiza el perfil propio.
  Future<Perfil> actualizarPerfil(
    String token,
    String perfilId, {
    required String nombre,
    String? rut,
    String? grupoSanguineo,
    DateTime? fechaNacimiento,
  }) async {
    final r = await http.put(
      Uri.parse('$baseUrl/perfiles/$perfilId'),
      headers: _auth(token, json: true),
      body: jsonEncode({
        'nombre': nombre,
        'rut': rut,
        'grupo_sanguineo': grupoSanguineo,
        'fecha_nacimiento':
            fechaNacimiento == null ? null : fechaParaApi(fechaNacimiento),
      }),
    );
    if (r.statusCode == 200) return Perfil.fromJson(_decodificar(r));
    throw ApiException(_extraerDetalle(r));
  }

  // --- Medicamentos (HU 4) -------------------------------------------------

  /// GET /perfiles/{perfil_id}/medicamentos
  Future<List<Medicamento>> listarMedicamentos(String token, String perfilId) async {
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/medicamentos'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, Medicamento.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  /// POST /perfiles/{perfil_id}/medicamentos
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

  /// DELETE /medicamentos/{id}
  Future<void> eliminarMedicamento(String token, String medicamentoId) async {
    final r = await http.delete(
      Uri.parse('$baseUrl/medicamentos/$medicamentoId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204) return;
    throw ApiException(_extraerDetalle(r));
  }

  // --- Rutinas de cuidado (HU 4) -------------------------------------------

  /// GET /perfiles/{perfil_id}/rutinas
  Future<List<RutinaCuidado>> listarRutinas(String token, String perfilId) async {
    final r = await http.get(
      Uri.parse('$baseUrl/perfiles/$perfilId/rutinas'),
      headers: _auth(token),
    );
    if (r.statusCode == 200) return _lista(r, RutinaCuidado.fromJson);
    throw ApiException(_extraerDetalle(r));
  }

  /// POST /perfiles/{perfil_id}/rutinas
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

  /// DELETE /rutinas/{id}
  Future<void> eliminarRutina(String token, String rutinaId) async {
    final r = await http.delete(
      Uri.parse('$baseUrl/rutinas/$rutinaId'),
      headers: _auth(token),
    );
    if (r.statusCode == 204) return;
    throw ApiException(_extraerDetalle(r));
  }

  String _extraerDetalle(http.Response respuesta) {
    try {
      final cuerpo = jsonDecode(respuesta.body);
      return cuerpo['detail']?.toString() ?? 'Error inesperado (${respuesta.statusCode})';
    } catch (_) {
      return 'Error inesperado (${respuesta.statusCode})';
    }
  }
}
