import 'package:flutter/material.dart';
import '../models/actividad.dart';
import '../models/perfil.dart';
import '../services/api_service.dart';
import 'agenda_screen.dart';

class AvancePerfil {
  final Perfil perfil;
  final int confirmadas;
  final int pendientes;
  final int total;

  const AvancePerfil({
    required this.perfil,
    required this.confirmadas,
    required this.pendientes,
    required this.total,
  });

  double get progreso => total == 0 ? 0.0 : confirmadas / total;
  String get resumenTexto => '$confirmadas de $total confirmadas';

  /// Un elemento de `GET /panel` (HU 8): el backend ya trae los totales del día.
  factory AvancePerfil.desdePanel(Map<String, dynamic> json) {
    final datos = Map<String, dynamic>.from(json['perfil'] as Map);
    datos['mi_acceso'] = json['mi_acceso'];
    return AvancePerfil(
      perfil: Perfil.fromJson(datos),
      confirmadas: (json['confirmadas'] as num?)?.toInt() ?? 0,
      pendientes: (json['pendientes'] as num?)?.toInt() ?? 0,
      total: (json['total'] as num?)?.toInt() ?? 0,
    );
  }

  static AvancePerfil desdeActividades(
    Perfil perfil,
    List<Actividad> actividades,
  ) {
    final confirmadas = actividades.where((a) => a.estaConfirmada).length;
    final total = actividades.length;
    return AvancePerfil(
      perfil: perfil,
      confirmadas: confirmadas,
      pendientes: total - confirmadas,
      total: total,
    );
  }
}

class PanelScreen extends StatefulWidget {
  final String token;

  const PanelScreen({super.key, required this.token});

  @override
  State<PanelScreen> createState() => _PanelScreenState();
}

class _PanelScreenState extends State<PanelScreen> {
  final _api = ApiService();
  List<AvancePerfil>? _avances;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      // Una sola llamada (GET /panel) en vez de una por cada perfil.
      final panel = await _api.obtenerPanel(widget.token, DateTime.now());
      final resultados = panel.map(AvancePerfil.desdePanel).toList();

      if (!mounted) return;
      setState(() {
        _avances = resultados;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final lista = _avances;
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
        child: Text('No hay perfiles disponibles en el panel.'),
      );
    } else {
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: lista.length,
          itemBuilder: (context, i) {
            final item = lista[i];
            final p = item.perfil;
            final subtipoTexto =
                p.esTitular ? 'Titular' : (p.subtipo ?? 'Dependiente');

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                borderRadius: BorderRadius.circular(12),
                onTap: () async {
                  await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => AgendaScreen(
                        token: widget.token,
                        perfilId: p.id,
                        puedeConfirmar: p.puedeConfirmar,
                      ),
                    ),
                  );
                  await _cargar();
                },
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            p.nombre,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Chip(
                            label: Text(subtipoTexto),
                            visualDensity: VisualDensity.compact,
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(item.resumenTexto),
                      const SizedBox(height: 8),
                      LinearProgressIndicator(value: item.progreso),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Panel de dependientes')),
      body: cuerpo,
    );
  }
}
