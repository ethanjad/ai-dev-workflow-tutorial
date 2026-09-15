"""Data loading and aggregation functions for the sales dashboard."""
import pandas as pd


def load_data(path="data/sales-data.csv"):
    return pd.read_csv(path, parse_dates=["date"])
