"""Extract stage: read raw CSV, log observable facts about the input."""
import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)


def extract_csv(path: str | Path) -> pd.DataFrame:
    """
    Read a raw CSV file into a DataFrame.

    Logs:
      - resolved path
      - file size (bytes + KB)
      - raw row count
      - column list

    Returns an unmodified DataFrame - transformation happens downstream.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path.resolve()}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path.resolve()}")

    size_bytes = path.stat().st_size
    log.info("Reading CSV: %s", path.resolve())
    log.info("File size: %d bytes (%.2f KB)", size_bytes, size_bytes / 1024)

    df = pd.read_csv(path)

    log.info("Raw rows: %d", len(df))
    log.info("Columns (%d): %s", len(df.columns), df.columns.tolist())

    if df.empty:
        log.warning("CSV is empty.")

    return df