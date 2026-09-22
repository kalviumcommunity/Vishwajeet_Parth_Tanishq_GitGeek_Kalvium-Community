import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(
    page_title="GitGeek Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View", ["Overview", "Dataset Upload"])


def get_placeholder_metrics():
    return {
        "ARR ($M)": ("$5.8M", "+12%"),
        "Net Retention": ("112%", "+3%"),
        "Gross Margin": ("78%", "-1%"),
        "CAC Payback": ("14 mos", "0"),
    }


def render_kpi_row(metrics):
    cols = st.columns(len(metrics))
    for col, (name, values) in zip(cols, metrics.items()):
        if len(values) == 2:
            metric, delta = values
            col.metric(name, metric, delta)
        else:
            metric, delta, delta_color = values
            col.metric(name, metric, delta, delta_color=delta_color)


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
        hovertemplate="**%{x}**