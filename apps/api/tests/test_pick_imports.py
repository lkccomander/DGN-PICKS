"""Manual imports preserve uncertainty, ownership and history without fixture links."""
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import PickCreate
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market
from dgn_picks_api.domains.odds.models import OddsSnapshot
from dgn_picks_api.domains.picks.imports import PickImportManifest, import_pick_manifest
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.picks.service import create_pick, grade_pick
from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.domains.teams.models import Player, Team
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.main import app


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([User(username="gato", display_name="Gato"), User(username="daran", display_name="Daran")])
        session.commit()
        yield session
    engine.dispose()


@pytest.fixture
def payload():
    return {
        "batch_key": "gato-2026-09-26", "user": "gato",
        "source_file": "picks09262026.md", "pick_date": "2026-09-26",
        "games": [{"key": "2026-09-26:test-away-at-home", "kickoff_at": "2026-09-26T18:00:00Z",
                   "season": 2026, "week": 4, "status": "final",
                   "home_team": {"name": "Test Home", "short_name": "Home", "abbreviation": "TH", "conference": "Test"},
                   "away_team": {"name": "Test Away", "short_name": "Away", "abbreviation": "TA", "conference": "Test"},
                   "source_urls": ["https://example.org/schedule"]}],
        "picks": [{"key": "01", "game_key": "2026-09-26:test-away-at-home",
                   "player_name": "Test Player", "player_team": "home", "player_position": "WR",
                   "original_text": "Over 48.5 rec yds test player", "description": "Test Player over 48.5 receiving yards",
                   "market_type": "player_receiving_yards", "side": "over", "line_value": "48.5",
                   "source_urls": ["https://example.org/roster"]}],
    }


def count(db, model):
    return db.scalar(select(func.count()).select_from(model))


def test_dry_run_performs_no_writes(db, payload):
    result = import_pick_manifest(db, PickImportManifest.model_validate(payload))
    assert not result["applied"] and len(result["would_create"]) == 1
    assert all(count(db, model) == 0 for model in (Pick, Game, Team, Player, Market, OddsSnapshot))
    assert not db.new and not db.dirty


def test_import_is_public_owned_unpriced_and_never_reuses_fixture_event(db, payload):
    home = Team(name="Test Home", short_name="Home", abbreviation="TH", conference="Test")
    away = Team(name="Test Away", short_name="Away", abbreviation="TA", conference="Test")
    db.add_all([home, away]); db.flush()
    db.add_all([
        Game(external_ids={"fixture": "matching-name-demo"}, season=2026, week=4,
             kickoff_at=datetime(2026, 9, 26, 18, tzinfo=UTC), home_team_id=home.id, away_team_id=away.id),
        Player(external_ids={"fixture": "Test Player"}, team_id=home.id, name="Test Player", position="WR"),
    ])
    db.commit()
    result = import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    pick = db.get(Pick, result["created"][0]["pick_id"])
    assert pick.user.username == "gato" and pick.line_value == Decimal("48.5")
    assert pick.american_odds is None and pick.decimal_odds is None and pick.profit_units is None
    assert pick.stake_units == 1 and pick.import_metadata["stake_defaulted"] is True
    assert pick.import_metadata["pick_date"] == "2026-09-26"
    assert pick.import_metadata["pick"]["original_text"] == payload["picks"][0]["original_text"]
    assert count(db, OddsSnapshot) == 0 and count(db, Game) == 2 and count(db, Player) == 2
    assert db.get(Game, pick.game_id).external_ids == {"manual_import": payload["games"][0]["key"]}
    assert db.get(Market, pick.market_id).status == "closed"
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    try:
        with TestClient(app) as client:
            public = client.get("/api/v1/picks?user=gato")
            assert public.status_code == 200
            assert len(public.json()) == 1 and public.json()[0]["decimal_odds"] is None
            assert public.json()[0]["import_metadata"]["source_file"] == "picks09262026.md"
            assert client.get("/api/v1/picks?user=daran").json() == []
    finally:
        app.dependency_overrides.clear()


