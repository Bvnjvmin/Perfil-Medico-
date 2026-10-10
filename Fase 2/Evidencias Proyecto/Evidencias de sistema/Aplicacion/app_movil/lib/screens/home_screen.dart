import 'package:flutter/material.dart';
import '../models/perfil.dart';
import '../models/usuario.dart';
import '../services/api_service.dart';
import '../services/token_storage.dart';
import 'agenda_screen.dart';
import 'login_screen.dart';
import 'medicamentos_screen.dart';
import 'perfil_screen.dart';
import 'rutinas_screen.dart';

/// Pantalla protegida: solo se puede ver con un token válido.
/// Al entrar, pide el token guardado y llama a GET /auth/me. Si no hay
/// token o el backend lo rechaza (401), vuelve directo al login.
/// Desde aquí se accede al perfil de salud, medicamentos, rutinas y agenda.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _api = ApiService();
  final _tokenStorage = TokenStorage();

  String? _token;
  Usuario? _usuario;
  Perfil? _perfil;

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

      // Si falla la carga del perfil no se cierra la sesión: se muestra sin perfil.
      Perfil? perfil;
      try {
        final perfiles = await _api.listarPerfiles(token);
        perfil = perfiles.isEmpty ? null : perfiles.first;
      } catch (_) {
        perfil = null;
      }

      if (!mounted) return;
      setState(() {
        _token = token;
        _usuario = usuario;
        _perfil = perfil;
      });
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

  Future<void> _abrirPerfil() async {
    final resultado = await Navigator.of(context).push<Perfil>(
      MaterialPageRoute(
        builder: (_) => PerfilScreen(token: _token!, perfil: _perfil),
      ),
    );
    if (resultado != null && mounted) setState(() => _perfil = resultado);
  }

  /// Medicamentos, rutinas y agenda cuelgan del perfil: sin perfil no se abren.
  void _abrirConPerfil(Widget Function(String token, String perfilId) construir) {
    final perfil = _perfil;
    if (perfil == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Primero completa tu perfil de salud.')),
      );
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => construir(_token!, perfil.id)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final usuario = _usuario;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil Médico+'),
        actions: [
          IconButton(
            onPressed: _cerrarSesion,
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
          ),
        ],
      ),
      body: usuario == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Column(
                  children: [
                    const CircleAvatar(radius: 40, child: Icon(Icons.person, size: 40)),
                    const SizedBox(height: 12),
                    Text(
                      usuario.nombre,
                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    Text(usuario.email),
                  ],
                ),
                const SizedBox(height: 24),
                ListTile(
                  leading: const Icon(Icons.badge_outlined),
                  title: const Text('Mi perfil de salud'),
                  subtitle: Text(_perfil == null ? 'Aún no lo completas' : _perfil!.nombre),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _abrirPerfil,
                ),
                ListTile(
                  leading: const Icon(Icons.medication),
                  title: const Text('Medicamentos'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfilId) => MedicamentosScreen(token: token, perfilId: perfilId),
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.favorite_border),
                  title: const Text('Rutinas de cuidado'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfilId) => RutinasScreen(token: token, perfilId: perfilId),
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.today),
                  title: const Text('Agenda de hoy'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfilId) => AgendaScreen(token: token, perfilId: perfilId),
                  ),
                ),
              ],
            ),
    );
  }
}
