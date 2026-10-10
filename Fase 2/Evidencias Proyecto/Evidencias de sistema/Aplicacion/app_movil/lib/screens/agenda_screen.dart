import 'package:flutter/material.dart';
import '../models/actividad_agenda.dart';
import '../services/agenda_storage.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

/// Agenda diaria (HU 5): junta los medicamentos y rutinas de cuidado del
/// perfil (endpoints de HU 4) y permite marcar cada actividad como hecha.
///
/// La confirmación se guarda en el dispositivo, por perfil y por día
/// (ver [AgendaStorage]); persistirla en el backend queda para el Sprint 3.
class AgendaScreen extends StatefulWidget {
  final String token;
  final String perfilId;

  const AgendaScreen({super.key, required this.token, required this.perfilId});

  @override
  State<AgendaScreen> createState() => _AgendaScreenState();
}

class _AgendaScreenState extends State<AgendaScreen> {
  final _api = ApiService();
  final _storage = AgendaStorage();
  final DateTime _hoy = DateTime.now();

  List<ActividadAgenda>? _actividades;
  Set<String> _confirmadas = <String>{};
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final medicamentos = await _api.listarMedicamentos(widget.token, widget.perfilId);
      final rutinas = await _api.listarRutinas(widget.token, widget.perfilId);
      final confirmadas = await _storage.cargar(widget.perfilId, _hoy);
      if (!mounted) return;
      setState(() {
        _actividades = construirAgenda(medicamentos, rutinas);
        _confirmadas = confirmadas;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  Future<void> _alternar(ActividadAgenda actividad, bool? valor) async {
    final nuevas = <String>{..._confirmadas};
    if (valor == true) {
      nuevas.add(actividad.clave);
    } else {
      nuevas.remove(actividad.clave);
    }
    setState(() => _confirmadas = nuevas);
    await _storage.guardar(widget.perfilId, _hoy, nuevas);
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
      final hechas = lista.where((a) => _confirmadas.contains(a.clave)).length;
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
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text('$hechas de ${lista.length} actividades confirmadas'),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(value: hechas / lista.length),
                ],
              ),
            ),
            for (final a in lista)
              CheckboxListTile(
                value: _confirmadas.contains(a.clave),
                onChanged: (v) => _alternar(a, v),
                controlAffinity: ListTileControlAffinity.leading,
                title: Text(
                  a.titulo,
                  style: TextStyle(
                    decoration: _confirmadas.contains(a.clave)
                        ? TextDecoration.lineThrough
                        : null,
                  ),
                ),
                subtitle: Text(a.detalle),
                secondary: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      a.tipo == TipoActividad.medicamento
                          ? Icons.medication
                          : Icons.favorite_border,
                      size: 18,
                    ),
                    const SizedBox(width: 6),
                    Text(horaCorta(a.hora).isEmpty ? '--:--' : horaCorta(a.hora)),
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