def test_repeat_preserves_graded_result_and_original_ingestion_time(db, payload):
    manifest = PickImportManifest.model_validate(payload)
    import_pick_manifest(db, manifest, apply=True)
    pick = db.scalar(select(Pick))
    grade_pick(db, pick.id, PickResult.WIN)
    old_time = pick.picked_at
    payload["games"][0]["status"] = "live"  # lifecycle state isn't imported taken terms
    repeated = import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    assert repeated["created"] == [] and len(repeated["existing"]) == 1
    assert count(db, Pick) == 1 and pick.result == "win" and pick.profit_units is None
    assert pick.picked_at == old_time
    assert db.get(Game, pick.game_id).status == "final"


@pytest.mark.parametrize("field,value", [("line_value", "49.5"), ("side", "under"), ("player_name", "Another Player"), ("stake_units", "2")])
def test_same_key_with_changed_terms_is_rejected(db, payload, field, value):
    import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    payload["picks"][0][field] = value
    with pytest.raises(ValueError, match="different identity or terms"):
        import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    pick = db.scalar(select(Pick))
    assert count(db, Pick) == 1 and pick.line_value == Decimal("48.5") and pick.stake_units == 1


def test_failed_later_item_rolls_back_entire_import(db, payload):
    second_game = deepcopy(payload["games"][0])
    second_game["key"] = "second-game"
    # Collision after the first pick was inserted must roll back that pick as well.
    second_game["home_team"]["name"] = "Different Team With Same Abbreviation"
    payload["games"].append(second_game)
    second_pick = deepcopy(payload["picks"][0])
    second_pick.update(key="02", game_key="second-game")
    payload["picks"].append(second_pick)
    with pytest.raises(ValueError, match="abbreviation"):
        import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    assert all(count(db, model) == 0 for model in (Pick, Game, Market, Player, Team))


def test_historical_import_does_not_weaken_normal_prediction_rules(db, payload):
    import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    pick = db.scalar(select(Pick))
    with pytest.raises(ValueError, match="open market"):
        create_pick(db, PickCreate(user="gato", game_id=pick.game_id, market_id=pick.market_id,
                                   selection_id=pick.selection_id, stake_units=1))


def test_unknown_or_inactive_owner_does_not_create_account(db, payload):
    payload["user"] = "absent"
    with pytest.raises(ValueError, match="existing active"):
        import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    assert count(db, User) == 2 and count(db, Pick) == 0
    payload["user"] = "gato"
    db.scalar(select(User).where(User.username == "gato")).active = False
    db.commit()
    with pytest.raises(ValueError, match="existing active"):
        import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)


def test_supplied_price_is_preserved_without_fake_snapshot(db, payload):
    payload["picks"][0]["american_odds"] = -110
    payload["picks"][0]["stake_units"] = "2"
    import_pick_manifest(db, PickImportManifest.model_validate(payload), apply=True)
    pick = db.scalar(select(Pick))
    assert pick.american_odds == -110 and pick.decimal_odds == Decimal("1.90909")
    assert pick.stake_units == 2 and pick.import_metadata["stake_defaulted"] is False
    assert count(db, OddsSnapshot) == 0


def test_invalid_manifest_rejects_duplicates_unknown_reference_and_naive_time(payload):
    duplicate = deepcopy(payload)
    duplicate["picks"].append(deepcopy(duplicate["picks"][0]))
    with pytest.raises(ValidationError, match="Duplicate pick"):
        PickImportManifest.model_validate(duplicate)
    missing_game = deepcopy(payload)
    missing_game["picks"][0]["game_key"] = "not-present"
    with pytest.raises(ValidationError, match="reference a game"):
        PickImportManifest.model_validate(missing_game)
    payload["games"][0]["kickoff_at"] = "2026-09-26T18:00:00"
    with pytest.raises(ValidationError, match="requires a timezone"):
        PickImportManifest.model_validate(payload)


def test_repeated_import_rejects_changed_player_reference(db, payload):
    manifest = PickImportManifest.model_validate(payload)
    import_pick_manifest(db, manifest, apply=True)
    pick = db.scalar(select(Pick))
    player = db.get(Player, db.get(Market, pick.market_id).player_id)
    player.name = "A Different Player"
    db.commit()
    with pytest.raises(ValueError, match="references changed"):
        import_pick_manifest(db, manifest, apply=True)
    assert count(db, Pick) == 1
