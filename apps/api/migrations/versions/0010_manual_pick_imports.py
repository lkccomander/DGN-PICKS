"""Preserve manual pick import identity and source provenance."""
from alembic import op
import sqlalchemy as sa

revision = "0010_manual_pick_imports"
down_revision = "0009_audit_integrity"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("picks", sa.Column("import_key", sa.String(128), nullable=True))
    op.add_column("picks", sa.Column("import_metadata", sa.JSON(), nullable=True))
    op.create_unique_constraint("uq_picks_user_import_key", "picks", ["user_id", "import_key"])


def downgrade():
    op.drop_constraint("uq_picks_user_import_key", "picks", type_="unique")
    op.drop_column("picks", "import_metadata")
    op.drop_column("picks", "import_key")
