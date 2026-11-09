import 'package:flutter/material.dart';
import '../services/api_sprint5.dart';

/// Botón grande «Necesito ayuda» (HU 14). Pide confirmar para evitar toques sin querer y
/// avisa al titular y a los cuidadores con alertas. Está pensado para el modo
/// simplificado, pero se puede usar en cualquier pantalla.
class BotonAyuda extends StatefulWidget {
  final String token;
  final String perfilId;
  const BotonAyuda({super.key, required this.token, required this.perfilId});

  @override
  State<BotonAyuda> createState() => _BotonAyudaState();
}

class _BotonAyudaState extends State<BotonAyuda> {
  final _api = ApiSprint5();
  bool _enviando = false;

  Future<void> _pedir() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('¿Pedir ayuda?', style: TextStyle(fontSize: 26)),
        content: const Text(
          'Se avisará a tus cuidadores ahora mismo.',
          style: TextStyle(fontSize: 20),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancelar', style: TextStyle(fontSize: 20)),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Sí, avisar', style: TextStyle(fontSize: 20)),
          ),
        ],
      ),
    );
    if (confirmar != true || !mounted) return;
    setState(() => _enviando = true);
    try {
      await _api.pedirAyuda(widget.token, widget.perfilId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Listo, avisamos a tus cuidadores.', style: TextStyle(fontSize: 20)),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 80,
      child: FilledButton.icon(
        style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
        onPressed: _enviando ? null : _pedir,
        icon: const Icon(Icons.sos, size: 36),
        label: Text(
          _enviando ? 'Avisando...' : 'Necesito ayuda',
          style: const TextStyle(fontSize: 28),
        ),
      ),
    );
  }
}
