# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")

class Settings(BaseSettings):
    # allow other env vars in .env without error
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    admin_password: str
    jwt_secret: str
    jwt_algorithm: str

    # optional, so having PUBLIC_BASE_URL in .env won’t crash
    public_base_url: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()


# keep a simple constant too (backward compatible with your imports)
PUBLIC_BASE_URL = settings.public_base_url or os.getenv("PUBLIC_BASE_URL")