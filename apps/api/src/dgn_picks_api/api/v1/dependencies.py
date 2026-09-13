from collections.abc import Generator
import os
import secrets

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from dgn_picks_api.db.session import SessionLocal
from dgn_picks_api.api.v1.auth import auth_configured, current_identity


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_development_write_access(
    x_dgn_write_key: str | None = Header(default=None),
) -> None:
    """Allow mutations only through the explicit local/development boundary.

    Production has no write access until a real admin/authentication boundary is
    implemented. The shared secret is intentionally supplied by the environment,
    never by source-controlled configuration.
    """
    write_mode = os.getenv("DGN_API_WRITE_MODE", "disabled").strip().lower()
    expected_key = os.getenv("DGN_API_WRITE_KEY")
    if write_mode != "development" or not expected_key or not x_dgn_write_key:
        raise HTTPException(status_code=403, detail="Development write access is disabled")
    if not secrets.compare_digest(x_dgn_write_key, expected_key):
        raise HTTPException(status_code=403, detail="Invalid development write key")


def require_authenticated_write_access(
    authorization: str | None = Header(default=None),
    x_dgn_write_key: str | None = Header(default=None),
) -> None:
    """Require an authenticated editor/admin once production auth is configured.

    The development key fallback is retained only for local migration and tests.
    """
    if not auth_configured():
        return require_development_write_access(x_dgn_write_key)
    identity = current_identity(authorization)
    if identity["role"] not in {"admin", "editor"}:
        raise HTTPException(status_code=403, detail="Editor role required")
