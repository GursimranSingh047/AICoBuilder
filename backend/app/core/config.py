from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional, List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ProjectPilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "changeme-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///./projectpilot.db"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OpenAI / Gemini compatibility
    # The settings object exposes `GEMINI_*` names for internal use but will
    # fall back to the `openai_api_key` / `OPENAI_MODEL` env vars at startup.
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Storage
    PROJECTS_DIR: str = "./generated_projects"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def projects_path(self) -> Path:
        path = Path(self.PROJECTS_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # pydantic v2 model config: read .env and ignore unknown env vars we handle manually
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    # If the config file or env didn't set GEMINI_API_KEY, allow reading
    # the new `openai_api_key` variable for backward/forward compatibility.
    if not s.GEMINI_API_KEY:
        s.GEMINI_API_KEY = os.getenv("openai_api_key") or os.getenv("OPENAI_API_KEY")

    # Respect explicit OPENAI_MODEL if provided. Read once and assign only when present
    openai_model = os.getenv("OPENAI_MODEL")
    if openai_model is not None and openai_model != "":
        s.GEMINI_MODEL = openai_model

    return s


settings = get_settings()