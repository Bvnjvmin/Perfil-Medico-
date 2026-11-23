# Tu párrafo de la sección 6 del informe 2.6 — para leer y corregir

El párrafo del 2.6 se armó a partir de tus 2.1 y 2.2. **Es tu reflexión: si una frase no es cierta o no suena a ti, se cambia.**

## Texto actual (tomado del 2.6 en `main`)

> **Benjamín Leiva (backend).** Al comenzar la asignatura mi interés estaba entre la programación y la inteligencia artificial. El proyecto confirmó el primero: diseñé y probé la API (43 rutas, 216 pruebas automatizadas), el servicio de alertas escalonadas, la integración con la pulsera y el asistente de IA, y dejé preparado el envío push en el backend. Trabajar el módulo de IA me mostró que la ingeniería alrededor del modelo (filtrar datos personales, limitar consultas, responder con un texto fijo ante urgencias) pesa tanto como la llamada al modelo; esa parte quedó probada solo en modo simulado y es lo que más me gustaría seguir explorando con un proveedor real. También aprendí a verificar lo que construyo: encontré y corregí desajustes entre app y backend, y probé la API sobre PostgreSQL con un script de 29 comprobaciones. Mis intereses siguen siendo los mismos y el proyecto los reforzó.

## Qué confirmar frase por frase

| Frase | Qué comprobar | Estado |
|---|---|---|
| «43 rutas» | Verificado: la API expone 43 rutas (paths) y 65 operaciones HTTP. Si alguien pregunta, «43 rutas, 65 operaciones» es lo exacto. | ✅ verificado en el código |
| «216 pruebas automatizadas» | Verificado: pytest recolecta 216 pruebas (ver `Verificacion_cifras_informe26.md`). | ✅ |
| «diseñé y probé... la integración con la pulsera y el asistente de IA» | Servicios y rutas son tuyos según el Sprint Backlog 5. El contexto y los casos de IA y la configuración de Traccar los hizo Sergio, y los permisos y la lógica de la IA fueron tuyos. Confirma que «diseñé» te representa. | Tú decides |
| «dejé preparado el envío push en el backend» | Cierto: `NotificadorFCM`, apagado por defecto, 6 pruebas simuladas, sin Firebase real. | ✅ |
| «probé la API sobre PostgreSQL con un script de 29 comprobaciones» | Cierto según `Evidencia_Backend_Sprint5.md` (10-nov, 29 de 29). | ✅ |
| «Mis intereses siguen siendo los mismos» | Solo tú puedes confirmarlo. En tu perfil anterior declarabas interés por IA y datos; si cambió tu énfasis, edítalo. | Tú decides |

## Proyección laboral (última frase de la sección)

El texto dice que sigues con «backend e IA aplicada». Confirma o cambia esa línea (el 2.6 lo deja entre corchetes: «Cada integrante confirma o actualiza su proyección»).

## Cómo corregirlo

El 2.6 está en `Fase 2/Evidencias Grupales/2.6_APT122_InformeFinal_PerfilMedico.docx`. Descárgalo desde GitHub, edita tu párrafo en Word y súbelo de nuevo con la web de GitHub (*Add file → Upload files*, mismo nombre). Avísales a Matías y Sergio para no pisar sus cambios: si ellos también editan, conviene que uno solo suba la versión final.
