import 'package:flutter/material.dart';
import '../models/perfil.dart';
import '../services/api_service.dart';

class CompartirPerfilScreen extends StatefulWidget {
  final String token;
  final Perfil perfil;

  const CompartirPerfilScreen({
    super.key,
    required this.token,
    required this.perfil,
  });

  @override
  State<CompartirPerfilScreen> createState() => _CompartirPerfilScreenState();
}

class _CompartirPerfilScreenState extends State<CompartirPerfilScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _api = ApiService();

  String _rol = 'cuidador';
  bool _puedeConfirmar = true;
  bool _puedeEditarRutinas = false;
  bool _enviando = false;
  String? _error;

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _invitar() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _enviando = true;
      _error = null;
    });

    try {
      await _api.compartirPerfil(
        widget.token,
        widget.perfil.id,
        email: _emailCtrl.text.trim(),
        rol: _rol,
        puedeConfirmar: _rol == 'lectura' ? false : _puedeConfirmar,
        puedeEditarRutinas: _rol == 'lectura' ? false : _puedeEditarRutinas,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Acceso compartido correctamente.')),
      );
      Navigator.of(context).pop(true);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final esLectura = _rol == 'lectura';

    return Scaffold(
      appBar: AppBar(
        title: Text('Compartir — ${widget.perfil.nombre}'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              const Text(
                'Invita a un cuidador o familiar ingresando el correo electrónico con el que está registrado en la aplicación.',
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _emailCtrl,
                decoration: const InputDecoration(
                  labelText: 'Correo electrónico del cuidador',
                  prefixIcon: Icon(Icons.email_outlined),
                ),
                keyboardType: TextInputType.emailAddress,
                validator: (v) => (v == null || !v.contains('@'))
                    ? 'Ingresa un correo válido'
                    : null,
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: _rol,
                decoration: const InputDecoration(labelText: 'Rol de acceso'),
                items: const [
                  DropdownMenuItem(
                    value: 'cuidador',
                    child: Text('Cuidador (permisos configurables)'),
                  ),
                  DropdownMenuItem(
                    value: 'lectura',
                    child: Text('Solo lectura'),
                  ),
                ],
                onChanged: (v) {
                  if (v == null) return;
                  setState(() => _rol = v);
                },
              ),
              const SizedBox(height: 16),
              SwitchListTile(
                title: const Text('Puede confirmar actividades en la agenda'),
                value: esLectura ? false : _puedeConfirmar,
                onChanged: esLectura
                    ? null
                    : (v) => setState(() => _puedeConfirmar = v),
              ),
              SwitchListTile(
                title: const Text('Puede agregar/editar medicamentos y rutinas'),
                value: esLectura ? false : _puedeEditarRutinas,
                onChanged: esLectura
                    ? null
                    : (v) => setState(() => _puedeEditarRutinas = v),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _enviando ? null : _invitar,
                icon: const Icon(Icons.share),
                label: _enviando
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Compartir perfil'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
