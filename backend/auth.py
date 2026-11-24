"""Stateless HMAC-signed HttpOnly cookie authentication for the /admin console."""

import hashlib
import hmac
import time
from fastapi import Cookie, HTTPException, status
from config import settings

COOKIE_NAME = "wtp_admin_session"


def verify_admin_password(candidate: str) -> bool:
    """Constant-time comparison against configured ADMIN_PASSWORD."""
    return hmac.compare_digest(candidate.encode("utf-8"), settings.admin_password.encode("utf-8"))


def create_session_token() -> str:
    """Create an HMAC-SHA256 signed expiration token."""
    expires_at = str(int(time.time()) + settings.session_ttl_seconds)
    sig = hmac.new(
        settings.session_secret.encode("utf-8"),
        expires_at.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{expires_at}.{sig}"


def verify_session_token(token: str | None) -> bool:
    """Verify signature and expiration of the session cookie."""
    if not token or "." not in token:
        return False
    expires_at_str, sig = token.split(".", 1)
    if not expires_at_str.isdigit():
        return False
    expected_sig = hmac.new(
        settings.session_secret.encode("utf-8"),
        expires_at_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return False
    return int(expires_at_str) > int(time.time())


def require_admin_session(wtp_admin_session: str | None = Cookie(default=None)) -> None:
    """FastAPI dependency enforcing authenticated admin session."""
    if not verify_session_token(wtp_admin_session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión de administrador no válida o expirada.",
        )
