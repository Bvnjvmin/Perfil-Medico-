# Product Vision — Perfil Médico+

**Equipo 7 · Capstone_005D · Ingeniería Informática, Sede Plaza Oeste**
**Product Owner:** Sergio Ocares
**Versión:** 1.0 · 5 de noviembre de 2026 (el producto lleva 4 sprints construidos)

## 1. Visión en una frase

> **Para** familias que cuidan a un adulto mayor, a una persona con una enfermedad crónica o a un niño, y que no siempre pueden estar presentes,
> **que necesitan** asegurarse de que las indicaciones de salud se cumplan a tiempo,
> **Perfil Médico+** es una aplicación móvil con backend
> **que** centraliza la información de salud, recuerda cada actividad de cuidado y avisa a los cuidadores autorizados cuando algo no se confirma.
> **A diferencia de** los papeles, las fotos de recetas, los chats de WhatsApp y las alarmas sueltas del teléfono,
> **nuestro producto** reúne todo en un solo lugar, con permisos por persona y un aviso que escala solo, sin asumir que haya una emergencia.

## 2. El problema

Muchas familias de la Región Metropolitana gestionan las horas médicas, los medicamentos, los controles y los antecedentes de salud de forma manual y repartida: papeles, fotos de recetas, calendarios, WhatsApp y alarmas del teléfono. Esa dispersión genera desorden, pérdida de información y dificulta cumplir las indicaciones, sobre todo en adultos mayores, personas con enfermedades crónicas y personas que necesitan apoyo permanente. Los familiares que cumplen el rol de cuidador, y que no siempre están físicamente presentes, no tienen cómo saber si una dosis o una rutina se hizo.

## 3. A quién ayudamos

| Usuario | Quién es | Qué necesita |
|---|---|---|
| **Titular** | El adulto responsable de la cuenta. Administra su propio perfil y los de las personas a su cargo. | Un solo lugar para planificar medicamentos y rutinas, y enterarse si algo no se confirma. |
| **Cuidador autorizado** | Un familiar u otra persona invitada a un perfil, con permisos que decide el titular. | Ver y confirmar actividades y recibir alertas, sin acceder a más de lo que se le permitió. |
| **Dependiente** | Adulto mayor no autovalente o niño. | Una vista muy simple, con botones grandes y un solo toque para confirmar. |

## 4. Propuesta de valor

El producto sigue un ciclo de seguimiento continuo:

```
Planificar → Recordar → Confirmar → Monitorear → Alertar → Acompañar
```

1. **Un perfil por persona.** Una cuenta titular puede tener su propio perfil y perfiles dependientes, cada uno con medicamentos, rutinas, alergias y contactos de emergencia.
2. **Recordatorios que no se olvidan.** Cada medicamento o rutina puede tener varias horas por día, y el sistema genera la agenda solo.
3. **Alertas que escalan.** Si una actividad no se confirma, el aviso sube de nivel (primero al titular, luego a los cuidadores que corresponda). El mensaje informa que no fue confirmada, sin asumir una emergencia.
4. **Permisos por perfil.** El titular decide qué puede hacer cada cuidador y puede quitarle el acceso en cualquier momento.
5. **Tres interfaces según quién la usa.** App completa para el titular y el cuidador, vista simplificada para el dependiente y, más adelante, una pulsera con botón SOS.

## 5. Objetivos del producto

**Objetivo general.** Desarrollar Perfil Médico+, una aplicación móvil con backend que centralice la salud personal y familiar mediante un modelo de cuenta titular con perfiles dependientes, gestionando rutinas de cuidado y generando alertas configurables hacia los cuidadores autorizados.

**Objetivos específicos y estado actual**

| # | Objetivo | Historias | Estado |
|---|---|---|---|
| 1 | Autenticación y gestión de cuentas, con perfiles propios y dependientes | HU 1, 2, 6 | ✅ Construido |
| 2 | Registro y seguimiento de rutinas de cuidado con confirmación | HU 4, 5 | ✅ Construido |
| 3 | Permisos configurables para invitar cuidadores | HU 7, 8 | ✅ Construido |
| 4 | Recordatorios y alertas escalonadas | HU 9, 10, 11 | 🟡 Construido; en validación del Product Owner. El push real al celular (FCM) queda pendiente |
| 5 | Indicadores de salud e historial de cumplimiento con gráficos | HU 12, 13 | ⏳ Sprint 5 |
| 6 | Módulo de orientación general con IA | HU 15 | ⏳ Sprints 5 y 6 |
| 7 y 8 | Pulsera inteligente con GPS, geocercas, caídas, SOS y batería baja | HU 17 a 19 | ⏳ Sprint 5 |
| 9 | Registro manual de glucosa y otros parámetros | HU 20 | ⏳ Sprint 6 |
| 10 | Recordatorios extendidos (indicaciones médicas y citas) | HU 21 | ⏳ Sprint 6 |
| 11 | Orientación sobre farmacias cercanas con IA | HU 22 | ⏳ Sprint 6 |

El detalle de cada historia está en el Product Backlog (`Fase 1/Evidencias Grupales/Cronograma_Actividades_Equipo_PerfilMedico.xlsx`, hoja *Product Backlog MVP*) y el avance de cada sprint, en `Metodologia_Scrum/`.

## 6. Diferenciadores

- **Pulsera ya existente en el mercado**, conectada con un servidor propio de Traccar, en vez de fabricar hardware.
- **Escalamiento de alertas** hacia cuidadores distintos según su nivel, y no un solo aviso a una sola persona.
- **Interfaz simplificada** pensada para quien no usa bien un celular.
- **Registro manual de glucosa**: la lectura la ingresa el cuidador desde un glucómetro certificado, porque no se mide de forma automática por seguridad.

## 7. Qué NO es Perfil Médico+

- No entrega diagnósticos ni reemplaza a un profesional de la salud. La IA da orientación general.
- No fabrica hardware propio.
- No mide la glucosa con relojes o pulseras.
- No asume una emergencia cuando una actividad no se confirma: informa y escala.

## 8. Qué entendemos por éxito

*Indicadores propuestos por el Product Owner; se revisan con el equipo en cada retrospectiva.*

| Indicador | Qué nos dice |
|---|---|
| Porcentaje de actividades confirmadas a tiempo | Si el recordatorio ayuda a cumplir las indicaciones (historial de cumplimiento, HU 13) |
| Tiempo entre una actividad no confirmada y la respuesta de un cuidador | Si el escalamiento funciona |
| Historias terminadas y aceptadas por el Product Owner al cierre de cada sprint | Si el equipo entrega lo comprometido |
| Criterios de aceptación probados con tres cuentas (titular, cuidador y persona ajena) | Si los permisos se respetan |

## 9. Modelo de negocio (proyección)

Modelo freemium: un plan **Gratis** (1 perfil, recordatorios básicos y confirmación manual) y un plan **Premium** ($3.490 CLP al mes o $29.990 CLP al año por el primer perfil dependiente) con pulsera conectada, alertas escalonadas, historial completo, reportes para el médico e IA. Cada perfil dependiente adicional tiene un 5 % de descuento. El detalle está en el README y en la Guía 1.5 de la Fase 1.

## 10. Equipo

| Integrante | Rol |
|---|---|
| Sergio Ocares | Product Owner: base de datos, indicadores e integración de IA |
| Benjamín Leiva | Backend: API, autenticación y orquestación de IA |
| Matías Pizarro | App móvil (Flutter): interfaz y experiencia de usuario |
