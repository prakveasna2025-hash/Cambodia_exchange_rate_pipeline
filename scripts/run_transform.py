"""
Day 4 runner: extract -> transform -> write to data/processed/.

Not the production pipeline — main.py owns that. This exists so
the transform stage can be exercised and its output inspected
without touching the database.
"""
import logging
from pathlib import Path

from src.extract import extract_csv
from src.transform import transform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("run_transform")

CSV_IN = Path("data/raw/KhmerRiel-USDExchangeRate2003-2023.csv")
CSV_OUT = Path("data/processed/exchange_rates_clean.csv")


def main() -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)

    raw = extract_csv(CSV_IN)
    clean = transform(raw)

    clean.to_csv(CSV_OUT, index=False)
    log.info("Wrote %d rows to %s", len(clean), CSV_OUT)

    print("\n--- First 5 rows ---")
    print(clean.head().to_string(index=False))
    print("\n--- Last 5 rows ---")
    print(clean.tail().to_string(index=False))


if __name__ == "__main__":
    main()