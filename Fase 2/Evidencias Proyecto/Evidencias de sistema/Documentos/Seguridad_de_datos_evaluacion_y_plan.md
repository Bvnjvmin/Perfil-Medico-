# Seguridad de los datos de salud — evaluación y plan antes del 4-dic

**Para:** Benjamín (dueño técnico), Sergio (informe y diapositiva), Matías (app) · **Fecha:** 23-nov-2026
**Actualización del 26-nov:** la Ley 21.719 se postergó al **15-oct-2027** con la Ley 21.855 (publicada el 23-nov-2026 en el Diario Oficial); ya no está «pendiente de publicación». La verificación del parche se repitió sobre el `main` del 26-nov: 226 pruebas pasan. El `.gitignore` ya trae las líneas de secretos (las agregó Sergio).
**Origen:** lectura del código del backend y de la app en `main`. No se hicieron pruebas de intrusión; esto es una revisión de código, no una auditoría.

## Lo primero: qué se puede prometer y qué no

**Ningún sistema puede garantizar que sus datos no serán robados.** Decirlo en la defensa sería un error y un profesor lo notaría. Lo que sí se puede mostrar es:

1. **Qué amenazas se consideraron** (robo de cuenta, acceso de un tercero a un perfil ajeno, robo de la base, intercepción de la red, fuga por la IA o por los registros).
2. **Qué controles ya existen** y están probados.
3. **Qué brechas hay**, cuáles se cierran antes de la presentación y cuáles quedan declaradas como trabajo futuro.

Eso es más creíble y es lo que pide la Ley 21.719 para datos sensibles: medidas de seguridad **proporcionales** al riesgo, no invulnerabilidad.

## Estado tras el parche de seguridad (23-nov, 11:30)

El código para cerrar las brechas 1, 2, 3, 4, 6 y 12 **ya está escrito, probado y empaquetado** (`seguridad.patch`, en el paquete de Benjamín). Con el parche aplicado, las pruebas pasan: **226** (las 216 anteriores y 10 nuevas de seguridad).

| # | Brecha | Estado |
|---|---|---|
| 1 | `SECRET_KEY` de ejemplo | ✅ **Resuelta en el parche:** la API no arranca con la clave de ejemplo ni con menos de 32 caracteres (comprobado). El script de la prueba con Docker genera una clave aleatoria si falta |
| 2 | Base de datos expuesta | 🟡 **Mitigada en el parche:** el puerto 5432 queda solo en `127.0.0.1` y la clave sale de `POSTGRES_PASSWORD` (con `postgres` por defecto para no romper volúmenes existentes). Para la defensa, poner una clave propia en el `.env`; ver la nota sobre volúmenes existentes en `.env.example` |
| 3 | Sin límite de intentos de login | ✅ **Resuelta en el parche:** 5 fallos por cuenta e IP o 20 por IP en 15 minutos → HTTP 429 con `Retry-After`; un login correcto reinicia el contador. Límite declarado: vive en memoria de un proceso |
| 4 | CORS abierto | ✅ **Resuelta en el parche:** cerrado por defecto; solo los orígenes de `CORS_ORIGENES` |
| 5 | Sin HTTPS | ⬜ **Declarar:** la demo es local con `http`; en producción iría detrás de un proxy con TLS |
| 6 | Registros con el texto de los avisos | ✅ **Resuelta en el parche:** por defecto solo se registra el tipo y el nivel (`NOTIFICADOR_LOG_CONTENIDO=false`) |
| 7 | Token de la pulsera en la URL | ⬜ **Se decidió no cambiarlo:** el servidor Traccar envía el token en la URL; el encabezado `X-Traccar-Token` ya está soportado. Declarar como límite; no se cambia a una semana de la presentación |
| 12 | Dependencias vulnerables | ✅ **Resuelta en el parche, y era grave:** `pip-audit` encontró que **PyJWT 2.7.0 (la biblioteca que firma las sesiones) tenía 17 vulnerabilidades conocidas**; se sube a 2.15.1. Es la única dependencia con hallazgos (39 revisadas) |
| 8, 9, 10, 11, 13 | Cifrado en reposo, RUT, auditoría, revocación de tokens, respaldos | ⬜ **Declarar como trabajo futuro** (requieren migraciones o infraestructura) |

**Lo que queda a mano de Benjamín:** aplicar el parche, correr la prueba con Docker, poner una `SECRET_KEY` y una `POSTGRES_PASSWORD` propias en el `.env` y agregar las líneas de `gitignore_agregar.txt` al `.gitignore`.

