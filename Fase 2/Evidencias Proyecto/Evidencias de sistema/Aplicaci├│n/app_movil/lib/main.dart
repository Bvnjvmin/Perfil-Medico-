import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const PerfilMedicoApp());
}

class PerfilMedicoApp extends StatelessWidget {
  const PerfilMedicoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Perfil Médico+',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF2E7D6B),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}
