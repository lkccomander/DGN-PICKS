from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.routes.markets import append_market_snapshot, market_history
from dgn_picks_api.api.v1.schemas import OddsSnapshotCreate
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.markets.models import Market, Selection
from dgn_picks_api.domains.odds.models import SportsbookSource
from dgn_picks_api.domains.teams.models import Team
from dgn_picks_api.domains.games.models import Game


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


@pytest.fixture
def odds_fixture(session):
    home = Team(name="Home", short_name="Home", abbreviation="HME", conference="C1")
    away = Team(name="Away", short_name="Away", abbreviation="AWY", conference="C2")
    source = SportsbookSource(name="local-fixture", source_type="fixture")
    session.add_all([home, away, source])
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
    market = Market(game_id=game.id, market_type="game_total")
    session.add(market)
    session.flush()
    selection = Selection(market_id=market.id, selection_key="over", side="over")
    session.add(selection)
    session.commit()
    return market, selection, source


def snapshot_payload(fixture, observed_at: datetime, decimal_odds: str = "1.90909"):
    market, selection, source = fixture
    return OddsSnapshotCreate(
        selection_id=selection.id,
        sportsbook_id=source.id,
        observed_at=observed_at,
        line_value=Decimal("52.5"),
        american_odds=-110,
        decimal_odds=Decimal(decimal_odds),
    )


def test_history_appends_and_derives_implied_probability(session, odds_fixture):
    market, _, _ = odds_fixture
    first = append_market_snapshot(
        market.id,
        snapshot_payload(odds_fixture, datetime(2026, 9, 7, 18, tzinfo=UTC)),
        session,
    )
    second = append_market_snapshot(
        market.id,
        snapshot_payload(odds_fixture, datetime(2026, 9, 7, 19, tzinfo=UTC), "2"),
        session,
    )
    history = market_history(market.id, session)
    assert [item.id for item in history] == [first.id, second.id]
    assert first.implied_probability == Decimal("0.52380977")
    assert second.decimal_odds == Decimal("2.00000")


def test_duplicate_history_is_rejected_without_overwrite(session, odds_fixture):
    market, _, _ = odds_fixture
    payload = snapshot_payload(odds_fixture, datetime(2026, 9, 7, 18, tzinfo=UTC))
    append_market_snapshot(market.id, payload, session)
    with pytest.raises(HTTPException) as duplicate:
        append_market_snapshot(market.id, payload, session)
    assert duplicate.value.status_code == 409


def test_history_rejects_wrong_selection_or_source(session, odds_fixture):
    market, selection, source = odds_fixture
    with pytest.raises(HTTPException) as wrong_selection:
        append_market_snapshot(
            market.id,
            OddsSnapshotCreate(
                selection_id=999,
                sportsbook_id=source.id,
                observed_at=datetime(2026, 9, 7, 18, tzinfo=UTC),
                decimal_odds=Decimal("2"),
            ),
            session,
        )
    assert wrong_selection.value.status_code == 422
    with pytest.raises(HTTPException) as wrong_source:
        append_market_snapshot(
            market.id,
            OddsSnapshotCreate(
                selection_id=selection.id,
                sportsbook_id=999,
                observed_at=datetime(2026, 9, 7, 18, tzinfo=UTC),
                decimal_odds=Decimal("2"),
            ),
            session,
        )
    assert wrong_source.value.status_code == 422
