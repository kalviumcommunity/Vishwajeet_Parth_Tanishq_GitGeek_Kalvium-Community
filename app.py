import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Trends", "Data Explorer"])

# Placeholder data for metrics
def get_placeholder_metrics():
    return {
        "Revenue": ("$5.2M", "+12.5%"),
        "Users": ("2,500", "+5.2%"),
        "AOV": ("$45", "+2.1%"),
        "Churn": ("5.2%", "-2.8%", "inverse"),
        "NPS": ("72", "+4%")
    }

def render_kpi_row(metrics):
    cols = st.columns(len(metrics))
    for (col, (name, values)) in zip(cols, metrics.items()):
        if len(values) == 2:
            metric, delta = values
            col.metric(name, metric, delta)
        else:
            metric, delta, delta_color = values
            col.metric(name, metric, delta, delta_color=delta_color)

# Main content based on selection
if page == "Overview":
    st.title("Business Overview")
    st.header("Key Performance Indicators")
    render_kpi_row(get_placeholder_metrics())
    st.divider()
    st.subheader("Methodology Notes")
    with st.expander("About These Metrics"):
        st.write(
            "Revenue is the sum of order amounts for the current month. "
            "Users counts active users. AOV is average order value. "
            "Churn is the percentage of customers who did not return within 30 days. "
            "NPS is the Net Promoter Score."
        )

elif page == "Trends":
    st.title("Trend Analysis")
    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    st.line_chart(data={"Revenue": [4.8, 5.0, 5.2, 5.1, 5.3, 5.5, 5.4, 5.6, 5.7, 5.8, 5.9, 6.0]})
    st.divider()
    st.header("Customer Metrics")
    st.subheader("Active Users Over Time")
    st.area_chart(data={"Users": [2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100]})
    with st.expander("Methodology Notes"):
        st.write("These charts use placeholder data. Replace with real queries and cache them using @st.cache_data.")

elif page == "Data Explorer":
    st.title("Data Explorer")
    st.header("Upload & Preview")
    uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()
            if df.empty:
                st.warning("Uploaded file is empty.")
                st.stop()
            st.success(f"Loaded: {uploaded_file.name} ({len(df)} rows, {len(df.columns)} columns)")

            # Sidebar filters
            st.sidebar.header("Filters")
            if st.sidebar.button("Reset Filters"):
                st.rerun()

            # Date filter (expects a 'date' column)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                min_date = df["date"].min().date()
                max_date = df["date"].max().date()
                date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date))
                if isinstance(date_range, tuple):
                    start_date, end_date = date_range
                else:
                    start_date = end_date = date_range
            else:
                start_date = end_date = None

            # Segment filter (expects a 'segment' column)
            if "segment" in df.columns:
                all_segments = df["segment"].dropna().unique().tolist()
                selected_segments = st.sidebar.multiselect("Segments", options=all_segments, default=all_segments)
            else:
                selected_segments = None

            # Revenue filter (expects a 'revenue' column)
            if "revenue" in df.columns:
                min_rev = int(df["revenue"].min())
                max_rev = int(df["revenue"].max())
                rev_min, rev_max = st.sidebar.slider("Revenue Range", min_value=min_rev, max_value=max_rev,
                                                      value=(min_rev, max_rev))
            else:
                rev_min = rev_max = None

            # Apply filters
            filtered_df = df.copy()
            if start_date and end_date:
                filtered_df = filtered_df[(filtered_df["date"].dt.date >= start_date) & (filtered_df["date"].dt.date <= end_date)]
            if selected_segments is not None:
                filtered_df = filtered_df[filtered_df["segment"].isin(selected_segments)]
            if rev_min is not None:
                filtered_df = filtered_df[(filtered_df["revenue"] >= rev_min) & (filtered_df["revenue"] <= rev_max)]

            if filtered_df.empty:
                st.warning("No data matches the selected filters.")
                st.stop()

            # Preview of filtered data
            st.header("Filtered Dataset Preview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", f"{len(filtered_df):,}")
            with col2:
                st.metric("Columns", str(len(filtered_df.columns)))
            with col3:
                total_nulls = filtered_df.isnull().sum().sum()
                total_cells = filtered_df.shape[0] * filtered_df.shape[1]
                null_pct = (total_nulls / total_cells) * 100 if total_cells > 0 else 0
                st.metric("Null %", f"{null_pct:.1f}%")
            st.divider()
            st.subheader("First 10 Rows")
            st.dataframe(filtered_df.head(10), use_container_width=True)
            st.subheader("Column Summary")
            summary = pd.DataFrame({
                "Column": filtered_df.columns,
                "Type": filtered_df.dtypes.astype(str).values,
                "Non-Null": filtered_df.notnull().sum().values,
                "Null Count": filtered_df.isnull().sum().values,
                "Null %": (filtered_df.isnull().sum() / len(filtered_df) * 100).round(1).values
            })
            st.dataframe(summary, use_container_width=True)
            st.subheader("Descriptive Statistics")
            st.dataframe(filtered_df.describe(include='all'), use_container_width=True)

            # Simple downstream demo using filtered data
            numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                col_sel = st.selectbox("Select numeric column for bar chart", numeric_cols, key="chart_col")
                st.bar_chart(filtered_df[col_sel].value_counts().head(20))
        except Exception:
            st.error("Could not read this file. Check format.")
            st.stop()
    else:
        st.subheader("Sample Data Table")
        df = pd.DataFrame({
            "Customer ID": [101, 102, 103, 104],
            "Revenue": [1200, 850, 430, 2100],
            "Orders": [12, 8, 5, 20]
        })
        with st.expander("View Raw Data"):
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv(index=False), "data.csv")
        st.divider()
        st.subheader("Additional Insights")
        st.write("Add more charts, filters, or export options here.")
