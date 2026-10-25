import 'package:flutter/material.dart';
import '../models/alerta.dart';
import '../models/perfil.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';
import 'agenda_screen.dart';

/// Recordatorios y alertas del usuario (HU 9 y HU 10). Tocar un aviso lo marca como
/// leído y abre la Agenda del perfil al que corresponde.
class AlertasScreen extends StatefulWidget {
  final String token;
  final List<Perfil> perfiles;

  const AlertasScreen({super.key, required this.token, required this.perfiles});

  @override
  State<AlertasScreen> createState() => _AlertasScreenState();
}

class _AlertasScreenState extends State<AlertasScreen> {
  final _api = ApiService();
  List<Alerta>? _alertas;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarAlertas(widget.token);
      if (!mounted) return;
      setState(() {
        _alertas = lista;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  Perfil? _perfilDe(String perfilId) {
    for (final p in widget.perfiles) {
      if (p.id == perfilId) return p;
    }
    return null;
  }

  Future<void> _abrir(Alerta alerta) async {
    if (!alerta.estaLeida) {
      try {
        await _api.marcarAlertaLeida(widget.token, alerta.id);
      } catch (_) {
        // Si falla, el aviso sigue sin leer; no se bloquea la navegación.
      }
    }
    if (!mounted) return;
    final perfil = _perfilDe(alerta.perfilId);
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => AgendaScreen(
          token: widget.token,
          perfilId: alerta.perfilId,
          puedeConfirmar: perfil?.puedeConfirmar ?? false,
        ),
      ),
    );
    await _cargar();
  }

  @override
  Widget build(BuildContext context) {
    final lista = _alertas;
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
            'No tienes avisos. Aquí aparecerán los recordatorios y las alertas de actividades sin confirmar.',
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
            final a = lista[i];
            final creada = DateTime.tryParse(a.creadaEn)?.toLocal();
            return ListTile(
              leading: Icon(
                a.esAlerta ? Icons.warning_amber_rounded : Icons.alarm,
                color: a.esAlerta ? Colors.orange.shade800 : null,
              ),
              title: Text(
                a.mensaje,
                style: TextStyle(
                  fontWeight: a.estaLeida ? FontWeight.normal : FontWeight.bold,
                ),
              ),
              subtitle: Text(
                [
                  if (a.esAlerta) 'Alerta de nivel ${a.nivel}' else 'Recordatorio',
                  if (creada != null) fechaHoraCorta(creada),
                ].join(' · '),
              ),
              trailing: a.estaLeida
                  ? null
                  : const Icon(Icons.circle, size: 12, color: Colors.teal),
              onTap: () => _abrir(a),
            );
          },
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Avisos')),
      body: cuerpo,
    );
  }
}
