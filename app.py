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
    # Placeholder chart
    st.line_chart(data={"Revenue": [4.8, 5.0, 5.2, 5.1, 5.3, 5.5, 5.4, 5.6, 5.7, 5.8, 5.9, 6.0]})
    st.divider()
    st.header("Customer Metrics")
    st.subheader("Active Users Over Time")
    st.area_chart(data={"Users": [2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100]})
    with st.expander("Methodology Notes"):
        st.write("These charts use placeholder data. Replace with real queries and cache them using @st.cache_data.")

elif page == "Data Explorer":
    st.title("Data Explorer")
    st.header("Filters and Tables")
    # Example filter
    date_range = st.date_input("Select date range", value=None)
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
