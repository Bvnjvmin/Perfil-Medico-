/// Modelos del Sprint 5. Coinciden con los esquemas de `backend/app/schemas/sprint5.py`
/// (ver `Contrato_API_Sprint5.md`).

double? _decimal(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString());
}

/// Evento de seguridad (HU 14 y HU 19): botón de asistencia, SOS, caída, batería baja,
/// inactividad o salida de una geocerca.
class EventoSeguridad {
  final String id;
  final String perfilId;
  final String perfilNombre;
  final String tipo; // asistencia | sos | caida | bateria_baja | inactividad | geocerca_salida
  final String origen; // app | pulsera | sistema
  final String mensaje;
  final String creadoEn;
  final String? atendidoEn;

  const EventoSeguridad({
    required this.id,
    required this.perfilId,
    required this.perfilNombre,
    required this.tipo,
    required this.origen,
    required this.mensaje,
    required this.creadoEn,
    this.atendidoEn,
  });

  bool get atendido => atendidoEn != null;

  /// Nombre corto para mostrar en pantalla.
  String get titulo {
    switch (tipo) {
      case 'asistencia':
        return 'Pidió ayuda';
      case 'sos':
        return 'Botón SOS';
      case 'caida':
        return 'Posible caída';
      case 'bateria_baja':
        return 'Batería baja';
      case 'inactividad':
        return 'Sin movimiento';
      case 'geocerca_salida':
        return 'Salió de una zona';
      default:
        return 'Evento';
    }
  }

  /// Los eventos que implican un riesgo inmediato se destacan en rojo.
  bool get esUrgente => tipo == 'sos' || tipo == 'caida' || tipo == 'asistencia';

  factory EventoSeguridad.fromJson(Map<String, dynamic> json) {
    return EventoSeguridad(
      id: json['id'].toString(),
      perfilId: (json['perfil_id'] ?? '').toString(),
      perfilNombre: (json['perfil_nombre'] ?? '').toString(),
      tipo: (json['tipo'] ?? '').toString(),
      origen: (json['origen'] ?? '').toString(),
      mensaje: (json['mensaje'] ?? '').toString(),
      creadoEn: (json['creado_en'] ?? '').toString(),
      atendidoEn: json['atendido_en']?.toString(),
    );
  }
}

/// Medición de un indicador de salud (HU 12 y HU 18).
class Indicador {
  final String id;
  final String tipo; // peso | presion | glucosa | frecuencia_cardiaca
  final double valor;
  final double? valorSecundario; // diastólica, solo en la presión
  final String unidad;
  final String fuente; // manual | pulsera
  final String medidoEn;
  final String? nota;

  const Indicador({
    required this.id,
    required this.tipo,
    required this.valor,
    this.valorSecundario,
    required this.unidad,
    required this.fuente,
    required this.medidoEn,
    this.nota,
  });

  static const tipos = ['peso', 'presion', 'glucosa', 'frecuencia_cardiaca'];

  static String nombreDeTipo(String tipo) {
    switch (tipo) {
      case 'peso':
        return 'Peso';
      case 'presion':
        return 'Presión arterial';
      case 'glucosa':
        return 'Glucosa';
      case 'frecuencia_cardiaca':
        return 'Frecuencia cardíaca';
      default:
        return tipo;
    }
  }

  /// "128/82 mmHg", "68 kg", etc.
  String get texto {
    final principal = _sinCeros(valor);
    if (valorSecundario != null) {
      return '$principal/${_sinCeros(valorSecundario!)} $unidad';
    }
    return '$principal $unidad';
  }

  factory Indicador.fromJson(Map<String, dynamic> json) {
    return Indicador(
      id: json['id'].toString(),
      tipo: (json['tipo'] ?? '').toString(),
      valor: _decimal(json['valor']) ?? 0,
      valorSecundario: _decimal(json['valor_secundario']),
      unidad: (json['unidad'] ?? '').toString(),
      fuente: (json['fuente'] ?? 'manual').toString(),
      medidoEn: (json['medido_en'] ?? '').toString(),
      nota: json['nota']?.toString(),
    );
  }
}

