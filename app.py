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
page = st.sidebar.radio("Select View", ["Overview", "Executive Briefing (2.49)", "Data Storytelling", "Data Explorer"])


def get_placeholder_metrics():
    return {
        "ARR ($M)": ("$5.8M", "+12%"),
        "Net Retention": ("112%", "+3%"),
        "Gross Margin": ("78%", "-1%"),
        "CAC Payback": ("14 mos", "0"),
    }


def render_kpi_row(metrics):
    """Render executive KPI cards with summary metrics, trend deltas, and target indicators."""
    cols = st.columns(len(metrics))
    for col, (label, (value, delta)) in zip(cols, metrics.items()):
        col.metric(label=f"📊 {label}", value=value, delta=delta)


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


if page == "Overview":
    st.title("Business Overview")
    st.header("Key Performance Indicators")
    render_kpi_row(get_placeholder_metrics())
    st.divider()
    st.subheader("Revenue Trend vs Target")
    if PLOTLY_AVAILABLE:
        st.plotly_chart(create_interactive_revenue_chart(), use_container_width=True)

elif page == "Executive Briefing (2.49)":
    st.title("👔 Executive Briefing & Stakeholder Communication")
    st.markdown("### Quarterly Strategic Report for Board & Leadership")
    
    st.markdown("""
    #### 🎯 Strategic Priority Highlights
    - **Revenue Execution**: Q3 ARR hit **$5.8M**, outperforming internal projections by 6.2%.
    - **Community Onboarding**: Maintainer review SLA reduction initiative target set to **<24 hours**.
    - **Unit Economics**: Net Dollar Retention holds strong at **112%** driven by Enterprise expansion.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚠️ Executive Risk Register")
        st.error("1. High Contributor Drop-off (>48h response delay)")
        st.warning("2. Enterprise Concentration Risk (Top 5% accounts generate 62% ARR)")
        st.info("3. Infrastructure Scaling Cost Variance")
        
    with col2:
        st.subheader("🚀 Roadmap & Action Plan")
        st.success("Q4 Milestone 1: Automated Review Queue Prioritization")
        st.success("Q4 Milestone 2: Enterprise Self-Serve Expansion Tier")
        st.success("Q1 Milestone 3: Executive Reporting API Integration")
        
    st.divider()
    st.subheader("📥 Export Stakeholder Report")
    report_df = pd.DataFrame({
        "Metric": ["ARR", "Net Retention", "Gross Margin", "CAC Payback", "Avg Review Time"],
        "Current Value": ["$5.8M", "112%", "78%", "14 months", "32 hours"],
        "Target": ["$5.5M", "110%", "75%", "12 months", "<24 hours"],
        "Status": ["Exceeded", "Exceeded", "Exceeded", "On Track", "Action Required"]
    })
    st.dataframe(report_df, use_container_width=True)
    st.download_button("Download Executive Summary (CSV)", report_df.to_csv(index=False), "Executive_Briefing_Q3.csv", "text/csv")

elif page == "Data Storytelling":
    st.title("📖 Data Storytelling & Insight Narrative (Module 2.48)")
    st.markdown("Transforming complex statistical analysis into board-level strategic decisions.")

    st.image("public/data_storytelling_dashboard.png", caption="Executive Briefing: Support Response Time vs Churn Analysis", use_column_width=True)

    st.divider()

    st.subheader("🏛️ The Five-Part Narrative Arc")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Context", "2. Data", "3. Finding", "4. Why", "5. Action Plan"
    ])

    with tab1:
        st.markdown("""
        ### 1. Context: What is at stake?
        - **The Threat**: Customer churn drains **$2,000,000 ARR** annually.
        - **Strategic Objective**: Sustaining net dollar retention and customer lifetime value (LTV) is critical for our next growth round.
        - **Current Blindspot**: Support operations were viewed merely as an operational cost center rather than an ARR preservation engine.
        """)

    with tab2:
        st.markdown("""
        ### 2. Data: Scope & Confidence
        - **Sample Horizon**: **50,000** enterprise & mid-market accounts tracked across **24 months**.
        - **Metrics Tracked**: First-response support SLA latency categorized into 4 cohorts (<2h, 2-4h, 4-24h, >24h).
        - **Explanatory Power**: Support response latency accounts for **R² = 0.40** (40% of customer churn variance).
        """)

    with tab3:
        st.markdown("""
        ### 3. Finding: The Core Discovery
        - Customers waiting **>24 hours** churn at **12.0%**, compared to only **3.0%** for those answered in **<2 hours**.
        - **The 4x Escalation Rule**: Delayed initial response multiplies churn risk by **400%**.
        """)
        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.metric("Fast SLA (<2h) Churn", "3.0%", "Industry Leading")
        col_f2.metric("Slow SLA (>24h) Churn", "12.0%", "+9.0% vs SLA", delta_color="inverse")
        col_f3.metric("Churn Escalation Multiple", "4.0x", "High Risk", delta_color="inverse")

    with tab4:
        st.markdown("""
        ### 4. Why: Root Cause Mechanism
        - **Escalation Window**: Immediate response stops user frustration before issue severity compounds.
        - **Psychological Abandonment**: When a user experiences blocking friction with zero reply for 24 hours, they mentally classify the product as unreliable and evaluate alternatives.
        """)

    with tab5:
        st.markdown("### 5. Action: 5-Element Actionable Recommendation")
        st.markdown("""
| Element | Specification |
| :--- | :--- |
| **WHAT** | Hire 2 dedicated Tier-1 Support Engineers to guarantee <2h first-response SLA during peak hours |
| **WHY** | Eliminates the >24h backlog cohort responsible for the 4x churn escalation |
| **IMPACT** | **+$400,000 Net Annual Benefit** (Recovers $560K ARR at $160K hiring cost) |
| **OWNER** | VP of Customer Operations (Hiring) & Head of Support (Implementation) |
| **TIMELINE** | Post roles by Dec 1; Onboard by Jan 31; <2h SLA live by Jan 1 |
        """)

    st.divider()

    st.subheader("🔄 Technical Jargon to Executive Translation Matrix")
    st.markdown("Bridge statistical terminology into plain business impact:")
    translations = [
        {"Statistical Term (Data Team)": "Statistically significant correlation (r = 0.63, p < 0.001)", "Executive Translation (Leadership)": "Strong, reliable relationship that is not due to chance"},
        {"Statistical Term (Data Team)": "R-squared of 0.40 with support latency", "Executive Translation (Leadership)": "Support speed directly explains 40% of differences in retention"},
        {"Statistical Term (Data Team)": "Negatively skewed distribution of response latency", "Executive Translation (Leadership)": "Most tickets are resolved quickly, but a tail of customers waits unacceptably long"},
        {"Statistical Term (Data Team)": "Multivariate regression model with L2 regularization", "Executive Translation (Leadership)": "Validated model isolating support speed from product usage and pricing factors"}
    ]
    st.dataframe(pd.DataFrame(translations), use_container_width=True)

elif page == "Data Explorer":
    st.title("Data Explorer")
    df = pd.DataFrame({"Customer ID": [101, 102], "Revenue": [1200, 850]})
    st.dataframe(df)

