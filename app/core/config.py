from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str = "local"

    ROBOFLOW_API_URL: str = "https://serverless.roboflow.com"
    ROBOFLOW_API_KEY: str
    ROBOFLOW_MODEL_ID: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
