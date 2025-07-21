import streamlit as st
import pandas as pd
from backend.data_ingestion import DataIngestor
from backend.storage import Storage
from PIL import Image
import io
import datetime

st.set_page_config(page_title="🧾 Receipt Analyzer", layout="wide")
st.title("🧾 Smart Receipt & Bill Analyzer")
st.markdown("Upload your receipts or bills to extract data and visualize your spending trends.")

# Initialize database handler
db = Storage()
ingestor = DataIngestor()

# ───────── Sidebar ─────────
with st.sidebar:
    st.header("📂 Upload Receipt")

    uploaded_file = st.file_uploader(
        "Choose a receipt file",
        type=["jpg", "jpeg", "png", "pdf", "txt"]
    )

    if uploaded_file and not st.session_state.get("file_uploaded"):
        file_bytes = uploaded_file.read()
        success, message = ingestor.ingest_file(
            filename=uploaded_file.name,
            content=file_bytes,
            content_type=uploaded_file.type
        )
        if success:
            st.success(message)
            st.session_state["file_uploaded"] = True
            st.session_state["refresh_dashboard"] = True
            st.rerun()
        else:
            st.error(message)

    if st.session_state.get("file_uploaded"):
        if st.button("Reset Upload State"):
            st.session_state["file_uploaded"] = False
            st.rerun()

# ───────── Main Dashboard ─────────
st.markdown("## 📊 Dashboard")
if "refresh_dashboard" in st.session_state:
    del st.session_state["refresh_dashboard"]

data = db.get_all_receipts_as_dataframe()

if data.empty:
    st.info("No receipts available. Please upload one.")
else:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("🧾 All Receipts")
        st.dataframe(data.style.format({"Amount": "₹{:.2f}"}), use_container_width=True)

    with col2:
        st.subheader("📈 Key Metrics")
        st.metric("Total Spend", f"₹{data['Amount'].sum():.2f}")
        st.metric("Avg per Receipt", f"₹{data['Amount'].mean():.2f}")
        top_vendor = data['Vendor'].mode()[0]
        st.metric("Top Vendor", top_vendor)

    st.divider()

    # ───── Visualizations ─────
    st.subheader("📉 Spending Insights")
    df = data.copy()
    df['Month'] = df['Date'].dt.to_period('M').astype(str)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Monthly Spend")
        monthly = df.groupby("Month")["Amount"].sum().reset_index()
        st.line_chart(monthly.rename(columns={"Month": "index"}).set_index("index"))

        st.markdown("#### Spend by Category")
        category = df.groupby("Category")["Amount"].sum().reset_index()
        st.bar_chart(category.rename(columns={"Category": "index"}).set_index("index"))

    with col4:
        st.markdown("#### Spend by Vendor")
        vendor = df.groupby("Vendor")["Amount"].sum().reset_index()
        st.bar_chart(vendor.rename(columns={"Vendor": "index"}).set_index("index"))

# ───── Admin Actions ─────
with st.expander("⚠️ Admin Actions"):
    if st.button("🗑️ Delete All Receipts (Danger Zone)"):
        with db._get_connection() as conn:
            conn.execute("DELETE FROM receipts")
            conn.commit()
        st.success("All receipts have been deleted.")
        st.session_state["refresh_dashboard"] = True
        st.rerun()
