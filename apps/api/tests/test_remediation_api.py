"""HTTP regressions for privacy, revocation, ownership and prediction lifecycle."""
from datetime import UTC, datetime
from decimal import Decimal
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from dgn_picks_api.main import app
from dgn_picks_api.db.base import Base
from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.domains.users.passwords import hash_password
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.picks.service import grade_pick
from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.seed.service import seed_local_data
from dgn_picks_api.seed.quarantine import quarantine_legacy_seed, LEGACY
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from test_picks_api import market_fixture


@pytest.fixture
def api(monkeypatch):
    for key, value in {"DGN_AUTH_SECRET": "test-signing-secret", "DGN_AUTH_USERNAME": "admin", "DGN_AUTH_PASSWORD": "operator-password", "DGN_AUTH_ROLE": "admin"}.items():
        monkeypatch.setenv(key, value)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user, game, market, selection, _ = market_fixture.__wrapped__(db)
        user.password_hash = hash_password("user-password")
        user.email = "gato@example.invalid"
        user.country = "CR"
        db.commit()
        def override():
            yield db
        app.dependency_overrides[get_db] = override
        with TestClient(app) as client:
            yield client, db, user, game, market, selection
        app.dependency_overrides.clear()
    engine.dispose()


def headers(client, username="gato", password="user-password"):
    result = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert result.status_code == 200
    return {"Authorization": "Bearer " + result.json()["access_token"]}


def pick_body(api):
    _, _, user, game, market, selection = api
    return {"user": user.username, "game_id": game.id, "market_id": market.id, "selection_id": selection.id, "stake_units": 1}


def test_public_projection_and_private_account_access(api):
    client, _, user, *_ = api
    for path in ("/api/v1/users", f"/api/v1/users/{user.id}"):
        response = client.get(path)
        assert response.status_code == 200
        rows = response.json() if isinstance(response.json(), list) else [response.json()]
        assert all("email" not in row and "country" not in row and "password_hash" not in row for row in rows)
    assert client.get("/api/v1/admin/users").status_code == 401
    assert client.get("/api/v1/admin/users", headers=headers(client)).status_code == 403
    private = client.get("/api/v1/admin/users", headers=headers(client, "admin", "operator-password"))
    assert private.status_code == 200 and private.json()[0]["email"] == user.email
    account = client.get("/api/v1/auth/account", headers=headers(client))
    assert account.status_code == 200 and account.json()["email"] == user.email


def test_deactivation_reactivation_and_password_change_revoke_sessions(api):
    client, _, user, *_ = api
    old = headers(client)
    admin = headers(client, "admin", "operator-password")
    assert client.patch(f"/api/v1/users/{user.id}", headers=admin, json={"active": False}).status_code == 200
    assert client.post("/api/v1/picks", headers=old, json=pick_body(api)).status_code == 401
    assert client.patch(f"/api/v1/users/{user.id}", headers=admin, json={"active": True}).status_code == 200
    assert client.get("/api/v1/auth/account", headers=old).status_code == 401
    current = headers(client)
    assert client.patch(f"/api/v1/users/{user.id}", headers=admin, json={"password": "replacement-password"}).status_code == 200
    assert client.get("/api/v1/auth/account", headers=current).status_code == 401
    assert client.get("/api/v1/auth/account", headers=headers(client, password="replacement-password")).status_code == 200


def test_deleted_account_token_is_invalid(api):
    client, _, user, *_ = api
    old = headers(client)
    admin = headers(client, "admin", "operator-password")
    assert client.delete(f"/api/v1/users/{user.id}", headers=admin).status_code == 204
    assert client.get("/api/v1/auth/account", headers=old).status_code == 401


