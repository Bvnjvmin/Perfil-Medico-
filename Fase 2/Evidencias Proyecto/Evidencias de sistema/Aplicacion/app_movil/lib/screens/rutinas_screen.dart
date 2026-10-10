import 'package:flutter/material.dart';
import '../models/rutina_cuidado.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

/// Lista, registra y elimina las rutinas de cuidado del perfil (HU 4):
/// alimentación, hidratación, vitaminas u otras.
class RutinasScreen extends StatefulWidget {
  final String token;
  final String perfilId;

  const RutinasScreen({super.key, required this.token, required this.perfilId});

  @override
  State<RutinasScreen> createState() => _RutinasScreenState();
}

class _RutinasScreenState extends State<RutinasScreen> {
  final _api = ApiService();
  List<RutinaCuidado>? _rutinas;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarRutinas(widget.token, widget.perfilId);
      if (!mounted) return;
      setState(() {
        _rutinas = lista;
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
      builder: (_) => const _NuevaRutinaDialog(),
    );
    if (datos == null) return;

    try {
      await _api.registrarRutina(
        widget.token,
        widget.perfilId,
        tipo: datos['tipo']!,
        descripcion: datos['descripcion'],
        frecuencia: datos['frecuencia']!,
        hora: datos['hora'],
      );
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  Future<void> _eliminar(RutinaCuidado r) async {
    try {
      await _api.eliminarRutina(widget.token, r.id);
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  IconData _icono(String tipo) {
    switch (tipo) {
      case 'alimentacion':
        return Icons.restaurant;
      case 'hidratacion':
        return Icons.water_drop;
      case 'vitaminas':
        return Icons.local_pharmacy;
      default:
        return Icons.favorite_border;
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _rutinas;
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
      cuerpo = const Center(child: Text('Aún no registras rutinas de cuidado.'));
    } else {
      cuerpo = ListView.builder(
        itemCount: lista.length,
        itemBuilder: (context, i) {
          final r = lista[i];
          final hora = horaCorta(r.hora);
          return ListTile(
            leading: Icon(_icono(r.tipo)),
            title: Text(r.titulo),
            subtitle: Text(
              '${r.tipoLegible} · ${r.frecuencia}${hora.isEmpty ? '' : ' · $hora'}',
            ),
            trailing: IconButton(
              icon: const Icon(Icons.delete_outline),
              tooltip: 'Eliminar',
              onPressed: () => _eliminar(r),
            ),
          );
        },
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Rutinas de cuidado')),
      floatingActionButton: FloatingActionButton(
        onPressed: _agregar,
        tooltip: 'Agregar rutina',
        child: const Icon(Icons.add),
      ),
      body: cuerpo,
    );
  }
}

class _NuevaRutinaDialog extends StatefulWidget {
  const _NuevaRutinaDialog();

  @override
  State<_NuevaRutinaDialog> createState() => _NuevaRutinaDialogState();
}

class _NuevaRutinaDialogState extends State<_NuevaRutinaDialog> {
  static const _tipos = <String, String>{
    'alimentacion': 'Alimentación',
    'hidratacion': 'Hidratación',
    'vitaminas': 'Vitaminas',
    'otro': 'Otro',
  };

  final _formKey = GlobalKey<FormState>();
  final _descripcionCtrl = TextEditingController();
  final _frecuenciaCtrl = TextEditingController();
  String _tipo = 'alimentacion';
  TimeOfDay? _hora;

  @override
  void dispose() {
    _descripcionCtrl.dispose();
    _frecuenciaCtrl.dispose();
    super.dispose();
  }

  Future<void> _elegirHora() async {
    final elegida = await showTimePicker(
      context: context,
      initialTime: _hora ?? const TimeOfDay(hour: 12, minute: 0),
    );
    if (elegida != null) setState(() => _hora = elegida);
  }

  void _aceptar() {
    if (!_formKey.currentState!.validate()) return;
    final descripcion = _descripcionCtrl.text.trim();
    Navigator.of(context).pop(<String, String?>{
      'tipo': _tipo,
      'descripcion': descripcion.isEmpty ? null : descripcion,
      'frecuencia': _frecuenciaCtrl.text.trim(),
      'hora': _hora == null ? null : horaParaApi(_hora!),
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Nueva rutina'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: 8,
                children: [
                  for (final entrada in _tipos.entries)
                    ChoiceChip(
                      label: Text(entrada.value),
                      selected: _tipo == entrada.key,
                      onSelected: (_) => setState(() => _tipo = entrada.key),
                    ),
                ],
              ),
              TextFormField(
                controller: _descripcionCtrl,
                decoration: const InputDecoration(
                  labelText: 'Descripción (opcional)',
                  hintText: 'Ej: Tomar un vaso de agua',
                ),
                maxLength: 200,
              ),
              TextFormField(
                controller: _frecuenciaCtrl,
                decoration: const InputDecoration(
                  labelText: 'Frecuencia',
                  hintText: 'Ej: 3 veces al día',
                ),
                validator: (v) =>
                    (v == null || v.trim().length < 2) ? 'Ingresa la frecuencia' : null,
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      _hora == null ? 'Sin hora' : 'Hora: ${_hora!.format(context)}',
                    ),
                  ),
                  TextButton(onPressed: _elegirHora, child: const Text('Elegir hora')),
                ],
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
        FilledButton(onPressed: _aceptar, child: const Text('Guardar')),
      ],
    );
  }
}