## Controles que ya existen (verificados en el código)

| Amenaza | Control | Dónde |
|---|---|---|
| Robo de contraseñas desde la base | Contraseñas con hash **bcrypt** (no se guardan en claro); mínimo 8 caracteres | `core/security.py`, `schemas/usuario.py` |
| Suplantación de sesión | Token JWT firmado con expiración de 24 horas | `core/security.py`, `core/config.py` |
| Token robado del celular | Se guarda en `flutter_secure_storage` (almacenamiento cifrado de Android), no en `SharedPreferences` | `app_movil/lib/services/token_storage.dart` |
| Acceso a perfiles ajenos | Permisos por perfil (`perfil_acceso`); una cuenta ajena recibe **404**; probado en las pruebas automáticas | rutas y `test_cuidador.py`, `test_perfil.py` |
| Fuga hacia la IA | Contexto mínimo; sin RUT, correo ni teléfonos; límite diario; el resumen enviado queda registrado | `services/ia.py`, `consulta_ia` |
| Pulsera falsa que inyecta datos | Clave compartida `TRACCAR_TOKEN`; si está vacía, la ruta está apagada (503) | `api/routes/traccar.py` |
| Secretos en el repositorio | Claves en `.env` local (en `.gitignore`); credenciales de Firebase fuera del repositorio | `.env.example`, `Notas_FCM_Sprint5.md` |
| Daño por error de tipeo | Validación de rangos y tipos en la API | `schemas/` |

## Brechas encontradas (ordenadas por riesgo)

| # | Brecha | Por qué importa | Arreglo | Esfuerzo | ¿Antes del 4-dic? |
|---|---|---|---|---|---|
| 1 | **`SECRET_KEY` tiene un valor por defecto público** en `config.py` y la API arranca igual | Quien conozca ese valor puede **fabricar tokens válidos** para cualquier usuario | Que la API **no arranque** si la clave es la de por defecto o tiene menos de 32 caracteres; prueba nueva | 1 h | **Sí** |
| 2 | **Base de datos expuesta**: `docker-compose.yml` publica el puerto 5432 con usuario y clave `postgres/postgres` | Cualquiera en la misma red puede leer todos los datos de salud | Quitar `ports` de `db` (la API la alcanza por la red interna) y mover usuario y clave a `.env` | 30 min | **Sí** |
| 3 | **Sin límite de intentos de inicio de sesión** | Permite adivinar contraseñas por fuerza bruta | Limitar intentos fallidos por correo y por IP (por ejemplo 5 en 15 minutos → 429); pruebas | 2 a 3 h | **Sí** |
| 4 | **CORS abierto** (`allow_origins=["*"]`) | Cualquier sitio web podría llamar a la API desde el navegador de un usuario | Lista de orígenes por variable de entorno; la app móvil no lo necesita | 30 min | **Sí** |
| 5 | **Sin HTTPS**: la demo usa `http://` | Las claves y los datos viajan sin cifrar en la red | En producción, TLS en un proxy inverso (Caddy o Nginx); en la demo, declararlo | 1 a 2 h para el proxy | Declarar; proxy si hay tiempo |
| 6 | Los **registros** del notificador en modo `log` incluyen título y texto de los avisos | Pueden contener nombres de medicamentos en los registros | Solo usar el modo `log` en desarrollo y no escribir el contenido en producción | 30 min | Sí |
| 7 | Token de la pulsera en la URL (`?token=`) | Queda en registros de servidores y proxys | Usar solo el encabezado `X-Traccar-Token` (ya soportado) | 30 min | Sí |
| 8 | **Datos de salud sin cifrado en reposo** (ni a nivel de columna ni de disco) | Si roban el disco o un respaldo, los datos se leen | En producción: volumen cifrado o base de datos administrada con cifrado. Cifrado por columna de RUT y alergias exige migración | alto | **No: declarar** |
| 9 | **RUT** guardado en `perfil.rut` en texto plano (opcional) | Es un identificador sensible | Preguntarse si hace falta; si no, quitar el campo o cifrarlo | medio | Declarar |
| 10 | **Sin registro de auditoría** de quién vio qué | No se puede investigar un acceso indebido | Tabla de accesos (migración) | alto | **No: declarar** |
| 11 | Token de 24 h **sin revocación ni refresco**; al cerrar sesión solo se borra del celular | Un token robado sirve hasta que expira | Bajar la duración o agregar refresco y lista de revocados | alto | **No: declarar** |
| 12 | Sin escaneo de **dependencias vulnerables** | Una biblioteca con falla conocida | Ejecutar `pip-audit` y revisar; activar Dependabot en GitHub | 1 h | Sí |
| 13 | Sin **respaldos** ni plan de recuperación | Pérdida de datos | Documentar (`pg_dump` programado) | 1 h | Declarar |

