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

    # --- Metadatos de la app ---
    PROJECT_NAME: str = "Perfil Médico+ API"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
