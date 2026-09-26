import logging

import pandas as pd

log = logging.getLogger(__name__)


def transform(df):
    out = pd.DataFrame({
        "rate_date":     pd.to_datetime(df["date"], errors="coerce"),
        "currency_code": "USD",
        "currency_name": "US Dollar",
        "buying_rate":   pd.to_numeric(df["purchase"], errors="coerce"),
        "selling_rate":  pd.to_numeric(df["sale"],     errors="coerce"),
        "source":        "NBC",
    })

    # DROP rule 1: unparseable dates
    bad_dates = out["rate_date"].isna()
    n_bad = int(bad_dates.sum())
    if n_bad:
        log.warning("Dropping %d rows: unparseable date", n_bad)
    out = out[~bad_dates]

    # DROP rule 2: duplicate (rate_date, currency_code)
    before = len(out)
    out = out.drop_duplicates(subset=["rate_date", "currency_code"], keep="last")
    n_dup = before - len(out)
    if n_dup:
        log.warning("Dropped %d duplicate (rate_date, currency_code) rows", n_dup)

    # Sort + reset index so the output is stable and readable
    out = out.sort_values("rate_date").reset_index(drop=True)

    log.info("Transform complete: %d rows in, %d rows out", len(df), len(out))
    return out