/// 68.0 -> "68"; 68.5 -> "68.5".
String _sinCeros(double v) =>
    v == v.roundToDouble() ? v.toStringAsFixed(0) : v.toStringAsFixed(1);

class PuntoSerie {
  final DateTime? medidoEn;
  final double valor;
  final double? valorSecundario;

  const PuntoSerie({this.medidoEn, required this.valor, this.valorSecundario});

  factory PuntoSerie.fromJson(Map<String, dynamic> json) {
    return PuntoSerie(
      medidoEn: DateTime.tryParse((json['medido_en'] ?? '').toString())?.toLocal(),
      valor: _decimal(json['valor']) ?? 0,
      valorSecundario: _decimal(json['valor_secundario']),
    );
  }
}

/// Serie lista para graficar (`GET .../indicadores/serie`).
class SerieIndicador {
  final String tipo;
  final String unidad;
  final List<PuntoSerie> puntos;
  final double? minimo;
  final double? maximo;
  final double? promedio;

  const SerieIndicador({
    required this.tipo,
    required this.unidad,
    required this.puntos,
    this.minimo,
    this.maximo,
    this.promedio,
  });

  factory SerieIndicador.fromJson(Map<String, dynamic> json) {
    return SerieIndicador(
      tipo: (json['tipo'] ?? '').toString(),
      unidad: (json['unidad'] ?? '').toString(),
      puntos: ((json['puntos'] as List?) ?? [])
          .map((e) => PuntoSerie.fromJson(e as Map<String, dynamic>))
          .toList(),
      minimo: _decimal(json['minimo']),
      maximo: _decimal(json['maximo']),
      promedio: _decimal(json['promedio']),
    );
  }
}

/// Cumplimiento de un conjunto de actividades (HU 13).
class CumplimientoParcial {
  final int total;
  final int cumplidas;
  final double? porcentaje; // null si no hubo actividades exigibles

  const CumplimientoParcial({
    required this.total,
    required this.cumplidas,
    this.porcentaje,
  });

  factory CumplimientoParcial.fromJson(Map<String, dynamic> json) {
    return CumplimientoParcial(
      total: (json['total'] as num?)?.toInt() ?? 0,
      cumplidas: (json['cumplidas'] as num?)?.toInt() ?? 0,
      porcentaje: _decimal(json['porcentaje']),
    );
  }
}

class CumplimientoDia extends CumplimientoParcial {
  final DateTime? fecha;

  const CumplimientoDia({
    this.fecha,
    required super.total,
    required super.cumplidas,
    super.porcentaje,
  });

  factory CumplimientoDia.fromJson(Map<String, dynamic> json) {
    final base = CumplimientoParcial.fromJson(json);
    return CumplimientoDia(
      fecha: DateTime.tryParse((json['fecha'] ?? '').toString()),
      total: base.total,
      cumplidas: base.cumplidas,
      porcentaje: base.porcentaje,
    );
  }
}

class Cumplimiento extends CumplimientoParcial {
  final Map<String, CumplimientoParcial> porCategoria;
  final List<CumplimientoDia> porDia;

  const Cumplimiento({
    required super.total,
    required super.cumplidas,
    super.porcentaje,
    required this.porCategoria,
    required this.porDia,
  });

  static String nombreDeCategoria(String c) {
    switch (c) {
      case 'medicamentos':
        return 'Medicamentos';
      case 'hidratacion':
        return 'Hidratación';
      case 'alimentacion':
        return 'Alimentación';
      case 'otras':
        return 'Otras rutinas';
      default:
        return c;
    }
  }

