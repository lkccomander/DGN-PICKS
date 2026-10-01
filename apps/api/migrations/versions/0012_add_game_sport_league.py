"""Add sport and league identity to games."""

from alembic import context, op
import sqlalchemy as sa

revision = "0012_add_game_sport_league"
down_revision = "0011_restore_pick_leg_snapshot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if context.is_offline_mode():
        op.add_column("games", sa.Column("sport", sa.String(32), nullable=False, server_default="ncaafb"))
        op.add_column("games", sa.Column("league", sa.String(32), nullable=False, server_default="NCAAFB"))
        return
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("games")}
    with op.batch_alter_table("games") as batch:
        if "sport" not in columns:
            batch.add_column(sa.Column("sport", sa.String(32), nullable=False, server_default="ncaafb"))
        if "league" not in columns:
            batch.add_column(sa.Column("league", sa.String(32), nullable=False, server_default="NCAAFB"))


def downgrade() -> None:
    with op.batch_alter_table("games") as batch:
        batch.drop_column("league")
        batch.drop_column("sport")
