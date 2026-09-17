from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import time

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from dgn_picks_api.domains.users.models import User
from dgn_picks_api.domains.users.passwords import verify_password


AUTH_ROLES = {"admin", "editor", "viewer", "user"}


def auth_configured() -> bool:
    return all(os.getenv(name) for name in ("DGN_AUTH_SECRET", "DGN_AUTH_USERNAME", "DGN_AUTH_PASSWORD"))


def signing_configured() -> bool:
    return bool(os.getenv("DGN_AUTH_SECRET"))


def _encode(payload: dict[str, object]) -> str:
    raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    secret = os.environ["DGN_AUTH_SECRET"].encode()
    signature = hmac.new(secret, raw.encode(), hashlib.sha256).digest()
    return f"{raw}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


def issue_token(username: str, role: str, user_id: int | None = None) -> str:
    if role not in AUTH_ROLES:
        raise ValueError("Unknown role")
    payload: dict[str, object] = {"sub": username, "role": role, "exp": int(time.time()) + 8 * 60 * 60}
    if user_id is not None:
        payload["user_id"] = user_id
    return _encode(payload)


def current_identity(authorization: str | None) -> dict[str, str]:
    if not signing_configured():
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    try:
        raw, encoded_signature = authorization[7:].split(".", 1)
        expected = hmac.new(os.environ["DGN_AUTH_SECRET"].encode(), raw.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(encoded_signature + "=" * (-len(encoded_signature) % 4))
        payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
    except (ValueError, TypeError, json.JSONDecodeError, binascii.Error):
        raise HTTPException(status_code=401, detail="Invalid bearer token") from None
    if not hmac.compare_digest(expected, supplied) or payload.get("exp", 0) < time.time() or payload.get("role") not in AUTH_ROLES:
        raise HTTPException(status_code=401, detail="Invalid or expired bearer token")
    identity = {"username": str(payload["sub"]), "role": str(payload["role"])}
    if payload.get("user_id") is not None:
        identity["user_id"] = str(payload["user_id"])
    return identity


def authenticate(username: str, password: str) -> str:
    if not auth_configured() or not hmac.compare_digest(username, os.environ["DGN_AUTH_USERNAME"]) or not hmac.compare_digest(password, os.environ["DGN_AUTH_PASSWORD"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return issue_token(username, os.getenv("DGN_AUTH_ROLE", "admin"))


def authenticate_user(db: Session, login: str, password: str) -> User:
    user = db.scalar(select(User).where(or_(User.username == login, User.email == login)))
    if user is None or not user.active or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
