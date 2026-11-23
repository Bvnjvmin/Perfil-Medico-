# Retrospectiva — Sprint 5 (S13–S14)

**Proyecto:** Perfil Médico+ · Capstone_005D · Grupo 7
**Periodo del sprint:** 2 al 14 de noviembre de 2026
**Fecha de redacción:** 23 de noviembre de 2026 (borrador)
**Scrum Master:** Matías Pizarro
**Participantes:** Matías Pizarro (App móvil y Scrum Master), Benjamín Leiva (Backend), Sergio Ocares (Base de datos, IA y Product Owner)

> Borrador armado a partir del repositorio (`Sprint_Backlog_Sprint5.md`, `Checklist_Aceptacion_PO_Sprint5.md`, `Evidencia_Backend_Sprint5.md`). Lo que dice cada sección sale de lo que está documentado ahí. Las conclusiones, los aprendizajes y las acciones se confirman en la reunión del equipo; los puntos marcados con «⬜ confirmar» necesitan la opinión de quien hizo ese trabajo.

## Resultado del sprint

Historias comprometidas: 7 (HU 12, 13, 14, 15, 17, 18 y 19) · Construidas y probadas en backend y emulador: 6 (HU 12, 13, 14, 15, 17 y 19) · No iniciada: 1 (HU 18) · Pruebas del backend: 210 de 210 · Aceptación del Product Owner: checklist de 31 criterios ejecutado el 10 y el 12-11, con el veredicto por firmar. Detalle en `Sprint_Backlog_Sprint5.md`.

**Estado final:** las HU 12, 13, 14, 15, 17 y 19 quedaron construidas, integradas al repositorio y probadas en backend y en el emulador, con la IA en modo simulado y la pulsera con el simulador. **La HU 18 (Health Connect) no se construyó** y queda como proyección por decisión del Product Owner (23-11): el backend ya acepta indicadores con `fuente = pulsera`, pero falta la lectura desde la app. **El push real con FCM** (arrastre de la HU 9) queda como límite conocido por la misma decisión.

- **Base de datos:** tablas `indicador_salud`, `pulsera`, `posicion`, `geocerca`, `evento_seguridad` y `consulta_ia`; cuatro migraciones nuevas con cabeza única `a5b6c7d8e9f0`, probadas en PostgreSQL 16 y repetidas en Docker (`alembic current` y `alembic check`). Subido el 06-11.
- **Backend:** indicadores, cumplimiento, botón de asistencia, pulsera, geocercas, eventos de seguridad, Traccar e IA de orientación general; 62 pruebas nuevas y 210 de 210 en total. Contrato en `Contrato_API_Sprint5.md`.
- **App:** pantallas de indicadores, cumplimiento, eventos de seguridad, pulsera y zonas, asistente de IA y botón «Necesito ayuda»; `flutter analyze` sin avisos y flujos probados en el emulador con capturas `S5_*`.

## ¿Qué funcionó bien este sprint?

- **El contrato de API y el simulador de pulsera estuvieron listos al inicio del sprint** (05-11), de modo que la app y la base de datos pudieron avanzar en paralelo con el backend.
- **Las migraciones se mantuvieron con una sola cabeza**, con una sola persona creándolas (acuerdo de la decisión 6), y se verificaron en Docker.
- **El backend quedó bien cubierto por pruebas:** 62 pruebas nuevas y la suite completa en 210 de 210, incluidos permisos por rol, límites de rango y el no repetir la alerta de batería baja.
- **La evidencia distingue lo cumplido de lo pendiente:** la sección 5.5 del Sprint Backlog lista los criterios sin captura (botón sin duplicados, límite de 30 consultas, solo el titular registra pulseras, Traccar y pulsera reales) en lugar de darlos por hechos.
- **La aceptación del Product Owner fue honesta sobre sus límites:** el checklist separa lo probado por el Product Owner (10), lo verificado en un entorno de prueba (18) y lo respaldado con evidencia del equipo (1), y deja anotado que la IA se probó solo en modo simulado y que la inactividad se probó con un plazo reducido.
- **La IA se diseñó con límites de privacidad verificables:** las preguntas de urgencia responden un texto fijo con el 131 y el *4141 sin consultar al modelo, y el contexto no incluye RUT, correo ni teléfonos (`S5_06.1d`).
- **El revisar contra el código sirvió:** la comparación del contrato con la API mostró que la ruta de permisos del cuidador es `PUT` y no `PATCH`, y el contrato se corrigió.

## ¿Qué no funcionó o nos costó más de lo esperado?

