import pytest
from fastapi import HTTPException

from dgn_picks_api.api.v1.auth import current_identity, issue_token
from dgn_picks_api.api.v1.routes.auth import login, me
from dgn_picks_api.api.v1.schemas import LoginRequest


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
