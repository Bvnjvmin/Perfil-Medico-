# Verificación de cifras del informe 2.6 y de la presentación

Hecha el 22-nov-2026 sobre `main` (último commit del 20-nov). Se clonó el repositorio, se instalaron las dependencias de `requirements.txt` en un entorno limpio (Python 3.13) y se ejecutó el backend.

| Cifra (dónde aparece) | Resultado | Cómo se comprobó |
|---|---|---|
| **216 pruebas automáticas** (2.6, diap. 7, 10 y 12) | ✅ **216 pasan, 0 fallan** | Se ejecutó `pytest app/tests` completo: 216 recolectadas y 216 pasaron (los 6 de FCM incluidos). Ojo: `backend/pytest.log` y la captura `S5_00.3` dicen 210, porque son anteriores a las 6 pruebas de FCM del 10-nov. |
| **43 rutas de API** (2.6, diap. 12) | ✅ con una aclaración | `openapi.json` tiene **43 rutas (paths)** y **65 operaciones HTTP** (GET, POST, PUT, DELETE...). Si alguien dice «43 endpoints», la comisión puede contar 65. Mejor decir «43 rutas, 65 operaciones». |
| **17 tablas / diagrama ER de 17 tablas** (diap. 9) | ✅ | 17 `__tablename__` en los modelos; el diagrama de `modelo_datos.md` tiene 17 entidades. |
| **Cabeza de migraciones `a5b6c7d8e9f0`** | ✅ | `alembic heads` la confirma; 15 archivos de migración. |
| **29 de 29 pruebas de humo** (2.6, diap. 12) | ⚠️ no reejecutada | Consta en `Evidencia_Backend_Sprint5.md` (10-nov, PostgreSQL, sin Docker). Requiere PostgreSQL; no se repitió. Queda como parte de la prueba D5 en Docker. |
| **Sprints 3 y 4 aceptados 17 de 17** (2.6, diap. 12) | ✅ | README y `Checklist_Aceptacion_PO_Sprint4.md` línea 57: «17 de 17». |
| **Capturas: 17 (Sprint 3), 34 (Sprint 4), S5_00 a S5_06** (2.6, sección 5) | 🟡 | La carpeta del Sprint 3 tiene **18** capturas (hay dos que empiezan con `S3_02`), la del Sprint 4 tiene 34 y la del Sprint 5 tiene 56. Corregir «17» por «18» en el 2.6 o quitar la cifra. |
| **17 de 22 historias con evidencia** (diap. 5 y 12) | ✅ con matiz | Ver el análisis de Sergio (`Verificacion_17_de_22_historias.md`): sale 17 contando HU 9 parcial, HU 15 en modo simulado y HU 17 y 19 con simulador. |
| **«Cinco sprints de dos semanas»** (diap. 7) | ✅ | Sprints 1 a 5 de dos semanas; el Sprint 6 es la semana 15. |

## Inconsistencias entre la presentación y el informe (corregir antes de ensayar)

1. **Diapositiva 4 (objetivos):** el guion dice «5 logrados, tres parciales, dos no desarrollados» (10 de 11). El 2.6 tiene **5 logrados, 4 parciales (objetivos 6, 7, 8 y 9) y 2 no desarrollados (10 y 11)**. Decir «cuatro parciales».
2. **Diapositiva 13 (obstáculo de Matías):** «el Docker exigía activar virtualización en la BIOS, por eso sus capturas siguen pendientes». Pero en el repositorio **sí existen capturas de Docker**: `S5_00.1_alembic_current_docker.png`, `S5_00.4_alembic_check.png` y `backend/evidencias/S5_alembic_docker.png`. Lo pendiente es la prueba completa (compose ps, health, pytest en contenedor, humo). Además, el 2.6 atribuye el problema de la BIOS a Sergio. Reformular: «Docker exigió activar la virtualización en la BIOS; las migraciones ya se probaron en Docker, falta documentar la prueba completa».
3. **Diapositiva 7:** dice «Estamos en el Sprint 6, semana 15». Hoy ya es la semana 16 (Fase 3 comienza el 23-nov). Cambiar a «el Sprint 6 (semana 15) fue de cierre».
4. **2.6, sección 4:** «Sprint 6 (en curso al redactar)». Si el informe se entrega como final, conviene dejarlo en pasado: «Sprint 6: cierre con pruebas, documentación e informe».

## Falta un entregable

El Cronograma (semana 15) lista para el Informe Final: «**manual técnico** + README + aplicación funcional con backend en Docker». En el repositorio no hay manual técnico. Se dejó un borrador en `Manual_Tecnico_BORRADOR.md`.

## Seguridad: una cosa para decidir

`docker-compose.yml` lee el `.env`, y `.env.example` trae `SECRET_KEY=pega-aqui-una-clave-larga-y-aleatoria`. Si alguien copia el ejemplo y no la cambia, el backend firma los JWT con una clave pública. En desarrollo no es grave; en la defensa conviene decir que en uso real se genera una clave aleatoria (el manual técnico lo indica en el paso 1).
