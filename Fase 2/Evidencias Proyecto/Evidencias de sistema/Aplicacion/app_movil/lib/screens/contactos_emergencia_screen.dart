import 'package:flutter/material.dart';
import '../models/contacto_emergencia.dart';
import '../services/api_service.dart';

class ContactosEmergenciaScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final bool puedeEditar;

  const ContactosEmergenciaScreen({
    super.key,
    required this.token,
    required this.perfilId,
    this.puedeEditar = true,
  });

  @override
  State<ContactosEmergenciaScreen> createState() =>
      _ContactosEmergenciaScreenState();
}

class _ContactosEmergenciaScreenState extends State<ContactosEmergenciaScreen> {
  final _api = ApiService();
  List<ContactoEmergencia>? _contactos;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarContactos(widget.token, widget.perfilId);
      if (!mounted) return;
      setState(() {
        _contactos = lista;
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
      builder: (_) => const _DialogoContacto(),
    );
    if (datos == null) return;

    try {
      await _api.registrarContacto(
        widget.token,
        widget.perfilId,
        nombre: datos['nombre']!,
        telefono: datos['telefono']!,
        parentesco: datos['parentesco'],
      );
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  Future<void> _eliminar(ContactoEmergencia c) async {
    try {
      await _api.eliminarContacto(widget.token, c.id);
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _contactos;
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
        child: Text('No hay contactos de emergencia registrados.'),
      );
    } else {
      cuerpo = ListView.builder(
        itemCount: lista.length,
        itemBuilder: (context, i) {
          final c = lista[i];
          final sub = [
            c.telefono,
            if (c.parentesco != null && c.parentesco!.isNotEmpty) c.parentesco!,
          ].join(' · ');

          return ListTile(
            leading: const Icon(Icons.contact_phone_outlined),
            title: Text(c.nombre),
            subtitle: Text(sub),
            trailing: widget.puedeEditar
                ? IconButton(
                    icon: const Icon(Icons.delete_outline),
                    tooltip: 'Eliminar',
                    onPressed: () => _eliminar(c),
                  )
                : null,
          );
        },
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Contactos de emergencia')),
      floatingActionButton: widget.puedeEditar
          ? FloatingActionButton(
              onPressed: _agregar,
              tooltip: 'Agregar contacto',
              child: const Icon(Icons.add),
            )
          : null,
      body: cuerpo,
    );
  }
}

class _DialogoContacto extends StatefulWidget {
  const _DialogoContacto();

  @override
  State<_DialogoContacto> createState() => _DialogoContactoState();
}

class _DialogoContactoState extends State<_DialogoContacto> {
  final _formKey = GlobalKey<FormState>();
  final _nombreCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _parentescoCtrl = TextEditingController();

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _telefonoCtrl.dispose();
    _parentescoCtrl.dispose();
    super.dispose();
  }

  void _guardar() {
    if (!_formKey.currentState!.validate()) return;
    final parentesco = _parentescoCtrl.text.trim();
    Navigator.of(context).pop(<String, String?>{
      'nombre': _nombreCtrl.text.trim(),
      'telefono': _telefonoCtrl.text.trim(),
      'parentesco': parentesco.isEmpty ? null : parentesco,
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Nuevo contacto'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nombreCtrl,
                decoration: const InputDecoration(labelText: 'Nombre completo'),
                validator: (v) => (v == null || v.trim().length < 2)
                    ? 'Ingresa el nombre'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _telefonoCtrl,
                decoration: const InputDecoration(
                  labelText: 'Teléfono',
                  hintText: '+56 9 1234 5678',
                ),
                keyboardType: TextInputType.phone,
                validator: (v) => (v == null || v.trim().length < 6)
                    ? 'Ingresa un teléfono válido'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _parentescoCtrl,
                decoration: const InputDecoration(
                  labelText: 'Parentesco / Relación (opcional)',
                  hintText: 'Ej: Madre, Hijo, Médico',
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