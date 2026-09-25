"""Add revocable user sessions and reversible pick archival."""
from alembic import op
import sqlalchemy as sa
revision = "0009_audit_integrity"
down_revision = "0008_user_account_credentials"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("session_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("picks", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("picks", sa.Column("archive_reason", sa.String(160), nullable=True))

def downgrade():
    op.drop_column("picks", "archive_reason")
    op.drop_column("picks", "archived_at")
    op.drop_column("users", "session_version")
