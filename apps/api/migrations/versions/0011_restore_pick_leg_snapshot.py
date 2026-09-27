"""Restore the optional snapshot reference removed by an old deploy wrapper."""
from alembic import context, op
import sqlalchemy as sa

revision = "0011_restore_pick_leg_snapshot"
down_revision = "0010_manual_pick_imports"
branch_labels = None
depends_on = None


def upgrade():
    if context.is_offline_mode():
        # PostgreSQL deployment SQL is repeatable for both damaged and healthy schemas.
        op.execute("ALTER TABLE pick_legs ADD COLUMN IF NOT EXISTS odds_snapshot_id INTEGER REFERENCES odds_snapshots(id)")
        op.execute("ALTER TABLE pick_legs ALTER COLUMN odds_snapshot_id DROP NOT NULL")
        return
    bind = op.get_bind()
    columns = {column["name"]: column for column in sa.inspect(bind).get_columns("pick_legs")}
    if "odds_snapshot_id" not in columns:
        with op.batch_alter_table("pick_legs") as batch:
            batch.add_column(sa.Column("odds_snapshot_id", sa.Integer(), nullable=True))
            batch.create_foreign_key("fk_pick_legs_odds_snapshot_id_odds_snapshots", "odds_snapshots", ["odds_snapshot_id"], ["id"])
    elif not columns["odds_snapshot_id"]["nullable"]:
        with op.batch_alter_table("pick_legs") as batch:
            batch.alter_column("odds_snapshot_id", existing_type=sa.Integer(), nullable=True)


def downgrade():
    # Preserve the restored data/reference: previous application models already use it.
    pass
