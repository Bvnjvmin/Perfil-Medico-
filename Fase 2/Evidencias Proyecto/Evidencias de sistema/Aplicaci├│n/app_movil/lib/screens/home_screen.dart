import 'package:flutter/material.dart';
import '../models/usuario.dart';
import '../services/api_service.dart';
import '../services/token_storage.dart';
import 'login_screen.dart';

/// Pantalla protegida: solo se puede ver con un token válido.
/// Al entrar, pide el token guardado y llama a GET /auth/me. Si no hay
/// token o el backend lo rechaza (401), vuelve directo al login.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _api = ApiService();
  final _tokenStorage = TokenStorage();

  Usuario? _usuario;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarUsuario();
  }

  Future<void> _cargarUsuario() async {
    final token = await _tokenStorage.obtener();
    if (token == null) {
      _volverALogin();
      return;
    }

    try {
      final usuario = await _api.obtenerUsuarioActual(token);
      setState(() => _usuario = usuario);
    } catch (e) {
      // Token vencido o inválido: se limpia y se vuelve al login.
      await _tokenStorage.borrar();
      _volverALogin();
    }
  }

  void _volverALogin() {
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  Future<void> _cerrarSesion() async {
    await _tokenStorage.borrar();
    _volverALogin();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mi perfil'),
        actions: [
          IconButton(
            onPressed: _cerrarSesion,
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
          ),
        ],
      ),
      body: Center(
        child: _usuario == null
            ? const CircularProgressIndicator()
            : Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const CircleAvatar(radius: 40, child: Icon(Icons.person, size: 40)),
                    const SizedBox(height: 16),
                    Text(_usuario!.nombre, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    Text(_usuario!.email),
                    const SizedBox(height: 8),
                    Chip(label: Text(_usuario!.rol.toUpperCase())),
                  ],
                ),
              ),
      ),
    );
  }
}
