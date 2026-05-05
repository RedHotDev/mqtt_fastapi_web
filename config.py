from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MQTT Settings
    broker_host: str = "m8.wqtt.ru"
    broker_port: int = 20606
    topic: str = "sensors/data"
    client_id: str = "fastapi_mqtt_client"
    mqtt_username: str = 'u_BJIUEH'
    mqtt_password: str = 'jlNoV6gO'

    # Database Settings
    database_url: str = "sqlite+aiosqlite:///./sensors.db"

    # FastAPI Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # ← ИГНОРИРУЕМ дополнительные поля в .env


settings = Settings()
