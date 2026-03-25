import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="SCM Inventory Dashboard", layout="wide")

st.title("📦 Supply Chain Inventory Command Center")
st.markdown("This app demonstrates real-time data filtering and analytics for SCM managers.")

# --- DATA LOADING ---
# Define the default file path (stored in the same directory)
DEFAULT_FILE = "Dummy_data_for_dummy_app.csv"

# Sidebar: File Upload
st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload a new version (CSV)", type="csv")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Logic to switch between default and uploaded data
if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.sidebar.success("Using uploaded file")
else:
    df = load_data(DEFAULT_FILE)
    st.sidebar.info("Using default repository data")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")

# Dynamic filters based on column categories
category_filter = st.sidebar.multiselect("Select Category", options=df["Category"].unique(), default=df["Category"].unique())
location_filter = st.sidebar.multiselect("Select Location", options=df["Location"].unique(), default=df["Location"].unique())
region_filter = st.sidebar.multiselect("Select Region", options=df["Supplier_Region"].unique(), default=df["Supplier_Region"].unique())
criticality_filter = st.sidebar.multiselect("Select Criticality", options=df["Criticality"].unique(), default=df["Criticality"].unique())

# Apply filters
filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Location"].isin(location_filter)) &
    (df["Supplier_Region"].isin(region_filter)) &
    (df["Criticality"].isin(criticality_filter))
]

# --- MAIN DASHBOARD ---
# 1. Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total SKUs", len(filtered_df))
col2.metric("Inventory Value", f"${filtered_df['Total_Inventory_Value'].sum():,.0f}")
col3.metric("Avg Lead Time", f"{filtered_df['Lead_Time_Days'].mean():.1f} Days")
col4.metric("Total Quantity", f"{filtered_df['Quantity'].sum():,}")

# 2. Data Table Section
st.subheader("📋 Inventory Records")
st.dataframe(filtered_df, use_container_width=True)

# 3. Analytics Section (Separate)
st.divider()
st.subheader("📊 Analytics & Insights")

viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.markdown("### Value by Category")
    fig_cat = px.bar(filtered_df, x="Category", y="Total_Inventory_Value", 
                     color="Category", title="Total Value per Category",
                     text_auto='.2s')
    st.plotly_chart(fig_cat, use_container_width=True)

with viz_col2:
    st.markdown("### Value by Location")
    fig_loc = px.pie(filtered_df, values="Total_Inventory_Value", names="Location", 
                     title="Distribution by Location", hole=0.4)
    st.plotly_chart(fig_loc, use_container_width=True)

# Comparison Section
st.markdown("### Unit Value vs Quantity Correlation")
fig_scatter = px.scatter(filtered_df, x="Quantity", y="Unit_Value", color="Criticality",
                         size="Total_Inventory_Value", hover_name="SKU", 
                         title="SKU Distribution (Size = Total Value)")
st.plotly_chart(fig_scatter, use_container_width=True)

