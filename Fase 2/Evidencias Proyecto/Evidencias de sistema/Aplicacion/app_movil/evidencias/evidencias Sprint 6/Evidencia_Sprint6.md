# Evidencias de Sistema — Sprint 6
**Proyecto:** Perfil Médico+ (APT122)
**Fecha de ejecución:** ⬜
**Entorno de pruebas:** ⬜ (Docker Compose + emulador Android / celular real)
**Cuentas de prueba:** ⬜ (datos simulados; no usar datos reales de personas)

> PLANTILLA. Cada captura se nombra `S6_NN.M_descripcion.png`, va en esta misma carpeta y se cita en una tabla con una frase que diga qué criterio respalda. No citar capturas que no existan.

---

## 1. Preparación del entorno (`S6_00`)

| Código | Archivo de evidencia | Descripción técnica |
| :--- | :--- | :--- |
| **`S6_00.1`** | `S6_00.1_docker_compose_ps.png` | ⬜ `docker compose ps`: `db` y `api` en ejecución |
| **`S6_00.2`** | `S6_00.2_pytest_en_contenedor.png` | ⬜ `pytest` dentro del contenedor (216 de 216) |
| **`S6_00.3`** | `S6_00.3_prueba_humo.png` | ⬜ Prueba de humo (29 comprobaciones) |
| **`S6_00.4`** | `S6_00.4_flutter_analyze_y_test.png` | ⬜ `flutter analyze` y `flutter test` con el código de FCM |

## 2. HU 9 — Push real con FCM (`S6_01`)

**Objetivo:** el aviso llega al celular con la app cerrada. Lo prueba una persona que no escribió el código.

| Código | Archivo de evidencia | Criterio que respalda |
| :--- | :--- | :--- |
| **`S6_01.1`** | `S6_01.1_fila_dispositivo_push.png` | ⬜ Fila en `dispositivo_push` tras iniciar sesión en el celular |
| **`S6_01.2`** | `S6_01.2_probar_fcm_salida.png` | ⬜ Salida de `scripts/probar_fcm.py` |
| **`S6_01.3`** | `S6_01.3_notificacion_app_cerrada.png` | ⬜ Notificación en el celular con la app cerrada |
| **`S6_01.4`** | `S6_01.4_aviso_app_abierta.png` | ⬜ Aviso en pantalla con la app abierta |
| **`S6_01.5`** | `S6_01.5_log_backend_envio.png` | ⬜ Registro del backend con el envío |
| **`S6_01.6`** | `S6_01.6_tras_cerrar_sesion.png` | ⬜ Tras cerrar sesión ya no llega nada |

Si el push no se logra: reemplazar esta sección por el texto de límite conocido de `backend/docs/Notas_FCM_Sprint5.md` y no citar capturas.

## 3. HU 20 — Glucosa (`S6_02`) — solo si el Product Owner la cubre con la HU 12

| Código | Archivo de evidencia | Criterio que respalda |
| :--- | :--- | :--- |
| **`S6_02.1`** | `S6_02.1_registrar_glucosa.png` | ⬜ Registro manual de una lectura en mg/dL |
| **`S6_02.2`** | `S6_02.2_historial_glucosa.png` | ⬜ Lectura visible en el historial y el gráfico |

## 4. Criterios sin captura

⬜ Listar lo que quedó sin evidencia, como en la sección 5.5 del Sprint Backlog.
