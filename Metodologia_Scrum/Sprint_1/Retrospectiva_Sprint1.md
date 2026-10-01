# Retrospectiva — Sprint 1 (S5–S6)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo del sprint:** 7 al 19 de septiembre de 2026
**Participantes:** Benjamín Leiva, Sergio Ocares, Matías Pizarro
**Fecha de la retrospectiva:** 16 de septiembre de 2026 (cierre del sprint; se sumaron daily meetings del 9 al 16 de septiembre, 6 días hábiles)

## Resultado del sprint

Historias comprometidas: 3 · Terminadas: 1 (HU 1) · Parciales: 2 (HU 2 y HU 3). Detalle en `Sprint_1_S5-S6.md`.

## ¿Qué funcionó bien este sprint?

- **El backend de autenticación quedó completo y verificable:** registro, login con JWT y endpoint protegido, con 7 pruebas automatizadas que pasan y despliegue reproducible con Docker.
- **El backend tiene pruebas automatizadas que corren sin Docker ni PostgreSQL** (SQLite en memoria), lo que permite confirmar que la API funciona sin depender de la app.
- **El modelo de datos se diseñó con criterio y se corrigió a tiempo:** la separación entre `USUARIO` (credencial) y `PERFIL` (persona), la tabla `ACTIVIDAD` y el rol por vínculo evitan rehacer el esquema cuando lleguen rutinas y perfiles dependientes.
- **La app se conectó al contrato real del backend** (mismos campos que `UsuarioOut`) en vez de simular datos.
- **Cada integrante entregó dentro de su módulo** (backend, base de datos, app), con la división de responsabilidades definida en el Cronograma.

## ¿Qué no funcionó o nos costó más de lo esperado?

- **La subida al repositorio se concentró al final del sprint.** Todos los commits de Fase 2 están entre el 16 y el 21 de septiembre, con el sprint comenzando el día 7. La Guía de Scrum pide commits frecuentes; así se pierde visibilidad del avance intermedio.
- **El Sprint Backlog y la Retrospectiva no se escribieron durante el sprint.** Se están redactando después del cierre, cuando la Guía los exige como evidencia por sprint.
- **HU 2 (datos básicos de salud) quedó sin implementar.** El diseño existe, pero las tablas `perfiles`, `alergias` y `contactos_emergencia` no están en el backend.
- **El diseño del modelo y el código se desalinearon:** el modelo de datos elimina el campo `rol` de `usuarios`, pero el backend y la app siguen usándolo.
- **La app no tiene evidencia de haber sido probada de punta a punta:** las 2 pruebas Flutter no se ejecutaron con el SDK real y no hay capturas del flujo contra el backend. Los commits de corrección posteriores a la primera subida indican que aparecieron errores de integración (por ejemplo, el manejo del valor del enum `rol`) que habrían salido antes con una prueba temprana.
- **Los nombres de carpeta con tilde se corrompieron al subir por el navegador**, lo que dejó carpetas duplicadas y rutas ilegibles en el repositorio.
- **Faltan archivos básicos de higiene del repositorio:** no hay `.gitignore` ni `.env.example`, aunque el README indica copiar ese archivo.

## ¿Qué vamos a cambiar o probar distinto en el próximo sprint?

| Acción | Responsable | Cuándo |
|---|---|---|
| Subir avances al repositorio como mínimo 2 veces por semana, en commits pequeños | Todos | Todo el Sprint 2 |
| Escribir el Sprint Backlog el primer día del sprint (Sprint Planning) y la retrospectiva el último día | Scrum Master del sprint | Inicio y cierre del Sprint 2 |
| Cerrar HU 2: implementar `perfiles`, `alergias`, `contactos_emergencia` con migración | Sergio / Benjamín | Primera semana del Sprint 2 |
| Actualizar en conjunto backend, modelo de datos y app al eliminar `rol` | Benjamín / Sergio / Matías | Primera semana del Sprint 2 |
| Ejecutar `flutter test` y una prueba manual contra el backend, guardando capturas | Matías | Antes de empezar HU 4 y HU 5 |
| Trabajar desde un clon local con git (no desde el navegador) para evitar problemas de codificación | Todos | Desde ahora |
| Agregar `.gitignore` y `.env.example` al repositorio | Benjamín | Inicio del Sprint 2 |
| Mantener las tareas del sprint en el tablero de GitHub Projects | Scrum Master del sprint | Todo el Sprint 2 |
