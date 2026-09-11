"""Remove the previously materialized Malakai seed input without a side."""

from alembic import op


revision = "0007_remove_malakai_seed_pick"
down_revision = "0006_backfill_pick_timestamps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This exact fixture definition has no Over/Under side and must remain
    # unresolved input, not a materialized pick.
    op.execute("""
        DELETE FROM picks
        USING users
        WHERE picks.user_id = users.id
          AND users.username = 'gato'
          AND picks.notes = 'Malakai Toney 72.5 rec yards'
    """)


def downgrade() -> None:
    # The original record had no valid selection side or price to restore.
    pass
