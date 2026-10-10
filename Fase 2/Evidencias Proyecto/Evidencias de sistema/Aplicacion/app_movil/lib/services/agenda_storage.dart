import 'package:shared_preferences/shared_preferences.dart';
import '../utils/hora.dart';

/// Guarda en el celular qué actividades de la agenda se confirmaron cada día.
///
/// Decisión de alcance del Sprint 2: el backend todavía no tiene la tabla
/// ACTIVIDAD ni un endpoint de confirmar (quedan para el Sprint 3), así que
/// la confirmación vive solo en el dispositivo, separada por perfil y por día.
class AgendaStorage {
  String _clave(String perfilId, DateTime dia) =>
      'agenda_confirmadas_${perfilId}_${fechaParaApi(dia)}';

  Future<Set<String>> cargar(String perfilId, DateTime dia) async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_clave(perfilId, dia)) ?? <String>[]).toSet();
  }

  Future<void> guardar(
    String perfilId,
    DateTime dia,
    Set<String> confirmadas,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_clave(perfilId, dia), confirmadas.toList());
  }
}