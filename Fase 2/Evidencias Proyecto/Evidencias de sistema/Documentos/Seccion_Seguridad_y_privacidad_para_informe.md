# Sección «Seguridad y privacidad de los datos» — texto para el informe y el manual

**Preparado por:** Benjamín Leiva (dueño técnico de G14 y G18) · **Fecha:** 26-nov-2026
**Cómo usarlo:** copiar el texto de abajo al informe (Informe Final y, si aplica, el 2.6) y al manual. Las cifras salen del código y de las corridas del equipo; las marcadas con ⬜ se completan cuando exista la evidencia. Sergio revisa el aviso de privacidad; Matías, lo que ve el usuario en la app.

---

## Texto para el informe

### X. Seguridad y privacidad de los datos de salud

Perfil Médico+ guarda datos de salud de personas mayores y de niños: medicamentos, alergias, indicadores como presión o glucosa, y la ubicación de una pulsera. La ley chilena los considera datos sensibles. Por eso la seguridad se trabajó como un requisito del proyecto y no como un detalle técnico. **El equipo no afirma que los datos sean invulnerables:** ningún sistema puede prometer eso. Lo que se hizo fue identificar las amenazas, aplicar controles y probarlos, y declarar con claridad lo que queda pendiente.

**Amenazas consideradas.** Robo o adivinación de contraseñas, acceso de una persona a un perfil que no es suyo, robo de la sesión desde el celular, acceso a la base de datos desde la red, fuga de datos hacia el asistente de IA o hacia los registros del servidor, y dependencias de software con fallas conocidas.

**Controles aplicados y verificados.**

| Amenaza | Medida |
|---|---|
| Robo de contraseñas | Las contraseñas se guardan con hash bcrypt y nunca se devuelven. El inicio de sesión se bloquea con un error 429 tras 5 intentos fallidos en 15 minutos |
| Acceso a datos ajenos | Cada ruta valida el permiso del vínculo con el perfil: una cuenta ajena recibe 404 y sin permiso, 403. Hay pruebas automáticas de esto |
| Robo de sesión | Token firmado que vence a las 24 horas; en el celular se guarda en el almacenamiento cifrado de Android |
| Suplantación de sesiones | La API no arranca con una clave de firma de ejemplo o de menos de 32 caracteres |
| Acceso a la base de datos | El puerto de PostgreSQL queda solo en el equipo local (`127.0.0.1`) |
| Fuga hacia la IA | La IA recibe un contexto mínimo: sin RUT, correo, teléfonos, ubicación ni pulsera. Una pregunta de urgencia recibe una respuesta fija con el 131 sin consultar al modelo. Hay un límite de 30 consultas al día por usuario |
| Fuga por los registros | El registro de avisos no escribe el texto, que puede nombrar medicamentos |
| Sitios web que llaman a la API | El acceso desde otros orígenes web está cerrado por defecto |
| Dependencias vulnerables | Un análisis con `pip-audit` encontró que la biblioteca que firma las sesiones (PyJWT 2.7.0) tenía 17 vulnerabilidades conocidas; se actualizó a la 2.15.1. Fue la única dependencia con hallazgos entre las 39 revisadas |
| Secretos en el repositorio | Las claves viven en un `.env` local que no se sube; los datos de prueba son ficticios |

Estos controles tienen 226 pruebas automáticas que pasan (216 del sistema y 10 de seguridad). ⬜ *Agregar la captura de la corrida con Docker cuando se repita D4 con el parche.*

**Datos personales y la ley.** La Ley 21.719 reforma la Ley 19.628 y trata los datos de salud como sensibles. La Ley 21.855, publicada en el Diario Oficial el 23 de noviembre de 2026, postergó su entrada en vigencia del 1 de diciembre de 2026 al **15 de octubre de 2027**. Aunque aún no rija, el proyecto aplica sus principios desde ahora: **minimización** (a la IA solo se envía lo necesario), **control de acceso por perfil** y **medidas de seguridad proporcionales** al riesgo. Quedan como trabajo futuro el aviso de privacidad y el consentimiento dentro de la app, guardar el consentimiento en el servidor y las funciones de descargar y eliminar la cuenta. *Este texto no es asesoría legal.*

**Datos que salen del sistema.** Cuando el asistente usa el modelo real (Claude Haiku 5.5, de Anthropic), el contexto mínimo de cada consulta viaja hacia la API de esa empresa, un servicio externo y fuera de Chile. En la demostración el asistente corre en modo simulado y no envía nada. Este flujo debe declararse en el aviso de privacidad.

**Límites declarados (trabajo futuro).** HTTPS en producción (la demostración es local con `http`); cifrado de los datos en reposo; registro de auditoría de accesos; revocación de sesiones al cerrar sesión (hoy solo se borra el token del celular); respaldos y plan de recuperación; el RUT, que es opcional, se guarda en texto plano; y el token de la pulsera viaja en la URL porque así lo envía el servidor Traccar. El límite de intentos de inicio de sesión vive en la memoria de un proceso, y detrás de un proxy vería una sola dirección IP.

**Alcance de la revisión.** Fue una revisión del código y de las dependencias, no una auditoría ni una prueba de intrusión.

---

## Evidencia que conviene capturar (cuando apliques el parche)

| # | Qué probar | Resultado esperado | Captura |
|---|---|---|---|
| E1 | Quitar la `SECRET_KEY` del `.env` (o dejar la de ejemplo) y hacer `docker compose up` | La API se cae con el mensaje «SECRET_KEY insegura». Volver a poner una clave real | `S5_SEG1_clave_insegura.png` |
| E2 | Iniciar sesión 6 veces con una contraseña incorrecta | La sexta responde **429** («Demasiados intentos fallidos»), aun con la contraseña correcta. Esperar 15 min o reiniciar la API | `S5_SEG2_login_429.png` |
| E3 | `docker compose ps` | El puerto de la base se ve como `127.0.0.1:5432->5432` | `S5_SEG3_puerto_base.png` |
| E4 | Llamar a la API con la cabecera `Origin: https://sitio-malicioso.example` | La respuesta no trae `access-control-allow-origin` | `S5_SEG4_cors.png` |
| E5 | `pip-audit -r requirements.txt` | Sin vulnerabilidades conocidas (con PyJWT 2.15.1) | `S5_SEG5_pip_audit.png` |

Ejemplo para E4: `curl -i -H "Origin: https://sitio-malicioso.example" http://localhost:8000/health`

## Qué decir en 30 segundos (diapositiva de seguridad)

> «Los datos de salud son sensibles, así que diseñamos pensando en las amenazas. Protegemos las contraseñas, aislamos cada perfil, limitamos lo que se envía a la IA y mantenemos las claves fuera del código. Además revisamos las dependencias y corregimos una biblioteca de sesiones con vulnerabilidades conocidas. No prometemos invulnerabilidad: lo que falta, como el cifrado en reposo, HTTPS en producción y la auditoría de accesos, está declarado como trabajo futuro.»
