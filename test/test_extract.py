import pandas as pd
import pytest

from src.extract import extract_csv


def test_extract_reads_csv(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text("date,purchase,sale\n2020-01-01,4000,4050\n")
    df = extract_csv(p)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert list(df.columns) == ["date", "purchase", "sale"]


def test_extract_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_csv("does/not/exist.csv")