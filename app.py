import streamlit as st

from calculations import load_data

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
