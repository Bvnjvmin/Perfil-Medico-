import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/usuario.dart';

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

  /// POST /auth/register — crea un usuario nuevo (titular o cuidador).
  Future<Usuario> registrar({
    required String nombre,
    required String email,
    required String password,
    String rol = 'titular',
  }) async {
    final respuesta = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: _headersJson,
      body: jsonEncode({
        'nombre': nombre,
        'email': email,
        'password': password,
        'rol': rol,
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

  String _extraerDetalle(http.Response respuesta) {
    try {
      final cuerpo = jsonDecode(respuesta.body);
      return cuerpo['detail']?.toString() ?? 'Error inesperado (${respuesta.statusCode})';
    } catch (_) {
      return 'Error inesperado (${respuesta.statusCode})';
    }
  }
}
