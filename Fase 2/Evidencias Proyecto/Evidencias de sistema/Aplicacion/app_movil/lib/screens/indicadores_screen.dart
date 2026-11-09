import 'package:flutter/material.dart';
import '../models/sprint5.dart';
import '../services/api_sprint5.dart';
import '../utils/hora.dart';
import '../widgets/graficos.dart';

/// Indicadores de salud (HU 12 y HU 18): último valor de cada tipo, registro manual y
/// gráfico de evolución al tocar un indicador.
class IndicadoresScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final String perfilNombre;
  final bool puedeRegistrar;

  const IndicadoresScreen({
    super.key,
    required this.token,
    required this.perfilId,
    required this.perfilNombre,
    required this.puedeRegistrar,
  });

  @override
  State<IndicadoresScreen> createState() => _IndicadoresScreenState();
}

class _IndicadoresScreenState extends State<IndicadoresScreen> {
  final _api = ApiSprint5();
  List<Indicador>? _ultimos;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.ultimosIndicadores(widget.token, widget.perfilId);
      if (!mounted) return;
      setState(() {
        _ultimos = lista;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  Indicador? _ultimoDe(String tipo) {
    for (final i in _ultimos ?? const <Indicador>[]) {
      if (i.tipo == tipo) return i;
    }
    return null;
  }

  Future<void> _registrar() async {
    final guardado = await showDialog<bool>(
      context: context,
      builder: (_) => _RegistrarIndicadorDialog(
        api: _api,
        token: widget.token,
        perfilId: widget.perfilId,
      ),
    );
    if (guardado == true) await _cargar();
  }

  void _abrirSerie(String tipo) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => SerieIndicadorScreen(
          token: widget.token,
          perfilId: widget.perfilId,
          tipo: tipo,
        ),
      ),
    );
  }

  IconData _icono(String tipo) {
    switch (tipo) {
      case 'peso':
        return Icons.monitor_weight_outlined;
      case 'presion':
        return Icons.speed;
      case 'glucosa':
        return Icons.water_drop_outlined;
      default:
        return Icons.favorite_border;
    }
  }

  @override
  Widget build(BuildContext context) {
    Widget cuerpo;
    if (_error != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: const TextStyle(color: Colors.red)),
        ),
      );
    } else if (_ultimos == null) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else {
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            for (final tipo in Indicador.tipos)
              Builder(builder: (context) {
                final ultimo = _ultimoDe(tipo);
                final medido = ultimo == null ? null : DateTime.tryParse(ultimo.medidoEn)?.toLocal();
                return Card(
                  child: ListTile(
                    leading: Icon(_icono(tipo), size: 32),
                    title: Text(Indicador.nombreDeTipo(tipo)),
                    subtitle: Text(
                      ultimo == null
                          ? 'Sin mediciones'
                          : '${ultimo.texto}${medido == null ? '' : ' · ${fechaHoraCorta(medido)}'}',
                    ),
                    trailing: const Icon(Icons.show_chart),
                    onTap: () => _abrirSerie(tipo),
                  ),
                );
              }),
            const SizedBox(height: 8),
            const Text(
              'Los valores se registran a mano y solo sirven de registro: no son un diagnóstico.',
              style: TextStyle(fontSize: 12, color: Colors.black54),
            ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Indicadores · ${widget.perfilNombre}')),
      body: cuerpo,
      floatingActionButton: widget.puedeRegistrar
          ? FloatingActionButton.extended(
              onPressed: _registrar,
              icon: const Icon(Icons.add),
              label: const Text('Registrar'),
            )
          : null,
    );
  }
}

class _RegistrarIndicadorDialog extends StatefulWidget {
  final ApiSprint5 api;
  final String token;
  final String perfilId;
  const _RegistrarIndicadorDialog({
    required this.api,
    required this.token,
    required this.perfilId,
  });

  @override
  State<_RegistrarIndicadorDialog> createState() => _RegistrarIndicadorDialogState();
}

class _RegistrarIndicadorDialogState extends State<_RegistrarIndicadorDialog> {
  String _tipo = 'peso';
  final _valor = TextEditingController();
  final _secundario = TextEditingController();
  final _nota = TextEditingController();
  bool _guardando = false;
  String? _error;

  @override
  void dispose() {
    _valor.dispose();
    _secundario.dispose();
    _nota.dispose();
    super.dispose();
  }

