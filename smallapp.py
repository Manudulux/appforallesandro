import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="SCM Command Center", layout="wide")

st.title("📦 Supply Chain Inventory Command Center")

# --- DATA LOADING ---
DEFAULT_FILE = "Dummy_data_for_dummy_app.csv"

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Check for upload, otherwise use default
uploaded_file = st.sidebar.file_uploader("Optional: Side-load new CSV", type="csv")

try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        df = load_data(DEFAULT_FILE)
except FileNotFoundError:
    st.error(f"Please ensure '{DEFAULT_FILE}' is in the same folder as this script.")
    st.stop()

# --- TOP LEVEL FILTERS ---
st.write("### 🔍 Global Filters")
# Creating three columns for the filters at the top
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    category_filter = st.multiselect("Category", options=sorted(df["Category"].unique()), default=df["Category"].unique())
with f_col2:
    location_filter = st.multiselect("Location", options=sorted(df["Location"].unique()), default=df["Location"].unique())
with f_col3:
    region_filter = st.multiselect("Supplier Region", options=sorted(df["Supplier_Region"].unique()), default=df["Supplier_Region"].unique())
with f_col4:
    criticality_filter = st.multiselect("Criticality", options=sorted(df["Criticality"].unique()), default=df["Criticality"].unique())

# Apply filtering logic
filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Location"].isin(location_filter)) &
    (df["Supplier_Region"].isin(region_filter)) &
    (df["Criticality"].isin(criticality_filter))
]

# --- TABS NAVIGATION ---
tab1, tab2 = st.tabs(["📋 Inventory Data", "📊 Analytics Dashboard"])

with tab1:
    # Key Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total SKUs", len(filtered_df))
    m2.metric("Inventory Value", f"${filtered_df['Total_Inventory_Value'].sum():,.0f}")
    m3.metric("Avg Lead Time", f"{filtered_df['Lead_Time_Days'].mean():.1f} Days")
    m4.metric("Total Quantity", f"{filtered_df['Quantity'].sum():,}")
    
    st.divider()
    st.subheader("Raw Inventory Records")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Inventory Breakdown & Performance")
    
    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        # Added 'color="Location"' to show the location name inside the category bars
        st.markdown("#### Value by Category & Location")
        fig_cat = px.bar(
            filtered_df, 
            x="Category", 
            y="Total_Inventory_Value", 
            color="Location",  # This adds the location breakdown you requested
            title="Total Value (Segmented by Location)",
            barmode="group", # Each location gets its own bar next to each other
            text_auto='.2s'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with viz_col2:
        st.markdown("#### Lead Time by Supplier Region")
        fig_lead = px.box(
            filtered_df, 
            x="Supplier_Region", 
            y="Lead_Time_Days",
            color="Supplier_Region",
            title="Lead Time Distribution"
        )
        st.plotly_chart(fig_lead, use_container_width=True)

    st.divider()
    
    # Advanced Scatter Chart
    st.markdown("#### Criticality Matrix (Value vs Quantity)")
    fig_scatter = px.scatter(
        filtered_df, 
        x="Quantity", 
        y="Unit_Value", 
        color="Criticality",
        size="Total_Inventory_Value", 
        hover_name="SKU",
        hover_data=["Location", "Category"],
        title="Inventory Matrix"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
