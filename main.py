import os
import logging
from urllib.parse import quote_plus
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from src.extract import extract_csv
from src.validate import validate

# ---------- Config ----------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DB_CONFIG = {
    "user":     os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "db":       os.getenv("POSTGRES_DB", "cambodia_fx"),
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     os.getenv("POSTGRES_PORT", "5432"),
}

CSV_PATH = Path("data/raw/KhmerRiel-USDExchangeRate2003-2023.csv")

CURRENCY = {
    "code": "USD",
    "name": "US Dollar",
}
SOURCE = "NBC"

TABLE = "exchange_rates"
STAGE = "exchange_rates_stage"


# ---------- Extract ----------
def extract(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path.resolve()}")
    df = pd.read_csv(path)
    log.info("Read %d rows from %s", len(df), path)
    log.debug("Columns: %s", df.columns.tolist())
    return df


# ---------- Transform ----------
def transform(df: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "purchase", "sale"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = pd.DataFrame({
        "rate_date":     pd.to_datetime(df["date"], errors="coerce").dt.date,
        "currency_code": CURRENCY["code"],
        "currency_name": CURRENCY["name"],
        "buying_rate":   pd.to_numeric(df["purchase"], errors="coerce"),
        "selling_rate":  pd.to_numeric(df["sale"],     errors="coerce"),
        "source":        SOURCE,
    })

    before = len(out)
    out = out.dropna(subset=["rate_date"])
    if len(out) != before:
        log.warning("Dropped %d rows with invalid dates", before - len(out))

    out = out.drop_duplicates(
        subset=["rate_date", "currency_code"], keep="last")
    log.info("Transformed to %d clean rows", len(out))
    return out


# ---------- Load ----------
def make_engine():
    c = DB_CONFIG
    url = (
        f"postgresql+psycopg2://{c['user']}:{quote_plus(c['password'])}"
        f"@{c['host']}:{c['port']}/{c['db']}"
    )
    return create_engine(url, pool_pre_ping=True)


def ensure_schema(engine) -> None:
    """Create the table + unique constraint if they don't exist yet."""
    ddl_table = f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            rate_date      DATE        NOT NULL,
            currency_code  VARCHAR(3)  NOT NULL,
            currency_name  VARCHAR(64) NOT NULL,
            buying_rate    NUMERIC(18, 6),
            selling_rate   NUMERIC(18, 6),
            source         VARCHAR(32) NOT NULL,
            loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (rate_date, currency_code)
        );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl_table))


def load(df: pd.DataFrame, engine) -> int:
    """Idempotent upsert via a staging table."""
    if df.empty:
        log.warning("Nothing to load.")
        return 0

    with engine.begin() as conn:
        df.to_sql(STAGE, conn, if_exists="replace",
                  index=False, method="multi")

        result = conn.execute(text(f"""
            INSERT INTO {TABLE}
                (rate_date, currency_code, currency_name, buying_rate, selling_rate, source)
            SELECT rate_date, currency_code, currency_name, buying_rate, selling_rate, source
            FROM {STAGE}
            ON CONFLICT (rate_date, currency_code) DO NOTHING;
        """))

        conn.execute(text(f"DROP TABLE {STAGE};"))

    inserted = result.rowcount or 0
    log.info("Inserted %d new rows (of %d attempted)", inserted, len(df))
    return inserted


# ---------- Main ----------
def main() -> None:
    df = extract_csv(CSV_PATH)
    df_clean = transform(df)
    validate(df_clean)

    engine = make_engine()
    load(df_clean, engine)


if __name__ == "__main__":
    main()
