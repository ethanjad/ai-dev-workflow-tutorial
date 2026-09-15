import plotly.express as px
import streamlit as st

from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
    sales_by_category,
    sales_by_region,
)

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Could not find data/sales-data.csv. Make sure the file exists "
        "before running the dashboard."
    )
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Sales", f"${compute_total_sales(df):,.0f}")
with col2:
    st.metric("Total Orders", f"{compute_total_orders(df):,}")

st.subheader("Sales Trend Over Time")
trend_df = monthly_sales_trend(df)
fig_trend = px.line(trend_df, x="month_label", y="total_amount", markers=True)
fig_trend.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
st.plotly_chart(fig_trend, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Sales by Category")
    category_df = sales_by_category(df)
    fig_cat = px.bar(category_df, x="category", y="total_amount")
    fig_cat.update_layout(xaxis_title="Category", yaxis_title="Sales ($)")
    st.plotly_chart(fig_cat, use_container_width=True)

with col4:
    st.subheader("Sales by Region")
    region_df = sales_by_region(df)
    fig_reg = px.bar(region_df, x="region", y="total_amount")
    fig_reg.update_layout(xaxis_title="Region", yaxis_title="Sales ($)")
    st.plotly_chart(fig_reg, use_container_width=True)
