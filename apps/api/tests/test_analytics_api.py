from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dgn_picks_api.api.v1.routes.analytics import get_summary
from dgn_picks_api.api.v1.routes.dev import seed
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.common.enums import PickResult
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.seed.report import SeedReport


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


def add_pick(session: Session, result: PickResult, stake: str, odds: str | None = "2") -> None:
    session.add(
        Pick(
            user_id=1,
            game_id=1,
            market_id=1,
            selection_id=None,
            stake_units=Decimal(stake),
            decimal_odds=Decimal(odds) if odds is not None else None,
            result=result,
        )
    )


def test_summary_aggregates_results_profit_and_roi(session):
    add_pick(session, PickResult.WIN, "2", "2.5")
    add_pick(session, PickResult.LOSS, "1", "1.9")
    add_pick(session, PickResult.PUSH, "3")
    add_pick(session, PickResult.PENDING, "4")
    add_pick(session, PickResult.VOID, "5")
    session.commit()

    summary = get_summary(session)

    assert summary.wins == 1
    assert summary.losses == 1
    assert summary.pushes == 1
    assert summary.pending == 1
    assert summary.void == 1
    assert summary.total_units_risked == Decimal("11.000")
    assert summary.profit_units == Decimal("2.00000")
    assert summary.roi == Decimal("2") / Decimal("11")


def test_summary_returns_null_roi_when_no_risked_picks(session):
    assert get_summary(session).roi is None


def test_seed_route_returns_report(monkeypatch, session):
    report = SeedReport(users_inserted=3, unresolved_definitions=["Malakai Toney"])
    monkeypatch.setattr("dgn_picks_api.seed.service.seed_local_data", lambda db: report, raising=False)

    response = seed(session)

    assert response.users_inserted == 3
    assert response.unresolved_definitions == ["Malakai Toney"]
    assert response.unresolved_count == 1


def test_pending_and_unpriced_results_do_not_fabricate_roi(session):
    add_pick(session, PickResult.PENDING, "4")
    session.commit()
    result = get_summary(session)
    assert result.profit_units is None and result.roi is None
    assert result.pending_units == Decimal("4")
    assert result.total_units_risked == 0
    add_pick(session, PickResult.WIN, "2", "2")
    add_pick(session, PickResult.LOSS, "1", None)
    session.commit()
    result = get_summary(session)
    assert result.profit_units is None and result.roi is None
    assert result.unpriced_settled_count == 1
    assert result.total_units_risked == Decimal("2")
