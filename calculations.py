"""Data loading and aggregation functions for the sales dashboard."""
import pandas as pd


def load_data(path="data/sales-data.csv"):
    return pd.read_csv(path, parse_dates=["date"])


def compute_total_sales(df):
    return df["total_amount"].sum()


def compute_total_orders(df):
    return df["order_id"].nunique()


def monthly_sales_trend(df):
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M")
    result = monthly.groupby("month")["total_amount"].sum().reset_index()
    result = result.sort_values("month")
    result["month_label"] = result["month"].dt.strftime("%b %Y")
    return result[["month_label", "total_amount"]].reset_index(drop=True)


def sales_by_category(df):
    result = df.groupby("category")["total_amount"].sum().reset_index()
    return result.sort_values("total_amount", ascending=False).reset_index(drop=True)
