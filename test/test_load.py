import pandas as pd

from src.load import make_engine, load


def test_load_empty_returns_zero_zero():
    # Empty df short-circuits before touching the engine, so None is fine.
    result = load(pd.DataFrame(), engine=None)
    assert result == (0, 0)


# def test_make_engine_reads_env_vars():
#     engine = make_engine()
#     url = engine.url
#     assert url.drivername == "postgresql+psycopg2"
#     assert url.database == "exchange_db"
#     assert url.username == "exchange_user"
def test_make_engine_reads_env_vars(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "exchange_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "change_me")
    monkeypatch.setenv("POSTGRES_DB", "exchange_db")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    engine = make_engine()
    url = engine.url
    assert url.drivername == "postgresql+psycopg2"
    assert url.database == "exchange_db"
    assert url.username == "exchange_user"
