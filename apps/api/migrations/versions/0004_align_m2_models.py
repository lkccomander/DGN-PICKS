"""Align the M2 schema with the current SQLAlchemy domain models."""

from alembic import op
import sqlalchemy as sa


revision = "0004_align_m2_models"
down_revision = "0003_align_game_table_name"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("games", sa.Column("external_ids", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("games", sa.Column("venue", sa.String(160), nullable=True))
    op.add_column("games", sa.Column("home_score", sa.Integer(), nullable=True))
    op.add_column("games", sa.Column("away_score", sa.Integer(), nullable=True))
    op.add_column("odds_snapshots", sa.Column("sportsbook_id", sa.Integer(), nullable=True))
    op.add_column(
        "odds_snapshots",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_foreign_key(
        "fk_odds_snapshots_sportsbook_id",
        "odds_snapshots",
        "sportsbook_sources",
        ["sportsbook_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_odds_snapshots_sportsbook_id", "odds_snapshots", type_="foreignkey")
    op.drop_column("odds_snapshots", "created_at")
    op.drop_column("odds_snapshots", "sportsbook_id")
    op.drop_column("games", "away_score")
    op.drop_column("games", "home_score")
    op.drop_column("games", "venue")
    op.drop_column("games", "external_ids")
