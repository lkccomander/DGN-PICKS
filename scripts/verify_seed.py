"""Verify deterministic seed behavior in an explicitly configured test database."""
from sqlalchemy import select, func
from dgn_picks_api.db.session import SessionLocal
from dgn_picks_api.domains.picks.models import Pick
from dgn_picks_api.seed.service import seed_local_data

if __name__ == "__main__":
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(Pick))
        first, second = seed_local_data(db), seed_local_data(db)
        assert len(first.unresolved_definitions) == len(second.unresolved_definitions) == 13
        assert first.picks_inserted == second.picks_inserted == second.snapshots_inserted == 0
        assert db.scalar(select(func.count()).select_from(Pick)) == before
        print("Seed repeatability verified; 13 unresolved definitions and no invented product picks")
