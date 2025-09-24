# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    admin_password: str
    jwt_secret: str
    jwt_algorithm: str

    class Config:
        env_file = ".env"

settings = Settings()