from dgn_picks_api.db.session import normalize_database_url


def test_normalize_railway_postgresql_url() -> None:
    assert normalize_database_url("postgresql://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"


def test_normalize_railway_postgres_url() -> None:
    assert normalize_database_url("postgres://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"


def test_preserve_explicit_driver() -> None:
    url = "postgresql+psycopg://user:pass@host/db"
    assert normalize_database_url(url) == url
