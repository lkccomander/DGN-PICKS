from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.routes.games import create_game, delete_game, update_game
from dgn_picks_api.api.v1.routes.markets import (
    create_market,
    create_selection,
    delete_market,
    delete_selection,
    update_market,
    update_selection,
)
from dgn_picks_api.api.v1.schemas import (
    GameCreate,
    GameUpdate,
    MarketCreate,
    MarketUpdate,
    SelectionCreate,
    SelectionUpdate,
)
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.markets.models import Market
from dgn_picks_api.domains.teams.models import Team


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


def make_teams(session):
    home = Team(name="Home", short_name="Home", abbreviation="HME", conference="C1")
    away = Team(name="Away", short_name="Away", abbreviation="AWY", conference="C2")
    session.add_all([home, away])
    session.flush()
    return home, away


def test_game_market_selection_crud(session):
    home, away = make_teams(session)
    game = create_game(
        GameCreate(
            season=2026,
            week=1,
            kickoff_at=datetime(2026, 9, 7, 20, tzinfo=UTC),
            home_team_id=home.id,
            away_team_id=away.id,
        ),
        session,
    )
    market = create_market(MarketCreate(game_id=game.id, market_type="game_spread"), session)
    selection = create_selection(
        market.id,
        SelectionCreate(market_id=market.id, selection_key="home", team_id=home.id, side="spread"),
        session,
    )

    update_game(game.id, GameUpdate(venue="DGN Stadium"), session)
    update_market(market.id, MarketUpdate(status="suspended"), session)
    update_selection(selection.id, SelectionUpdate(side="spread"), session)
    delete_selection(selection.id, session)
    delete_market(market.id, session)
    delete_game(game.id, session)


def test_game_and_market_references_are_validated(session):
    home, away = make_teams(session)
    with pytest.raises(HTTPException) as missing_team:
        create_game(
            GameCreate(
                season=2026,
                week=1,
                kickoff_at=datetime(2026, 9, 7, 20, tzinfo=UTC),
                home_team_id=home.id,
                away_team_id=999,
            ),
            session,
        )
    assert missing_team.value.status_code == 422

    with pytest.raises(HTTPException) as missing_game:
        create_market(MarketCreate(game_id=999, market_type="game_total"), session)
    assert missing_game.value.status_code == 422


def test_game_with_market_cannot_be_deleted(session):
    home, away = make_teams(session)
    game = create_game(
        GameCreate(
            season=2026,
            week=1,
            kickoff_at=datetime(2026, 9, 7, 20, tzinfo=UTC),
            home_team_id=home.id,
            away_team_id=away.id,
        ),
        session,
    )
    create_market(MarketCreate(game_id=game.id, market_type="game_moneyline"), session)
    with pytest.raises(HTTPException) as blocked:
        delete_game(game.id, session)
    assert blocked.value.status_code == 409
