import os
import subprocess
import sys


def main() -> int:
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url.startswith("postgresql://"):
        os.environ["DATABASE_URL"] = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return subprocess.call(
        [sys.executable, "-m", "alembic", "-c", "railway-alembic.ini", "upgrade", "head"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
