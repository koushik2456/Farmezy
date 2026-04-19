"""
Application Configuration.
Reads settings from environment variables (via .env file) using Pydantic Settings.
"""

import logging
import re
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve backend/.env from this file so imports work no matter the process cwd (conda, IDE, etc.).
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
_DOTENV_PATH = _BACKEND_DIR / ".env"
_log = logging.getLogger(__name__)

# Daily Price API (Agmarknet) — resource id must appear in the path: /resource/<uuid>
_DEFAULT_DATAGOV_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
_DEFAULT_AGMARKNET_BASE_URL = f"https://api.data.gov.in/resource/{_DEFAULT_DATAGOV_RESOURCE_ID}"


def _normalize_agmarknet_base_url(url: str) -> str:
    """
    If AGMARKNET_BASE_URL is set to https://api.data.gov.in/resource (no dataset id),
    every request returns HTTP 404. Append the default Daily Price resource id.
    """
    u = (url or "").strip().rstrip("/")
    if not u:
        return _DEFAULT_AGMARKNET_BASE_URL
    # Already has a resource uuid in the path
    if re.search(r"/resource/[0-9a-f]{8}-[0-9a-f-]{27,36}", u, re.I):
        return u
    # Truncated URL: ends with .../resource
    if u.endswith("/resource") or u.lower().endswith("api.data.gov.in/resource"):
        fixed = f"{u}/{_DEFAULT_DATAGOV_RESOURCE_ID}"
        _log.warning(
            "AGMARKNET_BASE_URL was missing the dataset UUID (got %r). Using %r. "
            "Set the full URL in backend/.env (copy from the dataset API page on data.gov.in).",
            url,
            fixed,
        )
        return fixed
    return u


def _resolve_sqlite_relative_to_project(url: str) -> str:
    """
    `sqlite:///./sepm_crop_db.db` is cwd-dependent; anchor it to the repo root so the API and
    seeder always share one file no matter where uvicorn was started from.
    """
    prefix = "sqlite:///./"
    if url.startswith(prefix):
        rel = url[len(prefix) :]
        abs_path = (_PROJECT_ROOT / rel).resolve()
        return f"sqlite:///{abs_path.as_posix()}"
    return url


def cors_origins_for_settings(frontend_origin: str) -> list[str]:
    """Allow both localhost and 127.0.0.1 so browser CORS matches Vite dev server URL."""
    base = (frontend_origin or "http://localhost:5173").rstrip("/")
    origins = {base}
    if "://localhost" in base:
        origins.add(base.replace("://localhost", "://127.0.0.1", 1))
    if "://127.0.0.1" in base:
        origins.add(base.replace("://127.0.0.1", "://localhost", 1))
    return sorted(origins)


class Settings(BaseSettings):
    # PostgreSQL or SQLite connection string
    DATABASE_URL: str = "sqlite:///./sepm_crop_db.db"

    # Frontend origin for CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # External Data API (data.gov.in — key must be valid and authorised for the resource)
    AGMARKNET_API_KEY: str = ""
    AGMARKNET_BASE_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    model_config = SettingsConfigDict(
        env_file=str(_DOTENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("AGMARKNET_API_KEY", mode="before")
    @classmethod
    def normalize_api_key(cls, v: Any) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
            s = s[1:-1].strip()
        return s


_settings = Settings()
_db_url = _resolve_sqlite_relative_to_project(_settings.DATABASE_URL)
_ag_url = _normalize_agmarknet_base_url(_settings.AGMARKNET_BASE_URL)
_updates: dict[str, Any] = {}
if _db_url != _settings.DATABASE_URL:
    _updates["DATABASE_URL"] = _db_url
if _ag_url != _settings.AGMARKNET_BASE_URL:
    _updates["AGMARKNET_BASE_URL"] = _ag_url
settings = _settings.model_copy(update=_updates) if _updates else _settings
CORS_ALLOW_ORIGINS = cors_origins_for_settings(settings.FRONTEND_ORIGIN)