  factory Cumplimiento.fromJson(Map<String, dynamic> json) {
    final base = CumplimientoParcial.fromJson(json);
    final categorias = <String, CumplimientoParcial>{};
    final bruto = json['por_categoria'];
    if (bruto is Map) {
      bruto.forEach((k, v) {
        categorias[k.toString()] =
            CumplimientoParcial.fromJson(v as Map<String, dynamic>);
      });
    }
    return Cumplimiento(
      total: base.total,
      cumplidas: base.cumplidas,
      porcentaje: base.porcentaje,
      porCategoria: categorias,
      porDia: ((json['por_dia'] as List?) ?? [])
          .map((e) => CumplimientoDia.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// Pulsera GPS vinculada a un perfil (HU 17).
class Pulsera {
  final String id;
  final String identificador;
  final String nombre;
  final String? modelo;
  final bool activa;
  final int? bateriaPct;
  final String? ultimaConexion;

  const Pulsera({
    required this.id,
    required this.identificador,
    required this.nombre,
    this.modelo,
    required this.activa,
    this.bateriaPct,
    this.ultimaConexion,
  });

  factory Pulsera.fromJson(Map<String, dynamic> json) {
    return Pulsera(
      id: json['id'].toString(),
      identificador: (json['identificador'] ?? '').toString(),
      nombre: (json['nombre'] ?? '').toString(),
      modelo: json['modelo']?.toString(),
      activa: json['activa'] as bool? ?? true,
      bateriaPct: (json['bateria_pct'] as num?)?.toInt(),
      ultimaConexion: json['ultima_conexion']?.toString(),
    );
  }
}

class Posicion {
  final double latitud;
  final double longitud;
  final String registradaEn;

  const Posicion({
    required this.latitud,
    required this.longitud,
    required this.registradaEn,
  });

  factory Posicion.fromJson(Map<String, dynamic> json) {
    return Posicion(
      latitud: _decimal(json['latitud']) ?? 0,
      longitud: _decimal(json['longitud']) ?? 0,
      registradaEn: (json['registrada_en'] ?? '').toString(),
    );
  }
}

/// Última ubicación conocida (`GET /perfiles/{id}/ubicacion`).
class Ubicacion {
  final Pulsera? pulsera;
  final Posicion? posicion;
  final List<String> dentroDe; // nombres de las geocercas donde está

  const Ubicacion({this.pulsera, this.posicion, this.dentroDe = const []});

  factory Ubicacion.fromJson(Map<String, dynamic> json) {
    return Ubicacion(
      pulsera: json['pulsera'] is Map<String, dynamic>
          ? Pulsera.fromJson(json['pulsera'] as Map<String, dynamic>)
          : null,
      posicion: json['posicion'] is Map<String, dynamic>
          ? Posicion.fromJson(json['posicion'] as Map<String, dynamic>)
          : null,
      dentroDe: ((json['dentro_de'] as List?) ?? []).map((e) => e.toString()).toList(),
    );
  }
}

class Geocerca {
  final String id;
  final String nombre;
  final double latitud;
  final double longitud;
  final int radioM;
  final bool activa;

  const Geocerca({
    required this.id,
    required this.nombre,
    required this.latitud,
    required this.longitud,
    required this.radioM,
    required this.activa,
  });

  factory Geocerca.fromJson(Map<String, dynamic> json) {
    return Geocerca(
      id: json['id'].toString(),
      nombre: (json['nombre'] ?? '').toString(),
      latitud: _decimal(json['latitud']) ?? 0,
      longitud: _decimal(json['longitud']) ?? 0,
      radioM: (json['radio_m'] as num?)?.toInt() ?? 0,
      activa: json['activa'] as bool? ?? true,
    );
  }
}

/// Consulta al asistente de IA (HU 15). Mostrar siempre [aviso] bajo la respuesta.
class ConsultaIA {
  final String id;
  final String pregunta;
  final String respuesta;
  final String proveedor; // simulado | anthropic | reglas
  final String creadaEn;
  final String aviso;

  const ConsultaIA({
    required this.id,
    required this.pregunta,
    required this.respuesta,
    required this.proveedor,
    required this.creadaEn,
    required this.aviso,
  });

  /// La respuesta fija de urgencia no pasa por el modelo.
  bool get esUrgencia => proveedor == 'reglas';

  factory ConsultaIA.fromJson(Map<String, dynamic> json) {
    return ConsultaIA(
      id: json['id'].toString(),
      pregunta: (json['pregunta'] ?? '').toString(),
      respuesta: (json['respuesta'] ?? '').toString(),
      proveedor: (json['proveedor'] ?? '').toString(),
      creadaEn: (json['creada_en'] ?? '').toString(),
      aviso: (json['aviso'] ??
              'Orientación general: no reemplaza a un profesional de la salud. Ante una urgencia llama al 131.')
          .toString(),
    );
  }
}
