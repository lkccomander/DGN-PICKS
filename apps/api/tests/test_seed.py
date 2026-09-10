import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select

from dgn_picks_api.db import models as _models  # noqa: F401
from dgn_picks_api.db.base import Base
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.domains.users.models import User
from dgn_picks_api.seed.service import seed_local_data


@pytest.fixture
def seed_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_seed_is_idempotent_and_keeps_picks_with_gato(seed_session):
    first = seed_local_data(seed_session)
    first_picks = seed_session.scalars(select(Pick)).all()

    second = seed_local_data(seed_session)
    second_picks = seed_session.scalars(select(Pick)).all()

    assert {user.username for user in seed_session.scalars(select(User)).all()} == {"gato", "daran", "noch"}
    assert first.picks_inserted == len(first_picks) == 6
    assert second.picks_inserted == 0
    assert len(second_picks) == len(first_picks)
    assert second.duplicate_snapshots == first.snapshots_inserted
    assert {pick.user.username for pick in second_picks} == {"gato"}
    assert set(first.unresolved_definitions) == {
        "Malakai Toney 72.5 rec yards",
        "Over 58.5 Auburn",
        "Over 54.5 UCLA",
        "Notre Dame -20.5",
        "Ole Miss -6.5",
        "Over 52.5 Houston",
        "Over 53.5 SMU",
    }
