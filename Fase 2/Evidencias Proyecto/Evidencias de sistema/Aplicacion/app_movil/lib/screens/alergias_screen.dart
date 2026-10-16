import 'package:flutter/material.dart';
import '../models/alergia.dart';
import '../services/api_service.dart';

class AlergiasScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final bool puedeEditar;

  const AlergiasScreen({
    super.key,
    required this.token,
    required this.perfilId,
    this.puedeEditar = true,
  });

  @override
  State<AlergiasScreen> createState() => _AlergiasScreenState();
}

class _AlergiasScreenState extends State<AlergiasScreen> {
  final _api = ApiService();
  List<Alergia>? _alergias;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarAlergias(widget.token, widget.perfilId);
      if (!mounted) return;
      setState(() {
        _alergias = lista;
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

  Future<void> _agregar() async {
    final datos = await showDialog<Map<String, String?>>(
      context: context,
      builder: (_) => const _DialogoAlergia(),
    );
    if (datos == null) return;

    try {
      await _api.registrarAlergia(
        widget.token,
        widget.perfilId,
        nombre: datos['nombre']!,
        severidad: datos['severidad'],
        reaccion: datos['reaccion'],
      );
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  Future<void> _eliminar(Alergia a) async {
    try {
      await _api.eliminarAlergia(widget.token, a.id);
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _alergias;
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
      cuerpo = const Center(child: Text('No hay alergias registradas.'));
    } else {
      cuerpo = ListView.builder(
        itemCount: lista.length,
        itemBuilder: (context, i) {
          final a = lista[i];
          final sub = [
            if (a.severidad != null && a.severidad!.isNotEmpty)
              'Severidad: ${a.severidad}',
            if (a.reaccion != null && a.reaccion!.isNotEmpty) a.reaccion!,
          ].join(' · ');

          return ListTile(
            leading: const Icon(Icons.warning_amber_rounded),
            title: Text(a.nombre),
            subtitle: sub.isEmpty ? null : Text(sub),
            trailing: widget.puedeEditar
                ? IconButton(
                    icon: const Icon(Icons.delete_outline),
                    tooltip: 'Eliminar',
                    onPressed: () => _eliminar(a),
                  )
                : null,
          );
        },
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Alergias')),
      floatingActionButton: widget.puedeEditar
          ? FloatingActionButton(
              onPressed: _agregar,
              tooltip: 'Agregar alergia',
              child: const Icon(Icons.add),
            )
          : null,
      body: cuerpo,
    );
  }
}

class _DialogoAlergia extends StatefulWidget {
  const _DialogoAlergia();

  @override
  State<_DialogoAlergia> createState() => _DialogoAlergiaState();
}

class _DialogoAlergiaState extends State<_DialogoAlergia> {
  final _formKey = GlobalKey<FormState>();
  final _nombreCtrl = TextEditingController();
  final _reaccionCtrl = TextEditingController();
  String _severidad = 'Moderada';

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _reaccionCtrl.dispose();
    super.dispose();
  }

  void _guardar() {
    if (!_formKey.currentState!.validate()) return;
    final reaccion = _reaccionCtrl.text.trim();
    Navigator.of(context).pop(<String, String?>{
      'nombre': _nombreCtrl.text.trim(),
      'severidad': _severidad,
      'reaccion': reaccion.isEmpty ? null : reaccion,
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Nueva alergia'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nombreCtrl,
                decoration: const InputDecoration(
                  labelText: 'Alérgeno / Sustancia',
                  hintText: 'Ej: Penicilina, Maní',
                ),
                validator: (v) => (v == null || v.trim().length < 2)
                    ? 'Ingresa el nombre de la alergia'
                    : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _severidad,
                decoration: const InputDecoration(labelText: 'Severidad'),
                items: const [
                  DropdownMenuItem(value: 'Leve', child: Text('Leve')),
                  DropdownMenuItem(value: 'Moderada', child: Text('Moderada')),
                  DropdownMenuItem(value: 'Grave', child: Text('Grave')),
                ],
                onChanged: (v) => setState(() => _severidad = v ?? 'Moderada'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _reaccionCtrl,
                decoration: const InputDecoration(
                  labelText: 'Reacción o notas (opcional)',
                  hintText: 'Ej: Urticaria, dificultad respiratoria',
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(onPressed: _guardar, child: const Text('Guardar')),
      ],
    );
  }
}