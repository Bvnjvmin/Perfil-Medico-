# backend/

**Responsable:** Benjamín Leiva
**Stack:** Python + FastAPI + PostgreSQL (vía SQLAlchemy/Alembic)

## Qué va aquí

Esta carpeta contendrá la API REST del proyecto, siguiendo la estructura definida en el Plan de Trabajo (ver `/docs`):

```
backend/
├── app/
│   ├── main.py            # punto de entrada de FastAPI
│   ├── routers/            # endpoints por módulo (auth, perfiles, rutinas, alertas...)
│   ├── models/              # modelos de datos (SQLAlchemy)
│   └── services/            # lógica de negocio
├── alembic/                 # migraciones de base de datos
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Módulos planificados (Fase 2)

| Sprint | Módulo | Semanas |
|---|---|---|
| 1 | Autenticación JWT y cuentas/perfiles | 5-6 |
| 2 | Medicamentos y rutinas | 7-8 |
| 3 | Perfiles dependientes y permisos de cuidadores | 9-10 |
| 4 | Recordatorios y alertas escalonadas | 11-12 |
| 5 | Indicadores de salud e integración de IA | 13-15 |

## Cómo correrlo (una vez implementado)

Ver instrucciones completas en el [README principal](../README.md).
