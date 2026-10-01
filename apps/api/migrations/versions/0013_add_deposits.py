"""Add pending deposit workflow."""

from alembic import op
import sqlalchemy as sa

revision = "0013_add_deposits"
down_revision = "0012_add_game_sport_league"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "deposits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_deposits_user_id", "deposits", ["user_id"])
    op.create_index("ix_deposits_status", "deposits", ["status"])
    op.create_index("ix_deposits_created_at", "deposits", ["created_at"])


def downgrade() -> None:
    op.drop_table("deposits")
