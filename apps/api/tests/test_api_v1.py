from decimal import Decimal

import pytest

from dgn_picks_api.api.v1.dependencies import get_db
from dgn_picks_api.api.v1.schemas import PickCreate, SeedReportResponse


def test_pick_create_accepts_valid_payload() -> None:
    payload = PickCreate(
        user="gato",
        game_id=1,
        market_id=2,
        selection_id=3,
        stake_units=Decimal("1.25"),
        notes="Opening line",
    )

    assert payload.user == "gato"
    assert payload.stake_units == Decimal("1.25")


@pytest.mark.parametrize("field", ["user", "game_id", "market_id", "stake_units"])
def test_pick_create_requires_required_fields(field: str) -> None:
    values = {
        "user": "gato",
        "game_id": 1,
        "market_id": 2,
        "stake_units": Decimal("1"),
    }
    values.pop(field)

    with pytest.raises(ValueError):
        PickCreate(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [("game_id", 0), ("market_id", -1), ("selection_id", 0), ("stake_units", 0), ("stake_units", "not-a-number")],
)
def test_pick_create_rejects_invalid_numeric_values(field: str, value: object) -> None:
    values = {"user": "gato", "game_id": 1, "market_id": 2, "stake_units": Decimal("1")}
    values[field] = value

    with pytest.raises(ValueError):
        PickCreate(**values)


def test_seed_report_response_includes_derived_unresolved_count() -> None:
    report = SeedReportResponse(
        users_inserted=3,
        users_existing=0,
        games_inserted=4,
        markets_inserted=5,
        snapshots_inserted=6,
        picks_inserted=13,
        duplicate_snapshots=0,
        unresolved_definitions=["Malakai Toney"],
        unresolved_count=1,
    )

    assert report.unresolved_count == len(report.unresolved_definitions)


def test_get_db_yields_and_closes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSession:
        closed = False

        def close(self) -> None:
            self.closed = True

    session = FakeSession()
    monkeypatch.setattr("dgn_picks_api.api.v1.dependencies.SessionLocal", lambda: session)

    dependency = get_db()
    assert next(dependency) is session
    assert not session.closed

    with pytest.raises(StopIteration):
        next(dependency)
    assert session.closed

