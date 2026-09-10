from collections.abc import Generator
import os
import secrets

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from dgn_picks_api.db.session import SessionLocal


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
