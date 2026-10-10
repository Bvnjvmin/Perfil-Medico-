import 'package:flutter/material.dart';
import '../models/perfil.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

/// Crea o edita el perfil de salud del titular (HU 2).
/// Al guardar vuelve a la pantalla anterior devolviendo el [Perfil] resultante.
class PerfilScreen extends StatefulWidget {
  final String token;
  final Perfil? perfil;

  const PerfilScreen({super.key, required this.token, this.perfil});

  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends State<PerfilScreen> {
  final _formKey = GlobalKey<FormState>();
  final _api = ApiService();
  late final TextEditingController _nombreCtrl;
  late final TextEditingController _rutCtrl;
  late final TextEditingController _grupoCtrl;
  DateTime? _fecha;

  bool _cargando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final p = widget.perfil;
    _nombreCtrl = TextEditingController(text: p?.nombre ?? '');
    _rutCtrl = TextEditingController(text: p?.rut ?? '');
    _grupoCtrl = TextEditingController(text: p?.grupoSanguineo ?? '');
    _fecha = p?.fechaNacimiento;
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _rutCtrl.dispose();
    _grupoCtrl.dispose();
    super.dispose();
  }

  String? _vacioANull(String texto) {
    final t = texto.trim();
    return t.isEmpty ? null : t;
  }

  Future<void> _elegirFecha() async {
    final elegida = await showDatePicker(
      context: context,
      initialDate: _fecha ?? DateTime(1990),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (elegida != null) setState(() => _fecha = elegida);
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _cargando = true;
      _error = null;
    });

    try {
      final existente = widget.perfil;
      final Perfil resultado;
      if (existente == null) {
        resultado = await _api.crearPerfil(
          widget.token,
          nombre: _nombreCtrl.text.trim(),
          rut: _vacioANull(_rutCtrl.text),
          grupoSanguineo: _vacioANull(_grupoCtrl.text),
          fechaNacimiento: _fecha,
        );
      } else {
        resultado = await _api.actualizarPerfil(
          widget.token,
          existente.id,
          nombre: _nombreCtrl.text.trim(),
          rut: _vacioANull(_rutCtrl.text),
          grupoSanguineo: _vacioANull(_grupoCtrl.text),
          fechaNacimiento: _fecha,
        );
      }
      if (!mounted) return;
      Navigator.of(context).pop(resultado);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _cargando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final esNuevo = widget.perfil == null;
    return Scaffold(
      appBar: AppBar(
        title: Text(esNuevo ? 'Crear perfil de salud' : 'Mi perfil de salud'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _nombreCtrl,
                decoration: const InputDecoration(labelText: 'Nombre completo'),
                validator: (v) =>
                    (v == null || v.trim().length < 2) ? 'Ingresa tu nombre' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _rutCtrl,
                decoration: const InputDecoration(
                  labelText: 'RUT (opcional)',
                  hintText: '12.345.678-9',
                ),
                validator: (v) =>
                    (v != null && v.trim().length > 12) ? 'Máximo 12 caracteres' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _grupoCtrl,
                decoration: const InputDecoration(
                  labelText: 'Grupo sanguíneo (opcional)',
                  hintText: 'Ej: O+',
                ),
              ),
              const SizedBox(height: 12),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Fecha de nacimiento'),
                subtitle: Text(_fecha == null ? 'Sin definir' : fechaCorta(_fecha!)),
                trailing: const Icon(Icons.calendar_today),
                onTap: _elegirFecha,
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _cargando ? null : _guardar,
                child: _cargando
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Text(esNuevo ? 'Crear perfil' : 'Guardar cambios'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}