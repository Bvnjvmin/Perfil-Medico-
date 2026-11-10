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
    # Solo con NOTIFICADOR=fcm (Firebase Cloud Messaging, API HTTP v1): ruta al archivo JSON de la
    # cuenta de servicio y el identificador del proyecto de Firebase. El archivo NO se sube al repositorio.
    FCM_CREDENCIALES: str = ""
    FCM_PROYECTO_ID: str = ""
    # Decisión 9 del Sprint 4: si es verdadero, la alerta de nivel 2 también llega al titular
    # (hoy solo llega a los cuidadores con nivel_escalamiento = 2).
    ALERTA_NIVEL_2_INCLUYE_TITULAR: bool = False

    # --- Pulsera, botón de asistencia y eventos de seguridad (Sprint 5, HU 14, 17, 18, 19) ---
    # Clave compartida con el servidor Traccar. Vacía = la ruta /traccar/posiciones queda apagada.
    TRACCAR_TOKEN: str = ""
    # Batería baja de la pulsera: por debajo de este porcentaje se avisa una vez.
    BATERIA_BAJA_PORCENTAJE: int = 15
    # Un mismo tipo de evento del mismo perfil no se repite dentro de esta ventana.
    EVENTO_VENTANA_DEDUP_MINUTOS: int = 10
    # Inactividad inusual: la pulsera reporta, pero no se movió más de INACTIVIDAD_RADIO_METROS
    # en INACTIVIDAD_MINUTOS, y solo se evalúa de día (hora local, [DESDE, HASTA)).
    INACTIVIDAD_MINUTOS: int = 180
    INACTIVIDAD_RADIO_METROS: int = 30
    INACTIVIDAD_DESDE_HORA: int = 8
    INACTIVIDAD_HASTA_HORA: int = 22
    # Las posiciones guardadas más viejas que esto se borran en el ciclo programado.
    POSICIONES_DIAS_RETENCION: int = 30

    # --- Módulo de IA, orientación general (Sprint 5, HU 15) ---
    # "simulado" no usa red ni credenciales (respuestas de ejemplo); "anthropic" llama a la API.
    IA_PROVEEDOR: str = "simulado"
    IA_API_KEY: str = ""
    IA_MODELO: str = "claude-haiku-5-5"
    IA_MAX_TOKENS: int = 600
    IA_TIMEOUT_SEGUNDOS: int = 30
    # Tope de consultas por usuario y por día (control de costo).
    IA_MAX_CONSULTAS_DIA: int = 30

    # --- Metadatos de la app ---
    PROJECT_NAME: str = "Perfil Médico+ API"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
