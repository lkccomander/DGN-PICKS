"""Operator import routes have no unauthenticated or development-key bypass."""
from decimal import Decimal

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from dgn_picks_api.api.v1.auth import issue_token
from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.main import app
from dgn_picks_api.seed.service import seed_local_data
from test_pick_imports import db, payload  # noqa: F401 - isolated fixtures


@pytest.fixture
def operator_api(db, monkeypatch):
    for key, value in {"DGN_AUTH_SECRET": "import-test-secret", "DGN_AUTH_USERNAME": "admin",
                       "DGN_AUTH_PASSWORD": "import-test-password", "DGN_AUTH_ROLE": "admin",
                       "DGN_API_WRITE_MODE": "development", "DGN_API_WRITE_KEY": "test-key"}.items():
        monkeypatch.setenv(key, value)
    user = db.scalar(select(User).where(User.username == "gato"))
    operator = {"Authorization": "Bearer " + issue_token("admin", "admin")}
    ordinary = {"Authorization": "Bearer " + issue_token(user.username, "user", user_id=user.id, session_version=user.session_version)}
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    try:
        with TestClient(app) as client:
            yield client, operator, ordinary
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("suffix", ["", "/legacy-seed-quarantine"])
def test_import_actions_require_editor_bearer_identity(operator_api, payload, suffix):
    client, _, ordinary = operator_api
    url = "/api/v1/admin/pick-imports" + suffix
    kwargs = {"json": payload} if not suffix else {}
    assert client.post(url, **kwargs).status_code == 401
    assert client.post(url, headers={"X-DGN-Write-Key": "test-key"}, **kwargs).status_code == 401
    assert client.post(url, headers=ordinary, **kwargs).status_code == 403


def test_operator_http_import_defaults_to_dry_run_and_repeats_safely(operator_api, db, payload):
    client, operator, _ = operator_api
    url = "/api/v1/admin/pick-imports"
    dry = client.post(url, headers=operator, json=payload)
    assert dry.status_code == 200 and not dry.json()["applied"]
    assert len(dry.json()["would_create"]) == 1 and db.scalar(select(Pick)) is None
    applied = client.post(url + "?apply=true", headers=operator, json=payload)
    assert applied.status_code == 200 and len(applied.json()["created"]) == 1
    repeated = client.post(url + "?apply=true", headers=operator, json=payload)
    assert repeated.status_code == 200 and len(repeated.json()["existing"]) == 1
    assert repeated.json()["created"] == []
    public = client.get("/api/v1/picks?user=gato")
    assert public.status_code == 200 and len(public.json()) == 1
    assert public.json()[0]["decimal_odds"] is None
    payload["picks"][0]["line_value"] = "100.5"
    assert client.post(url + "?apply=true", headers=operator, json=payload).status_code == 422
    assert db.scalar(select(Pick)).line_value == Decimal("48.5")


def test_legacy_operator_action_only_archives_strict_known_matches(operator_api, db):
    client, operator, _ = operator_api
    seed_local_data(db)
    user = db.scalar(select(User).where(User.username == "gato"))
    game = next(game for game in db.scalars(select(Game)) if game.external_ids.get("fixture") == "fixture-stanford-duke")
    market = db.scalar(select(Market).where(Market.game_id == game.id, Market.market_type == "game_spread"))
    selection = db.scalar(select(Selection).where(Selection.market_id == market.id))
    def row(stake):
        return Pick(user_id=user.id, game_id=game.id, market_id=market.id, selection_id=selection.id,
                    line_value=Decimal("24.5"), american_odds=-110, decimal_odds=Decimal("1.90909"),
                    stake_units=Decimal(stake), notes="Stanford +24.5")
    strict, edited = row("1"), row("2")
    db.add_all([strict, edited]); db.commit()
    terms = (strict.line_value, strict.decimal_odds, strict.notes, strict.picked_at)
    url = "/api/v1/admin/pick-imports/legacy-seed-quarantine"
    dry = client.post(url, headers=operator)
    assert dry.status_code == 200
    assert dry.json() == {"eligible": [strict.id], "review_required": [edited.id], "archived": []}
    assert strict.archived_at is None
    applied = client.post(url + "?apply=true", headers=operator)
    assert applied.status_code == 200 and applied.json()["archived"] == [strict.id]
    assert strict.archived_at is not None and edited.archived_at is None
    assert terms == (strict.line_value, strict.decimal_odds, strict.notes, strict.picked_at)
    assert client.post(url + "?apply=true", headers=operator).json()["archived"] == []
    assert client.get(f"/api/v1/picks/{strict.id}").status_code == 404
    assert len(client.get("/api/v1/seed/pick-definitions?user=gato").json()) == 13