- **El push real con FCM sigue sin hacerse por segundo sprint consecutivo.** El backend lo tiene apagado por defecto y con 6 pruebas, pero no hay proyecto de Firebase ni la app registra el token. *Aprendizaje:* decidir los servicios externos en la planificación, como se había acordado en el Sprint 4. ⬜ confirmar con Benjamín y Matías.
- **La HU 18 quedó sin iniciar.** Dependía de una decisión (decisión 3) que se tomó recién al cierre. *Aprendizaje:* decidir en la planificación si una historia que depende de hardware o de una plataforma externa entra al sprint.
- **La pulsera y Traccar reales no se probaron.** Se dejaron los archivos de Traccar en el repositorio, pero sin levantar el servidor ni capturar un envío real; la demo usa el simulador y debe decirse así. ⬜ confirmar.
- **El checklist del Product Owner se ejecutó dentro de las fechas del sprint en parte, pero su veredicto sigue sin firmarse.** Las filas 1 a 10 se probaron el 10-11 y el resto, el 12-11, y a la fecha de este borrador falta el veredicto y la fecha de firma. Parte de los criterios (18 de 31) se verificó en un entorno de prueba y no en el Docker del proyecto. *Aprendizaje:* repetir esas verificaciones en el Docker del proyecto antes de firmar.
- **El Sprint Backlog 5 siguió diciendo «día 12 de 13, en cierre» hasta el 23-11 y la retrospectiva no existía.** Es la misma acción pendiente del Sprint 4 (cerrar el backlog y la retrospectiva el último día del sprint, con el resultado real). *Aprendizaje:* agendar ese cierre como tarea del último día, con «aceptación pendiente» si hace falta.
- **Los commits de la app y de su evidencia no tienen hashes anotados** en la sección 8 del Sprint Backlog (la fila de Matías sigue como «completar con los hashes»). ⬜ confirmar con Matías.
- **La IA se probó solo en modo simulado.** No se pudo probar el límite de 30 consultas ni la respuesta de un modelo real fuera de las pruebas automáticas. *Aprendizaje:* decidir el proveedor y la clave antes del sprint si se quiere probar con uno real.
- **La API no tiene una ruta para omitir actividades;** la prueba de que las omitidas no cuentan en el cumplimiento se hizo con un `UPDATE` directo en PostgreSQL. Queda anotado como nota técnica.
- **La inactividad se probó con un plazo reducido** (5 minutos, evento a las 22:14, fuera de la ventana por defecto). El valor de 3 horas entre 08:00 y 22:00 lo cubren las pruebas automáticas, no la prueba manual.

## Seguimiento de las acciones de la retrospectiva del Sprint 4

El estado de cada acción sale de lo documentado en el repositorio. Las marcadas «⬜ verificar» necesitan revisar el historial de git.

| Acción acordada | Estado |
|---|---|
| Decidir los servicios externos (FCM, proveedor de IA, Traccar) y sus credenciales en la planificación | 🟡 Traccar y la IA quedaron con configuración en el repositorio; FCM y la prueba con un proveedor de IA real quedaron sin resolver |
| Publicar el Sprint Backlog 5 el primer día del sprint | ⬜ verificar con `git log` la fecha del primer commit del backlog (el sprint empezó el 02-11) |
| Ejecutar el checklist del Product Owner a mitad de sprint y completarlo al cierre | 🟡 Se ejecutó el 10 y el 12-11; falta el veredicto firmado |
| Verificar que cada captura citada exista y pegar el hash del commit | ⬜ verificar; los hashes de la app siguen sin anotarse (sección 8 del Sprint Backlog) |
| Subir al repositorio al menos dos veces por semana y revisar el historial a mitad de sprint | ⬜ verificar con `git log --since=2026-11-02` |
| Cerrar el Sprint Backlog y la retrospectiva el último día del sprint | ❌ El backlog se actualizó y la retrospectiva se redactó el 23-11, nueve días después del cierre |

## ¿Qué vamos a cambiar o probar distinto en el próximo sprint?

Propuesta para confirmar en la reunión del equipo. El Sprint 6 dura una semana (S15) y incluye glucosa manual, recordatorios extendidos, farmacias vía IA, pruebas integrales, documentación e Informe Final.

| Acción | Responsable | Cuándo |
|---|---|---|
| Cerrar el Sprint Backlog 6 y su retrospectiva el último día del sprint, con el resultado real | Scrum Master | Último día del Sprint 6 |
| Firmar el checklist del Sprint 5 (veredicto y fecha) y repetir en el Docker del proyecto las filas verificadas en el entorno de prueba | Sergio / Benjamín | Antes de la entrega final |
| Anotar en la sección 8 del Sprint Backlog los hashes de los commits de la app y de la evidencia | Matías | Al subir cada cambio |
| Declarar en el informe y en la defensa los límites conocidos: FCM sin implementar, IA en modo simulado, demo con simulador de pulsera, HU 18 como proyección | Todos | Informe Final y presentación |
| Mantener una sola cabeza de migraciones de Alembic | Sergio | Todo el Sprint 6 |

## Qué pasa al Sprint 6

Lo previsto del Product Backlog: registro manual de glucosa, recordatorios extendidos, farmacias cercanas vía IA, pruebas integrales, documentación (manual técnico y Docker) e informe final. La HU 18 no pasa al Sprint 6: queda como proyección. El push real con FCM, la prueba con Traccar y pulsera reales y la prueba de la IA con un proveedor real quedan como límites conocidos.
