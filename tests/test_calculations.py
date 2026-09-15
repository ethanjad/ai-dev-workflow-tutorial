import pandas as pd
import pytest

from calculations import load_data


def test_load_data_reads_csv_and_parses_dates():
    df = load_data("data/sales-data.csv")
    assert "date" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert len(df) == 482


def test_load_data_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_data("data/does-not-exist.csv")
