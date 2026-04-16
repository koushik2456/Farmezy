"""
Application Configuration.
Reads settings from environment variables (via .env file) using Pydantic Settings.
"""

import logging
import os
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve backend/.env from this file so imports work no matter the process cwd (conda, IDE, etc.).
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_DOTENV_PATH = _BACKEND_DIR / ".env"

_config_log = logging.getLogger(__name__)


def _is_cmdstan_home(path: Path) -> bool:
    """True if this directory looks like a CmdStan installation (conda-forge layout)."""
    return path.is_dir() and (path / "stan").is_dir()


def _try_cmdstan_from_conda_prefix() -> str | None:
    """If CMDSTAN is unset, point at conda-forge `cmdstan` under CONDA_PREFIX (Windows + Linux)."""
    prefix = (os.environ.get("CONDA_PREFIX") or "").strip()
    if not prefix:
        return None
    root = Path(prefix)
    candidates = [
        root / "Library" / "lib" / "cmdstan",  # Windows conda-forge
        root / "lib" / "cmdstan",  # Linux / macOS conda
    ]
    for c in candidates:
        if _is_cmdstan_home(c):
            return str(c)
    return None


class Settings(BaseSettings):
    # PostgreSQL or SQLite connection string
    DATABASE_URL: str = "sqlite:///./sepm_crop_db.db"

    # Frontend origin for CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # External Data API (data.gov.in — key must be valid and authorised for the resource)
    AGMARKNET_API_KEY: str = ""
    AGMARKNET_BASE_URL: str = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    # Optional: custom CmdStan install for Prophet (cmdstanpy). Leave unset to use bundled/default.
    CMDSTAN: str = ""

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


settings = Settings()
_cmdstan = (settings.CMDSTAN or "").strip()
if _cmdstan:
    os.environ["CMDSTAN"] = _cmdstan
elif not (os.environ.get("CMDSTAN") or "").strip():
    auto = _try_cmdstan_from_conda_prefix()
    if auto:
        os.environ["CMDSTAN"] = auto
        _config_log.info(
            "CMDSTAN was not set in .env; using conda CmdStan at %s (avoids blocked pip-bundled Stan on Windows).",
            auto,
        )
    elif (os.environ.get("CONDA_PREFIX") or "").strip():
        _config_log.warning(
            "conda env is active but no CmdStan install found under CONDA_PREFIX. "
            "Prophet may hit 'Operation not permitted' on Windows. Fix: conda install -c conda-forge cmdstan "
            "then restart the API, or set CMDSTAN in backend/.env to your cmdstan folder.",
        )
