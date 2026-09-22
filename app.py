import streamlit as st
import pandas as pd

# ── App config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# ── Sidebar navigation ─────────────────────────────────────────────────────
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Trends", "Data Explorer"]
)

# ── Helper: render KPI row ──────────────────────────────────────────────────
def render_kpi_row():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", "$5.2M", "+12.5%")
    with col2:
        st.metric("Users", "2,500", "+5.2%")
    with col3:
        st.metric("AOV", "$45", "+2.1%")
    with col4:
        st.metric("Churn", "5.2%", "-2.8%", delta_color="inverse")
    with col5:
        st.metric("NPS", "72", "+4")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 – Overview
# ════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("Business Overview")
    st.header("Key Performance Indicators")
    render_kpi_row()
    st.divider()
    st.header("Summary")
    st.subheader("Monthly Highlights")
    st.write("KPI summary cards and key metrics are displayed above.")
    with st.expander("About These Metrics"):
        st.write(
            "Revenue is calculated as the sum of all order amounts for the "
            "current month. Users counts distinct active users. AOV is the "
            "average order value. Churn is the percentage of customers who "
            "did not return within 30 days. NPS is Net Promoter Score."
        )

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 – Trends
# ════════════════════════════════════════════════════════════════════════════
elif page == "Trends":
    st.title("Trend Analysis")
    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    st.line_chart(
        data={"Revenue ($M)": [4.8, 5.0, 5.2, 5.1, 5.3, 5.5,
                                5.4, 5.6, 5.7, 5.8, 5.9, 6.0]}
    )
    st.divider()
    st.header("Customer Metrics")
    st.subheader("Active Users Over Time")
    st.area_chart(
        data={"Users": [2000, 2100, 2200, 2300, 2400, 2500,
                        2600, 2700, 2800, 2900, 3000, 3100]}
    )
    with st.expander("Methodology Notes"):
        st.write(
            "These charts use placeholder data. Replace with real queries "
            "and cache them using @st.cache_data."
        )

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 – Data Explorer  (Dataset Upload & Dynamic Preview)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Data Explorer":
    st.title("Data Explorer")

    # ── Task 1: File Upload ─────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "json"]
    )

    if uploaded_file is not None:
        # ── Task 4: Error handling ──────────────────────────────────────────
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload CSV or JSON.")
                st.stop()

            if len(df) == 0:
                st.warning("The uploaded file is empty. Please check your data.")
                st.stop()

            st.success(
                "File loaded: " + uploaded_file.name
                + " (" + str(len(df)) + " rows, "
                + str(len(df.columns)) + " columns)"
            )

        except Exception as e:
            st.error("Could not read this file. Please check the format.")
            st.stop()

        # ── Task 2: Automatic Preview ───────────────────────────────────────
        st.header("Dataset Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", str(len(df.columns)))
        with col3:
            total_nulls = df.isnull().sum().sum()
            total_cells = df.shape[0] * df.shape[1]
            null_pct = (total_nulls / total_cells) * 100
            st.metric("Null %", f"{null_pct:.1f}%")

        st.divider()

        st.subheader("First 10 Rows")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
        })
        st.dataframe(summary, use_container_width=True)

        # ── Task 3: Descriptive Statistics ──────────────────────────────────
        st.subheader("Descriptive Statistics")
        st.dataframe(df.describe(), use_container_width=True)

        # ── Task 5: Downstream usage – filter & chart ───────────────────────
        st.divider()
        st.subheader("Quick Exploration")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select a column to visualise", numeric_cols)
            st.bar_chart(df[selected_col].value_counts().head(20))
        else:
            st.info("No numeric columns found for charting.")

    else:
        # None state – no file uploaded yet
        st.info("Upload a CSV or JSON file to begin.")
