import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/models/usuario.dart';

void main() {
  test('Usuario.fromJson construye correctamente desde la respuesta del backend', () {
    final json = {
      'id': 'abc-123',
      'nombre': 'Ana Cuidadora',
      'email': 'ana@perfilmedico.cl',
      'creado_en': '2026-01-15T10:30:00+00:00',
    };

    final usuario = Usuario.fromJson(json);

    expect(usuario.id, 'abc-123');
    expect(usuario.nombre, 'Ana Cuidadora');
    expect(usuario.email, 'ana@perfilmedico.cl');
    expect(usuario.creadoEn.year, 2026);
  });
}
