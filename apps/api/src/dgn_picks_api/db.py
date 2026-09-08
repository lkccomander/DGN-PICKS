import os

from sqlalchemy import create_engine

def normalize_database_url(value: str) -> str:
    for prefix in ("postgres://", "postgresql://"):
        if value.startswith(prefix):
            return "postgresql+psycopg://" + value[len(prefix):]
    return value


DATABASE_URL = normalize_database_url(os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://dgn_picks:dgn_picks_local@localhost:5432/dgn_picks",
))
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
