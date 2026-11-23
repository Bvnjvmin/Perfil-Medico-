# Ensayo — diapositivas 1 a 4, 13 y 14 (Benjamín)

Texto fuente: el guion compartido del grupo (lo que sigue lo resume y agrega tiempos y puntos de apoyo). Meta: hablar sin leer.

## Tiempos (aprox. 4 minutos tuyos + tu parte de la 13 y la 14)

| Diap. | Tema | Tiempo | Puntos clave (si se te olvida el guion) |
|---|---|---|---|
| 1 | Portada | 20 s | Grupo 7, Perfil Médico+, Capstone; te presentas y nombras a Sergio y Matías |
| 2 | Integrantes | 40 s | Tú: API FastAPI, autenticación, rutinas, alertas, permisos y pruebas. Sergio: PO, base de datos e IA. Matías: Scrum Master y app Flutter |
| 3 | Descripción | 1 min | Problema: todo disperso (papel, calendario, WhatsApp). Solución: cuenta titular con perfiles dependientes; si algo no se confirma, avisa al cuidador. Flujo: planificar → recordar → confirmar → monitorear → alertar → acompañar |
| 4 | Objetivos | 1 min 20 s | General: app con backend que centraliza la salud familiar. De 11 específicos: 5 del MVP logrados; 3 parciales por simuladores (IA, pulsera, eventos de caída); 2 no desarrollados (recordatorios extendidos y farmacias vía IA) |

> **Revisar antes de ensayar:** el guion dice «5 logrados, 3 parciales, 2 no desarrollados» (10 de 11). En el 2.6 los objetivos 6, 7, 8 y 9 están **parciales** (4 parciales) y 10 y 11 «no desarrollados». Es decir: 5 logrados + 4 parciales + 2 no desarrollados = 11. Cuando la diapositiva 4 diga «tres parciales», no coincide con el informe. Acuerden con el equipo cuál versión se dice (la del informe es la correcta) y corrijan el guion.

## Diapositiva 13 — tus dos obstáculos

1. Subidas tardías al repositorio: se corrigió con el acuerdo de subir dos veces por semana. *(Cuidado: la retrospectiva del Sprint 4 dice que ese acuerdo se cumplió a medias; si la comisión pregunta, dilo así: «mejoró, pero seguimos subiendo concentrado».)*
2. Desalineación entre app y backend: se resolvió con el contrato de API escrito antes de construir.

## Diapositiva 14 — preguntas

Te corresponden: backend, pulsera, Docker y pruebas.

### Preguntas probables y respuestas cortas (solo con lo verificado)

| Pregunta | Respuesta |
|---|---|
| ¿Por qué la pulsera y la IA son simuladas? | No teníamos pulsera ni proveedor de IA contratado. El flujo completo se probó con un simulador y con el modo simulado, y los declaramos como límite. |
| ¿Cuántas pruebas tiene el backend y qué cubren? | 216 pruebas automáticas (autenticación, perfiles, permisos, agenda, alertas, indicadores, cumplimiento, asistencia, pulsera, IA y FCM simulado). Además una prueba de humo de 29 comprobaciones sobre PostgreSQL. |
| ¿Cuántas rutas? | 43 rutas, que son 65 operaciones HTTP. |
| ¿Cómo protegen los datos? | Autenticación con JWT; permisos por perfil (una cuenta ajena recibe 404); la IA no recibe RUT, correo ni teléfonos y tiene límite de 30 consultas al día; las preguntas de urgencia reciben una respuesta fija con el 131 y el *4141 sin consultar al modelo. |
| ¿Por qué no hay push real? | El backend lo tiene implementado pero apagado y sin verificar con Firebase real; falta el proyecto de Firebase y la parte de la app. Quedó como límite declarado. |
| ¿Docker funciona? | Compose del backend y la base de datos pasó `docker compose config` y las migraciones se probaron en Docker (`alembic current` y `alembic check`). **Solo di que el Docker completo está probado si ya corriste el script y tienes las capturas.** |
| ¿Qué harían distinto? | Decidir los servicios externos al planificar, y subir avances parciales durante la semana. |

## Cómo ensayar

1. Lee tu parte en voz alta con cronómetro. Objetivo: 4 minutos.
2. Repítela sin mirar el guion, solo con los puntos clave.
3. Ensayo completo con Matías y Sergio: 14 diapositivas, 14 minutos, con las preguntas probables de arriba.
