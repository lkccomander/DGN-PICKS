"""Add persisted account credentials for public user accounts."""

from alembic import op
import sqlalchemy as sa


revision = "0008_user_account_credentials"
down_revision = "0007_remove_malakai_seed_pick"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=320), nullable=True))
    op.add_column("users", sa.Column("country", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(length=512), nullable=True))
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "country")
    op.drop_column("users", "email")
