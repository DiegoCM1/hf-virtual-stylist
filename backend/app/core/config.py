# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # v2 style: read backend/.env and ignore extra keys (e.g., PUBLIC_BASE_URL)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    admin_password: str
    jwt_secret: str
    jwt_algorithm: str

    # optional; maps from PUBLIC_BASE_URL in .env automatically
    public_base_url: str | None = None

settings = Settings()

# single source of truth for the rest of the app
PUBLIC_BASE_URL: str | None = settings.public_base_url
