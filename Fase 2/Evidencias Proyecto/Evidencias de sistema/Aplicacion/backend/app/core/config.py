"""
Configuración central del backend, leída desde variables de entorno (.env).

Por qué existe este archivo: en vez de escribir contraseñas, claves secretas o
URLs de base de datos directamente en el código, las leemos desde el entorno.
Así el mismo código sirve para desarrollo local, Docker, o producción, solo
cambiando el archivo .env — sin tocar una sola línea de Python.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Base de datos ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/perfil_medico"

    # --- Autenticación / JWT ---
    SECRET_KEY: str = "cambia-esta-clave-en-produccion-por-una-generada-al-azar"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # --- Tareas programadas, recordatorios y alertas (Sprint 4) ---
    # La tarea que genera actividades y envía avisos corre dentro de la API solo si
    # TAREAS_PROGRAMADAS es verdadero (docker-compose lo activa; las pruebas no).
    TAREAS_PROGRAMADAS: bool = False
    TAREAS_INTERVALO_SEGUNDOS: int = 60
    # Zona horaria en la que se interpretan las horas de las actividades.
    ZONA_HORARIA: str = "America/Santiago"
    # Se generan las actividades de hoy y de los días siguientes hasta cubrir 24 a 48 h.
    GENERAR_DIAS_ADELANTE: int = 2
    # Minutos antes de la hora en que se envía el recordatorio (HU 9).
    RECORDATORIO_MINUTOS_ANTES: int = 10
    # Minutos después de la hora sin confirmar para la alerta de nivel 1 y de nivel 2 (HU 10).
    ALERTA_PLAZO_1_MINUTOS: int = 30
    ALERTA_PLAZO_2_MINUTOS: int = 60
    # Cómo se entregan los avisos al dispositivo: "log" solo los registra en el log.
    NOTIFICADOR: str = "log"

    # --- Metadatos de la app ---
    PROJECT_NAME: str = "Perfil Médico+ API"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
