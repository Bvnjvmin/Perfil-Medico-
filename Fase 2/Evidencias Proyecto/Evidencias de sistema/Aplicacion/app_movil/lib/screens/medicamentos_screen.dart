import 'package:flutter/material.dart';
import '../models/medicamento.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

/// Lista, registra y elimina los medicamentos del perfil (HU 4).
class MedicamentosScreen extends StatefulWidget {
  final String token;
  final String perfilId;

  const MedicamentosScreen({super.key, required this.token, required this.perfilId});

  @override
  State<MedicamentosScreen> createState() => _MedicamentosScreenState();
}

class _MedicamentosScreenState extends State<MedicamentosScreen> {
  final _api = ApiService();
  List<Medicamento>? _medicamentos;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarMedicamentos(widget.token, widget.perfilId);
      if (!mounted) return;
      setState(() {
        _medicamentos = lista;
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
      builder: (_) => const _NuevoMedicamentoDialog(),
    );
    if (datos == null) return;

    try {
      await _api.registrarMedicamento(
        widget.token,
        widget.perfilId,
        nombre: datos['nombre']!,
        dosis: datos['dosis']!,
        frecuencia: datos['frecuencia']!,
        horaInicio: datos['hora'],
      );
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  Future<void> _eliminar(Medicamento m) async {
    try {
      await _api.eliminarMedicamento(widget.token, m.id);
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      _mostrarMensaje(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _medicamentos;
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
      cuerpo = const Center(child: Text('Aún no registras medicamentos.'));
    } else {
      cuerpo = ListView.builder(
        itemCount: lista.length,
        itemBuilder: (context, i) {
          final m = lista[i];
          final hora = horaCorta(m.horaInicio);
          return ListTile(
            leading: const Icon(Icons.medication),
            title: Text(m.nombre),
            subtitle: Text(
              '${m.dosis} · ${m.frecuencia}${hora.isEmpty ? '' : ' · $hora'}',
            ),
            trailing: IconButton(
              icon: const Icon(Icons.delete_outline),
              tooltip: 'Eliminar',
              onPressed: () => _eliminar(m),
            ),
          );
        },
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Medicamentos')),
      floatingActionButton: FloatingActionButton(
        onPressed: _agregar,
        tooltip: 'Agregar medicamento',
        child: const Icon(Icons.add),
      ),
      body: cuerpo,
    );
  }
}

class _NuevoMedicamentoDialog extends StatefulWidget {
  const _NuevoMedicamentoDialog();

  @override
  State<_NuevoMedicamentoDialog> createState() => _NuevoMedicamentoDialogState();
}

class _NuevoMedicamentoDialogState extends State<_NuevoMedicamentoDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nombreCtrl = TextEditingController();
  final _dosisCtrl = TextEditingController();
  final _frecuenciaCtrl = TextEditingController();
  TimeOfDay? _hora;

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _dosisCtrl.dispose();
    _frecuenciaCtrl.dispose();
    super.dispose();
  }

  Future<void> _elegirHora() async {
    final elegida = await showTimePicker(
      context: context,
      initialTime: _hora ?? const TimeOfDay(hour: 8, minute: 0),
    );
    if (elegida != null) setState(() => _hora = elegida);
  }

  void _aceptar() {
    if (!_formKey.currentState!.validate()) return;
    Navigator.of(context).pop(<String, String?>{
      'nombre': _nombreCtrl.text.trim(),
      'dosis': _dosisCtrl.text.trim(),
      'frecuencia': _frecuenciaCtrl.text.trim(),
      'hora': _hora == null ? null : horaParaApi(_hora!),
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Nuevo medicamento'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nombreCtrl,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: (v) =>
                    (v == null || v.trim().length < 2) ? 'Ingresa el nombre' : null,
              ),
              TextFormField(
                controller: _dosisCtrl,
                decoration: const InputDecoration(
                  labelText: 'Dosis',
                  hintText: 'Ej: 500 mg',
                ),
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Ingresa la dosis' : null,
              ),
              TextFormField(
                controller: _frecuenciaCtrl,
                decoration: const InputDecoration(
                  labelText: 'Frecuencia',
                  hintText: 'Ej: cada 8 horas',
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