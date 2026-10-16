import 'package:flutter/material.dart';
import '../models/perfil.dart';
import '../services/api_service.dart';
import 'perfil_screen.dart';

class MisPerfilesScreen extends StatefulWidget {
  final String token;

  const MisPerfilesScreen({super.key, required this.token});

  @override
  State<MisPerfilesScreen> createState() => _MisPerfilesScreenState();
}

class _MisPerfilesScreenState extends State<MisPerfilesScreen> {
  final _api = ApiService();
  List<Perfil>? _perfiles;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarPerfiles(widget.token);
      if (!mounted) return;
      setState(() {
        _perfiles = lista;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  void _mostrarMensaje(String texto) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(texto)));
  }

  Future<void> _agregarDependiente() async {
    final creado = await Navigator.of(context).push<Perfil>(
      MaterialPageRoute(
        builder: (_) => PerfilScreen(
          token: widget.token,
          esDependiente: true,
        ),
      ),
    );
    if (creado != null) await _cargar();
  }

  Future<void> _editarPerfil(Perfil p) async {
    final actualizado = await Navigator.of(context).push<Perfil>(
      MaterialPageRoute(
        builder: (_) => PerfilScreen(
          token: widget.token,
          perfil: p,
          esDependiente: p.esDependiente,
        ),
      ),
    );
    if (actualizado != null) await _cargar();
  }

  Future<void> _confirmarEliminar(Perfil p) async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar dependiente'),
        content: Text(
          '¿Eliminar el perfil de "${p.nombre}"? '
          'Se borrarán también todos sus medicamentos y rutinas.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );

    if (confirmar != true) return;

    try {
      await _api.eliminarPerfil(widget.token, p.id);
      if (!mounted) return;
      _mostrarMensaje('Perfil eliminado.');
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _perfiles;
    Widget cuerpo;

    if (_error != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: const TextStyle(color: Colors.red)),
        ),
      );
    } else if (lista == null) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else if (lista.isEmpty) {
      cuerpo = const Center(
        child: Text('Aún no tienes perfiles registrados.'),
      );
    } else {
      cuerpo = ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: lista.length,
        itemBuilder: (context, i) {
          final p = lista[i];
          final etiqueta = p.esPropio ? 'Tuyo' : 'Compartido contigo';
          final subtitulo = p.esTitular
              ? 'Titular · $etiqueta'
              : 'Dependiente (${p.subtipo ?? "Sin subtipo"}) · $etiqueta';

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                child: Icon(
                  p.esTitular ? Icons.person : Icons.family_restroom,
                ),
              ),
              title: Text(p.nombre),
              subtitle: Text(subtitulo),
              trailing: p.esSoloLectura
                  ? null
                  : Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.edit_outlined),
                          tooltip: 'Editar',
                          onPressed: () => _editarPerfil(p),
                        ),
                        if (p.esDependiente && p.esPropio)
                          IconButton(
                            icon: const Icon(Icons.delete_outline,
                                color: Colors.red),
                            tooltip: 'Eliminar',
                            onPressed: () => _confirmarEliminar(p),
                          ),
                      ],
                    ),
            ),
          );
        },
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Mis perfiles')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _agregarDependiente,
        icon: const Icon(Icons.person_add),
        label: const Text('Agregar dependiente'),
      ),
      body: cuerpo,
    );
  }
}