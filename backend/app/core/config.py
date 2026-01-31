from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Lifeguard"
    environment: str = "development"
    debug: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_url: str = "http://localhost:8000"

    # Database
    database_url: str = "postgresql+asyncpg://lifeguard:lifeguard@localhost:5432/lifeguard"

    # Telegram
    telegram_bot_token: str = ""
    telegram_webapp_url: str = "http://localhost:5173"

    # Security
    secret_key: str = "your-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
