import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:app_movil/models/actividad_agenda.dart';
import 'package:app_movil/models/medicamento.dart';
import 'package:app_movil/models/rutina_cuidado.dart';
import 'package:app_movil/services/agenda_storage.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Medicamento med(String id, String nombre, String? hora, {bool activo = true}) =>
      Medicamento(
        id: id,
        perfilId: 'p1',
        nombre: nombre,
        dosis: '500 mg',
        frecuencia: 'cada 8 horas',
        horaInicio: hora,
        activo: activo,
      );

  RutinaCuidado rutina(String id, String tipo, String? hora) => RutinaCuidado(
        id: id,
        perfilId: 'p1',
        tipo: tipo,
        frecuencia: '3 veces al día',
        hora: hora,
        activo: true,
      );

  test('construirAgenda ordena por hora, deja sin hora al final y omite inactivos', () {
    final agenda = construirAgenda(
      [
        med('m1', 'Paracetamol', '20:00:00'),
        med('m2', 'Antiguo', '07:00:00', activo: false),
        med('m3', 'Vitamina D', null),
      ],
      [rutina('r1', 'hidratacion', '08:00:00')],
    );

    expect(agenda.map((a) => a.clave).toList(), ['rut:r1', 'med:m1', 'med:m3']);
    expect(agenda.first.tipo, TipoActividad.rutina);
  });

  test('AgendaStorage guarda las confirmaciones por perfil y por día', () async {
    SharedPreferences.setMockInitialValues({});
    final storage = AgendaStorage();
    final dia = DateTime(2026, 10, 8);

    await storage.guardar('p1', dia, {'med:m1', 'rut:r1'});

    expect(await storage.cargar('p1', dia), {'med:m1', 'rut:r1'});
    expect(await storage.cargar('p1', DateTime(2026, 10, 9)), isEmpty);
    expect(await storage.cargar('otro-perfil', dia), isEmpty);
  });
}