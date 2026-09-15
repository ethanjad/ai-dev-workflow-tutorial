import pandas as pd
import pytest

from calculations import load_data, compute_total_sales


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime([
            "2024-01-05", "2024-01-15", "2024-02-10", "2024-02-20",
        ]),
        "order_id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004"],
        "product": ["Widget A", "Widget B", "Gadget A", "Gadget B"],
        "category": ["Electronics", "Accessories", "Electronics", "Accessories"],
        "region": ["North", "South", "North", "South"],
        "quantity": [1, 2, 1, 3],
        "unit_price": [100.0, 25.0, 200.0, 10.0],
        "total_amount": [100.0, 50.0, 200.0, 30.0],
    })


def test_compute_total_sales_sums_total_amount(sample_df):
    assert compute_total_sales(sample_df) == 380.0


def test_load_data_reads_csv_and_parses_dates():
    df = load_data("data/sales-data.csv")
    assert "date" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert len(df) == 482


def test_load_data_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_data("data/does-not-exist.csv")
