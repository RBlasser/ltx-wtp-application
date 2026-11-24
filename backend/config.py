"""Strict environment configuration loader (fail-fast, no silent defaults for secrets)."""

import os


def require_env(name: str) -> str:
    """Return required environment variable or raise RuntimeError."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_bool_env(name: str) -> bool:
    """Parse required boolean environment variable ('true'/'false')."""
    raw = require_env(name).lower()
    if raw in ("true", "1", "yes"):
        return True
    if raw in ("false", "0", "no"):
        return False
    raise RuntimeError(f"Invalid boolean value for {name}: {raw!r}")


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.database_url: str = require_env("DATABASE_URL")
        self.admin_password: str = require_env("ADMIN_PASSWORD")
        self.session_secret: str = require_env("SESSION_SECRET")
        self.cookie_secure: bool = get_bool_env("COOKIE_SECURE")
        self.session_ttl_seconds: int = 8 * 3600


settings = Settings()
