from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.routes.picks import list_picks, post_pick
from dgn_picks_api.api.v1.schemas import PickCreate
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.games.models import Game
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import OddsSnapshot, SportsbookSource
from dgn_picks_api.domains.picks.service import create_pick
from dgn_picks_api.domains.teams.models import Team
from dgn_picks_api.domains.users.models import User


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


@pytest.fixture
def market_fixture(session):
    user = User(username="gato", display_name="Gato")
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
    market = Market(game_id=game.id, market_type="game_total", period="game")
    session.add(market)
    session.flush()
    selection = Selection(market_id=market.id, selection_key="over", side="over")
    source = SportsbookSource(name="fixture", source_type="fixture")
    session.add_all([selection, source])
    session.flush()
    snapshot = OddsSnapshot(
        selection_id=selection.id,
        sportsbook_id=source.id,
        observed_at=datetime(2026, 9, 7, 18, tzinfo=UTC),
        line_value=Decimal("52.5"),
        american_odds=-110,
        decimal_odds=Decimal("1.90909"),
    )
    session.add(snapshot)
    session.commit()
    return user, game, market, selection, source


def payload(fixture) -> PickCreate:
    _, game, market, selection, _ = fixture
    return PickCreate(
        user="gato",
        game_id=game.id,
        market_id=market.id,
        selection_id=selection.id,
        stake_units=Decimal("1"),
    )


def test_create_pick_copies_current_snapshot(session, market_fixture):
    pick = create_pick(session, payload(market_fixture))
    assert pick.line_value == Decimal("52.500")
    assert pick.american_odds == -110
    assert pick.decimal_odds == Decimal("1.90909")


def test_create_pick_rejects_invalid_references(session, market_fixture):
    request = payload(market_fixture)
    with pytest.raises(ValueError, match="Unknown user"):
        create_pick(session, request.model_copy(update={"user": "missing"}))
    with pytest.raises(ValueError, match="Unknown market"):
        create_pick(session, request.model_copy(update={"market_id": 999}))
    with pytest.raises(ValueError, match="Unknown selection"):
        create_pick(session, request.model_copy(update={"selection_id": 999}))


def test_unresolved_selection_is_rejected(session, market_fixture):
    _, game, market, _, _ = market_fixture
    unresolved = Selection(market_id=market.id, selection_key="unresolved", side=None)
    session.add(unresolved)
    session.commit()
    with pytest.raises(ValueError, match="unresolved"):
        create_pick(
            session,
            PickCreate(
                user="gato",
                game_id=game.id,
                market_id=market.id,
                selection_id=unresolved.id,
                stake_units=Decimal("1"),
            ),
        )


def test_pick_taken_price_does_not_change_after_later_snapshot(session, market_fixture):
    _, _, _, selection, source = market_fixture
    pick = create_pick(session, payload(market_fixture))
    session.add(
        OddsSnapshot(
            selection_id=selection.id,
            sportsbook_id=source.id,
            observed_at=datetime(2026, 9, 7, 19, tzinfo=UTC),
            line_value=Decimal("53.5"),
            american_odds=100,
            decimal_odds=Decimal("2"),
        )
    )
    session.commit()
    session.refresh(pick)
    assert pick.line_value == Decimal("52.500")
    assert pick.american_odds == -110


def test_list_picks_filters_user_and_utc_date(session, market_fixture):
    pick = create_pick(session, payload(market_fixture))
    pick.picked_at = datetime(2026, 9, 7, 23, 30, tzinfo=UTC)
    session.commit()
    assert list_picks(user="gato", pick_date=datetime(2026, 9, 7, tzinfo=UTC).date(), db=session) == [pick]
    assert list_picks(user="daran", db=session) == []
    assert list_picks(pick_date=(datetime(2026, 9, 7, tzinfo=UTC) + timedelta(days=1)).date(), db=session) == []


def test_post_pick_converts_domain_errors_to_422(session, market_fixture):
    with pytest.raises(Exception) as raised:
        post_pick(payload(market_fixture).model_copy(update={"user": "missing"}), session)
    assert getattr(raised.value, "status_code", None) == 422
