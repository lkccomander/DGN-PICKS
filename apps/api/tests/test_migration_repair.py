"""Repeated deployment repairs missing snapshot references without losing leg data."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
import sqlalchemy as sa


@pytest.mark.parametrize("column_state", ["missing", "nullable", "required"])
def test_restore_snapshot_reference_preserves_existing_rows(column_state):
    path = Path(__file__).resolve().parents[1] / "migrations/versions/0011_restore_pick_leg_snapshot.py"
    spec = spec_from_file_location("repair_snapshot_migration", path)
    migration = module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    snapshots = sa.Table("odds_snapshots", metadata, sa.Column("id", sa.Integer(), primary_key=True))
    columns = [sa.Column("id", sa.Integer(), primary_key=True), sa.Column("receipt", sa.String(80), nullable=False)]
    if column_state != "missing":
        columns.append(sa.Column("odds_snapshot_id", sa.Integer(), sa.ForeignKey("odds_snapshots.id"), nullable=column_state == "nullable"))
    legs = sa.Table("pick_legs", metadata, *columns)
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(snapshots.insert(), {"id": 7})
        row = {"id": 1, "receipt": "keep this existing pick leg"}
        if column_state != "missing":
            row["odds_snapshot_id"] = 7
        connection.execute(legs.insert(), row)
        migration.op = Operations(MigrationContext.configure(connection))
        migration.context = SimpleNamespace(is_offline_mode=lambda: False)
        migration.upgrade()
        migration.upgrade()
        actual = connection.execute(sa.text("SELECT id, receipt, odds_snapshot_id FROM pick_legs")).one()
        assert actual == (1, "keep this existing pick leg", None if column_state == "missing" else 7)
        columns_after = {column["name"]: column for column in sa.inspect(connection).get_columns("pick_legs")}
        assert columns_after["odds_snapshot_id"]["nullable"]
        foreign_keys = sa.inspect(connection).get_foreign_keys("pick_legs")
        assert any(fk["constrained_columns"] == ["odds_snapshot_id"] and fk["referred_table"] == "odds_snapshots" for fk in foreign_keys)
    engine.dispose()
