"""Virtual credits are owner-scoped, non-monetary and issued once per approval."""
from decimal import Decimal

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from dgn_picks_api.api.v1.auth import issue_token
from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.balances.models import BalanceTransaction
from dgn_picks_api.domains.deposits.models import Deposit
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.main import app


@pytest.fixture
def credits_api(monkeypatch):
    monkeypatch.setenv("DGN_AUTH_SECRET", "virtual-credit-test-secret")
    monkeypatch.setenv("DGN_AUTH_USERNAME", "operator")
    monkeypatch.setenv("DGN_AUTH_PASSWORD", "virtual-credit-test-password")
    monkeypatch.setenv("DGN_AUTH_ROLE", "admin")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        owner, other = User(username="owner", display_name="Owner"), User(username="other", display_name="Other")
        db.add_all([owner, other]); db.commit()
        def headers(user):
            return {"Authorization": "Bearer " + issue_token(user.username, "user", user_id=user.id, session_version=user.session_version)}
        operator = {"Authorization": "Bearer " + issue_token("operator", "admin")}
        def override():
            yield db
        app.dependency_overrides[get_db] = override
        try:
            with TestClient(app) as client:
                yield client, db, owner, other, headers(owner), headers(other), operator
        finally:
            app.dependency_overrides.clear()
    engine.dispose()


def test_credit_authorization_and_owner_scoping(credits_api):
    client, db, owner, other, own, theirs, operator = credits_api
    assert client.post("/api/v1/deposits", json={"amount": "5"}).status_code == 401
    assert client.get("/api/v1/deposits").status_code == 401
    for url in ["/api/v1/admin/deposits", "/api/v1/admin/balances"]:
        assert client.get(url).status_code == 401
        assert client.get(url, headers=own).status_code == 403
    request = client.post("/api/v1/deposits", headers=own, json={"amount": "25.50", "user_id": other.id})
    assert request.status_code == 201
    assert request.json()["user_id"] == owner.id
    assert client.get("/api/v1/deposits", headers=theirs).json() == []
    assert len(client.get("/api/v1/deposits", headers=own).json()) == 1
    assert Decimal(client.get("/api/v1/auth/account", headers=own).json()["balance"]) == 0
    url = f'/api/v1/admin/deposits/{request.json()["id"]}'
    assert client.patch(url, headers=own, json={"status": "approved"}).status_code == 403
    assert db.scalar(select(BalanceTransaction)) is None


def test_credit_approval_is_once_and_balances_are_private(credits_api):
    client, db, owner, _, own, theirs, operator = credits_api
    request = client.post("/api/v1/deposits", headers=own, json={"amount": "75.25"}).json()
    url = f'/api/v1/admin/deposits/{request["id"]}'
    reviewed = client.patch(url, headers=operator, json={"status": "approved"})
    assert reviewed.status_code == 200 and reviewed.json()["reviewed_at"] is not None
    assert client.patch(url, headers=operator, json={"status": "approved"}).status_code == 409
    assert client.patch(url, headers=operator, json={"status": "rejected"}).status_code == 409
    entries = db.scalars(select(BalanceTransaction)).all()
    assert len(entries) == 1 and entries[0].kind == "virtual_credit"
    assert "non-monetary" in entries[0].reason
    assert entries[0].amount == Decimal("75.25")
    assert Decimal(client.get("/api/v1/auth/account", headers=own).json()["balance"]) == Decimal("75.25")
    assert Decimal(client.get("/api/v1/auth/account", headers=theirs).json()["balance"]) == 0
    assert "balance" not in client.get(f"/api/v1/users/{owner.id}").json()


def test_credit_monthly_limit_and_rejection(credits_api):
    client, db, _, _, own, _, operator = credits_api
    request = client.post("/api/v1/deposits", headers=own, json={"amount": "1000"})
    assert request.status_code == 201
    over = client.post("/api/v1/deposits", headers=own, json={"amount": "0.01"})
    assert over.status_code == 409 and "credits" in over.json()["detail"] and "USD" not in over.json()["detail"]
    assert client.patch(f'/api/v1/admin/deposits/{request.json()["id"]}', headers=operator, json={"status": "rejected"}).status_code == 200
    assert db.scalar(select(BalanceTransaction)) is None
    replacement = client.post("/api/v1/deposits", headers=own, json={"amount": "1000"})
    assert replacement.status_code == 201
    assert client.patch(f'/api/v1/admin/deposits/{replacement.json()["id"]}', headers=operator, json={"status": "approved"}).status_code == 200
    assert client.post("/api/v1/deposits", headers=own, json={"amount": "0.01"}).status_code == 409
    for amount in ["0", "-1", "1000.01", "1.001"]:
        assert client.post("/api/v1/deposits", headers=own, json={"amount": amount}).status_code == 422


def test_virtual_adjustments_preserve_auditable_legacy_history(credits_api):
    client, db, owner, _, own, _, operator = credits_api
    legacy = BalanceTransaction(user_id=owner.id, amount=Decimal("4"), kind="deposit", reason="Original legacy record")
    db.add(legacy); db.commit()
    payload = {"user_id": owner.id, "amount": "-1.50", "reason": "Virtual-credit correction"}
    assert client.post("/api/v1/admin/balances/adjust", json=payload).status_code == 401
    assert client.post("/api/v1/admin/balances/adjust", headers=own, json=payload).status_code == 403
    adjusted = client.post("/api/v1/admin/balances/adjust", headers=operator, json=payload)
    assert adjusted.status_code == 201 and adjusted.json()["kind"] == "manual_adjustment"
    assert Decimal(client.get("/api/v1/auth/account", headers=own).json()["balance"]) == Decimal("2.50")
    history = client.get("/api/v1/admin/balances", headers=operator).json()
    assert len(history) == 2 and any(x["reason"] == "Original legacy record" and x["kind"] == "deposit" for x in history)
    assert client.post("/api/v1/admin/balances/adjust", headers=operator, json={**payload, "user_id": 9999}).status_code == 404


def test_credit_history_prevents_owner_deletion_and_survives_deactivation(credits_api):
    client, db, owner, other, own, _, operator = credits_api
    requested = client.post("/api/v1/deposits", headers=own, json={"amount": "12.50"}).json()
    url = f"/api/v1/users/{owner.id}"
    pending_delete = client.delete(url, headers=operator)
    assert pending_delete.status_code == 409
    assert "deactivate instead" in pending_delete.json()["detail"]
    assert client.patch(f'/api/v1/admin/deposits/{requested["id"]}', headers=operator, json={"status": "approved"}).status_code == 200
    assert client.delete(url, headers=operator).status_code == 409
    assert client.patch(url, headers=operator, json={"active": False}).status_code == 200
    assert db.get(User, owner.id).active is False
    request = db.get(Deposit, requested["id"])
    ledger = db.scalar(select(BalanceTransaction).where(BalanceTransaction.user_id == owner.id))
    assert request.status == "approved" and request.amount == Decimal("12.50")
    assert ledger.amount == Decimal("12.50") and ledger.kind == "virtual_credit"
    assert client.delete(f"/api/v1/users/{other.id}", headers=operator).status_code == 204
    # A manual ledger entry also preserves its owner without a request row.
    ledger_owner = User(username="ledger-owner", display_name="Ledger owner")
    db.add(ledger_owner); db.flush()
    db.add(BalanceTransaction(user_id=ledger_owner.id, amount=Decimal("1"), kind="manual_adjustment", reason="Paper credit"))
    db.commit()
    assert client.delete(f"/api/v1/users/{ledger_owner.id}", headers=operator).status_code == 409
