import pandas as pd
import pytest

from src.validate import (
    validate_required_columns,
    validate_dates,
    validate_positive_rates,
    validate_no_duplicates,
    validate,
)


def make_df(**overrides):
    base = {
        "rate_date": ["2024-01-01", "2024-01-02"],
        "currency_code": ["USD", "USD"],
        "currency_name": ["US Dollar", "US Dollar"],
        "buying_rate": [4100, 4110],
        "selling_rate": [4120, 4130],
        "source": ["NBC", "NBC"],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_required_columns_pass():
    validate_required_columns(make_df())


def test_required_columns_fail():
    df = make_df().drop(columns=["buying_rate"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_required_columns(df)


def test_dates_pass():
    validate_dates(make_df())


def test_dates_fail():
    df = make_df(rate_date=["2024-01-01", "not-a-date"])
    with pytest.raises(ValueError, match="Unparseable rate_date"):
        validate_dates(df)


def test_positive_rates_pass():
    validate_positive_rates(make_df())


def test_positive_rates_fail():
    df = make_df(buying_rate=[4100, -5])
    with pytest.raises(ValueError, match="Invalid buying_rate"):
        validate_positive_rates(df)


def test_no_duplicates_pass():
    validate_no_duplicates(make_df())


def test_no_duplicates_fail():
    df = make_df(rate_date=["2024-01-01", "2024-01-01"])
    with pytest.raises(ValueError, match="Duplicate"):
        validate_no_duplicates(df)


def test_validate_pass():
    validate(make_df())


def test_validate_fail():
    df = make_df(buying_rate=[4100, 0])
    with pytest.raises(ValueError):
        validate(df)
