"""
Application Configuration.
Reads settings from environment variables (via .env file) using Pydantic Settings.
"""

from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL or SQLite connection string
    DATABASE_URL: str = "sqlite:///./sepm_crop_db.db"

    # Frontend origin for CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # External Data API (data.gov.in — key must be valid and authorised for the resource)
    AGMARKNET_API_KEY: str = ""
    AGMARKNET_BASE_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    @field_validator("AGMARKNET_API_KEY", mode="before")
    @classmethod
    def normalize_api_key(cls, v: Any) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
            s = s[1:-1].strip()
        return s

    class Config:
        env_file = "backend/.env"
        env_file_encoding = "utf-8"


settings = Settings()
