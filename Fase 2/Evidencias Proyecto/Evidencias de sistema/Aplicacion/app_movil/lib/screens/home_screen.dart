import 'package:flutter/material.dart';
import '../models/perfil.dart';
import '../models/usuario.dart';
import '../services/api_service.dart';
import '../services/token_storage.dart';
import 'agenda_screen.dart';
import 'alergias_screen.dart';
import 'alertas_screen.dart';
import 'compartir_perfil_screen.dart';
import 'contactos_emergencia_screen.dart';
import 'login_screen.dart';
import 'medicamentos_screen.dart';
import 'mis_perfiles_screen.dart';
import 'modo_simplificado_screen.dart';
import 'panel_screen.dart';
import 'perfil_screen.dart';
import 'rutinas_screen.dart';

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
  List<Perfil> _perfiles = [];
  Perfil? _perfilActivo;

  Perfil? get _perfilTitular {
    for (final p in _perfiles) {
      if (p.esTitular && p.esPropio) return p;
    }
    for (final p in _perfiles) {
      if (p.esTitular) return p;
    }
    return null;
  }

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

      List<Perfil> perfiles = [];
      try {
        perfiles = await _api.listarPerfiles(token);
      } catch (_) {
        perfiles = [];
      }

      if (!mounted) return;
      setState(() {
        _token = token;
        _usuario = usuario;
        _perfiles = perfiles;
        _sincronizarPerfilActivo();
      });
    } catch (e) {
      await _tokenStorage.borrar();
      _volverALogin();
    }
  }

  void _sincronizarPerfilActivo() {
    if (_perfiles.isEmpty) {
      _perfilActivo = null;
      return;
    }
    if (_perfilActivo != null) {
      final coincidencia =
          _perfiles.where((p) => p.id == _perfilActivo!.id).toList();
      if (coincidencia.isNotEmpty) {
        _perfilActivo = coincidencia.first;
        return;
      }
    }
    _perfilActivo = _perfilTitular ?? _perfiles.first;
  }

  Future<void> _recargarPerfiles() async {
    if (_token == null) return;
    try {
      final perfiles = await _api.listarPerfiles(_token!);
      if (!mounted) return;
      setState(() {
        _perfiles = perfiles;
        _sincronizarPerfilActivo();
      });
    } catch (_) {}
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
    final titular = _perfilTitular;
    final resultado = await Navigator.of(context).push<Perfil>(
      MaterialPageRoute(
        builder: (_) => PerfilScreen(token: _token!, perfil: titular),
      ),
    );
    if (resultado != null && mounted) {
      await _recargarPerfiles();
    }
  }

  Future<void> _abrirMisPerfiles() async {
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => MisPerfilesScreen(token: _token!),
      ),
    );
    await _recargarPerfiles();
  }

  Future<void> _abrirPanel() async {
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => PanelScreen(token: _token!),
      ),
    );
    await _recargarPerfiles();
  }

  Future<void> _abrirAlertas() async {
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => AlertasScreen(token: _token!, perfiles: _perfiles),
      ),
    );
  }

  void _abrirModoSimplificado() {
    final perfil = _perfilActivo;
    if (perfil == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Primero completa tu perfil de salud.')),
      );
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ModoSimplificadoScreen(token: _token!, perfil: perfil),
      ),
    );
  }

  void _abrirConPerfil(
      Widget Function(String token, Perfil perfil) construir) {
    final perfil = _perfilActivo;
    if (perfil == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Primero completa tu perfil de salud.')),
      );
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => construir(_token!, perfil)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final usuario = _usuario;
    final titular = _perfilTitular;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil Médico+'),
        actions: [
          IconButton(
            onPressed: _token == null ? null : _abrirAlertas,
            icon: const Icon(Icons.notifications_none),
            tooltip: 'Avisos',
          ),
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
                    const CircleAvatar(
                        radius: 40, child: Icon(Icons.person, size: 40)),
                    const SizedBox(height: 12),
                    Text(
                      usuario.nombre,
                      style: const TextStyle(
                          fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    Text(usuario.email),
                  ],
                ),
                const SizedBox(height: 24),
                if (_perfiles.isNotEmpty) ...[
                  DropdownButtonFormField<String>(
                    key: ValueKey(_perfilActivo?.id),
                    initialValue: _perfilActivo?.id,
                    decoration: const InputDecoration(
                      labelText: 'Perfil con el que se trabaja',
                      prefixIcon: Icon(Icons.switch_account),
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      for (final p in _perfiles)
                        DropdownMenuItem(
                          value: p.id,
                          child: Text(
                            p.esTitular
                                ? '${p.nombre} (Titular)'
                                : '${p.nombre} (${p.subtipo ?? "Dependiente"})',
                          ),
                        ),
                    ],
                    onChanged: (id) {
                      if (id == null) return;
                      setState(() {
                        _perfilActivo =
                            _perfiles.firstWhere((p) => p.id == id);
                      });
                    },
                  ),
                  const SizedBox(height: 16),
                ],
                ListTile(
                  leading: const Icon(Icons.badge_outlined),
                  title: const Text('Mi perfil de salud'),
                  subtitle: Text(
                      titular == null ? 'Aún no lo completas' : titular.nombre),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _abrirPerfil,
                ),
                ListTile(
                  leading: const Icon(Icons.group_outlined),
                  title: const Text('Mis perfiles'),
                  subtitle: const Text('Titular y dependientes'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _abrirMisPerfiles,
                ),
                ListTile(
                  leading: const Icon(Icons.dashboard_outlined),
                  title: const Text('Panel'),
                  subtitle: const Text('Avance diario de cada perfil'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _abrirPanel,
                ),
                ListTile(
                  leading: const Icon(Icons.accessibility_new),
                  title: const Text('Modo simplificado'),
                  subtitle: const Text(
                      'Pantalla con letra y botones grandes para el perfil activo'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _abrirModoSimplificado,
                ),
                const Divider(),
                ListTile(
                  leading: const Icon(Icons.medication),
                  title: const Text('Medicamentos'),
                  subtitle: _perfilActivo != null
                      ? Text('Activo: ${_perfilActivo!.nombre}')
                      : null,
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfil) => MedicamentosScreen(
                      token: token,
                      perfilId: perfil.id,
                      puedeEditar: perfil.puedeEditarRutinas,
                    ),
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.favorite_border),
                  title: const Text('Rutinas de cuidado'),
                  subtitle: _perfilActivo != null
                      ? Text('Activo: ${_perfilActivo!.nombre}')
                      : null,
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfil) => RutinasScreen(
                      token: token,
                      perfilId: perfil.id,
                      puedeEditar: perfil.puedeEditarRutinas,
                    ),
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.today),
                  title: const Text('Agenda de hoy'),
                  subtitle: _perfilActivo != null
                      ? Text('Activo: ${_perfilActivo!.nombre}')
                      : null,
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfil) => AgendaScreen(
                      token: token,
                      perfilId: perfil.id,
                      puedeConfirmar: perfil.puedeConfirmar,
                    ),
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.warning_amber_rounded),
                  title: const Text('Alergias'),
                  subtitle: _perfilActivo != null
                      ? Text('Activo: ${_perfilActivo!.nombre}')
                      : null,
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfil) => AlergiasScreen(
                      token: token,
                      perfilId: perfil.id,
                      puedeEditar: !perfil.esSoloLectura,
                    ),
                  ),
                ),
                ListTile(
                  leading: const Icon(Icons.contact_phone_outlined),
                  title: const Text('Contactos de emergencia'),
                  subtitle: _perfilActivo != null
                      ? Text('Activo: ${_perfilActivo!.nombre}')
                      : null,
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _abrirConPerfil(
                    (token, perfil) => ContactosEmergenciaScreen(
                      token: token,
                      perfilId: perfil.id,
                      puedeEditar: !perfil.esSoloLectura,
                    ),
                  ),
                ),
                if (_perfilActivo == null || _perfilActivo!.esPropio)
                  ListTile(
                    leading: const Icon(Icons.share_outlined),
                    title: const Text('Compartir perfil'),
                    subtitle: const Text('Invitar a un cuidador por correo'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => _abrirConPerfil(
                      (token, perfil) => CompartirPerfilScreen(
                        token: token,
                        perfil: perfil,
                      ),
                    ),
                  ),
              ],
            ),
    );
  }
}
