import 'package:flutter/material.dart';
import '../models/sprint5.dart';
import '../services/api_sprint5.dart';

/// Asistente de IA (HU 15): orientación general sobre los datos del perfil. Siempre
/// muestra el aviso de que no reemplaza a un profesional de la salud.
class IaScreen extends StatefulWidget {
  final String token;
  final String perfilId;
  final String perfilNombre;

  const IaScreen({
    super.key,
    required this.token,
    required this.perfilId,
    required this.perfilNombre,
  });

  @override
  State<IaScreen> createState() => _IaScreenState();
}

class _IaScreenState extends State<IaScreen> {
  final _api = ApiSprint5();
  final _pregunta = TextEditingController();
  final _scroll = ScrollController();
  List<ConsultaIA> _consultas = [];
  bool _cargando = true;
  bool _enviando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  @override
  void dispose() {
    _pregunta.dispose();
    _scroll.dispose();
    super.dispose();
  }

  Future<void> _cargar() async {
    try {
      final lista = await _api.historialIA(widget.token, widget.perfilId);
      if (!mounted) return;
      // El backend entrega las más nuevas primero; en pantalla van de arriba hacia abajo.
      setState(() {
        _consultas = lista.reversed.toList();
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

  Future<void> _enviar() async {
    final texto = _pregunta.text.trim();
    if (texto.length < 3 || _enviando) return;
    setState(() => _enviando = true);
    try {
      final consulta = await _api.preguntarIA(widget.token, widget.perfilId, texto);
      if (!mounted) return;
      _pregunta.clear();
      setState(() => _consultas = [..._consultas, consulta]);
      await Future<void>.delayed(const Duration(milliseconds: 100));
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Widget _burbuja(ConsultaIA c) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Align(
          alignment: Alignment.centerRight,
          child: Container(
            margin: const EdgeInsets.only(left: 48, bottom: 6),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(c.pregunta),
          ),
        ),
        Container(
          margin: const EdgeInsets.only(right: 24, bottom: 16),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: c.esUrgencia ? Colors.red.shade50 : Colors.grey.shade100,
            border: c.esUrgencia ? Border.all(color: Colors.red.shade300) : null,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(c.respuesta),
              const SizedBox(height: 8),
              Text(c.aviso, style: const TextStyle(fontSize: 12, color: Colors.black54)),
            ],
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    Widget lista;
    if (_cargando) {
      lista = const Center(child: CircularProgressIndicator());
    } else if (_error != null) {
      lista = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: const TextStyle(color: Colors.red)),
        ),
      );
    } else if (_consultas.isEmpty) {
      lista = const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Pregunta sobre los medicamentos y las rutinas de este perfil. '
            'Es orientación general y no reemplaza a un profesional de la salud.',
            textAlign: TextAlign.center,
          ),
        ),
      );
    } else {
      lista = ListView(
        controller: _scroll,
        padding: const EdgeInsets.all(16),
        children: [for (final c in _consultas) _burbuja(c)],
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Asistente · ${widget.perfilNombre}')),
      body: Column(
        children: [
          Expanded(child: lista),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 4, 12, 8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _pregunta,
                      minLines: 1,
                      maxLines: 4,
                      maxLength: 1000,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _enviar(),
                      decoration: const InputDecoration(
                        hintText: 'Escribe tu pregunta',
                        counterText: '',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _enviando ? null : _enviar,
                    icon: _enviando
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send),
                    tooltip: 'Enviar',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
