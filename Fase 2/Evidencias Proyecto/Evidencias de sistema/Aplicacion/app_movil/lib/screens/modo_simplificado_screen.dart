import 'dart:async';
import 'package:flutter/material.dart';
import '../models/actividad.dart';
import '../models/perfil.dart';
import '../services/api_service.dart';
import '../utils/hora.dart';

/// Interfaz simplificada para el perfil dependiente (HU 11): texto y botones grandes,
/// solo las actividades de hoy y confirmación con un toque. No permite editar ni
/// borrar nada. Se entra desde el Home de la cuenta del titular y se sale con el botón
/// de salir (pide confirmar, para que no se salga por accidente).
class ModoSimplificadoScreen extends StatefulWidget {
  final String token;
  final Perfil perfil;

  const ModoSimplificadoScreen({
    super.key,
    required this.token,
    required this.perfil,
  });

  @override
  State<ModoSimplificadoScreen> createState() => _ModoSimplificadoScreenState();
}

class _ModoSimplificadoScreenState extends State<ModoSimplificadoScreen> {
  final _api = ApiService();
  Timer? _temporizador;

  List<Actividad>? _actividades;
  String? _error;
  String? _confirmando; // id de la actividad que se está confirmando

  @override
  void initState() {
    super.initState();
    _cargar();
    // Cada minuto se vuelve a consultar, para ver las actividades que se generan solas.
    _temporizador =
        Timer.periodic(const Duration(minutes: 1), (_) => _cargar());
  }

  @override
  void dispose() {
    _temporizador?.cancel();
    super.dispose();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.listarActividades(
        widget.token,
        widget.perfil.id,
        DateTime.now(),
      );
      if (!mounted) return;
      setState(() {
        _actividades = lista;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      // Si ya hay una lista en pantalla se conserva; el error solo se muestra al inicio.
      if (_actividades == null) setState(() => _error = e.toString());
    }
  }

  Future<void> _confirmar(Actividad actividad) async {
    if (!widget.perfil.puedeConfirmar || _confirmando != null) return;
    setState(() => _confirmando = actividad.id);
    try {
      final actualizada =
          await _api.confirmarActividad(widget.token, actividad.id);
      if (!mounted) return;
      setState(() {
        final lista = _actividades;
        if (lista != null) {
          final i = lista.indexWhere((a) => a.id == actividad.id);
          if (i >= 0) lista[i] = actualizada;
        }
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      if (mounted) setState(() => _confirmando = null);
    }
  }

  Future<void> _pedirSalir() async {
    final salir = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('¿Salir del modo simplificado?'),
        content: const Text('Se vuelve al menú completo.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Quedarme'),
          ),
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Salir'),
          ),
        ],
      ),
    );
    if (salir == true && mounted) Navigator.of(context).pop();
  }

  Widget _tarjeta(Actividad a) {
    final hora = horaCorta(a.hora);
    final hecha = a.estaConfirmada;
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  a.origenTipo == 'medicamento'
                      ? Icons.medication
                      : Icons.favorite_border,
                  size: 36,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    a.titulo,
                    style: const TextStyle(
                        fontSize: 28, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              [if (hora.isNotEmpty) 'A las $hora', if (a.detalle != null) a.detalle!]
                  .join(' · '),
              style: const TextStyle(fontSize: 20),
            ),
            const SizedBox(height: 16),
            if (hecha)
              Row(
                children: [
                  Icon(Icons.check_circle,
                      size: 40, color: Colors.green.shade700),
                  const SizedBox(width: 12),
                  Text(
                    'Hecha',
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Colors.green.shade700,
                    ),
                  ),
                ],
              )
            else if (widget.perfil.puedeConfirmar)
              SizedBox(
                width: double.infinity,
                height: 72,
                child: FilledButton.icon(
                  onPressed: _confirmando == null ? () => _confirmar(a) : null,
                  icon: const Icon(Icons.check, size: 32),
                  label: Text(
                    _confirmando == a.id ? 'Guardando...' : 'Hecho',
                    style: const TextStyle(fontSize: 26),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lista = _actividades;
    Widget cuerpo;

    if (_error != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            _error!,
            style: const TextStyle(fontSize: 22, color: Colors.red),
            textAlign: TextAlign.center,
          ),
        ),
      );
    } else if (lista == null) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else if (lista.isEmpty) {
      cuerpo = const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Hoy no hay actividades.',
            style: TextStyle(fontSize: 26),
            textAlign: TextAlign.center,
          ),
        ),
      );
    } else {
      // Primero las que faltan, después las hechas; dentro de cada grupo, por hora.
      final ordenadas = [...lista]..sort((x, y) {
          if (x.estaConfirmada != y.estaConfirmada) {
            return x.estaConfirmada ? 1 : -1;
          }
          return x.hora.compareTo(y.hora);
        });
      final hechas = lista.where((a) => a.estaConfirmada).length;
      cuerpo = RefreshIndicator(
        onRefresh: _cargar,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              'Hoy, ${fechaCorta(DateTime.now())}',
              style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              '$hechas de ${lista.length} hechas',
              style: const TextStyle(fontSize: 22),
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: hechas / lista.length,
              minHeight: 14,
            ),
            const SizedBox(height: 20),
            if (!widget.perfil.puedeConfirmar)
              const Padding(
                padding: EdgeInsets.only(bottom: 16),
                child: Text(
                  'Este perfil es de solo lectura: no se pueden confirmar actividades.',
                  style: TextStyle(fontSize: 20),
                ),
              ),
            for (final a in ordenadas) _tarjeta(a),
          ],
        ),
      );
    }

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _pedirSalir();
      },
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: false,
          title: Text(
            widget.perfil.nombre,
            style: const TextStyle(fontSize: 24),
          ),
          actions: [
            IconButton(
              onPressed: _pedirSalir,
              icon: const Icon(Icons.exit_to_app, size: 32),
              tooltip: 'Salir del modo simplificado',
            ),
          ],
        ),
        body: cuerpo,
      ),
    );
  }
}
