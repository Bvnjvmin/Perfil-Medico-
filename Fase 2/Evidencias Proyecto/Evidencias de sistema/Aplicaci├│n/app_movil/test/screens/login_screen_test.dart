import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app_movil/screens/login_screen.dart';

void main() {
  testWidgets('Muestra errores de validación si se envía el formulario vacío',
      (tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));

    await tester.tap(find.text('Entrar'));
    await tester.pump();

    expect(find.text('Ingresa un correo válido'), findsOneWidget);
    expect(find.text('Mínimo 8 caracteres'), findsOneWidget);
  });
}
