# ===============================================
# McDonald's Real-Time Order & Payment Dashboard
# ===============================================

# Import required libraries
import streamlit as st                      # For interactive dashboard
import pandas as pd                         # For data manipulation
from pymongo import MongoClient             # For MongoDB connection
import altair as alt                        # For charts
from datetime import datetime

# ----------------------------
# MongoDB Connection Settings
# ----------------------------

# Replace with your MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://kartik_root:pavilion15@kartik-test-cluster.peofmgn.mongodb.net/?retryWrites=true&w=majority&appName=Kartik-test-cluster"
DB_NAME = "kartik_test_database"
COLLECTION_NAME = "mcdonalds_project"

# Connect to MongoDB
@st.cache_resource
def get_mongo_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

collection = get_mongo_collection()

# ----------------------------
# Data Fetching Function
# ----------------------------
@st.cache_data(ttl=30)
def fetch_data():
    data = list(collection.find())
    if not data:
        return pd.DataFrame()

    # Flatten JSON-like data into DataFrame
    df = pd.json_normalize(data)

    # Handle ORDER_TIME and PAYMENT_TIME field variations
    def extract_datetime(field):
        # If "$date" key exists after flattening
        if f"{field}.$date" in df.columns:
            return pd.to_datetime(df[f"{field}.$date"], errors="coerce")
        # If datetime already stored as normal object
        elif field in df.columns:
            return pd.to_datetime(df[field], errors="coerce")
        else:
            return pd.NaT

    df["ORDER_TIME"] = extract_datetime("ORDER_TIME")
    df["PAYMENT_TIME"] = extract_datetime("PAYMENT_TIME")

    # Drop any documents without valid timestamps
    df = df.dropna(subset=["ORDER_TIME", "PAYMENT_TIME"], how="any")

    return df

# ----------------------------
# Streamlit Page Configuration
# ----------------------------
st.set_page_config(page_title="McDonald's Realtime Dashboard", layout="wide")

st.title("🍔 McDonald's Real-Time Order & Payment Dashboard")
st.markdown("Live data visualization from Kafka → MongoDB → Streamlit")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Fetch the latest data
df = fetch_data()

# ----------------------------
# Handle Empty Data
# ----------------------------
if df.empty:
    st.warning("No data found in MongoDB collection yet.")
    st.stop()

# ----------------------------
# KPIs
# ----------------------------
col1, col2, col3 = st.columns(3)

total_revenue = df["PAYMENT_AMOUNT"].sum()
total_orders = len(df)
avg_order_value = df["PAYMENT_AMOUNT"].mean()

col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("🧾 Total Orders", f"{total_orders}")
col3.metric("📊 Avg Order Value", f"${avg_order_value:,.2f}")

st.markdown("---")

# ----------------------------
# Charts Section
# ----------------------------

# Payment Method Distribution
payment_chart = (
    alt.Chart(df)
    .mark_arc()
    .encode(
        theta=alt.Theta(field="PAYMENT_METHOD", type="nominal", stack=True),
        color=alt.Color(field="PAYMENT_METHOD", type="nominal", legend=alt.Legend(title="Payment Method")),
        tooltip=["PAYMENT_METHOD", alt.Tooltip("PAYMENT_AMOUNT", aggregate="sum", title="Total Amount ($)")]
    )
    .properties(title="Payment Method Distribution")
)

# Revenue Over Time
revenue_chart = (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        x=alt.X("PAYMENT_TIME:T", title="Time"),
        y=alt.Y("PAYMENT_AMOUNT:Q", aggregate="sum", title="Revenue ($)"),
        tooltip=["PAYMENT_TIME", "PAYMENT_AMOUNT"]
    )
    .properties(title="Revenue Trend Over Time")
)

col1, col2 = st.columns(2)
col1.altair_chart(payment_chart, use_container_width=True)
col2.altair_chart(revenue_chart, use_container_width=True)

st.markdown("---")

# ----------------------------
# Top-Selling Items
# ----------------------------
# Flatten order items
items = []
for _, row in df.iterrows():
    for item in row["ORDER_ITEMS"]:
        items.append({
            "ITEM_NAME": item["ITEM_NAME"],
            "QUANTITY": item["QUANTITY"],
            "PRICE": item["PRICE"],
            "ORDER_TOTAL": row["ORDER_TOTAL"]
        })

items_df = pd.DataFrame(items)

# Aggregate item sales
item_summary = (
    items_df.groupby("ITEM_NAME")
    .agg({"QUANTITY": "sum", "PRICE": "mean"})
    .reset_index()
    .sort_values(by="QUANTITY", ascending=False)
)

st.subheader("🍟 Top-Selling Items")
bar_chart = (
    alt.Chart(item_summary)
    .mark_bar()
    .encode(
        x=alt.X("ITEM_NAME", sort="-y", title="Menu Item"),
        y=alt.Y("QUANTITY", title="Total Quantity Sold"),
        tooltip=["ITEM_NAME", "QUANTITY"]
    )
    .properties(height=300)
)
st.altair_chart(bar_chart, use_container_width=True)

st.markdown("---")

# ----------------------------
# Recent Orders Table
# ----------------------------
st.subheader("🕒 Latest Orders")
st.dataframe(
    df[["CUSTOMER_ID", "ORDER_TOTAL", "PAYMENT_METHOD", "PAYMENT_AMOUNT", "ORDER_TIME", "PAYMENT_TIME"]]
    .sort_values("PAYMENT_TIME", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
)

st.caption("Data refreshes automatically every 30 seconds (or click 'Refresh Data').")
