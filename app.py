import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="GitGeek Executive Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Cached Data Access Layer (@st.cache_data for instant reruns)
# -----------------------------------------------------------------------------
@st.cache_data
def get_executive_kpis():
    """Returns core top-level KPIs formatted for horizontal status scanning."""
    return {
        "Revenue": ("$5.2M", "+12.5%"),
        "Active Users": ("2,500", "+5.2%"),
        "AOV": ("$45", "+2.1%"),
        "Churn Rate": ("5.2%", "-2.8%", "inverse"),
        "NPS Score": ("72", "+4", "normal"),
    }


@st.cache_data
def load_monthly_trends_data():
    """Simulates monthly revenue and targets over 12 rolling months."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    revenue = [4.8, 5.0, 5.2, 5.1, 5.3, 5.5, 5.4, 5.6, 5.7, 5.8, 5.9, 6.0]
    target = [4.5, 4.7, 4.9, 5.0, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9]
    churn = [3.8, 3.6, 3.5, 3.7, 3.4, 3.2, 3.3, 3.1, 3.0, 3.0, 2.9, 2.8]
    return pd.DataFrame({
        "Month": months,
        "Actual Revenue ($M)": revenue,
        "Target Revenue ($M)": target,
        "Churn Rate (%)": churn
    })


@st.cache_data
def load_segment_breakdown_data():
    """Generates segment breakdown data across Enterprise, Mid-Market, and Startup tiers."""
    return pd.DataFrame({
        "Segment": ["Enterprise Tier", "Mid-Market Tier", "Startup Tier"],
        "Customer Count": [240, 1150, 4800],
        "Annual Revenue ($M)": [3.6, 1.4, 0.8],
        "Avg Contract Value ($)": [15000, 1217, 166],
        "Net Retention (%)": [124, 108, 94]
    })


@st.cache_data
def load_data_explorer_sample():
    """Provides a sample filtered customer transaction table for deep exploration."""
    np.random.seed(42)
    n = 250
    return pd.DataFrame({
        "Customer ID": [f"CUST-{1000 + i}" for i in range(n)],
        "Segment": np.random.choice(["Enterprise", "Mid-Market", "Startup"], n, p=[0.15, 0.35, 0.50]),
        "Region": np.random.choice(["North America", "EMEA", "APAC", "LATAM"], n),
        "Annual Spend ($)": np.random.exponential(scale=2500, size=n).round(2),
        "Support Tickets": np.random.poisson(lam=2.5, size=n),
        "Status": np.random.choice(["Active", "At Risk", "Churned"], n, p=[0.82, 0.12, 0.06])
    })


# -----------------------------------------------------------------------------
# 3. Sidebar Navigation & Global Filters
# -----------------------------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Trends",
        "Segments",
        "Data Explorer",
        "Executive Briefing (2.49)",
        "Data Storytelling (2.48)"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### Global Filters")
selected_fiscal_year = st.sidebar.selectbox("Fiscal Year", ["FY2024", "FY2023", "FY2022"])
currency_toggle = st.sidebar.radio("Display Units", ["USD ($)", "EUR (€)", "GBP (£)"])
st.sidebar.info("💡 Changes in the sidebar automatically reload relevant cached views.")


# -----------------------------------------------------------------------------
# 4. View 1: Business Overview
# -----------------------------------------------------------------------------
if page == "Overview":
    st.title("Business Overview")
    st.markdown("Real-time executive snapshot of company financial performance and customer retention.")

    # Section 1: KPI Cards in 5 Horizontal Columns
    st.header("Key Performance Indicators")
    kpis = get_executive_kpis()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", kpis["Revenue"][0], kpis["Revenue"][1])
    with col2:
        st.metric("Users", kpis["Active Users"][0], kpis["Active Users"][1])
    with col3:
        st.metric("AOV", kpis["AOV"][0], kpis["AOV"][1])
    with col4:
        st.metric("Churn", kpis["Churn Rate"][0], kpis["Churn Rate"][1], delta_color=kpis["Churn Rate"][2])
    with col5:
        st.metric("NPS", kpis["NPS Score"][0], kpis["NPS Score"][1])

    st.divider()

    # Section 2: Executive Summary Chart
    st.header("Quarterly Performance Trajectory")
    st.subheader("Monthly Revenue vs Planned Target")
    df_trends = load_monthly_trends_data()

    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trends["Month"], y=df_trends["Actual Revenue ($M)"],
            name="Actual Revenue ($M)", mode="lines+markers",
            line=dict(color="#10b981", width=3),
            marker=dict(size=7, color="#10b981")
        ))
        fig.add_trace(go.Scatter(
            x=df_trends["Month"], y=df_trends["Target Revenue ($M)"],
            name="Target Revenue ($M)", mode="lines",
            line=dict(color="#64748b", width=2, dash="dash")
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            margin=dict(l=30, r=30, t=30, b=30),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df_trends.set_index("Month")[["Actual Revenue ($M)", "Target Revenue ($M)"]])

    # Progressive Disclosure: Methodology & Data Lineage
    with st.expander("Methodology & Calculation Notes"):
        st.markdown("""
        - **Revenue Definition**: Recognized GAAP ARR booked at month-end close.
        - **Churn Rate**: Unadjusted customer count attrition within 90 days of contract renewal.
        - **NPS Score**: Trailing 30-day transactional survey score from active admin users.
        """)


# -----------------------------------------------------------------------------
# 5. View 2: Trend Analysis
# -----------------------------------------------------------------------------
elif page == "Trends":
    st.title("Trend Analysis")
    st.markdown("Detailed longitudinal tracking of growth drivers and operational health.")

    st.header("Revenue & Churn Dynamics")
    col_t1, col_t2 = st.columns(2)

    df_trends = load_monthly_trends_data()

    with col_t1:
        st.subheader("Monthly Revenue Trajectory ($M)")
        if PLOTLY_AVAILABLE:
            fig_rev = px.bar(
                df_trends, x="Month", y="Actual Revenue ($M)",
                color_discrete_sequence=["#0284c7"],
                template="plotly_dark"
            )
            fig_rev.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.6)")
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.bar_chart(df_trends.set_index("Month")["Actual Revenue ($M)"])

    with col_t2:
        st.subheader("Monthly Churn Rate (%)")
        if PLOTLY_AVAILABLE:
            fig_churn = px.line(
                df_trends, x="Month", y="Churn Rate (%)",
                color_discrete_sequence=["#ef4444"],
                markers=True,
                template="plotly_dark"
            )
            fig_churn.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.6)")
            st.plotly_chart(fig_churn, use_container_width=True)
        else:
            st.line_chart(df_trends.set_index("Month")["Churn Rate (%)"])

    st.divider()

    with st.expander("View Underlying Trend Data"):
        st.dataframe(df_trends, use_container_width=True)
        st.download_button(
            "Download Monthly Trends CSV",
            df_trends.to_csv(index=False),
            "monthly_trends.csv",
            "text/csv"
        )


# -----------------------------------------------------------------------------
# 6. View 3: Segment Breakdown
# -----------------------------------------------------------------------------
elif page == "Segments":
    st.title("Segment Breakdown")
    st.markdown("Deep dive into customer cohort profitability, retention, and concentration.")

    df_segments = load_segment_breakdown_data()

    st.header("Segment Concentration & Contribution")
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.subheader("Revenue Contribution by Tier ($M)")
        if PLOTLY_AVAILABLE:
            fig_seg = px.pie(
                df_segments, names="Segment", values="Annual Revenue ($M)",
                color_discrete_sequence=["#0284c7", "#f59e0b", "#10b981"],
                hole=0.4,
                template="plotly_dark"
            )
            fig_seg.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_seg, use_container_width=True)
        else:
            st.dataframe(df_segments[["Segment", "Annual Revenue ($M)"]])

    with col_s2:
        st.subheader("Net Dollar Retention by Tier (%)")
        if PLOTLY_AVAILABLE:
            fig_ndr = px.bar(
                df_segments, x="Segment", y="Net Retention (%)",
                color="Segment",
                color_discrete_sequence=["#0284c7", "#f59e0b", "#10b981"],
                template="plotly_dark"
            )
            fig_ndr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.6)")
            st.plotly_chart(fig_ndr, use_container_width=True)
        else:
            st.bar_chart(df_segments.set_index("Segment")["Net Retention (%)"])

    st.divider()

    st.header("Comparative Tier Metrics")
    st.dataframe(df_segments, use_container_width=True)

    with st.expander("Segment Definitions & Thresholds"):
        st.markdown("""
        - **Enterprise Tier**: Annual contract value exceeding $10,000 with dedicated SLA.
        - **Mid-Market Tier**: Annual contract value between $1,000 and $9,999.
        - **Startup Tier**: Self-serve tier with contract value under $1,000.
        """)


# -----------------------------------------------------------------------------
# 7. View 4: Data Explorer
# -----------------------------------------------------------------------------
elif page == "Data Explorer":
    st.title("Data Explorer")
    st.markdown("Interactive query, filtering, and export engine for self-serve analytics.")

    df_raw = load_data_explorer_sample()

    st.header("Filter & Query Parameters")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        segment_filter = st.multiselect("Select Tier", ["Enterprise", "Mid-Market", "Startup"], default=["Enterprise", "Mid-Market", "Startup"])
    with f_col2:
        region_filter = st.multiselect("Select Region", ["North America", "EMEA", "APAC", "LATAM"], default=["North America", "EMEA", "APAC", "LATAM"])
    with f_col3:
        status_filter = st.multiselect("Account Status", ["Active", "At Risk", "Churned"], default=["Active", "At Risk", "Churned"])

    # Filter evaluation
    filtered_df = df_raw[
        (df_raw["Segment"].isin(segment_filter)) &
        (df_raw["Region"].isin(region_filter)) &
        (df_raw["Status"].isin(status_filter))
    ]

    st.divider()

    st.subheader(f"Filtered Results ({len(filtered_df):,} accounts matching criteria)")
    st.dataframe(filtered_df, use_container_width=True)

    # Actionable download
    st.download_button(
        label="📥 Export Filtered Dataset (CSV)",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_customer_data.csv",
        mime="text/csv"
    )

    with st.expander("Data Schema & Field Descriptions"):
        st.markdown("""
        | Column Name | Type | Description |
        | :--- | :--- | :--- |
        | `Customer ID` | String | Unique surrogate customer account key |
        | `Segment` | Categorical | Enterprise, Mid-Market, or Startup classification |
        | `Region` | Categorical | Billing jurisdiction |
        | `Annual Spend ($)` | Float | Cumulative recognized gross billing over 12 months |
        | `Support Tickets` | Integer | Total service inquiries logged in trailing 90 days |
        | `Status` | Categorical | Account operational posture (Active, At Risk, Churned) |
        """)


# -----------------------------------------------------------------------------
# 8. View 5: Executive Briefing (2.49)
# -----------------------------------------------------------------------------
elif page == "Executive Briefing (2.49)":
    st.title("👔 Executive Briefing & Stakeholder Communication")
    st.markdown("Quarterly Strategic Report for Board & Leadership.")

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


# -----------------------------------------------------------------------------
# 9. View 6: Data Storytelling & Insight Narrative (2.48)
# -----------------------------------------------------------------------------
elif page == "Data Storytelling (2.48)":
    st.title("📖 Data Storytelling & Insight Narrative")
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
