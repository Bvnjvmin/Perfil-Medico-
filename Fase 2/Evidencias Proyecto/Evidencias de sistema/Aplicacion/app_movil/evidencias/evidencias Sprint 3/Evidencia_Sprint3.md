# Evidencia de Pruebas — Sprint 3 (HU 5, HU 6, HU 7 y HU 8)

**Rol:** Matías Pizarro (App Móvil y Scrum Master)
**Periodo:** 5 al 17 de octubre de 2026 · **Pruebas del 15 y 16 de octubre**
**Entorno:** Emulador Android conectado al backend local (`http://10.0.2.2:8000`) con Docker Compose, y pruebas automatizadas con Flutter y pytest.
**Cuentas usadas:** titular `McBackToTheFuture@gmail.com` (Marty) y cuidador invitado `SigmaSwag23@hotmail.com` (Sergio).

## 1. Validación automatizada

| Comando | Resultado | Evidencia |
| :--- | :--- | :--- |
| `flutter analyze` | 4 avisos de nivel *info* y ningún error: uso de `value` en lugar de `initialValue` en `DropdownButtonFormField` (`alergias_screen.dart`, `compartir_perfil_screen.dart`, `home_screen.dart` y `perfil_screen.dart`). | `app_movil/analyze.log` |
| `flutter test` | `All tests passed!` — 10 de 10 pruebas pasan. | `app_movil/test.log` |
| `pytest` (backend) | 119 pruebas pasan (17-10). | `backend/pytest.log` |

Pruebas existentes en `app_movil/test/`: `perfil_y_dependiente_test.dart` (deserialización de `Perfil` con `tipo`, `subtipo` y `mi_acceso`; subtipo obligatorio en el formulario; `Medicamento.fromJson` y `RutinaCuidado`), `agenda_test.dart` (contrato de `Actividad` y cálculo de avance del panel), `usuario_test.dart` y `login_screen_test.dart`.
Pruebas del backend en `backend/app/tests/`: dependientes, actividad, cuidador y panel.

> Nota sobre el backend: la primera corrida de `pytest` (16-10) dio 53 pruebas pasadas, 12 fallidas y 54 con error. La causa no era la app ni el backend: las pruebas usaban una fecha fija (`2026-10-14`) y la agenda solo genera actividades desde el día anterior a la creación del medicamento. Benjamín cambió las fechas fijas por la fecha de hoy el 17-10 y el `pytest.log` actual muestra las 119 pruebas pasando.

> Nota sobre los logs antiguos: los logs de HU3 y HU5 de la carpeta `evidencias/` corresponden a pruebas anteriores (`cuidado_test.dart`, `AgendaStorage`) que ya no existen. Los logs del Sprint 3 son los de la tabla anterior.

## 2. Flujos funcionales en el emulador

Las capturas están en esta misma carpeta (`evidencias Sprint 3/`).

