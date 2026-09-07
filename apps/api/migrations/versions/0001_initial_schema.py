"""Create the local MVP domain tables."""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(32), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_table("sports", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(64), nullable=False, unique=True))
    op.create_table("events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("sport_id", sa.Integer(), sa.ForeignKey("sports.id"), nullable=False), sa.Column("external_key", sa.String(128), nullable=False, unique=True), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("markets", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False), sa.Column("market_type", sa.String(32), nullable=False), sa.Column("selection", sa.String(128), nullable=False), sa.Column("line", sa.Numeric(8, 3)))
    op.create_table("odds_snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("market_id", sa.Integer(), sa.ForeignKey("markets.id"), nullable=False), sa.Column("book", sa.String(64), nullable=False), sa.Column("price", sa.Integer(), nullable=False), sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_table("picks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_table("pick_legs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("pick_id", sa.Integer(), sa.ForeignKey("picks.id"), nullable=False), sa.Column("market_id", sa.Integer(), sa.ForeignKey("markets.id"), nullable=False), sa.Column("odds_snapshot_id", sa.Integer(), sa.ForeignKey("odds_snapshots.id"), nullable=False))
def downgrade() -> None:
    for table in ("pick_legs", "picks", "odds_snapshots", "markets", "events", "sports", "users"): op.drop_table(table)
