import pandas as pd

REQUIRED_COLUMNS = [
    "rate_date",
    "currency_code",
    "currency_name",
    "buying_rate",
    "selling_rate",
    "source",
]


def validate_required_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_dates(df):
    parsed = pd.to_datetime(df["rate_date"], errors="coerce")
    bad = parsed.isna()
    if bad.any():
        raise ValueError(f"Unparseable rate_date rows: {bad.sum()}")


def validate_positive_rates(df):
    for col in ["buying_rate", "selling_rate"]:
        values = pd.to_numeric(df[col], errors="coerce")
        bad = values.isna() | (values <= 0)
        if bad.any():
            raise ValueError(f"Invalid {col} rows: {bad.sum()}")


def validate_no_duplicates(df):
    dup = df.duplicated(subset=["rate_date", "currency_code"])
    if dup.any():
        raise ValueError(
            f"Duplicate (rate_date, currency_code) rows: {dup.sum()}")


def validate(df):
    validate_required_columns(df)
    validate_dates(df)
    validate_positive_rates(df)
    validate_no_duplicates(df)
