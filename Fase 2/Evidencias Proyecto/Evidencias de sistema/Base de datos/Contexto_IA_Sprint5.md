# Contexto del asistente de IA (HU 15)

**Rol:** Sergio Ocares, IA y Product Owner. Este documento define qué sabe el asistente, qué nunca ve, cómo responde y qué límites tiene. Lo implementa `app/services/ia.py`.

## Qué es y qué no es

Responde dudas generales sobre los medicamentos, rutinas e indicadores del perfil consultado. **No diagnostica, no receta, no cambia dosis.** Cada respuesta muestra el aviso: «Orientación general: no reemplaza a un profesional de la salud. Ante una urgencia llama al 131.»

## Datos que se envían al modelo

| Dato | ¿Se envía? | Detalle |
|---|---|---|
| Nombre de pila | Sí | Solo el primer nombre |
| Edad | Sí | Calculada; no se envía la fecha de nacimiento |
| Alergias | Sí | Las del perfil |
| Medicamentos activos | Sí | Nombre y dosis |
| Cumplimiento de los últimos 7 días | Sí | Solo porcentajes |
| Últimos indicadores (peso, presión, glucosa, pulso) | Solo si el usuario tiene `puede_ver_indicadores` | Si no tiene el permiso, no se incluyen |
| RUT, correo, teléfonos, contactos de emergencia | **Nunca** | |
| Ubicación y pulsera | **Nunca** | |

## Instrucciones del sistema (resumen)

Español neutro, respuestas breves (máximo unos 600 tokens), lenguaje simple. No dar diagnósticos ni indicar dosis; ante síntomas de cuidado recomendar consultar a un profesional; no inventar datos que no estén en el contexto; si no se sabe, decirlo.

## Regla de urgencia

Si la pregunta contiene señales de urgencia (dolor de pecho, dificultad para respirar, desmayo, sangrado abundante, intento de hacerse daño, etc.), **no se consulta al modelo**: se responde un texto fijo que indica llamar al 131 (SAMU) o al *4141 (Salud Responde) y avisar a un cuidador. La lista de palabras está en `app/services/ia.py` y puede ampliarse; las pruebas `test_ia.py` la cubren.

## Límites

- 30 consultas por usuario al día (configurable, `IA_MAX_CONSULTAS_DIA`); sobre eso, error 429.
- Si el proveedor falla, error 503 y no se guarda la consulta.
- Se guarda el historial (pregunta, respuesta, proveedor) por perfil, visible para quien consultó.

## Proveedores

- `simulado` (por defecto): no genera respuestas médicas; devuelve un texto fijo que repite los datos registrados del perfil y la pregunta, marcado como «Modo simulado», y recomienda consultar a un profesional. No usa red ni clave. Sirve para desarrollar, probar los permisos, los límites y la regla de urgencia, y para mostrar el flujo en la demo sin costo. **La calidad de las respuestas solo se puede evaluar con el proveedor `anthropic`.**
- `anthropic`: llama a la API de Anthropic con el modelo `IA_MODELO` (por defecto `claude-haiku-5-5`). Requiere `IA_API_KEY` y salida a internet.

**Decisión pendiente (Sergio):** usar solo el simulado en la entrega, o crear una clave de API para la demo. La clave nunca se sube al repositorio; va en el `.env` local. El código de `anthropic` se probó con respuestas simuladas, **no** contra la API real.

## Riesgos y cómo se manejan

| Riesgo | Mitigación |
|---|---|
| El modelo da consejo médico indebido | Instrucciones del sistema, aviso fijo en cada respuesta, casos de prueba (`casos_prueba_ia.md`) |
| Urgencia respondida con lentitud o ambigüedad | Respuesta fija sin pasar por el modelo |
| Fuga de datos personales | Lista cerrada de datos enviados; RUT, correo y teléfonos nunca salen |
| Costo descontrolado | Límite diario por usuario y `IA_MAX_TOKENS` |
| El usuario toma la respuesta como indicación médica | Aviso visible en la app y copy de la pantalla |