**Meta realista:** cerrar las brechas 1 a 4, 6 y 12 (el código ya está escrito: queda aplicarlo y probarlo) y declarar el resto, incluida la 7.

## Quién hace qué (y quién debe ser el dueño)

Recomendación: **Benjamín es el dueño** de esta tarea (G14) porque todos los arreglos importantes están en el backend, el Docker y los secretos, y él controla las migraciones. Los otros dos tienen partes acotadas:

| Persona | Parte |
|---|---|
| **Benjamín** (dueño) | Aplicar `seguridad.patch`, correr las pruebas y la prueba con Docker, poner claves propias en el `.env`; brecha 13 (respaldos, solo documentar); decidir si hay migración (consentimiento, RUT) |
| **Sergio** | Aviso de privacidad, apartado del informe y la diapositiva; cuadro de amenazas; dueño de lo que se declara como límite |
| **Matías** | Consentimiento y avisos en la app (`Privacidad_en_la_app_especificacion.md`); confirmar que el token solo viva en el almacenamiento seguro; `usesCleartextTraffic` solo en la versión de depuración |

## Calendario (actualizado el 26-nov, hasta el 4-dic)

| Cuándo | Qué |
|---|---|
| Jue 26 | Aplicar `parche_unico.patch` en una rama, correr `pytest` y `prueba_docker_sprint5.sh` (D4 esperado: 226) y tomar las capturas de seguridad E1 a E5 |
| Vie 27 | Unir todo a `main` (plazo de G18); correr de nuevo las pruebas y la prueba de Docker |
| Sáb 28 | Ensayo grupal; la diapositiva de seguridad ya incluida; diarios 3.1 entregados |
| Lun 30 | Segundo ensayo; texto de seguridad y privacidad ya en el informe y el manual |
| Mar 1 a jue 3-dic | Solo correcciones de texto; nada de cambios de código |

## Cómo mostrarlo (una diapositiva)

**Título:** «Seguridad de los datos de salud»

| Amenaza | Medida |
|---|---|
| Robo de contraseñas | Hash bcrypt; límite de intentos |
| Acceso a datos ajenos | Permisos por perfil; cuenta ajena = 404 |
| Robo de sesión | Token con expiración; almacenamiento cifrado en el celular |
| Fuga hacia la IA | Contexto mínimo, sin RUT, correo ni teléfono |
| Secretos | Claves fuera del repositorio; API no arranca con clave débil |
| **Trabajo futuro** | Cifrado en reposo, HTTPS en producción, auditoría de accesos |

**Qué decir (30 s):**
> «Los datos de salud son sensibles, así que diseñamos pensando en las amenazas: protegemos las contraseñas, aislamos cada perfil, limitamos lo que se envía a la IA y mantenemos las claves fuera del código. No prometemos invulnerabilidad: lo que falta, como el cifrado en reposo y la auditoría de accesos, está declarado como trabajo futuro.»

## Preguntas probables

| Pregunta | Respuesta corta |
|---|---|
| ¿Pueden robar los datos de los usuarios? | Ningún sistema lo garantiza; reducimos el riesgo con los controles de la tabla y declaramos lo que falta. |
| ¿Cómo se protegen las contraseñas? | Con bcrypt; nunca se guardan ni se devuelven en claro. |
| ¿Qué pasa si roban el celular? | El token está en el almacenamiento seguro de Android y vence en 24 horas; falta la revocación remota (trabajo futuro). |
| ¿Cifran la base de datos? | Hoy no a nivel de aplicación; en producción iría sobre un disco o servicio cifrado. Está declarado. |
| ¿Cómo sabrían si alguien accedió indebidamente? | Hoy no hay registro de auditoría; es trabajo futuro. |
| ¿Usan HTTPS? | La demo es local con http; en producción iría detrás de un proxy con TLS. |

## Marco de referencia (para citar en el informe)

Usar como guía la **OWASP Top 10** y el **OWASP ASVS** (lista de verificación de seguridad de aplicaciones) y la **Ley 21.719** (medidas de seguridad proporcionales para datos sensibles). Verificar el texto exacto de cada una antes de citarlo.
