import os
import logging
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

log = logging.getLogger(__name__)


def make_engine():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "cambodia_fx")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    url = (
        f"postgresql+psycopg2://{user}:{quote_plus(password)}"
        f"@{host}:{port}/{db}"
    )
    return create_engine(url, pool_pre_ping=True)


TABLE = "exchange_rates"
STAGE = "exchange_rates_stage"


def load(df, engine) -> tuple[int, int]:
    """UPSERT via staging table. Returns (inserted, updated)."""
    if df.empty:
        log.warning("Nothing to load.")
        return 0, 0

    with engine.begin() as conn:
        df.to_sql(STAGE, conn, if_exists="replace",
                  index=False, method="multi")

        updated = conn.execute(text(f"""
            SELECT COUNT(*)
            FROM {STAGE} s
            JOIN {TABLE} t
              ON t.rate_date = s.rate_date
             AND t.currency_code = s.currency_code;
        """)).scalar() or 0

        inserted = len(df) - updated

        conn.execute(text(f"""
            INSERT INTO {TABLE}
                (rate_date, currency_code, currency_name, buying_rate, selling_rate, source)
            SELECT rate_date, currency_code, currency_name, buying_rate, selling_rate, source
            FROM {STAGE}
            ON CONFLICT (rate_date, currency_code)
            DO UPDATE SET
                currency_name = EXCLUDED.currency_name,
                buying_rate   = EXCLUDED.buying_rate,
                selling_rate  = EXCLUDED.selling_rate,
                source        = EXCLUDED.source,
                loaded_at     = NOW();
        """))

        conn.execute(text(f"DROP TABLE {STAGE};"))

    log.info("Load: %d inserted, %d updated (of %d attempted)",
             inserted, updated, len(df))
    return inserted, updated
