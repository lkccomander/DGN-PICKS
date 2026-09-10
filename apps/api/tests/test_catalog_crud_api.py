import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.routes.teams import (
    create_player,
    create_team,
    delete_player,
    delete_team,
    get_player,
    update_player,
    update_team,
)
from dgn_picks_api.api.v1.schemas import PlayerCreate, PlayerUpdate, TeamCreate, TeamUpdate
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


def test_team_and_player_crud(session):
    team = create_team(
        TeamCreate(
            name="New Team",
            short_name="New",
            abbreviation="NEW",
            conference="C1",
        ),
        session,
    )
    player = create_player(PlayerCreate(team_id=team.id, name="Player One", position="QB"), session)
    assert get_player(player.id, session).team_id == team.id

    updated_team = update_team(team.id, TeamUpdate(conference="C2"), session)
    updated_player = update_player(player.id, PlayerUpdate(name="Player Two"), session)
    assert updated_team.conference == "C2"
    assert updated_player.name == "Player Two"

    delete_player(player.id, session)
    delete_team(team.id, session)
    with pytest.raises(HTTPException) as missing:
        get_player(player.id, session)
    assert missing.value.status_code == 404


def test_player_requires_existing_team(session):
    with pytest.raises(HTTPException) as missing:
        create_player(PlayerCreate(team_id=999, name="Ghost", position="QB"), session)
    assert missing.value.status_code == 422


def test_team_and_player_references_block_deletion(session):
    team = create_team(
        TeamCreate(name="Referenced", short_name="Ref", abbreviation="REF", conference="C1"),
        session,
    )
    player = create_player(PlayerCreate(team_id=team.id, name="Referenced Player", position="WR"), session)
    with pytest.raises(HTTPException) as team_blocked:
        delete_team(team.id, session)
    assert team_blocked.value.status_code == 409

    game = Game(
        season=2026,
        week=1,
        kickoff_at="2026-09-07 20:00:00",
        home_team_id=team.id,
        away_team_id=team.id,
    )
    market = Market(game_id=1, market_type="player_receiving_yards", player_id=player.id)
    session.add_all([game, market])
    session.flush()
    market_selection = Selection(market_id=market.id, selection_key="player", player_id=player.id)
    session.add(market_selection)
    session.commit()

    with pytest.raises(HTTPException) as player_blocked:
        delete_player(player.id, session)
    assert player_blocked.value.status_code == 409
