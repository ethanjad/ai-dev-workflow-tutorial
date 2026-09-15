"""Data loading and aggregation functions for the sales dashboard."""
import pandas as pd


def load_data(path="data/sales-data.csv"):
    return pd.read_csv(path, parse_dates=["date"])


def compute_total_sales(df):
    return df["total_amount"].sum()


def compute_total_orders(df):
    return df["order_id"].nunique()