  double? _numero(String texto) => double.tryParse(texto.trim().replaceAll(',', '.'));

  Future<void> _guardar() async {
    final valor = _numero(_valor.text);
    final secundario = _numero(_secundario.text);
    if (valor == null) {
      setState(() => _error = 'Escribe un número válido.');
      return;
    }
    if (_tipo == 'presion' && secundario == null) {
      setState(() => _error = 'La presión necesita sistólica y diastólica.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      await widget.api.registrarIndicador(
        widget.token,
        widget.perfilId,
        tipo: _tipo,
        valor: valor,
        valorSecundario: _tipo == 'presion' ? secundario : null,
        nota: _nota.text,
      );
      if (!mounted) return;
      Navigator.of(context).pop(true);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _guardando = false;
        _error = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final esPresion = _tipo == 'presion';
    return AlertDialog(
      title: const Text('Registrar indicador'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              initialValue: _tipo,
              decoration: const InputDecoration(labelText: 'Indicador'),
              items: [
                for (final t in Indicador.tipos)
                  DropdownMenuItem(value: t, child: Text(Indicador.nombreDeTipo(t))),
              ],
              onChanged: (v) => setState(() => _tipo = v ?? 'peso'),
            ),
            TextField(
              controller: _valor,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(labelText: esPresion ? 'Sistólica (la alta)' : 'Valor'),
            ),
            if (esPresion)
              TextField(
                controller: _secundario,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: 'Diastólica (la baja)'),
              ),
            TextField(
              controller: _nota,
              maxLength: 500,
              decoration: const InputDecoration(labelText: 'Nota (opcional)'),
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _guardando ? null : () => Navigator.of(context).pop(false),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _guardando ? null : _guardar,
          child: Text(_guardando ? 'Guardando...' : 'Guardar'),
        ),
      ],
    );
  }
}

/// Evolución de un indicador en los últimos días (HU 18).
class SerieIndicadorScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final String tipo;

  const SerieIndicadorScreen({
    super.key,
    required this.token,
    required this.perfilId,
    required this.tipo,
  });

  @override
  State<SerieIndicadorScreen> createState() => _SerieIndicadorScreenState();
}

class _SerieIndicadorScreenState extends State<SerieIndicadorScreen> {
  final _api = ApiSprint5();
  SerieIndicador? _serie;
  String? _error;
  int _dias = 30;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _serie = null;
      _error = null;
    });
    try {
      final serie = await _api.serieIndicador(
        widget.token,
        widget.perfilId,
        tipo: widget.tipo,
        dias: _dias,
      );
      if (!mounted) return;
      setState(() => _serie = serie);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  String _num(double? v) {
    if (v == null) return '–';
    return v == v.roundToDouble() ? v.toStringAsFixed(0) : v.toStringAsFixed(1);
  }

  @override
  Widget build(BuildContext context) {
    final serie = _serie;
    Widget cuerpo;
    if (_error != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: const TextStyle(color: Colors.red)),
        ),
      );
    } else if (serie == null) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else {
      cuerpo = ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Center(
            child: SegmentedButton<int>(
              segments: const [
                ButtonSegment(value: 7, label: Text('7 días')),
                ButtonSegment(value: 30, label: Text('30 días')),
                ButtonSegment(value: 90, label: Text('90 días')),
              ],
              selected: {_dias},
              onSelectionChanged: (s) {
                _dias = s.first;
                _cargar();
              },
            ),
          ),
          const SizedBox(height: 20),
          if (serie.puntos.isEmpty)
            const Padding(
              padding: EdgeInsets.all(24),
              child: Text('No hay mediciones en este período.', textAlign: TextAlign.center),
            )
          else ...[
            LineaSerie(serie: serie),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Text('Mínimo: ${_num(serie.minimo)} ${serie.unidad}'),
                Text('Promedio: ${_num(serie.promedio)} ${serie.unidad}'),
                Text('Máximo: ${_num(serie.maximo)} ${serie.unidad}'),
              ],
            ),
            if (widget.tipo == 'presion')
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text(
                  'Trazo oscuro: sistólica. Trazo claro: diastólica.',
                  style: TextStyle(fontSize: 12, color: Colors.black54),
                ),
              ),
          ],
        ],
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text(Indicador.nombreDeTipo(widget.tipo))),
      body: cuerpo,
    );
  }
}
