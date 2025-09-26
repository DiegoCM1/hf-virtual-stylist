# app/core/config.py
from pydantic_settings import BaseSettings
import os

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")

class Settings(BaseSettings):
    database_url: str
    admin_password: str
    jwt_secret: str
    jwt_algorithm: str

    class Config:
        env_file = ".env"

settings = Settings()

