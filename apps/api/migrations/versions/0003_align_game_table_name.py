"""Align the legacy M1 event table with the M2 Game model name."""
from alembic import op

revision = "0003_align_game_table_name"
down_revision = "0002_m2_domain_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("events", "games")
    op.alter_column("markets", "event_id", new_column_name="game_id")


def downgrade() -> None:
    op.alter_column("markets", "game_id", new_column_name="event_id")
    op.rename_table("games", "events")
