import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/models/actividad.dart';
import 'package:app_movil/models/alerta.dart';
import 'package:app_movil/screens/panel_screen.dart';

void main() {
  group('Alerta.fromJson (HU 9 y HU 10)', () {
    test('lee un recordatorio sin leer', () {
      final a = Alerta.fromJson({
        'id': 'a1',
        'perfil_id': 'p1',
        'actividad_id': 'x1',
        'tipo': 'recordatorio',
        'nivel': 0,
        'mensaje': 'En 10 minutos: Losartán',
        'creada_en': '2026-10-22T08:20:00Z',
        'leida_en': null,
      });
      expect(a.esAlerta, isFalse);
      expect(a.estaLeida, isFalse);
      expect(a.nivel, 0);
      expect(a.perfilId, 'p1');
    });

    test('lee una alerta escalonada ya leída', () {
      final a = Alerta.fromJson({
        'id': 'a2',
        'perfil_id': 'p1',
        'actividad_id': 'x1',
        'tipo': 'alerta',
        'nivel': 2,
        'mensaje': 'No se confirmó: Losartán',
        'creada_en': '2026-10-22T09:30:00Z',
        'leida_en': '2026-10-22T09:35:00Z',
      });
      expect(a.esAlerta, isTrue);
      expect(a.estaLeida, isTrue);
      expect(a.nivel, 2);
    });
  });

  group('Actividad con estado vencida', () {
    test('estaVencida solo es verdadera para vencida', () {
      Actividad con(String estado) => Actividad(
            id: '1',
            perfilId: 'p1',
            fecha: '2026-10-22',
            origenTipo: 'medicamento',
            origenId: 'm1',
            titulo: 'Losartán',
            hora: '08:00:00',
            estado: estado,
          );
      expect(con('vencida').estaVencida, isTrue);
      expect(con('pendiente').estaVencida, isFalse);
      expect(con('confirmada').estaConfirmada, isTrue);
    });
  });

  group('AvancePerfil.desdePanel (HU 8)', () {
    test('usa los totales que envía GET /panel', () {
      final item = AvancePerfil.desdePanel({
        'perfil': {
          'id': 'p1',
          'nombre': 'Abuela Rosa',
          'tipo': 'dependiente',
          'subtipo': 'adulto_mayor',
        },
        'mi_acceso': {
          'rol': 'cuidador',
          'puede_confirmar': true,
          'puede_editar_rutinas': false,
        },
        'total': 4,
        'confirmadas': 1,
        'pendientes': 3,
      });
      expect(item.perfil.nombre, 'Abuela Rosa');
      expect(item.perfil.subtipo, 'Adulto mayor');
      expect(item.perfil.puedeConfirmar, isTrue);
      expect(item.perfil.puedeEditarRutinas, isFalse);
      expect(item.resumenTexto, '1 de 4 confirmadas');
      expect(item.progreso, closeTo(0.25, 1e-9));
    });
  });
}
