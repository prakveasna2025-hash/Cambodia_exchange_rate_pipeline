import pandas as pd

from src.transform import transform


def test_happy_path_returns_clean_schema():
    raw = pd.DataFrame({
        "date":     ["2020-01-02", "2020-01-03"],
        "purchase": [4000, 4010],
        "sale":     [4050, 4060],
    })
    out = transform(raw)

    assert list(out.columns) == [
        "rate_date", "currency_code", "currency_name",
        "buying_rate", "selling_rate", "source",
    ]
    assert len(out) == 2
    assert out["currency_code"].iloc[0] == "USD"
    assert out["source"].iloc[0] == "NBC"


def test_drops_unparseable_dates():
    raw = pd.DataFrame({
        "date":     ["2020-01-02", "not-a-date", "2020-01-03"],
        "purchase": [4000, 4000, 4000],
        "sale":     [4050, 4050, 4050],
    })
    out = transform(raw)
    assert len(out) == 2