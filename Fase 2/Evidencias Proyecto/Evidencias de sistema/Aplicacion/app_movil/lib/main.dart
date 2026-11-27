import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'services/notificaciones_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Prepara Firebase para las notificaciones push. Si el proyecto de Firebase no está
  // configurado (falta google-services.json), la app sigue funcionando sin push.
  await NotificacionesService.instance.iniciarFirebase();
  runApp(const PerfilMedicoApp());
}

class PerfilMedicoApp extends StatelessWidget {
  const PerfilMedicoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Perfil Médico+',
      // Permite mostrar un aviso encima de cualquier pantalla cuando llega una
      // notificación con la app abierta.
      scaffoldMessengerKey: NotificacionesService.mensajeroKey,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF2E7D6B),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}
