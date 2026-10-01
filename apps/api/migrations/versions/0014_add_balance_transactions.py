"""Add auditable account balance ledger."""

from alembic import op
import sqlalchemy as sa

revision = "0014_add_balance_transactions"
down_revision = "0013_add_deposits"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "balance_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("reason", sa.String(240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_balance_transactions_user_id", "balance_transactions", ["user_id"])
    op.create_index("ix_balance_transactions_kind", "balance_transactions", ["kind"])
    op.create_index("ix_balance_transactions_created_at", "balance_transactions", ["created_at"])


def downgrade() -> None:
    op.drop_table("balance_transactions")
