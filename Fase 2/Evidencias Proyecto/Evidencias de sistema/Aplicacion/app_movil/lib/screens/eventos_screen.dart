import 'package:flutter/material.dart';
import '../models/sprint5.dart';
import '../services/api_sprint5.dart';
import '../utils/hora.dart';

/// Eventos de seguridad (HU 14 y HU 19): botón de ayuda, SOS, caída, batería baja,
/// inactividad y salida de geocerca, de los perfiles propios y de aquellos donde el
/// usuario recibe alertas. Cada evento se puede marcar como atendido.
class EventosScreen extends StatefulWidget {
  final String token;
  const EventosScreen({super.key, required this.token});

  @override
  State<EventosScreen> createState() => _EventosScreenState();
}

class _EventosScreenState extends State<EventosScreen> {
  final _api = ApiSprint5();
  List<EventoSeguridad>? _eventos;
  String? _error;
  bool _soloPendientes = false;
  String? _atendiendo;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarEventos(widget.token, soloPendientes: _soloPendientes);
      if (!mounted) return;
      setState(() {
        _eventos = lista;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  Future<void> _atender(EventoSeguridad evento) async {
    if (_atendiendo != null) return;
    setState(() => _atendiendo = evento.id);
    try {
      await _api.marcarAtendido(widget.token, evento.id);
      await _cargar();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _atendiendo = null);
    }
  }

  IconData _icono(String tipo) {
    switch (tipo) {
      case 'sos':
        return Icons.sos;
      case 'caida':
        return Icons.personal_injury_outlined;
      case 'asistencia':
        return Icons.back_hand_outlined;
      case 'bateria_baja':
        return Icons.battery_alert;
      case 'inactividad':
        return Icons.hourglass_bottom;
      case 'geocerca_salida':
        return Icons.share_location;
      default:
        return Icons.warning_amber_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _eventos;
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
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'No hay eventos. Aquí aparecerán los pedidos de ayuda y las alertas de la pulsera.',
            textAlign: TextAlign.center,
          ),
        ),
      );
    } else {
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView.separated(
          itemCount: lista.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, i) {
            final e = lista[i];
            final creado = DateTime.tryParse(e.creadoEn)?.toLocal();
            final color = e.atendido
                ? Colors.grey
                : (e.esUrgente ? Colors.red.shade700 : Colors.orange.shade800);
            return ListTile(
              leading: Icon(_icono(e.tipo), color: color, size: 30),
              title: Text(
                '${e.titulo} · ${e.perfilNombre}',
                style: TextStyle(fontWeight: e.atendido ? FontWeight.normal : FontWeight.bold),
              ),
              subtitle: Text(
                [
                  e.mensaje,
                  if (creado != null) fechaHoraCorta(creado),
                  if (e.atendido) 'Atendido',
                ].join('\n'),
              ),
              isThreeLine: true,
              trailing: e.atendido
                  ? const Icon(Icons.check_circle, color: Colors.green)
                  : TextButton(
                      onPressed: _atendiendo == null ? () => _atender(e) : null,
                      child: Text(_atendiendo == e.id ? '...' : 'Atender'),
                    ),
            );
          },
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Eventos de seguridad'),
        actions: [
          IconButton(
            tooltip: _soloPendientes ? 'Mostrar todos' : 'Solo pendientes',
            icon: Icon(_soloPendientes ? Icons.filter_alt : Icons.filter_alt_outlined),
            onPressed: () {
              setState(() {
                _soloPendientes = !_soloPendientes;
                _eventos = null;
              });
              _cargar();
            },
          ),
        ],
      ),
      body: cuerpo,
    );
  }
}
