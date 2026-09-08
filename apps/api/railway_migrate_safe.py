import os
import subprocess
import sys

from sqlalchemy import create_engine, text


def normalize_database_url(value: str) -> str:
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


def remove_empty_duplicate_column(database_url: str) -> None:
    engine = create_engine(database_url)
    with engine.begin() as connection:
        exists = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'pick_legs' AND column_name = 'odds_snapshot_id')")
        ).scalar()
        if not exists:
            return
        count = connection.execute(text("SELECT COUNT(*) FROM pick_legs")).scalar_one()
        if count:
            raise RuntimeError("pick_legs contains data; refusing to remove duplicate odds_snapshot_id")
        connection.execute(text("ALTER TABLE pick_legs DROP COLUMN odds_snapshot_id"))


def main() -> int:
    database_url = normalize_database_url(os.environ["DATABASE_URL"])
    os.environ["DATABASE_URL"] = database_url
    remove_empty_duplicate_column(database_url)
    return subprocess.call([sys.executable, "-m", "alembic", "-c", "railway-alembic.ini", "upgrade", "head"])


if __name__ == "__main__":
    raise SystemExit(main())
