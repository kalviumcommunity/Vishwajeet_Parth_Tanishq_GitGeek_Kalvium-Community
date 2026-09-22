import streamlit as st
import pandas as pd
try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

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
    """Render executive KPI cards with summary metrics, trend deltas, and target indicators."""
    cols = st.columns(len(metrics))
    for (col, (name, values)) in zip(cols, metrics.items()):
        with col:
            if len(values) == 2:
                metric, delta = values
                st.metric(label=f"📊 {name}", value=metric, delta=delta, help=f"Key metric tracking {name.lower()} against prior period.")
            else:
                metric, delta, delta_color = values
                st.metric(label=f"⚡ {name}", value=metric, delta=delta, delta_color=delta_color, help=f"Core performance indicator: {name}.")


def create_interactive_revenue_chart():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    revenue = [4.8, 5.0, 5.2, 5.1, 5.3, 5.5, 5.4, 5.6, 5.7, 5.8, 5.9, 6.0]
    target = [4.5, 4.7, 4.9, 5.0, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=revenue, name="Actual Revenue ($M)",
        mode="lines+markers",
        line=dict(color="#1ed760", width=3, shape="spline"),
        marker=dict(size=8, color="#1ed760"),
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:.2f}M<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=months, y=target, name="Target Revenue ($M)",
        mode="lines",
        line=dict(color="#8b9690", width=2, dash="dash"),
        hovertemplate="<b>%{x}</b><br>Target: $%{y:.2f}M<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_dark",
        title="Interactive Monthly Revenue Trend vs Target",
        xaxis_title="Month",
        yaxis_title="Revenue ($M)",
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,16,15,0.8)",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_interactive_user_chart():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    users = [2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=users, name="Active Users",
        fill="tozeroy",
        fillcolor="rgba(30, 215, 96, 0.15)",
        line=dict(color="#38f27d", width=2.5, shape="spline"),
        hovertemplate="<b>%{x}</b><br>Active Users: %{y:,}<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_dark",
        title="Active Users Growth (Area Trend)",
        xaxis_title="Month",
        yaxis_title="Active Users",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,16,15,0.8)",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

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
    st.header("Interactive Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    if HAS_PLOTLY:
        st.plotly_chart(create_interactive_revenue_chart(), use_container_width=True)
    else:
        st.line_chart(data={"Revenue": [4.8, 5.0, 5.2, 5.1, 5.3, 5.5, 5.4, 5.6, 5.7, 5.8, 5.9, 6.0]})

    st.divider()
    st.header("Customer Growth Trends")
    st.subheader("Active Users Over Time")
    if HAS_PLOTLY:
        st.plotly_chart(create_interactive_user_chart(), use_container_width=True)
    else:
        st.area_chart(data={"Users": [2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100]})

    with st.expander("Methodology Notes"):
        st.write("These interactive Plotly charts display monthly performance metrics and target comparisons.")

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

