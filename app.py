import streamlit as st

from calculations import load_data, compute_total_sales, compute_total_orders

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
