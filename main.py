import logging
from pathlib import Path

from dotenv import load_dotenv

from src.extract import extract_csv
from src.transform import transform
from src.validate import validate
from src.load import make_engine, load

# ---------- Config ----------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

CSV_PATH = Path("data/raw/KhmerRiel-USDExchangeRate2003-2023.csv")


# ---------- Main ----------
def main() -> None:
    raw = extract_csv(CSV_PATH)
    clean = transform(raw)
    validate(clean)

    engine = make_engine()
    inserted, updated = load(clean, engine)

    extracted = len(raw)
    valid = len(clean)
    rejected = extracted - valid

    log.info(
        "Run summary: extracted=%d valid=%d rejected=%d inserted=%d updated=%d",
        extracted, valid, rejected, inserted, updated,
    )


if __name__ == "__main__":
    main()