| Paso | Historia | Qué se hizo en la App | Resultado esperado | Capturas | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | HU 6 | Registrar un dependiente eligiendo el subtipo (*Adulto mayor* o *Niño*). | `201 Created`; el dependiente aparece en "Mis perfiles" como "Dependiente (Adulto mayor) · Tuyo". | `S3_01_crear_dependiente.png`, `S3_02_perfil_activo_dependiente.png` | OK |
| 2 | HU 6 | Seleccionar el dependiente en el Home y revisar los módulos. | Medicamentos, Rutinas, Agenda, Alergias y Contactos muestran "Activo: Dr. Emmett Brown". | `S3_02.1_perfil_activo_dependiente.png` | OK |
| 3 | HU 6 | Crear un dependiente de prueba, eliminarlo y confirmar el diálogo. | `DELETE /perfiles/{id}`; mensaje "Perfil eliminado." y el perfil desaparece de la lista. | `S3_03_prueba_crear_perfil_para_eliminar_dependiente.png`, `S3_03.1_eliminar_dependiente.png`, `S3_03.2_perfil_dependiente_eliminado.png` | OK |
| 4 | HU 5 | Marcar y desmarcar actividades en la Agenda de hoy, cerrar sesión, volver a entrar y abrir la Agenda. | `POST /actividades/{id}/confirmar` y `/desconfirmar`; el estado se mantiene tras volver a iniciar sesión (4 de 6 confirmadas). | `S3_04.1_agenda_antes_de_cerrar_sesion.png`, `S3_04.2_agenda_tras_volver_a_iniciar_sesion.png`, `S3_04_agenda_backend.png` | OK |
| 5 | HU 8 | Abrir el Panel de dependientes. | Una tarjeta por perfil con su avance. Los valores coinciden con la Agenda de cada perfil (4 de 6 y 6 de 8). | `S3_05_panel_dependientes.png` | OK |
| 6.1 | HU 7 | Registrar la cuenta del cuidador. | Cuenta creada. | `S3_06.0_registro_cuenta_cuidador.png` | OK |
| 6.2 | HU 7 | El titular comparte sus perfiles con rol "Solo lectura" (sin permiso para confirmar ni para editar). | `201 Created`; mensaje "Acceso compartido correctamente.". Se compartieron los dos perfiles: el del titular y el de Dr. Emmett Brown. | `S3_06.1_permisos_cuidador.png`, `S3_06.2_permisos_cuidador.png` | OK |
| 6.3 | HU 7 | Compartir con un correo no registrado. | La app muestra el mensaje del backend: "No existe una cuenta con ese correo". | `S3_06.3_no_se_pueden_compartir_datos_ni_permisos_sin_una_cuenta_registrada.png` | OK |
| 6.4 | HU 7 | Iniciar sesión con la cuenta del cuidador. | El cuidador ve los perfiles compartidos en el selector del Home. | `S3_06.7_home_cuenta_cuidador.png` | OK |
| 6.5 | HU 7 | Abrir "Mis perfiles" como cuidador. | Etiqueta "Compartido contigo" en ambos perfiles y sin íconos de editar ni eliminar. | `S3_06.4_mis_perfiles_compartido.png` | OK |
| 6.6 | HU 7 | Abrir Medicamentos y Agenda como cuidador (rol "Solo lectura"). | Sin botón de agregar en Medicamentos; casillas de la Agenda bloqueadas. | `S3_06.5_medicamentos_solo_lectura.png`, `S3_06.6_agenda_solo_lectura.png` | OK |

## 3. Correcciones hechas durante el sprint
* `api_service.dart` no compilaba: los modelos `Alergia` y `ContactoEmergencia` no tenían `perfilId`. Se agregó el campo.
* Rutas y campos de alergias y contactos alineados con el backend (`sustancia`, `relacion`, `/contactos-emergencia`).
* `compartirPerfil` enviaba `rol` en lugar de `rol_vinculo`, por lo que "Solo lectura" se guardaba como cuidador. Corregido.
* Se eliminaron los respaldos en memoria de la agenda (`agenda_storage.dart`), que ocultaban errores reales del backend.
* El subtipo de dependiente se enviaba como texto ("Adulto mayor") y el backend exige `adulto_mayor` o `nino`. La app ahora traduce en ambos sentidos.

## 4. Pendientes conocidos
* En la cuenta de un cuidador, "Mi perfil de salud" muestra el nombre de un titular ajeno (el Home usa cualquier titular al que se tiene acceso si no hay uno propio). Debería decir "Aún no lo completas".
* El backend no guarda la "reacción" de una alergia; el campo no se envía.
* El Panel hace una llamada por perfil; el backend ya ofrece `GET /panel?fecha=` para hacerlo en una sola.
* Sin timeouts ni manejo explícito de `SocketException` en las llamadas HTTP.
* Los 4 avisos de `flutter analyze` (`value` → `initialValue`) se corrigen en el Sprint 4.
* Aceptación del Product Owner: pendiente (`Checklist_Aceptacion_PO_Sprint3.md`, a cargo de Sergio).
