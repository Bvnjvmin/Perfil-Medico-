# Retrospectiva del Sprint 3 — Equipo Perfil Médico

**Fecha de cierre:** Sábado 17 de octubre de 2026
**Scrum Master:** Matías Pizarro
**Participantes:** Matías Pizarro (App Móvil), Benjamín Leiva (Backend), Sergio Ocares (Frontend Web / QA)

## 1. Balance general
Se integró la agenda con el backend (HU 5), se habilitó la gestión de dependientes (HU 6), se implementaron los permisos de cuidadores (HU 7) y el panel de avance (HU 8). Los flujos de las cuatro historias se validaron en el emulador, incluido HU 7 con dos cuentas (titular y cuidador). Queda pendiente adjuntar los logs de `flutter analyze`, `flutter test` y `pytest` (ver sección 3).

## 2. Lo que funcionó bien
* **Contratos definidos antes de programar:** acordar el formato JSON evitó bloqueos de sprints anteriores.
* **Análisis y pruebas automatizadas:** `flutter analyze`, `flutter test` y las pruebas del backend ayudaron a detectar inconsistencias entre app y servidor.
* **Backend ya disponible:** las rutas de actividades, cuidadores y panel permitieron quitar los respaldos locales de la agenda.

## 3. Desafíos y aspectos a mejorar
* **Desalineación entre app y backend:** se detectaron nombres de campo y rutas distintos (`rol` vs `rol_vinculo`, `/contactos` vs `/contactos-emergencia`, `nombre` vs `sustancia`). Los respaldos en memoria ocultaron varios de estos errores. *Aprendizaje:* contrastar cada llamada contra la documentación de la API (`/docs`) antes de dar una historia por terminada.
* **Mensajes de error que engañan:** un 404 se mostró como "función no disponible" cuando en realidad el correo no estaba registrado. *Aprendizaje:* mostrar siempre el `detail` que devuelve el backend.
* **Formato de datos entre app y backend:** el subtipo de dependiente se enviaba como "Adulto mayor" y el backend exige `adulto_mayor` o `nino`. *Aprendizaje:* probar cada formulario contra el backend real, no solo con pruebas de modelo.
* **Evidencia desactualizada:** los logs de `evidencias/` pertenecían a pruebas de sprints anteriores. *Aprendizaje:* generar los logs al cierre de cada sprint, no reutilizarlos.
* **Tiempo ajustado:** codificar varias historias, validar en emulador y hacer de Scrum Master en un período corto obligó a priorizar; las mejoras visuales de M7 quedaron como opcionales.

## 4. Acciones y acuerdos

| Acción de mejora | Responsable | Plazo | Indicador de éxito |
| :--- | :--- | :--- | :--- |
| Mantener `flutter analyze` y `flutter test` en verde antes de cada commit a `main`. | Matías Pizarro | Permanente | 100% de tests aprobados y 0 issues. |
| Revisar cada integración app-backend contra `/docs` de FastAPI. | Matías Pizarro y Benjamín Leiva | Cada historia | Sin diferencias de campos ni rutas. |
| Adjuntar los logs de `flutter analyze`, `flutter test` y `pytest` del Sprint 3. | Matías Pizarro | Antes de la entrega final | Tres archivos `.log` en `evidencias/`. |
| Corregir "Mi perfil de salud" para cuentas de cuidador (no mostrar el titular ajeno). | Matías Pizarro | Siguiente sprint | Muestra "Aún no lo completas" si no hay perfil propio. |
| Pasar el Panel a `GET /panel?fecha=`; agregar timeouts y manejo de errores de red. | Matías Pizarro | Siguiente sprint | Una sola llamada al panel; mensaje claro si no hay red. |
| Consolidar evidencias y capturas conforme se cierra cada historia. | Todo el equipo | Cierre de cada sprint | Documentación lista antes de la entrega. |
