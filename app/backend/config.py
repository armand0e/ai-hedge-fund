from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables from the project root .env (if present) while
# still allowing process-level environment variables to override.
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """Application settings sourced from environment variables with optional .env fallback."""

    frontend_origin: Optional[str] = Field(default=None, alias="FRONTEND_ORIGIN")
    public_url: Optional[str] = Field(default=None, alias="PUBLIC_URL")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_host: str = Field(default="0.0.0.0", alias="FRONTEND_HOST")
    frontend_port: int = Field(default=5173, alias="FRONTEND_PORT")
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
