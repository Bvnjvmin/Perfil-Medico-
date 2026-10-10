import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/models/medicamento.dart';
import 'package:app_movil/models/perfil.dart';
import 'package:app_movil/models/rutina_cuidado.dart';

void main() {
  test('Perfil.fromJson lee los campos opcionales y la fecha de nacimiento', () {
    final perfil = Perfil.fromJson({
      'id': 'p1',
      'nombre': 'Ana Cuidadora',
      'rut': '12.345.678-9',
      'grupo_sanguineo': 'O+',
      'fecha_nacimiento': '1990-05-20',
    });

    expect(perfil.nombre, 'Ana Cuidadora');
    expect(perfil.grupoSanguineo, 'O+');
    expect(perfil.fechaNacimiento?.year, 1990);
  });

  test('Perfil.fromJson acepta campos opcionales nulos', () {
    final perfil = Perfil.fromJson({
      'id': 'p1',
      'nombre': 'Ana',
      'rut': null,
      'grupo_sanguineo': null,
      'fecha_nacimiento': null,
    });

    expect(perfil.rut, isNull);
    expect(perfil.fechaNacimiento, isNull);
  });

  test('Medicamento.fromJson construye desde la respuesta del backend', () {
    final m = Medicamento.fromJson({
      'id': 'm1',
      'perfil_id': 'p1',
      'nombre': 'Paracetamol',
      'dosis': '500 mg',
      'frecuencia': 'cada 8 horas',
      'hora_inicio': '08:00:00',
      'activo': true,
    });

    expect(m.nombre, 'Paracetamol');
    expect(m.horaInicio, '08:00:00');
    expect(m.activo, isTrue);
  });

  test('RutinaCuidado usa la descripción como título y el tipo legible', () {
    final conDescripcion = RutinaCuidado.fromJson({
      'id': 'r1',
      'perfil_id': 'p1',
      'tipo': 'hidratacion',
      'descripcion': 'Tomar un vaso de agua',
      'frecuencia': '3 veces al día',
      'hora': null,
      'activo': true,
    });
    final sinDescripcion = RutinaCuidado.fromJson({
      'id': 'r2',
      'perfil_id': 'p1',
      'tipo': 'alimentacion',
      'descripcion': null,
      'frecuencia': '3 veces al día',
      'hora': '13:00:00',
      'activo': true,
    });

    expect(conDescripcion.titulo, 'Tomar un vaso de agua');
    expect(conDescripcion.tipoLegible, 'Hidratación');
    expect(sinDescripcion.titulo, 'Alimentación');
  });
}