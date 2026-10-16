import 'package:flutter/material.dart';
import '../models/actividad.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

/// Agenda diaria conectada a la API (Cierre de HU 5 - Sprint 3).
class AgendaScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final bool puedeConfirmar;

  const AgendaScreen({
    super.key,
    required this.token,
    required this.perfilId,
    this.puedeConfirmar = true,
  });

  @override
  State<AgendaScreen> createState() => _AgendaScreenState();
}

class _AgendaScreenState extends State<AgendaScreen> {
  final _api = ApiService();
  final DateTime _hoy = DateTime.now();

  List<Actividad>? _actividades;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarActividades(
        widget.token,
        widget.perfilId,
        _hoy,
      );
      if (!mounted) return;
      setState(() {
        _actividades = lista;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  Future<void> _alternar(int index, bool? valor) async {
    if (!widget.puedeConfirmar || _actividades == null) return;

    final original = _actividades![index];
    final marcar = valor == true;
    final estadoOptimista = marcar ? 'confirmada' : 'pendiente';

    // Actualiza la casilla de inmediato
    setState(() {
      _actividades![index] = original.copyWith(estado: estadoOptimista);
    });

    try {
      final actualizada = marcar
          ? await _api.confirmarActividad(widget.token, original.id)
          : await _api.desconfirmarActividad(widget.token, original.id);
      if (!mounted) return;
      setState(() {
        _actividades![index] = actualizada;
      });
    } catch (e) {
      // Si el servidor falla, vuelve atrás y muestra el error
      if (!mounted) return;
      setState(() {
        _actividades![index] = original;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _actividades;
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
            'No hay actividades. Agrega medicamentos o rutinas de cuidado para verlas aquí.',
            textAlign: TextAlign.center,
          ),
        ),
      );
    } else {
      final hechas = lista.where((a) => a.estaConfirmada).length;
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hoy, ${fechaCorta(_hoy)}',
                    style: const TextStyle(
                        fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text('$hechas de ${lista.length} actividades confirmadas'),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(value: hechas / lista.length),
                ],
              ),
            ),
            for (var i = 0; i < lista.length; i++)
              CheckboxListTile(
                value: lista[i].estaConfirmada,
                onChanged:
                    widget.puedeConfirmar ? (v) => _alternar(i, v) : null,
                controlAffinity: ListTileControlAffinity.leading,
                title: Text(
                  lista[i].titulo,
                  style: TextStyle(
                    decoration: lista[i].estaConfirmada
                        ? TextDecoration.lineThrough
                        : null,
                  ),
                ),
                subtitle: Text(lista[i].detalle ?? ''),
                secondary: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      lista[i].origenTipo == 'medicamento'
                          ? Icons.medication
                          : Icons.favorite_border,
                      size: 18,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      horaCorta(lista[i].hora).isEmpty
                          ? '--:--'
                          : horaCorta(lista[i].hora),
                    ),
                  ],
                ),
              ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Agenda de hoy')),
      body: cuerpo,
    );
  }
}
