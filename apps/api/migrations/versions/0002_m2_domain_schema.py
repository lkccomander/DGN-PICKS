"""Add M2 domain fields and normalized reference tables."""
from alembic import op
import sqlalchemy as sa

revision = "0002_m2_domain_schema"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(80), nullable=False, server_default=""))
    op.add_column("users", sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("events", sa.Column("season", sa.Integer(), nullable=False, server_default="2026"))
    op.add_column("events", sa.Column("week", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("events", sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("events", sa.Column("home_team_id", sa.Integer(), nullable=True))
    op.add_column("events", sa.Column("away_team_id", sa.Integer(), nullable=True))
    op.add_column("events", sa.Column("status", sa.String(16), nullable=False, server_default="scheduled"))
    op.add_column("markets", sa.Column("period", sa.String(24), nullable=False, server_default="game"))
    op.add_column("markets", sa.Column("player_id", sa.Integer(), nullable=True))
    op.add_column("markets", sa.Column("team_id", sa.Integer(), nullable=True))
    op.add_column("markets", sa.Column("status", sa.String(16), nullable=False, server_default="open"))
    op.add_column("odds_snapshots", sa.Column("selection_id", sa.Integer(), nullable=True))
    op.add_column("odds_snapshots", sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("odds_snapshots", sa.Column("line_value", sa.Numeric(10, 3), nullable=True))
    op.add_column("odds_snapshots", sa.Column("american_odds", sa.Integer(), nullable=True))
    op.add_column("odds_snapshots", sa.Column("decimal_odds", sa.Numeric(10, 5), nullable=True))
    op.add_column("odds_snapshots", sa.Column("implied_probability", sa.Numeric(10, 8), nullable=True))
    op.add_column("odds_snapshots", sa.Column("source_event_id", sa.String(160), nullable=True))
    op.add_column("picks", sa.Column("game_id", sa.Integer(), nullable=True))
    op.add_column("picks", sa.Column("market_id", sa.Integer(), nullable=True))
    op.add_column("picks", sa.Column("selection_id", sa.Integer(), nullable=True))
    op.add_column("picks", sa.Column("picked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("picks", sa.Column("line_value", sa.Numeric(10, 3), nullable=True))
    op.add_column("picks", sa.Column("american_odds", sa.Integer(), nullable=True))
    op.add_column("picks", sa.Column("decimal_odds", sa.Numeric(10, 5), nullable=True))
    op.add_column("picks", sa.Column("stake_units", sa.Numeric(10, 3), nullable=False, server_default="1.0"))
    op.add_column("picks", sa.Column("result", sa.String(16), nullable=False, server_default="pending"))
    op.add_column("picks", sa.Column("profit_units", sa.Numeric(10, 5), nullable=True))
    op.add_column("picks", sa.Column("notes", sa.String(1000), nullable=True))
    op.create_table("teams", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("external_ids", sa.JSON(), nullable=False), sa.Column("name", sa.String(120), nullable=False, unique=True), sa.Column("short_name", sa.String(80), nullable=False), sa.Column("abbreviation", sa.String(8), nullable=False, unique=True), sa.Column("conference", sa.String(64), nullable=False), sa.Column("logo_url", sa.String(500)), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("players", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("external_ids", sa.JSON(), nullable=False), sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("position", sa.String(16), nullable=False), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("sportsbook_sources", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(80), nullable=False, unique=True), sa.Column("source_type", sa.String(32), nullable=False), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("selections", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("market_id", sa.Integer(), sa.ForeignKey("markets.id"), nullable=False), sa.Column("selection_key", sa.String(80), nullable=False), sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id")), sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id")), sa.Column("side", sa.String(16)), sa.UniqueConstraint("market_id", "selection_key"))
    op.add_column("pick_legs", sa.Column("selection_id", sa.Integer(), nullable=True))
    op.add_column("pick_legs", sa.Column("odds_snapshot_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("pick_legs", "odds_snapshot_id")
    op.drop_column("pick_legs", "selection_id")
    for table in ("selections", "sportsbook_sources", "players", "teams"):
        op.drop_table(table)
    for table, columns in {
        "picks": ("notes", "profit_units", "result", "stake_units", "decimal_odds", "american_odds", "line_value", "picked_at", "selection_id", "market_id", "game_id"),
        "odds_snapshots": ("source_event_id", "implied_probability", "decimal_odds", "american_odds", "line_value", "observed_at", "selection_id"),
        "markets": ("status", "team_id", "player_id", "period"),
        "events": ("status", "away_team_id", "home_team_id", "kickoff_at", "week", "season"),
        "users": ("active", "display_name"),
    }.items():
        for column in columns:
            op.drop_column(table, column)
