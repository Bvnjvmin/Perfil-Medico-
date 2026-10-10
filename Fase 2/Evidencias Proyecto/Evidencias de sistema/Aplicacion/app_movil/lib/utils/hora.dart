import 'package:flutter/material.dart';

String _dos(int n) => n.toString().padLeft(2, '0');

/// "08:05:00": formato de hora que acepta el backend (campo `time` de Pydantic).
String horaParaApi(TimeOfDay t) => '${_dos(t.hour)}:${_dos(t.minute)}:00';

/// "08:05:00" -> "08:05" para mostrar en pantalla. Vacío si no hay hora.
String horaCorta(String? hora) {
  if (hora == null || hora.length < 5) return '';
  return hora.substring(0, 5);
}

/// "2026-10-08": formato de fecha que acepta el backend y que usamos de clave.
String fechaParaApi(DateTime d) => '${d.year}-${_dos(d.month)}-${_dos(d.day)}';

/// "08/10/2026" para mostrar en pantalla.
String fechaCorta(DateTime d) => '${_dos(d.day)}/${_dos(d.month)}/${d.year}';