import 'package:flutter/material.dart';
import '../models/sprint5.dart';

/// Barras de cumplimiento por día (HU 13). Sin paquetes externos.
class BarrasCumplimiento extends StatelessWidget {
  final List<CumplimientoDia> dias;
  const BarrasCumplimiento({super.key, required this.dias});

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).colorScheme.primary;
    return SizedBox(
      height: 170,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          for (final d in dias)
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 3),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Text(
                      d.porcentaje == null ? '–' : '${d.porcentaje!.round()}%',
                      style: const TextStyle(fontSize: 11),
                    ),
                    const SizedBox(height: 2),
                    Container(
                      height: 110 * ((d.porcentaje ?? 0) / 100).clamp(0.0, 1.0).toDouble(),
                      decoration: BoxDecoration(
                        color: d.porcentaje == null ? Colors.grey.shade300 : color,
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      d.fecha == null
                          ? ''
                          : '${d.fecha!.day.toString().padLeft(2, '0')}/${d.fecha!.month.toString().padLeft(2, '0')}',
                      style: const TextStyle(fontSize: 10),
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

/// Línea con la evolución de un indicador (HU 18). Si es presión, dibuja también la
/// diastólica con un trazo más claro.
class LineaSerie extends StatelessWidget {
  final SerieIndicador serie;
  const LineaSerie({super.key, required this.serie});

  @override
  Widget build(BuildContext context) {
    final esquema = Theme.of(context).colorScheme;
    return SizedBox(
      height: 180,
      width: double.infinity,
      child: CustomPaint(
        painter: _LineaPainter(serie.puntos, esquema.primary, esquema.outlineVariant),
      ),
    );
  }
}

class _LineaPainter extends CustomPainter {
  final List<PuntoSerie> puntos;
  final Color color;
  final Color colorSecundario;
  _LineaPainter(this.puntos, this.color, this.colorSecundario);

  @override
  void paint(Canvas canvas, Size size) {
    if (puntos.isEmpty) return;
    final valores = <double>[
      for (final p in puntos) p.valor,
      for (final p in puntos)
        if (p.valorSecundario != null) p.valorSecundario!,
    ];
    var minimo = valores.reduce((a, b) => a < b ? a : b);
    var maximo = valores.reduce((a, b) => a > b ? a : b);
    if (maximo - minimo < 1) {
      minimo -= 1;
      maximo += 1;
    }
    const margen = 12.0;
    final ancho = size.width - margen * 2;
    final alto = size.height - margen * 2;

    Offset punto(int i, double v) {
      final x = puntos.length == 1 ? size.width / 2 : margen + ancho * i / (puntos.length - 1);
      final y = margen + alto * (1 - (v - minimo) / (maximo - minimo));
      return Offset(x, y);
    }

    void trazar(double? Function(PuntoSerie) valorDe, Color c) {
      final linea = Paint()
        ..color = c
        ..strokeWidth = 2.5
        ..style = PaintingStyle.stroke;
      final relleno = Paint()..color = c;
      Offset? anterior;
      for (var i = 0; i < puntos.length; i++) {
        final v = valorDe(puntos[i]);
        if (v == null) continue;
        final actual = punto(i, v);
        if (anterior != null) canvas.drawLine(anterior, actual, linea);
        canvas.drawCircle(actual, 3.5, relleno);
        anterior = actual;
      }
    }

    final eje = Paint()
      ..color = Colors.grey.shade300
      ..strokeWidth = 1;
    canvas.drawLine(Offset(margen, size.height - margen), Offset(size.width - margen, size.height - margen), eje);
    trazar((p) => p.valorSecundario, colorSecundario);
    trazar((p) => p.valor, color);
  }

  @override
  bool shouldRepaint(covariant _LineaPainter anterior) => anterior.puntos != puntos;
}