def test_pick_auth_ownership_and_price_preservation(api):
    client, db, _, _, _, selection = api
    auth = headers(client)
    body = pick_body(api)
    assert client.post("/api/v1/picks", json=body, headers={"X-DGN-Write-Key": "anything"}).status_code == 401
    assert client.post("/api/v1/picks", json={**body, "user": "daran"}, headers=auth).status_code == 403
    created = client.post("/api/v1/picks", json=body, headers=auth)
    assert created.status_code == 201
    pick = created.json()
    assert client.patch(f"/api/v1/picks/{pick['id']}/grade", headers=auth, json={"result": "win"}).status_code == 403
    edited = client.patch(f"/api/v1/picks/{pick['id']}", json={"user": "gato", "stake_units": 2}, headers=auth)
    assert edited.status_code == 200
    assert edited.json()["line_value"] == pick["line_value"]
    assert edited.json()["decimal_odds"] == pick["decimal_odds"]
    assert client.delete(f"/api/v1/picks/{pick['id']}?user=daran", headers=auth).status_code == 403
    assert client.delete(f"/api/v1/picks/{pick['id']}?user=gato", headers=auth).status_code == 204


@pytest.mark.parametrize("market_status,game_status", [("closed", "scheduled"), ("suspended", "scheduled"), ("open", "final"), ("open", "cancelled"), ("open", "postponed")])
def test_new_predictions_reject_unavailable_events(api, market_status, game_status):
    client, db, _, game, market, _ = api
    game.status, market.status = game_status, market_status
    db.commit()
    assert client.post("/api/v1/picks", headers=headers(client), json=pick_body(api)).status_code == 422


def test_quarantine_is_explicit_idempotent_and_preserves_terms(api):
    client, db, *_ = api
    seed_local_data(db)
    event = next(g for g in db.scalars(select(Game)) if g.external_ids.get("fixture") == "fixture-stanford-duke")
    market = db.scalar(select(Market).where(Market.game_id == event.id, Market.market_type == "game_spread"))
    selection = db.scalar(select(Selection).where(Selection.market_id == market.id))
    user = db.scalar(select(User).where(User.username == "gato"))
    def legacy(stake):
        return Pick(user_id=user.id, game_id=event.id, market_id=market.id, selection_id=selection.id,
                    line_value=Decimal("24.5"), american_odds=-110, decimal_odds=Decimal("1.90909"),
                    stake_units=Decimal(stake), notes="Stanford +24.5")
    pristine, changed = legacy("1"), legacy("2")
    db.add_all([pristine, changed]); db.commit()
    before = (pristine.line_value, pristine.decimal_odds, pristine.american_odds, pristine.picked_at, pristine.notes)
    dry = quarantine_legacy_seed(db)
    assert dry["eligible"] == [pristine.id] and dry["review_required"] == [changed.id]
    assert pristine.archived_at is None
    quarantine_legacy_seed(db, apply=True)
    assert before == (pristine.line_value, pristine.decimal_odds, pristine.american_odds, pristine.picked_at, pristine.notes)
    assert changed.archived_at is None
    assert quarantine_legacy_seed(db, apply=True)["archived"] == []
    assert client.get(f"/api/v1/picks/{pristine.id}").status_code == 404
    assert all(p["id"] != pristine.id for p in client.get("/api/v1/picks").json())
    assert client.patch(f"/api/v1/picks/{pristine.id}", headers=headers(client), json={"user": "gato", "stake_units": 5}).status_code == 404


def test_qa_settlement_examples_are_separate_from_product_users(api):
    _, db, _, game, market, selection = api
    qa = User(username="qa-only", display_name="Isolated QA")
    db.add(qa); db.flush()
    examples = json.loads((Path(__file__).resolve().parents[3] / "data/fixtures/qa-pick-outcomes.json").read_text())
    for example in examples:
        pick = Pick(user_id=qa.id, game_id=game.id, market_id=market.id, selection_id=selection.id,
                    stake_units=Decimal(example["stake"]), decimal_odds=Decimal(example["odds"]))
        db.add(pick); db.commit()
        if example["result"] != "pending":
            grade_pick(db, pick.id, PickResult(example["result"]))
        assert pick.profit_units == (Decimal(example["profit"]) if example["profit"] is not None else None)
        assert pick.user.username == "qa-only"
