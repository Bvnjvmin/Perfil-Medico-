import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/models/sprint5.dart';

void main() {
  test('EventoSeguridad.fromJson lee el evento y marca los urgentes', () {
    final evento = EventoSeguridad.fromJson({
      'id': 'e1',
      'perfil_id': 'p1',
      'perfil_nombre': 'Abuela',
      'tipo': 'sos',
      'origen': 'pulsera',
      'mensaje': 'La pulsera de Abuela registró que se presionó el botón SOS.',
      'creado_en': '2026-11-05T21:39:02-03:00',
      'atendido_en': null,
    });

    expect(evento.titulo, 'Botón SOS');
    expect(evento.esUrgente, isTrue);
    expect(evento.atendido, isFalse);
  });

  test('Un evento con atendido_en se considera atendido y bajo batería no es urgente', () {
    final evento = EventoSeguridad.fromJson({
      'id': 'e2',
      'perfil_id': 'p1',
      'perfil_nombre': 'Abuela',
      'tipo': 'bateria_baja',
      'origen': 'pulsera',
      'mensaje': 'Batería baja',
      'creado_en': '2026-11-05T21:39:02-03:00',
      'atendido_en': '2026-11-05T22:00:00-03:00',
    });

    expect(evento.atendido, isTrue);
    expect(evento.esUrgente, isFalse);
  });

  test('Indicador acepta el valor como texto y arma el texto de la presión', () {
    final presion = Indicador.fromJson({
      'id': 'i1',
      'tipo': 'presion',
      'valor': '128.00',
      'valor_secundario': '82.00',
      'unidad': 'mmHg',
      'fuente': 'manual',
      'medido_en': '2026-11-05T10:00:00-03:00',
    });
    final peso = Indicador.fromJson({
      'id': 'i2',
      'tipo': 'peso',
      'valor': 68.5,
      'unidad': 'kg',
      'fuente': 'manual',
      'medido_en': '2026-11-05T10:00:00-03:00',
    });

    expect(presion.texto, '128/82 mmHg');
    expect(peso.texto, '68.5 kg');
  });

  test('Cumplimiento.fromJson lee las categorías, los días y un porcentaje nulo', () {
    final c = Cumplimiento.fromJson({
      'total': 10,
      'cumplidas': 8,
      'porcentaje': 80.0,
      'por_categoria': {
        'medicamentos': {'total': 6, 'cumplidas': 6, 'porcentaje': 100.0},
        'hidratacion': {'total': 0, 'cumplidas': 0, 'porcentaje': null},
      },
      'por_dia': [
        {'fecha': '2026-11-04', 'total': 5, 'cumplidas': 4, 'porcentaje': 80.0},
        {'fecha': '2026-11-05', 'total': 0, 'cumplidas': 0, 'porcentaje': null},
      ],
    });

    expect(c.porcentaje, 80.0);
    expect(c.porCategoria['medicamentos']!.cumplidas, 6);
    expect(c.porCategoria['hidratacion']!.porcentaje, isNull);
    expect(c.porDia.length, 2);
    expect(c.porDia.first.fecha?.day, 4);
    expect(Cumplimiento.nombreDeCategoria('hidratacion'), 'Hidratación');
  });

  test('Ubicacion.fromJson acepta un perfil sin pulsera ni posición', () {
    final u = Ubicacion.fromJson({
      'perfil_id': 'p1',
      'pulsera': null,
      'posicion': null,
      'dentro_de': [],
    });

    expect(u.pulsera, isNull);
    expect(u.posicion, isNull);
    expect(u.dentroDe, isEmpty);
  });

  test('ConsultaIA marca como urgencia la respuesta fija y trae el aviso', () {
    final c = ConsultaIA.fromJson({
      'id': 'c1',
      'pregunta': 'Me duele el pecho',
      'respuesta': 'Llama al 131.',
      'proveedor': 'reglas',
      'creada_en': '2026-11-05T21:00:00-03:00',
    });

    expect(c.esUrgencia, isTrue);
    expect(c.aviso, contains('131'));
  });
}
