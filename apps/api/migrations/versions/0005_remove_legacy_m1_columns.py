"""Remove legacy M1 columns superseded by the M2 domain models."""

from alembic import op
import sqlalchemy as sa


revision = "0005_remove_legacy_m1_columns"
down_revision = "0004_align_m2_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table, columns in {
        "games": ("sport_id", "external_key", "starts_at"),
        "markets": ("selection", "line"),
        "odds_snapshots": ("market_id", "book", "price", "captured_at"),
        "picks": ("title", "status", "created_at"),
    }.items():
        for column in columns:
            op.drop_column(table, column)


def downgrade() -> None:
    # Legacy fields are restored as nullable because existing M2 rows do not
    # contain the old M1 representation.
    op.add_column("picks", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("picks", sa.Column("status", sa.String(24), nullable=True))
    op.add_column("picks", sa.Column("title", sa.String(160), nullable=True))
    op.add_column("odds_snapshots", sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("odds_snapshots", sa.Column("price", sa.Integer(), nullable=True))
    op.add_column("odds_snapshots", sa.Column("book", sa.String(64), nullable=True))
    op.add_column("odds_snapshots", sa.Column("market_id", sa.Integer(), nullable=True))
    op.add_column("markets", sa.Column("line", sa.Numeric(8, 3), nullable=True))
    op.add_column("markets", sa.Column("selection", sa.String(128), nullable=True))
    op.add_column("games", sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("games", sa.Column("external_key", sa.String(128), nullable=True))
    op.add_column("games", sa.Column("sport_id", sa.Integer(), nullable=True))
