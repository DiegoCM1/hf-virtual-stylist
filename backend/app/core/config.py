# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    # v2 style: read backend/.env and ignore extra keys (e.g., PUBLIC_BASE_URL)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database - PostgreSQL (required, get from Railway dashboard)
    database_url: str = ""  # Must be set in .env or environment
    admin_password: str = "not-used"
    jwt_secret: str = "not-used"
    jwt_algorithm: str = "HS256"

    # --- Storage ---
    storage_backend: str = "local"
    public_base_url: str | None = None # For LocalStorage fallback
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_url: str = ""

settings = Settings()

# single source of truth for the rest of the app
PUBLIC_BASE_URL: str | None = settings.public_base_url

# --- ControlNet (env-driven) ---
CONTROLNET_ENABLED = os.getenv("CONTROLNET_ENABLED", "0") == "1"
CONTROLNET_MODEL = os.getenv("CONTROLNET_MODEL", None)  # e.g. "diffusers/controlnet-openpose-sdxl-1.0"
CONTROLNET_WEIGHT = float(os.getenv("CONTROLNET_WEIGHT", "1.15"))
CONTROLNET_GUIDANCE_START = float(os.getenv("CONTROLNET_GUIDANCE_START", "0.0"))
CONTROLNET_GUIDANCE_END = float(os.getenv("CONTROLNET_GUIDANCE_END", "0.75"))

CONTROL_IMAGE_RECTO = os.getenv("CONTROL_IMAGE_RECTO", None)
CONTROL_IMAGE_CRUZADO = os.getenv("CONTROL_IMAGE_CRUZADO", None)
