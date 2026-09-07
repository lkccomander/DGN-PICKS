import os

from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://dgn_picks:dgn_picks_local@localhost:5432/dgn_picks",
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
