import pandas as pd

REQUIRED_COLUMNS = [
    "rate_date",
    "currency_code",
    "currency_name",
    "buying_rate",
    "selling_rate",
    "source",
]

# ================================================
# validate_required_columns(df)	missing columns
# ================================================
def validate_required_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

# ================================================
# validate_dates(df)	unparseable rate_date
# ================================================
def validate_dates(df):
    parsed = pd.to_datetime(df["rate_date"], errors="coerce")
    bad = parsed.isna()
    if bad.any():
        raise ValueError(f"Unparseable rate_date rows: {bad.sum()}")

# ==========================================================================
# validate_positive_rates(df)	buying_rate/selling_rate ≤ 0 or non-numeric
# ==========================================================================
def validate_positive_rates(df):
    for col in ["buying_rate", "selling_rate"]:
        values = pd.to_numeric(df[col], errors="coerce")
        bad = values.isna() | (values <= 0)
        if bad.any():
            raise ValueError(f"Invalid {col} rows: {bad.sum()}")

# ==================================================================
# validate_no_duplicates(df)	duplicate (rate_date, currency_code)
# ==================================================================
def validate_no_duplicates(df):
    dup = df.duplicated(subset=["rate_date", "currency_code"])
    if dup.any():
        raise ValueError(
            f"Duplicate (rate_date, currency_code) rows: {dup.sum()}")

# ================================================
# validate(df)	runs all four, in order
# ================================================
def validate(df):
    validate_required_columns(df)
    validate_dates(df)
    validate_positive_rates(df)
    validate_no_duplicates(df)
