import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi import HTTPException

from dgn_picks_api.api.v1.auth import current_identity, issue_token
from dgn_picks_api.api.v1.routes.auth import login, me, register
from dgn_picks_api.api.v1.schemas import LoginRequest, RegistrationRequest
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.users.models import User


def configure_auth(monkeypatch):
    monkeypatch.setenv("DGN_AUTH_SECRET", "test-secret")
    monkeypatch.setenv("DGN_AUTH_USERNAME", "admin")
    monkeypatch.setenv("DGN_AUTH_PASSWORD", "password")
    monkeypatch.setenv("DGN_AUTH_ROLE", "admin")


def test_login_issues_role_bearing_token(monkeypatch):
    configure_auth(monkeypatch)
    response = login(LoginRequest(username="admin", password="password"))
    assert response.role == "admin"
    assert current_identity(f"Bearer {response.access_token}") == {"username": "admin", "role": "admin"}


def test_invalid_credentials_and_expired_or_tampered_tokens(monkeypatch):
    configure_auth(monkeypatch)
    with pytest.raises(HTTPException) as invalid:
        login(LoginRequest(username="admin", password="wrong"))
    assert invalid.value.status_code == 401
    with pytest.raises(HTTPException) as tampered:
        current_identity(f"Bearer {issue_token('admin', 'admin')}x")
    assert tampered.value.status_code == 401


def test_me_requires_bearer_token(monkeypatch):
    configure_auth(monkeypatch)
    with pytest.raises(HTTPException) as missing:
        me(None)
    assert missing.value.status_code == 401


def test_public_registration_and_database_login(monkeypatch):
    configure_auth(monkeypatch)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        response = register(
            RegistrationRequest(
                username="new-user",
                email="new@example.com",
                display_name="New User",
                password="correct horse battery staple",
                country="Costa Rica",
            ),
            db,
        )
        assert response.user.username == "new-user"
        assert response.user.country == "Costa Rica"
        assert db.get(User, response.user.id).password_hash != "correct horse battery staple"
        signed_in = login(LoginRequest(username="new@example.com", password="correct horse battery staple"), db)
        assert signed_in.username == "new-user"
        assert signed_in.role == "user"
        assert current_identity(f"Bearer {signed_in.access_token}") == {"username": "new-user", "role": "user", "user_id": str(response.user.id)}


def test_public_registration_rejects_duplicate_email(monkeypatch):
    configure_auth(monkeypatch)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        payload = RegistrationRequest(username="one", email="same@example.com", display_name="One", password="password-one")
        register(payload, db)
        with pytest.raises(HTTPException) as duplicate:
            register(RegistrationRequest(username="two", email="same@example.com", display_name="Two", password="password-two"), db)
        assert duplicate.value.status_code == 409
