import 'package:flutter/material.dart';
import '../models/sprint5.dart';
import '../services/api_sprint5.dart';
import '../widgets/graficos.dart';

/// Historial de cumplimiento (HU 13): porcentaje general, por categoría y por día.
class CumplimientoScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final String perfilNombre;

  const CumplimientoScreen({
    super.key,
    required this.token,
    required this.perfilId,
    required this.perfilNombre,
  });

  @override
  State<CumplimientoScreen> createState() => _CumplimientoScreenState();
}

class _CumplimientoScreenState extends State<CumplimientoScreen> {
  final _api = ApiSprint5();
  Cumplimiento? _datos;
  String? _error;
  int _dias = 7;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    setState(() {
      _datos = null;
      _error = null;
    });
    try {
      final hoy = DateTime.now();
      final datos = await _api.cumplimiento(
        widget.token,
        widget.perfilId,
        desde: hoy.subtract(Duration(days: _dias - 1)),
        hasta: hoy,
      );
      if (!mounted) return;
      setState(() => _datos = datos);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  String _porcentaje(CumplimientoParcial p) =>
      p.porcentaje == null ? 'Sin datos' : '${p.porcentaje!.round()} %';

  @override
  Widget build(BuildContext context) {
    final datos = _datos;
    Widget cuerpo;

    if (_error != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: const TextStyle(color: Colors.red)),
        ),
      );
    } else if (datos == null) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else {
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Center(
              child: SegmentedButton<int>(
                segments: const [
                  ButtonSegment(value: 7, label: Text('7 días')),
                  ButtonSegment(value: 14, label: Text('14 días')),
                  ButtonSegment(value: 30, label: Text('30 días')),
                ],
                selected: {_dias},
                onSelectionChanged: (s) {
                  _dias = s.first;
                  _cargar();
                },
              ),
            ),
            const SizedBox(height: 20),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text(
                      _porcentaje(datos),
                      style: const TextStyle(fontSize: 44, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      datos.total == 0
                          ? 'Aún no hay actividades en este período'
                          : '${datos.cumplidas} de ${datos.total} actividades cumplidas',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (datos.porDia.isNotEmpty) ...[
              const Text('Por día', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              // Con 30 barras no cabe el texto: se muestran solo los últimos 14 días.
              BarrasCumplimiento(
                dias: datos.porDia.length > 14
                    ? datos.porDia.sublist(datos.porDia.length - 14)
                    : datos.porDia,
              ),
              const SizedBox(height: 16),
            ],
            const Text('Por categoría', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            for (final entrada in datos.porCategoria.entries)
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(Cumplimiento.nombreDeCategoria(entrada.key)),
                subtitle: LinearProgressIndicator(
                  value: ((entrada.value.porcentaje ?? 0) / 100).clamp(0.0, 1.0).toDouble(),
                  minHeight: 8,
                ),
                trailing: Text(_porcentaje(entrada.value)),
              ),
            const SizedBox(height: 8),
            const Text(
              'Cuentan las actividades confirmadas, vencidas y las pendientes de días pasados. '
              'Las omitidas y las de hoy que aún no llegan a su hora no cuentan.',
              style: TextStyle(fontSize: 12, color: Colors.black54),
            ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Cumplimiento · ${widget.perfilNombre}')),
      body: cuerpo,
    );
  }
}
