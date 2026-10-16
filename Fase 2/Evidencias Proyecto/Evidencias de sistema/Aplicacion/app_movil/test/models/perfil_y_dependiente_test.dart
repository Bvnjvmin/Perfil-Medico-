import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/models/medicamento.dart';
import 'package:app_movil/models/perfil.dart';
import 'package:app_movil/models/rutina_cuidado.dart';
import 'package:app_movil/screens/perfil_screen.dart';

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
    expect(perfil.esTitular, isTrue);
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

  test('Perfil.fromJson parsea tipo, subtipo, activo y mi_acceso (HU 6 y HU 7)', () {
    final perfil = Perfil.fromJson({
      'id': 'dep-10',
      'nombre': 'Abuelita Rosa',
      'tipo': 'dependiente',
      'subtipo': 'Adulto mayor',
      'activo': true,
      'mi_acceso': {
        'rol': 'cuidador',
        'puede_confirmar': true,
        'puede_editar_rutinas': false,
      },
    });

    expect(perfil.id, 'dep-10');
    expect(perfil.nombre, 'Abuelita Rosa');
    expect(perfil.esDependiente, isTrue);
    expect(perfil.subtipo, 'Adulto mayor');
    expect(perfil.puedeConfirmar, isTrue);
    expect(perfil.puedeEditarRutinas, isFalse);
    expect(perfil.esPropio, isFalse);
  });

  testWidgets('Formulario de dependiente valida que el subtipo sea obligatorio (HU 6)',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: PerfilScreen(
          token: 'token-prueba',
          esDependiente: true,
        ),
      ),
    );

    await tester.enterText(
      find.byType(TextFormField).first,
      'Pedrito Pizarro',
    );
    await tester.tap(find.text('Crear perfil'));
    await tester.pump();

    expect(find.text('Selecciona un subtipo'), findsOneWidget);
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
