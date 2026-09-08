"""Backfill and require pick timestamps for API serialization."""

from alembic import op
import sqlalchemy as sa


revision = "0006_backfill_pick_timestamps"
down_revision = "0005_remove_legacy_m1_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE picks SET picked_at = NOW() WHERE picked_at IS NULL")
    op.alter_column(
        "picks",
        "picked_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )


def downgrade() -> None:
    op.alter_column(
        "picks",
        "picked_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=None,
    )
