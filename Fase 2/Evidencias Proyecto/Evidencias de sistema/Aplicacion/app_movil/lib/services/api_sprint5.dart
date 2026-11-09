import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/sprint5.dart';
import 'api_service.dart' show ApiException, ApiService;

/// Llamadas del Sprint 5 al backend (ver `Contrato_API_Sprint5.md`).
///
/// Vive en un archivo aparte para no tocar `api_service.dart`; reutiliza su dirección
/// base y su excepción. Todas las funciones reciben el token del usuario.
class ApiSprint5 {
  static const _limite = Duration(seconds: 15);
  static const _json = {'Content-Type': 'application/json'};

  Map<String, String> _auth(String token, {bool json = false}) => {
        'Authorization': 'Bearer $token',
        if (json) ..._json,
      };

  Uri _uri(String ruta, [Map<String, String>? consulta]) =>
      Uri.parse('${ApiService.baseUrl}$ruta').replace(queryParameters: consulta);

  Future<http.Response> _enviar(Future<http.Response> Function() peticion) async {
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

  dynamic _decodificar(http.Response r) => jsonDecode(utf8.decode(r.bodyBytes));

  List<T> _lista<T>(http.Response r, T Function(Map<String, dynamic>) desde) =>
      (_decodificar(r) as List).map((e) => desde(e as Map<String, dynamic>)).toList();

  /// Mensaje legible a partir del `detail` de FastAPI.
  String _detalle(http.Response r) {
    try {
      final detalle = _decodificar(r)['detail'];
      if (detalle is List) {
        final mensajes = detalle
            .map((e) => e is Map ? (e['msg'] ?? '').toString() : e.toString())
            .where((m) => m.isNotEmpty)
            .toList();
        if (mensajes.isNotEmpty) return mensajes.join('\n');
      } else if (detalle != null) {
        return detalle.toString();
      }
    } catch (_) {}
    return 'Error inesperado (${r.statusCode})';
  }

  bool _ok(http.Response r, [List<int> codigos = const [200, 201, 204]]) =>
      codigos.contains(r.statusCode);

  // --- Botón de asistencia y eventos (HU 14 y HU 19) ----------------------

  /// POST /perfiles/{id}/asistencia. Devuelve el evento (201 nuevo, 200 si ya
  /// había uno reciente: pulsar varias veces no duplica el aviso).
  Future<EventoSeguridad> pedirAyuda(String token, String perfilId, {String? mensaje}) async {
    final r = await _enviar(() => http.post(
          _uri('/perfiles/$perfilId/asistencia'),
          headers: _auth(token, json: true),
          body: jsonEncode({if (mensaje != null && mensaje.trim().isNotEmpty) 'mensaje': mensaje.trim()}),
        ));
    if (_ok(r, [200, 201])) return EventoSeguridad.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  Future<List<EventoSeguridad>> listarEventos(String token, {bool soloPendientes = false}) async {
    final r = await _enviar(() => http.get(
          _uri('/eventos', {'solo_pendientes': '$soloPendientes'}),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return _lista(r, EventoSeguridad.fromJson);
    throw ApiException(_detalle(r));
  }

  Future<EventoSeguridad> marcarAtendido(String token, String eventoId) async {
    final r = await _enviar(() => http.post(
          _uri('/eventos/$eventoId/atendido'),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return EventoSeguridad.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  // --- Indicadores (HU 12 y HU 18) ----------------------------------------

  Future<List<Indicador>> ultimosIndicadores(String token, String perfilId) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/indicadores/ultimos'),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) {
      return ((_decodificar(r)['ultimos'] as List?) ?? [])
          .map((e) => Indicador.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw ApiException(_detalle(r));
  }

  Future<List<Indicador>> listarIndicadores(String token, String perfilId, {String? tipo}) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/indicadores', {if (tipo != null) 'tipo': tipo}),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return _lista(r, Indicador.fromJson);
    throw ApiException(_detalle(r));
  }

  /// En la presión, [valor] es la sistólica y [valorSecundario] la diastólica.
  Future<Indicador> registrarIndicador(
    String token,
    String perfilId, {
    required String tipo,
    required double valor,
    double? valorSecundario,
    String? nota,
  }) async {
    final r = await _enviar(() => http.post(
          _uri('/perfiles/$perfilId/indicadores'),
          headers: _auth(token, json: true),
          body: jsonEncode({
            'tipo': tipo,
            'valor': valor,
            if (valorSecundario != null) 'valor_secundario': valorSecundario,
            if (nota != null && nota.trim().isNotEmpty) 'nota': nota.trim(),
          }),
        ));
    if (_ok(r, [201, 200])) return Indicador.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  Future<void> eliminarIndicador(String token, String perfilId, String indicadorId) async {
    final r = await _enviar(() => http.delete(
          _uri('/perfiles/$perfilId/indicadores/$indicadorId'),
          headers: _auth(token),
        ));
    if (_ok(r)) return;
    throw ApiException(_detalle(r));
  }

  Future<SerieIndicador> serieIndicador(String token, String perfilId,
      {required String tipo, int dias = 30}) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/indicadores/serie', {'tipo': tipo, 'dias': '$dias'}),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return SerieIndicador.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  // --- Cumplimiento (HU 13) ------------------------------------------------

  /// Por defecto, los últimos 7 días. El máximo es de 92 días.
  Future<Cumplimiento> cumplimiento(String token, String perfilId,
      {DateTime? desde, DateTime? hasta}) async {
    String f(DateTime d) =>
        '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/cumplimiento', {
            if (desde != null) 'desde': f(desde),
            if (hasta != null) 'hasta': f(hasta),
          }),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return Cumplimiento.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  // --- Pulsera, ubicación y geocercas (HU 17) -----------------------------

  Future<List<Pulsera>> listarPulseras(String token, String perfilId) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/pulseras'),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return _lista(r, Pulsera.fromJson);
    throw ApiException(_detalle(r));
  }

  Future<Pulsera> registrarPulsera(String token, String perfilId,
      {required String identificador, required String nombre, String? modelo}) async {
    final r = await _enviar(() => http.post(
          _uri('/perfiles/$perfilId/pulseras'),
          headers: _auth(token, json: true),
          body: jsonEncode({
            'identificador': identificador.trim(),
            'nombre': nombre.trim(),
            if (modelo != null && modelo.trim().isNotEmpty) 'modelo': modelo.trim(),
          }),
        ));
    if (_ok(r, [201, 200])) return Pulsera.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  Future<void> eliminarPulsera(String token, String perfilId, String pulseraId) async {
    final r = await _enviar(() => http.delete(
          _uri('/perfiles/$perfilId/pulseras/$pulseraId'),
          headers: _auth(token),
        ));
    if (_ok(r)) return;
    throw ApiException(_detalle(r));
  }

  Future<Ubicacion> ubicacion(String token, String perfilId) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/ubicacion'),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return Ubicacion.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  Future<List<Geocerca>> listarGeocercas(String token, String perfilId) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/geocercas'),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return _lista(r, Geocerca.fromJson);
    throw ApiException(_detalle(r));
  }

  Future<Geocerca> crearGeocerca(String token, String perfilId,
      {required String nombre,
      required double latitud,
      required double longitud,
      required int radioM}) async {
    final r = await _enviar(() => http.post(
          _uri('/perfiles/$perfilId/geocercas'),
          headers: _auth(token, json: true),
          body: jsonEncode({
            'nombre': nombre.trim(),
            'latitud': latitud,
            'longitud': longitud,
            'radio_m': radioM,
          }),
        ));
    if (_ok(r, [201, 200])) return Geocerca.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  Future<void> eliminarGeocerca(String token, String perfilId, String geocercaId) async {
    final r = await _enviar(() => http.delete(
          _uri('/perfiles/$perfilId/geocercas/$geocercaId'),
          headers: _auth(token),
        ));
    if (_ok(r)) return;
    throw ApiException(_detalle(r));
  }

  // --- Asistente de IA (HU 15) --------------------------------------------

  /// 429 si se pasó del tope diario; 503 si el asistente no está disponible.
  Future<ConsultaIA> preguntarIA(String token, String perfilId, String pregunta) async {
    final r = await _enviar(() => http.post(
          _uri('/perfiles/$perfilId/ia/consultas'),
          headers: _auth(token, json: true),
          body: jsonEncode({'pregunta': pregunta.trim()}),
        ));
    if (_ok(r, [201, 200])) return ConsultaIA.fromJson(_decodificar(r));
    throw ApiException(_detalle(r));
  }

  Future<List<ConsultaIA>> historialIA(String token, String perfilId) async {
    final r = await _enviar(() => http.get(
          _uri('/perfiles/$perfilId/ia/consultas'),
          headers: _auth(token),
        ));
    if (_ok(r, [200])) return _lista(r, ConsultaIA.fromJson);
    throw ApiException(_detalle(r));
  }
}
