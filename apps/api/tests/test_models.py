from sqlalchemy import UniqueConstraint

from dgn_picks_api.db.base import Base
from dgn_picks_api.db.models import OddsSnapshot, Pick, User


def test_m2_models_are_registered_with_metadata() -> None:
    assert {"users", "picks", "odds_snapshots"}.issubset(Base.metadata.tables)
    assert User.__tablename__ == "users"
    assert Pick.__tablename__ == "picks"


def test_odds_snapshots_have_a_duplicate_guard() -> None:
    constraints = OddsSnapshot.__table__.constraints
    assert any(
        isinstance(constraint, UniqueConstraint)
        and {column.name for column in constraint.columns}
        == {"selection_id", "sportsbook_id", "observed_at", "source_event_id"}
        for constraint in constraints
    )
