import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/models/actividad.dart';
import 'package:app_movil/models/perfil.dart';
import 'package:app_movil/screens/panel_screen.dart';

void main() {
  group('Pruebas de Actividad y Panel (M3 y M5)', () {
    test('Actividad.fromJson parsea todos los campos del contrato', () {
      final json = {
        'id': '101',
        'perfil_id': '2',
        'fecha': '2026-10-14',
        'origen_tipo': 'medicamento',
        'origen_id': '5',
        'titulo': 'Losartán 50mg',
        'detalle': '1 comprimido',
        'hora': '08:00',
        'estado': 'confirmada',
        'confirmada_en': '2026-10-14T08:05:00',
        'confirmada_por_id': '1',
      };

      final actividad = Actividad.fromJson(json);

      expect(actividad.id, '101');
      expect(actividad.perfilId, '2');
      expect(actividad.origenTipo, 'medicamento');
      expect(actividad.titulo, 'Losartán 50mg');
      expect(actividad.estaConfirmada, isTrue);
      expect(actividad.confirmadaPorId, '1');
    });

    test('ResumenAvancePerfil cuenta correctamente confirmadas y pendientes', () {
      final perfil = Perfil(id: '2', nombre: 'Dependiente 1', tipo: 'dependiente');
      final actividades = [
        Actividad(
          id: '1',
          perfilId: '2',
          fecha: '2026-10-14',
          origenTipo: 'medicamento',
          origenId: '1',
          titulo: 'Med 1',
          hora: '08:00',
          estado: 'confirmada',
        ),
        Actividad(
          id: '2',
          perfilId: '2',
          fecha: '2026-10-14',
          origenTipo: 'rutina',
          origenId: '2',
          titulo: 'Caminata',
          hora: '10:00',
          estado: 'pendiente',
        ),
        Actividad(
          id: '3',
          perfilId: '2',
          fecha: '2026-10-14',
          origenTipo: 'medicamento',
          origenId: '3',
          titulo: 'Med 2',
          hora: '20:00',
          estado: 'confirmada',
        ),
      ];

      final resumen =
          AvancePerfil.desdeActividades(perfil, actividades);

      expect(resumen.confirmadas, 2);
      expect(resumen.pendientes, 1);
      expect(resumen.total, 3);
      expect(resumen.resumenTexto, '2 de 3 confirmadas');
    });
  });
}
