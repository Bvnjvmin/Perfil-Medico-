import 'package:flutter/material.dart';
import '../models/sprint5.dart';
import '../services/api_sprint5.dart';
import '../utils/hora.dart';

/// Pulsera, ubicación y geocercas (HU 17 y HU 19).
///
/// Muestra las coordenadas de la última posición (sin mapa, para no agregar
/// dependencias). Con la pulsera registrada, permite crear zonas circulares; al salir
/// de una, el backend crea un evento de seguridad.
class PulseraScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final String perfilNombre;
  final bool puedeEditar;

  const PulseraScreen({
    super.key,
    required this.token,
    required this.perfilId,
    required this.perfilNombre,
    required this.puedeEditar,
  });

  @override
  State<PulseraScreen> createState() => _PulseraScreenState();
}

class _PulseraScreenState extends State<PulseraScreen> {
  final _api = ApiSprint5();
  Ubicacion? _ubicacion;
  List<Geocerca> _geocercas = [];
  bool _cargando = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final ubicacion = await _api.ubicacion(widget.token, widget.perfilId);
      final geocercas = await _api.listarGeocercas(widget.token, widget.perfilId);
      if (!mounted) return;
      setState(() {
        _ubicacion = ubicacion;
        _geocercas = geocercas;
        _cargando = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _cargando = false;
        _error = e.toString();
      });
    }
  }

  void _mensaje(String texto) =>
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(texto)));

  Future<void> _registrarPulsera() async {
    final identificador = TextEditingController();
    final nombre = TextEditingController(text: 'Pulsera de ${widget.perfilNombre}');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Registrar pulsera'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: identificador,
              decoration: const InputDecoration(
                labelText: 'Identificador (IMEI)',
                helperText: 'El mismo que se configuró en Traccar',
              ),
            ),
            TextField(controller: nombre, decoration: const InputDecoration(labelText: 'Nombre')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Guardar')),
        ],
      ),
    );
    final id = identificador.text;
    final nom = nombre.text;
    identificador.dispose();
    nombre.dispose();
    if (ok != true || !mounted) return;
    try {
      await _api.registrarPulsera(widget.token, widget.perfilId, identificador: id, nombre: nom);
      await _cargar();
    } catch (e) {
      if (mounted) _mensaje(e.toString());
    }
  }

  Future<void> _crearGeocerca() async {
    final nombre = TextEditingController();
    final lat = TextEditingController();
    final lon = TextEditingController();
    final radio = TextEditingController(text: '150');
    final posicion = _ubicacion?.posicion;
    if (posicion != null) {
      lat.text = posicion.latitud.toStringAsFixed(5);
      lon.text = posicion.longitud.toStringAsFixed(5);
    }
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Nueva zona'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: nombre, decoration: const InputDecoration(labelText: 'Nombre (ej. Casa)')),
              TextField(
                controller: lat,
                keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
                decoration: const InputDecoration(
                  labelText: 'Latitud',
                  helperText: 'Se rellena con la última posición de la pulsera',
                ),
              ),
              TextField(
                controller: lon,
                keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
                decoration: const InputDecoration(labelText: 'Longitud'),
              ),
              TextField(
                controller: radio,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Radio en metros (20 a 50000)'),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Guardar')),
        ],
      ),
    );
    final n = nombre.text;
    final la = double.tryParse(lat.text.trim().replaceAll(',', '.'));
    final lo = double.tryParse(lon.text.trim().replaceAll(',', '.'));
    final r = int.tryParse(radio.text.trim());
    nombre.dispose();
    lat.dispose();
    lon.dispose();
    radio.dispose();
    if (ok != true || !mounted) return;
    if (n.trim().isEmpty || la == null || lo == null || r == null) {
      _mensaje('Completa el nombre, las coordenadas y el radio con números válidos.');
      return;
    }
    try {
      await _api.crearGeocerca(widget.token, widget.perfilId,
          nombre: n, latitud: la, longitud: lo, radioM: r);
      await _cargar();
    } catch (e) {
      if (mounted) _mensaje(e.toString());
    }
  }

  Future<void> _borrarGeocerca(Geocerca g) async {
    try {
      await _api.eliminarGeocerca(widget.token, widget.perfilId, g.id);
      await _cargar();
    } catch (e) {
      if (mounted) _mensaje(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    Widget cuerpo;
    if (_cargando) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else if (_error != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: const TextStyle(color: Colors.red)),
        ),
      );
    } else {
      final pulsera = _ubicacion?.pulsera;
      final posicion = _ubicacion?.posicion;
      final registrada = posicion == null ? null : DateTime.tryParse(posicion.registradaEn)?.toLocal();
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (pulsera == null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      const Icon(Icons.watch_outlined, size: 48),
                      const SizedBox(height: 8),
                      const Text(
                        'Este perfil aún no tiene una pulsera registrada.',
                        textAlign: TextAlign.center,
                      ),
                      if (widget.puedeEditar) ...[
                        const SizedBox(height: 12),
                        FilledButton(onPressed: _registrarPulsera, child: const Text('Registrar pulsera')),
                      ],
                    ],
                  ),
                ),
              )
            else
              Card(
                child: ListTile(
                  leading: const Icon(Icons.watch_outlined, size: 32),
                  title: Text(pulsera.nombre),
                  subtitle: Text([
                    if (pulsera.bateriaPct != null) 'Batería ${pulsera.bateriaPct} %',
                    if (pulsera.ultimaConexion != null)
                      'Última conexión ${fechaHoraCorta(DateTime.tryParse(pulsera.ultimaConexion!)?.toLocal() ?? DateTime.now())}',
                  ].join(' · ')),
                ),
              ),
            const SizedBox(height: 8),
            Card(
              child: ListTile(
                leading: const Icon(Icons.location_on_outlined, size: 32),
                title: const Text('Última ubicación'),
                subtitle: Text(
                  posicion == null
                      ? 'Aún no hay lecturas de la pulsera.'
                      : '${posicion.latitud.toStringAsFixed(5)}, ${posicion.longitud.toStringAsFixed(5)}'
                          '${registrada == null ? '' : '\n${fechaHoraCorta(registrada)}'}'
                          '${_ubicacion!.dentroDe.isEmpty ? '' : '\nDentro de: ${_ubicacion!.dentroDe.join(', ')}'}',
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Expanded(
                  child: Text('Zonas', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
                if (widget.puedeEditar)
                  TextButton.icon(
                    onPressed: _crearGeocerca,
                    icon: const Icon(Icons.add),
                    label: const Text('Nueva zona'),
                  ),
              ],
            ),
            if (_geocercas.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text('Sin zonas. Al crear una, se avisa cuando la persona sale de ella.'),
              ),
            for (final g in _geocercas)
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.share_location),
                title: Text(g.nombre),
                subtitle: Text('Radio ${g.radioM} m'),
                trailing: widget.puedeEditar
                    ? IconButton(
                        icon: const Icon(Icons.delete_outline),
                        tooltip: 'Eliminar zona',
                        onPressed: () => _borrarGeocerca(g),
                      )
                    : null,
              ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Pulsera · ${widget.perfilNombre}')),
      body: cuerpo,
    );
  }
}
