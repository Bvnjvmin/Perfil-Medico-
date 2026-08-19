# Perfil Medico+
Proyecto para Capstone (Grupo 7)

# Objetivo de negocio
Muchas personas deben gestionar sus horas médicas, tratamientos y medicamentos de forma manual o a través de múltiples plataformas no integradas, lo que genera desorganización, pérdida de información y errores en el seguimiento de indicaciones médicas. Esta problemática afecta especialmente a pacientes frecuentes del sistema de salud, adultos mayores y personas con enfermedades crónicas que requieren un seguimiento constante.
Perfil Médico+ nace para resolver esa dispersión: centraliza en un solo sistema toda la información médica relevante del usuario y de su grupo familiar, acompañándolo con recordatorios, recomendaciones personalizadas y una primera orientación ante síntomas. El proyecto se sitúa en el contexto de la Región Metropolitana de Chile —particularmente en comunas con alta demanda de servicios de salud públicos y privados, como Maipú— donde la digitalización de estos procesos puede tener un impacto directo en la eficiencia y accesibilidad de la información para el paciente.
A diferencia de las apps de expediente médico o de agendamiento existentes en el mercado —que suelen cubrir solo un aspecto del cuidado (agenda, historial o medicamentos) de forma aislada—, el diferenciador de Perfil Médico+ es unir en una sola cuenta la gestión del propio paciente y la de las personas a su cargo (hijos y adultos mayores), combinando seguimiento clínico, recordatorios y una primera orientación por IA en un solo flujo pensado para el cuidador familiar.


# Cómo funciona
El usuario registra su perfil de paciente (RUT, nombre, edad, sistema de salud —Isapre o Fonasa— y tipo sanguíneo) y desde ahí gestiona sus horas médicas: registra citas realizadas, recibe recordatorios y puede redirigirse a las plataformas oficiales de los centros médicos en Chile para agendar nuevas horas. El sistema mantiene además un registro de exámenes e historial médico, y un módulo de control de medicamentos que envía recordatorios de dosis y frecuencia.
Un sistema de control parental permite vincular la información médica de hijos y de adultos mayores a cargo, de modo que un mismo usuario pueda supervisar el cuidado de su grupo familiar desde una sola cuenta. Sobre esa base de datos, la plataforma entrega recomendaciones personalizadas según las enfermedades o condiciones médicas del paciente, consejos de salud según la estación del año y las condiciones climáticas, y sugiere farmacias cercanas con disponibilidad, precios y marcas de los medicamentos que el usuario necesita. Un módulo de inteligencia artificial complementa la experiencia respondiendo consultas básicas sobre síntomas y entregando una primera orientación médica, sin reemplazar la atención profesional.

# Componentes
- Gestión de horas médicas: registro de citas, recordatorios e integración con centros médicos para agendamiento externo.
- Registro de exámenes e historial médico del paciente.
- Perfil del paciente: datos personales, sistema de salud y tipo sanguíneo.
- Control de medicamentos con recordatorios de dosis y frecuencia.
- Recomendador de farmacias cercanas (disponibilidad, precios, marcas).
- Control parental: vinculación de hijos y adultos mayores a cargo.
- Motor de recomendaciones personalizadas según condiciones médicas y estación del año.
- Módulo de inteligencia artificial para consultas básicas de síntomas y orientación médica inicial.

# Tecnología
El proyecto se plantea como un sistema informático compuesto por una aplicación móvil y una plataforma web, desarrollado como prototipo funcional (MVP) que prioriza la gestión de horas médicas, medicamentos y el perfil del paciente. El plan de trabajo contempla análisis de requerimientos, diseño de arquitectura de software, desarrollo de frontend y backend, implementación de base de datos, integración de servicios externos, desarrollo del módulo de inteligencia artificial y pruebas del sistema, bajo una metodología ágil y con datos simulados para las etapas de validación.
Como propuesta de stack: aplicación móvil en Flutter/Dart (multiplataforma iOS/Android), backend en Python con FastAPI y base de datos relacional PostgreSQL para el almacenamiento estructurado de horas, tratamientos y medicamentos; autenticación de usuarios mediante JWT y control de acceso diferenciado por rol (paciente titular / perfil dependiente) para sostener el control parental. El módulo de inteligencia artificial para orientación de síntomas se integraría mediante la API de un modelo de lenguaje (por ejemplo, Anthropic Claude), y la interfaz se diseñaría en Figma antes de su implementación. Se contempla además notificaciones push (recordatorios de dosis y citas) y despliegue en la nube para la etapa de validación con datos simulados.
Dado que el sistema administra datos médicos sensibles, se considerará cifrado de la información en tránsito y en reposo, control de acceso por rol y buenas prácticas de protección de datos personales desde el diseño.
