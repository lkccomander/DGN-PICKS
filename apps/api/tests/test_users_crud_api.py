from datetime import UTC, datetime
from os import environ

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.dependencies import require_development_write_access
from dgn_picks_api.api.v1.routes.users import create_user, delete_user, get_user, update_user
from dgn_picks_api.api.v1.schemas import UserCreate, UserUpdate
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.teams.models import Team
from dgn_picks_api.domains.users.models import User


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


def test_user_crud_create_read_update_delete(session):
    user = create_user(UserCreate(username="new-user", display_name="New User"), session)
    assert get_user(user.id, session).username == "new-user"

    updated = update_user(user.id, UserUpdate(display_name="Renamed", active=False), session)
    assert updated.display_name == "Renamed"
    assert updated.active is False

    response = delete_user(user.id, session)
    assert response.status_code == 204
    with pytest.raises(HTTPException, match="User not found"):
        get_user(user.id, session)


def test_user_crud_rejects_duplicate_and_missing_users(session):
    create_user(UserCreate(username="same", display_name="Same"), session)
    with pytest.raises(HTTPException) as duplicate:
        create_user(UserCreate(username="same", display_name="Again"), session)
    assert duplicate.value.status_code == 409
    with pytest.raises(HTTPException) as missing:
        update_user(999, UserUpdate(active=False), session)
    assert missing.value.status_code == 404


def test_user_with_picks_cannot_be_deleted(session):
    user = User(username="owner", display_name="Owner")
    home = Team(name="Home", short_name="Home", abbreviation="HME", conference="C1")
    away = Team(name="Away", short_name="Away", abbreviation="AWY", conference="C2")
    session.add_all([user, home, away])
    session.flush()
    game = Game(
        season=2026,
        week=1,
        kickoff_at=datetime(2026, 9, 7, 20, tzinfo=UTC),
        home_team_id=home.id,
        away_team_id=away.id,
    )
    session.add(game)
    session.flush()
    session.add(Pick(user_id=user.id, game_id=game.id, market_id=1, stake_units=1))
    session.commit()

    with pytest.raises(HTTPException) as blocked:
        delete_user(user.id, session)
    assert blocked.value.status_code == 409
    assert "deactivate" in blocked.value.detail


def test_development_write_boundary_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("DGN_API_WRITE_MODE", raising=False)
    monkeypatch.delenv("DGN_API_WRITE_KEY", raising=False)
    with pytest.raises(HTTPException) as denied:
        require_development_write_access("anything")
    assert denied.value.status_code == 403


def test_development_write_boundary_requires_matching_key(monkeypatch):
    monkeypatch.setenv("DGN_API_WRITE_MODE", "development")
    monkeypatch.setenv("DGN_API_WRITE_KEY", "local-secret")
    with pytest.raises(HTTPException) as wrong:
        require_development_write_access("wrong")
    assert wrong.value.status_code == 403
    require_development_write_access("local-secret")
