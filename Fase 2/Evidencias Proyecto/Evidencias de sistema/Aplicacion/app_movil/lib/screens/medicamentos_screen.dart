import 'package:flutter/material.dart';
import '../models/medicamento.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

class MedicamentosScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final bool puedeEditar;

  const MedicamentosScreen({
    super.key,
    required this.token,
    required this.perfilId,
    this.puedeEditar = true,
  });

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
      final lista =
          await _api.listarMedicamentos(widget.token, widget.perfilId);
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
      builder: (_) => const _MedicamentoDialog(),
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

  Future<void> _editar(Medicamento m) async {
    final datos = await showDialog<Map<String, String?>>(
      context: context,
      builder: (_) => _MedicamentoDialog(existente: m),
    );
    if (datos == null) return;

    try {
      await _api.actualizarMedicamento(
        widget.token,
        m.id,
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
            trailing: widget.puedeEditar
                ? Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.edit_outlined),
                        tooltip: 'Editar',
                        onPressed: () => _editar(m),
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete_outline),
                        tooltip: 'Eliminar',
                        onPressed: () => _eliminar(m),
                      ),
                    ],
                  )
                : null,
          );
        },
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Medicamentos')),
      floatingActionButton: widget.puedeEditar
          ? FloatingActionButton(
              onPressed: _agregar,
              tooltip: 'Agregar medicamento',
              child: const Icon(Icons.add),
            )
          : null,
      body: cuerpo,
    );
  }
}

class _MedicamentoDialog extends StatefulWidget {
  final Medicamento? existente;
  const _MedicamentoDialog({this.existente});

  @override
  State<_MedicamentoDialog> createState() => _MedicamentoDialogState();
}

class _MedicamentoDialogState extends State<_MedicamentoDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nombreCtrl;
  late final TextEditingController _dosisCtrl;
  late final TextEditingController _frecuenciaCtrl;
  TimeOfDay? _hora;

  @override
  void initState() {
    super.initState();
    final m = widget.existente;
    _nombreCtrl = TextEditingController(text: m?.nombre ?? '');
    _dosisCtrl = TextEditingController(text: m?.dosis ?? '');
    _frecuenciaCtrl = TextEditingController(text: m?.frecuencia ?? '');
  }

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
      'hora': _hora == null
          ? widget.existente?.horaInicio
          : horaParaApi(_hora!),
    });
  }

  @override
  Widget build(BuildContext context) {
    final esEdicion = widget.existente != null;
    return AlertDialog(
      title: Text(esEdicion ? 'Editar medicamento' : 'Nuevo medicamento'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nombreCtrl,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: (v) => (v == null || v.trim().length < 2)
                    ? 'Ingresa el nombre'
                    : null,
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
                validator: (v) => (v == null || v.trim().length < 2)
                    ? 'Ingresa la frecuencia'
                    : null,
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      _hora == null
                          ? (widget.existente?.horaInicio != null
                              ? 'Hora: ${horaCorta(widget.existente!.horaInicio)}'
                              : 'Sin hora')
                          : 'Hora: ${_hora!.format(context)}',
                    ),
                  ),
                  TextButton(
                      onPressed: _elegirHora, child: const Text('Elegir hora')),
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
