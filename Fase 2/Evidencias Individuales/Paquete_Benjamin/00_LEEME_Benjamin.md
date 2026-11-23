# Paquete de Benjamín Leiva (backend) — Perfil Médico+

Preparado el domingo 22-nov-2026 a partir del repositorio (rama `main`) y de lo que se pudo verificar sin Docker.

## Qué hay aquí

| Archivo | Para qué sirve |
|---|---|
| `prueba_docker_sprint5.sh` | Ejecuta los pasos D0 a D6 de la guía de Docker y guarda cada salida en `evidencias_docker/`. |
| `Guia_capturas_Docker.md` | Qué captura tomar en cada paso y cómo nombrarla. |
| `Evidencia_Docker_Sprint5_PLANTILLA.md` | Documento para pegar las capturas y los resultados reales (no tiene resultados inventados). |
| `Verificacion_cifras_informe26.md` | Cifras del informe 2.6 y de la presentación comprobadas contra el código. |
| `Manual_Tecnico_BORRADOR.md` | **Entregable que falta:** el Cronograma pide un manual técnico en el Informe Final y no está en el repositorio. Borrador armado desde el código. | 
| `Revision_parrafo_seccion6.md` | Tu párrafo de la sección 6 con una lista de cosas por confirmar. |
| `Ensayo_diapositivas_1-4_13_14.md` | Guion, tiempos y preguntas probables de tus diapositivas. |
| `Mensaje_para_el_grupo.md` | Texto corto para enviar a Matías y Sergio. |

## Lo que falta hacer en tu computador (y por qué)

- **Las capturas de Docker.** Todavía no se corrió con el servicio de Docker activo, así que el script está listo y revisado en sintaxis, pero **no fue ejecutado con Docker**. Hay que correrlo en tu computador.
- **Borrar la plantilla 2.1 vacía.** Ya está hecho: el archivo `2.1_APT122_DiarioReflexionFase2.docx` (la plantilla sin nombre) se eliminó del repositorio el 07-oct-2026 (commit `0205988`). Hoy en `main` solo están los tres diarios 2.1 con nombre (`Leiva_`, `Ocares_`, `Pizarro_`). Nada que hacer.

## Orden sugerido (unos 60 a 90 minutos)

1. Abre Docker Desktop y espera a que diga *running*.
2. Desde la carpeta `backend` del repositorio: `bash prueba_docker_sprint5.sh` (en Windows usa Git Bash o WSL).
3. Toma las capturas D1 a D5 según `Guia_capturas_Docker.md` mientras corre.
4. Si quieres la parte de Traccar: `bash prueba_docker_sprint5.sh traccar` (D6).
5. Completa `Evidencia_Docker_Sprint5_PLANTILLA.md` con lo que realmente salió (si algo falló, se anota como falló).
6. Sube al repositorio por la web de GitHub, con tu cuenta, solo las capturas y el documento. **No subas el `.env` ni la carpeta `evidencias_docker/` con tokens.**
7. Lee `Revision_parrafo_seccion6.md` y corrige tu párrafo en el 2.6 si algo no te representa.
8. Ensaya con `Ensayo_diapositivas_1-4_13_14.md`.

## Lo que viene (Fase 3, según el Cronograma)

- **Semana 16 (23 al 28-nov):** Diario de Reflexión de la Fase 3 (3.1, individual) y guion de presentación (3.3). El guion ya existe en el material compartido del grupo (hay que aplicarle los ajustes que figuran en tu hoja de ensayo).
- **Semana 17 (30-nov al 5-dic):** ensayo grupal, material de apoyo y demo.
- **Semana 18 (7 al 12-dic):** defensa final.
- **Entregable que no está en el repositorio:** el manual técnico (hay un borrador en el paquete de Benjamín).
