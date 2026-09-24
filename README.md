# Contributor Retention Analytics

A Sprint 1 MVP for the problem statement:

> Open-source maintainers have contributor activity, PR review timelines, and issue participation records, but no workflow reveals which onboarding experiences discourage first-time contributors from returning.

## What this MVP does

- Shows first-time contributor count, return rate, average response/review/merge times.
- Separates contributors into **Returned** and **Did not return**.
- Calculates onboarding factors from pull-request activity.
- Highlights possible drop-off factors.
- Generates maintainer recommendations from the observed data.
- Runs immediately in **Demo Mode** with sample data.
- Can analyze a public GitHub repository through the GitHub REST API.

## Tech stack

- Node.js + Express
- Vanilla HTML/CSS/JavaScript
- GitHub REST API
- Chart.js via CDN

## Run locally

1. Install Node.js 18+.
2. Open this folder in a terminal.
3. Run:

```bash
npm install
npm start
```

4. Open http://localhost:3000

## GitHub mode

Copy `.env.example` to `.env` and optionally add a GitHub personal access token:

```env
GITHUB_TOKEN=your_token_here
PORT=3000
```

Then enter a public repository such as `facebook/react` or `nodejs/node` in the dashboard.

### Important MVP limitation

GitHub's public API and repository history can be large. This MVP intentionally analyzes a bounded set of recent pull requests so it is easy to run during a sprint. For a production version, add pagination, caching, background jobs, database storage, GitHub App authentication, and a more rigorous cohort definition.

## Suggested Sprint 1 demo

1. Open the dashboard in Demo Mode.
2. Explain the onboarding funnel.
3. Show Returned vs Did Not Return.
4. Explain first response time, review activity, and merge time.
5. Show the factors panel and recommendations.
6. Switch to a public GitHub repo to demonstrate real-data analysis.

## Project structure

```text
contributor-retention-analytics/
├── public/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── distribution_charts.png
│   ├── segment_insights.png
│   ├── funnel_analysis.png
│   ├── anomaly_monitoring.png
│   ├── query_optimization.png
│   ├── business_visualisation_principles.png
│   └── data_storytelling_dashboard.png
├── queries/
│   ├── monthly_active_users.sql
│   ├── revenue_by_segment.sql
│   ├── conversion_funnel.sql
│   ├── retention_cohort.sql
│   ├── rolling_7day_active_users.sql
│   ├── optimization_select_star_antipattern.sql
│   ├── optimization_early_filtering.sql
│   ├── optimization_cte_structuring.sql
│   └── optimization_benchmark_comparison.sql
├── data/
│   ├── demo.json
│   ├── business_metrics.duckdb
│   ├── customer_revenue.csv
│   ├── customer_churn_segments.csv
│   ├── funnel_events.csv
│   ├── hourly_kpi_metrics.csv
│   └── anomalies.csv
├── init_db.py
├── metrics_runner.py
├── run_filtering_analysis.py
├── joins_runner.py
├── distribution_runner.py
├── segment_aggregation_runner.py
├── funnel_analysis_runner.py
├── anomaly_runner.py
├── query_optimization_runner.py
├── visualisation_principles_runner.py
├── data_storytelling_runner.py
├── streamlit_structure_runner.py
├── session_state_runner.py
├── insight_delivery_runner.py
├── app.py
├── main.py
├── requirements.txt
├── INSIGHT_DELIVERY_GUIDE.md
├── VIDEO_SCRIPT_INSIGHT_DELIVERY.md
├── STREAMLIT_SESSION_STATE_GUIDE.md
├── VIDEO_SCRIPT_STREAMLIT_SESSION_STATE.md
├── STREAMLIT_NAVIGATION_GUIDE.md
├── VIDEO_SCRIPT_STREAMLIT_NAVIGATION.md
├── DATA_STORYTELLING_GUIDE.md
├── VIDEO_SCRIPT_DATA_STORYTELLING.md
├── VISUALISATION_DESIGN_GUIDE.md
├── VIDEO_SCRIPT_VISUALISATION.md
├── QUERY_OPTIMIZATION_GUIDE.md
├── VIDEO_SCRIPT_OPTIMIZATION.md
├── ANOMALY_DETECTION_GUIDE.md
├── VIDEO_SCRIPT_ANOMALY.md
├── FUNNEL_ANALYSIS_GUIDE.md
├── VIDEO_SCRIPT_FUNNEL.md
├── SEGMENT_AGGREGATION_GUIDE.md
├── VIDEO_SCRIPT_SEGMENT_INSIGHTS.md
├── DISTRIBUTION_ANALYSIS_GUIDE.md
├── VIDEO_SCRIPT_DISTRIBUTION.md
├── .env.example
├── .gitignore
├── package.json
├── README.md
└── server.js
```

---

## 2.38 SQL Business Metrics Query Design

This module implements centralized, reusable SQL business metric queries that define consistent single-source-of-truth KPIs.

### Included Business Metrics Queries
- **Task 1**: `queries/monthly_active_users.sql` (Monthly Active Users with Enterprise & SMB conditional breakdown)
- **Task 2**: `queries/revenue_by_segment.sql` (Segment revenue, order counts, AOV, and revenue per customer)
- **Task 3**: `queries/conversion_funnel.sql` (Daily signup, verification, and first-purchase conversion funnel)
- **Bonus**: `queries/retention_cohort.sql` (Cohort retention matrix using CTEs)
- **Bonus**: `queries/rolling_7day_active_users.sql` (Trailing 7-day active user window)

### Running Metrics & Automated Validation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database and seed sample data
python init_db.py

# 3. Execute all queries and run validation assertions
python metrics_runner.py
```

---

## SQL Filtering, Grouping & Aggregation (WHERE vs. HAVING)

Demonstrates the architectural distinction between filtering row-level attributes before grouping (`WHERE`) versus filtering aggregated group metrics after grouping (`HAVING`).

### Core Problem
*"Show Enterprise customers with >$10k annual spending - do you filter before or after grouping? Do you use WHERE or HAVING?"*
- Filter `customer_type = 'Enterprise'` **BEFORE** grouping in `WHERE` (row-level property).
- Filter `SUM(amount) > 10000` **AFTER** grouping in `HAVING` (aggregated spend across rows).

### Included Queries
- **Core Architecture**: `queries/enterprise_annual_spending.sql`
- **Task 1**: `queries/where_filtering.sql` (Data hygiene: status, refunds, date filtering before aggregation)
- **Task 2**: `queries/group_by_aggregation.sql` (Multi-dimension grouping by segment & month)
- **Task 3**: `queries/having_filtering.sql` (Group-level threshold filtering after aggregation)
- **Task 4**: `queries/where_having_combined.sql` (Production pattern combining WHERE & HAVING)
- **Task 5**: `queries/order_by_ranking.sql` (Top-performer isolation with `RANK()` and `LIMIT`)
- **Bonus**: `queries/percentage_share.sql` (Analytic percentage share computation using window functions)

### Running Filtering & Aggregation Validation
```bash
python run_filtering_analysis.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`WHERE_VS_HAVING_GUIDE.md`](./WHERE_VS_HAVING_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_FILTERING.md`](./VIDEO_SCRIPT_FILTERING.md)

---

## 2.40 SQL Joins & Multi-Table Analysis

Demonstrates relational joins, referential integrity audits, and multi-table data lineage validation without duplicate fan-out.

### Key Capabilities
- **Task 1**: `queries/task1_left_join_orders.sql` & `queries/join_row_count_validation.sql` (LEFT JOIN with row count expansion validation)
- **Task 2**: `queries/task2_unmatched_customers.sql` & `queries/task2_orphaned_orders.sql` (IS NULL audit for inactive users & orphaned records)
- **Task 3**: `queries/task3_inner_join.sql`, `queries/task3_left_join.sql`, `queries/task3_full_outer_join.sql` (Mathematical join comparison)
- **Task 4**: `queries/task4_multi_table_join.sql` (4-table lineage join with zero-duplication financial validation)
- **Task 5**: Strategy documentation in [`JOIN_STRATEGY_DOCUMENTATION.md`](./JOIN_STRATEGY_DOCUMENTATION.md) and [`VIDEO_SCRIPT_JOINS.md`](./VIDEO_SCRIPT_JOINS.md)

### Running Joins Validation
```bash
python joins_runner.py
```

---

## 2.28 Distribution Analysis for Business Trends

Statistical distribution analysis, skewness and kurtosis computation, visualization, and customer segment decomposition to prevent misleading metric reporting.

### Core Business Problem
*"A revenue dataset has an arithmetic mean of $5,000. But 80% of customers spend under $500 (median $454), while a handful of enterprise accounts spend $50,000. The mean is dangerously misleading; distribution analysis is required to reveal the true bimodal business structure."*

### Key Deliverables & Capabilities
- **Task 1: Summary Statistics & Central Tendency Comparison**:
  - Highlights the $5,000 mean vs. $454 median distortion.
  - Demonstrates why median and IQR best reflect the typical customer in skewed distributions.
- **Task 2: Skewness & Kurtosis Statistical Interpretation**:
  - `skewness = stats.skew(df['revenue'])` (2.21 > 1.0 $\rightarrow$ Highly skewed, use median).
  - `kurtosis = stats.kurtosis(df['revenue'])` (3.51 > 3.0 $\rightarrow$ Heavy tails, expect extreme outliers).
- **Task 3: Visualizing Distributions (Histogram & KDE)**:
  - 50-bin discrete histogram with mean and median lines.
  - Smooth Kernel Density Estimate (KDE) plot showing continuous probability density.
- **Task 4: Segment Comparison & Bimodal Decomposition**:
  - Contrasts High-Value (> Q3) vs. Low-Value (< Q1) customer tiers.
  - Bimodal decomposition separating Small Business (mean $444) from Enterprise (mean $23,222).
  - Multi-panel visual plot saved to [`public/distribution_analysis.png`](./public/distribution_analysis.png).
- **Task 5: Automated Verification Assertions**:
  - Validates statistical thresholds, sample sizes, and chart outputs.

### Running Distribution Analysis
```bash
# Run standalone distribution analysis
python distribution_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`DISTRIBUTION_ANALYSIS_GUIDE.md`](./DISTRIBUTION_ANALYSIS_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_DISTRIBUTION.md`](./VIDEO_SCRIPT_DISTRIBUTION.md)

---

## 2.30 GroupBy Aggregation & Segment Insights

Multi-dimensional GroupBy analysis, Split-Apply-Combine patterns, pivot tables, segment ranking, and strategic business interventions to overcome the dataset-wide average fallacy.

### Core Business Problem
*"A company reports an average churn rate of 9.25%. Marketing plans a broad generic retention campaign. But when segmented by customer type, Enterprise customers (5% of customer base) have 1% churn and generate 70% of revenue, while SMB customers (40% of base) suffer from 12% churn. Reporting a single blended average hides where business levers and risks actually exist."*

### Key Deliverables & Capabilities
- **Task 1: Dataset-Wide Averages vs. Segment Realities**:
  - Highlights the fallacy of reporting a single 9.25% blended churn rate when customer segments diverge from 1% to 12%.
- **Task 2: Split-Apply-Combine Pattern (.agg, .transform, .apply)**:
  - `.agg(['sum', 'count', 'mean'])` for group summary collapse.
  - `.transform('mean')` for broadcasting group averages back to individual rows without losing dimensionality.
  - `.apply(lambda x: x.nlargest(3).sum())` for custom group-level logic.
- **Task 3: Multi-Dimensional GroupBy & `.unstack()`**:
  - Multi-index grouping across `customer_type` and `product` with `.unstack()` reshaping into a 2D matrix.
- **Task 4: Two-Dimensional Pivot Tables**:
  - `pd.pivot_table()` for revenue totals and product vulnerability churn matrices.
- **Task 5: Segment Ranking & Actionable Business Insights**:
  - Ranks segments by churn risk and revenue contribution.
  - Generates concrete, evidence-based strategic interventions for Enterprise, SMB, and Startup cohorts.
- **Task 6: Visualizations & Automated Assertions**:
  - 4-panel visual dashboard saved to [`public/segment_insights.png`](./public/segment_insights.png).
  - Complete automated test suite validating metrics, shapes, and pivot equivalence.

### Running Segment Aggregation Analysis
```bash
# Run standalone segment aggregation
python segment_aggregation_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`SEGMENT_AGGREGATION_GUIDE.md`](./SEGMENT_AGGREGATION_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_SEGMENT_INSIGHTS.md`](./VIDEO_SCRIPT_SEGMENT_INSIGHTS.md)

---

## 2.33 Funnel Analysis & Drop-Off Detection

Granular sequential journey mapping, step-by-step drop-off measurement, programmatic bottleneck isolation, and business revenue impact simulation.

### Core Business Problem
*"A company has 10,000 users click 'Sign Up' and 2,000 make a first purchase. Leadership knows aggregate conversion is 20%, but cannot pinpoint where the remaining 8,000 dropped off. Without granular step metrics, engineering wastes time optimizing top-of-funnel signup screens instead of fixing a massive 50% post-payment abandonment leak."*

### Key Deliverables & Capabilities
- **Task 1: Sequential Funnel Mapping**:
  - Granular 6-stage user onboarding tracking: Sign Up Clicked (10k) $\rightarrow$ Email Entered (8k) $\rightarrow$ Password Created (6k) $\rightarrow$ Email Verified (5k) $\rightarrow$ Payment Added (4k) $\rightarrow$ First Purchase (2k).
- **Task 2: Consecutive Drop-Off & Completion Mathematics**:
  - Measures Absolute Drop ($N_i - N_{i+1}$), Drop-Off Rate (%), Completion Rate (%), and Cumulative Conversion (%).
- **Task 3: Programmatic Bottleneck Detection**:
  - Identifies **Payment Added $\rightarrow$ First Purchase** as the primary leak with a **50.0% drop rate (2,000 lost users)**.
  - Pinpoints late-stage checkout friction (gateway timeouts, hidden fees, ambiguous confirmation CTAs).
- **Task 4: Financial & Business Impact Modeling**:
  - Quantifies revenue gains: reducing bottleneck drop-off to 30% yields **+$119.3k (+40% ARR)**, while full friction removal doubles first-purchase ARR to **~$596.5k (+100%)**.
- **Task 5: Funnel Visualizations Dashboard**:
  - 4-panel visual dashboard saved to [`public/funnel_analysis.png`](./public/funnel_analysis.png).
- **Task 6: Automated Verification Assertions**:
  - Automated assertions verifying sample volumes, drop rates, bottleneck detection, and chart integrity.

### Running Funnel Analysis
```bash
# Run standalone funnel analysis
python funnel_analysis_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`FUNNEL_ANALYSIS_GUIDE.md`](./FUNNEL_ANALYSIS_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_FUNNEL.md`](./VIDEO_SCRIPT_FUNNEL.md)

---

## 2.36 Anomaly Detection & Risk Identification

Dual-layer operational monitoring framework combining static threshold rules with adaptive 24-hour rolling Z-scores to flag silent outages, fraud surges, and pricing exploits.

### Core Business Problem
*"A payment processing error causes all transactions to fail silently for 2 hours. Revenue drops from ~$25k/hr to $0. Nobody notices until customer complaints arrive, causing $50k+ in unrecoverable losses. Meanwhile, a bot registration attack floods 10,000 fake accounts unnoticed, and a catalog pricing bug sells premium licenses for $1.10. Without continuous automated anomaly detection, businesses remain blind to catastrophic operational risks."*

### Key Deliverables & Capabilities
- **Task 1: Threshold-Based Alert Engine**:
  - Configures static operational boundaries (`STATIC_THRESHOLDS`) for hourly/daily revenue, transaction volume, and signup rate.
  - Generates immediate Warning/Critical flags on min/max boundary breaches.
- **Task 2: Statistical Z-Score & 24-Hour Rolling Monitoring**:
  - Implements shifted 24-hour moving baselines ($\mu_t, \sigma_t$) to prevent anomaly contamination.
  - Classifies severity dynamically: Normal ($|Z| < 2.0$), Warning ($2.0 \le |Z| < 3.0$), and Critical ($|Z| \ge 3.0$).
- **Task 3: Real Scenario Detection & Incident Isolation**:
  - **Payment Processing Blackout**: Catches two-hour $0.00 revenue drop ($Z = -4.52$ and $Z = -3.22$, saving ~$37.3k - $50k+).
  - **Bot Registration Surge**: Uncovers 3:00 AM spike to 260 signups ($Z = +32.51$, 10x normal rate).
  - **Catalog Pricing Exploit**: Flags 4x transaction surge (1,350 tx, $Z = +18.26$) with collapsed $1.10 unit revenue ($Z = -4.46$).
- **Task 4: Auditable Incident Log Export**:
  - Compiles structured incident records to [`data/anomalies.csv`](./data/anomalies.csv) with timestamps, metric values, rolling statistics, Z-scores, severities, and root cause diagnoses.
- **Task 5: Multi-Panel Visual Dashboard**:
  - High-resolution visual dashboard saved to [`public/anomaly_monitoring.png`](./public/anomaly_monitoring.png) featuring revenue confidence corridors, velocity dual-axis time series, normal distribution bell curve overlay, and executive governance matrix.
- **Task 6: Automated Verification Assertions**:
  - Strict assertions validating sample lengths, threshold alerts, Z-scores, outage detections, and file generation.

### Running Anomaly Detection
```bash
# Run standalone anomaly detection
python anomaly_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`ANOMALY_DETECTION_GUIDE.md`](./ANOMALY_DETECTION_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_ANOMALY.md`](./VIDEO_SCRIPT_ANOMALY.md)

---

## SQL Query Optimization & Performance Tuning

Engineering patterns and performance benchmarks for scaling analytical queries: eliminating `SELECT *`, applying early filter pushdown before joins, structuring logic with Common Table Expressions (CTEs), and analyzing execution plans.

### Core Business Problem
*"An analytical dashboard query runs against a 100M-row transaction table with SELECT *, pulling 50 columns when only 5 are needed. It then joins a 10M-row customer table, creating a 500GB intermediate result in memory, before a WHERE filter discards 90% of rows. The dashboard times out, analysts wait 45+ seconds, and business decisions stall. The query—not the database—is the bottleneck."*

### Key Deliverables & Capabilities
- **Task 1: Eliminating the `SELECT *` Antipattern**:
  - Replaces broad scans with explicit column projections.
  - Benchmarked on 50k rows: reduces transferred columns by **85.7%** (35 cols $\rightarrow$ 5 cols) and delivers a **13.0x speedup**.
- **Task 2: Early Filtering (WHERE Before JOIN)**:
  - Pushes predicate filters into derived subqueries and scan steps before joining.
  - Prunes **80.0% of warehouse rows** (50,000 $\rightarrow$ 10,000) before hash table allocation, collapsing memory buffers by **10x**.
- **Task 3: Common Table Expressions (CTEs)**:
  - Restructures 5-level nested subqueries into a modular 3-stage pipeline: `recent_transactions` $\rightarrow$ `customer_summary` $\rightarrow$ high-value customer join.
  - Implements clean top-to-bottom narrative flow and isolated unit testability.
- **Task 4: Compounding Performance Measurement**:
  - Quantifies compounding latency reductions: **45s (Baseline) $\rightarrow$ 30s (Explicit Columns) $\rightarrow$ 8s (Early Filtering) $\rightarrow$ 2s (CTE + Pushdown)**, achieving a **22.5x total speedup**.
- **Task 5: Multi-Panel Visual Dashboard**:
  - High-resolution dashboard saved to [`public/query_optimization.png`](./public/query_optimization.png) showcasing the latency waterfall, memory buffer comparison, execution operator plan, and production checklist.
- **Task 6: Automated Verification Assertions**:
  - Automated assertions validating column counts, pruning ratios, CTE business rules, and file generation.

### Running Query Optimization
```bash
# Run standalone query optimization benchmarks
python query_optimization_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`QUERY_OPTIMIZATION_GUIDE.md`](./QUERY_OPTIMIZATION_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_OPTIMIZATION.md`](./VIDEO_SCRIPT_OPTIMIZATION.md)

---

## 2.45 Business Visualisation Principles

Standards for turning complex enterprise data into self-explanatory visuals: matching chart types to data relationships, enforcing the 5 labelling elements, human-readable formatting, dual-encoding for accessibility, and contextual annotations.

### Core Business Problem
*"An analyst presents quarterly product line performance as a pie chart. The CEO asks which product grew the fastest, but the pie chart cannot communicate growth or velocity over time. Switching to an unformatted raw data table stalls the meeting as leadership scans dozens of numbers. The charts fail because they were chosen based on what looked decorative rather than what the data needed to communicate."*

### Key Deliverables & Capabilities
- **Task 1: The 5 Fundamental Chart Types**:
  - **Horizontal Bar Chart**: Category comparison with sorted lengths and direct `$M` value labels.
  - **Multi-Line Time Series**: Continuous temporal trends comparing customer segments, preventing discrete categorical line anti-patterns.
  - **Distribution Histogram**: Reveals typical values, spread, outliers, and contrasts Median vs skewed Mean.
  - **Scatter Plot with Trendline**: Explores correlations (Marketing Spend vs Revenue), adding OLS regression lines and marginal ROI metrics ($r = 0.95$).
  - **Stacked Bar Chart**: Part-to-whole quarterly composition constrained to $\le 5$ segments with total bar height labels.
- **Task 2: Complete Labelling & Human Readability**:
  - Implements the 5 essential elements: Actionable Title, explicit X & Y axes with units, non-overlapping legend, and direct data labels.
  - Enforces currency formatting (`$5.2M` instead of `5200000`) and date readability (`Jan 2024`) via `FuncFormatter`.
- **Task 3: Unified Palette & Accessibility**:
  - Consistent global palette (`PALETTE` & `CHART_COLORS`).
  - Dual-encoding for color blindness (combining colors with unique marker shapes `o`, `s`, `^` and line patterns `--`, `:`).
- **Task 4: Contextual Annotations & Reference Lines**:
  - Highlights peaks and anomalies via `ax.annotate` with arrow pointers.
  - Adds horizontal target benchmark lines (`axhline`) to transform displays into actionable insight delivery tools.
- **Task 5: Multi-Panel Visual Dashboard**:
  - Publication-ready 6-panel showcase saved to [`public/business_visualisation_principles.png`](./public/business_visualisation_principles.png).
- **Task 6: Automated Verification Assertions**:
  - Comprehensive assertions verifying segment limits, correlation math, skewness logic, currency formatters, and image integrity.

### Running Visualisation Principles
```bash
# Run standalone visualisation principles suite
python visualisation_principles_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`VISUALISATION_DESIGN_GUIDE.md`](./VISUALISATION_DESIGN_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_VISUALISATION.md`](./VIDEO_SCRIPT_VISUALISATION.md)

---

## 2.48 Data Storytelling & Insight Narrative

Transforms quantitative analysis into executive decisions using the **Five-Part Narrative Arc**, concrete evidence frameworks, technical jargon translation, and 5-element actionable recommendations.

### Core Business Problem
*"An analyst discovers that customer churn correlates strongly with support response time. They present 15 slides filled with scatter plots, regression equations, and p-values. The executive team nods politely, takes no action, and moves to the next agenda item. Three months later, churn has increased, and leadership asks why nobody warned them. The failure wasn't the analysis — it was the narrative."*

### Key Deliverables & Capabilities
- **The Five-Part Narrative Arc**:
  1. **Context (The Stakes)**: Customer churn drains **$2.0M ARR** annually.
  2. **Data (Scope & Methodology)**: **50,000 customers** across **24 months**; support latency explains **40% of churn variance ($R^2 = 0.40$)**.
  3. **Finding (The Core Discovery)**: >24h response churns at **12.0%** vs **3.0%** for <2h (**4.0x escalation multiple**).
  4. **Why (Root Cause Mechanism)**: Resolution speed halts problem escalation; delayed tickets lead to psychological abandonment before answers arrive.
  5. **Action (5-Element Recommendation)**:
     - **WHAT**: Hire 2 dedicated Tier-1 Support Engineers to guarantee <2h first-response SLA.
     - **WHY**: Eliminates the critical >24h queue backlog driving 4x churn.
     - **IMPACT**: **+$400,000 Net Annual Benefit** (Recovers $560K ARR at $160K cost, 250% ROI).
     - **OWNER**: VP of Customer Operations & Head of Support.
     - **TIMELINE**: Post roles by Dec 1; Hire by Jan 31; <2h SLA live by Jan 1.
- **Jargon Translation Matrix**:
  - Translates abstract statistical formulas ($r=0.63, p<0.001$, $R^2=0.40$, skewed distributions) into clear executive decision criteria.
- **Visual Narrative Dashboard**:
  - Boardroom-ready 4-panel visual artifact saved to [`public/data_storytelling_dashboard.png`](./public/data_storytelling_dashboard.png) featuring:
    1. Churn Rate Escalation Bar Chart.
    2. ROI Waterfall & Financial Value Bridge.
    3. The 5-Part Narrative Arc Flowchart.
    4. The 5-Element Executive Proposal Scorecard.
- **Interactive Streamlit Dashboard View**:
  - Dedicated "Data Storytelling" page in `app.py` with tabbed narrative exploration and jargon dictionary.

### Running Data Storytelling
```bash
# Run standalone data storytelling runner & validation suite
python data_storytelling_runner.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`DATA_STORYTELLING_GUIDE.md`](./DATA_STORYTELLING_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_DATA_STORYTELLING.md`](./VIDEO_SCRIPT_DATA_STORYTELLING.md)

---

## 2.51 Streamlit App Structure & Navigation

Scaffolds a multi-section interactive application with sidebar navigation, layout columns, expanders for progressive disclosure, visual hierarchy, and `@st.cache_data` optimization to prevent cluttered single-page dashboards.

### Core Business Problem
*"A data team builds a Streamlit app with 15 charts, 8 filters, and 3 data tables in a single scrollable page. The operations manager opens it, scrolls for 30 seconds, cannot find the churn dashboard, gives up, and goes back to requesting reports via email. The app had every feature. It had no structure. Without navigation, every feature is invisible."*

### Key Deliverables & Architecture
- **Sidebar Navigation**:
  - `st.sidebar.radio` providing instant one-click switching across 6 dedicated sections:
    1. **Overview**: Executive status snapshot with top-line metrics and revenue trajectory.
    2. **Trends**: Monthly time-series dynamics for revenue and churn.
    3. **Segments**: Tier-by-tier contribution (Enterprise, Mid-Market, Startup) and Net Dollar Retention.
    4. **Data Explorer**: Self-serve multidimensional query filtering and CSV dataset export.
    5. **Executive Briefing (2.49)**: Strategic quarterly board highlights and risk register.
    6. **Data Storytelling (2.48)**: Five-part narrative arc, interactive tabs, and jargon translator.
- **Horizontal Scanning (`st.columns`)**:
  - 5-column layout on the Overview page displaying executive KPI cards (Revenue, Users, AOV, Churn, NPS) above the fold.
- **Progressive Disclosure (`st.expander`)**:
  - Keeps primary views clean by hiding methodology notes, data schemas, and raw tables behind expandable drawers.
- **Visual Hierarchy**:
  - Consistent layout structure using `st.title` (page anchor), `st.header` (major section), `st.subheader` (chart title), and `st.divider` (clean section separation).
- **Execution & Caching Model (`@st.cache_data`)**:
  - Explains the Streamlit top-to-bottom script rerun model and utilizes `@st.cache_data` to ensure zero lag on subsequent reruns.
- **Automated Validation Suite (`streamlit_structure_runner.py`)**:
  - Validates Streamlit imports, sidebar navigation routes, column grids, expander hierarchy, and caching decorators.

### Running Streamlit Application & Tests
```bash
# Run standalone Streamlit structure verification suite
python streamlit_structure_runner.py

# Launch interactive Streamlit web dashboard
streamlit run app.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`STREAMLIT_NAVIGATION_GUIDE.md`](./STREAMLIT_NAVIGATION_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_STREAMLIT_NAVIGATION.md`](./VIDEO_SCRIPT_STREAMLIT_NAVIGATION.md)

---

## 2.52 Streamlit Session State & Workflow Management

Implements persistent state management across script reruns using `st.session_state` to prevent analytical workflows from resetting when independent widgets or filters are adjusted.

### Core Business Problem
*"An analyst builds a two-step workflow: Step 1 selects a customer segment for analysis. Step 2 computes churn metrics for that segment. The user selects Enterprise in step 1, sees the metrics in step 2, then changes a date filter. Streamlit reruns the script. The segment selection resets to default. Step 2 now shows metrics for all segments instead of Enterprise. The user must re-select Enterprise every time they touch any other control."*

### Key Deliverables & Architecture
- **Persistent Session State (`st.session_state`)**:
  - Stores multi-step state across full script reruns (`selected_segment`, `workflow_step`, `analysis_result`, `selected_tier_metric`, `workflow_history`).
- **Safe Default Initialization Pattern**:
  - Employs `if key not in st.session_state:` checks before variable assignment to prevent reruns from overwriting in-flight user decisions.
- **Multi-Step Analytical Workflow Dependency**:
  - Step 1 selects and confirms the target cohort (`All`, `Enterprise`, `Mid-Market`, `Startup`).
  - Step 2 conditionally renders only when confirmed (`workflow_step >= 2`), calculating dynamic cohort spend, support ticket counts, and observed churn without resetting.
- **Widget State Synchronization**:
  - Reads `st.session_state` directly into widget `index` parameters to keep UI visual dropdowns perfectly synchronized with session memory.
- **Targeted Reset Mechanism**:
  - Dedicated "Reset Workflow State" button that deletes only specific workflow keys and triggers `st.rerun()`, preserving clean isolation without wiping unrelated session settings.
- **Automated Validation Suite (`session_state_runner.py`)**:
  - Simulates script reruns, step transitions, filter interactions, and reset actions across 5 automated test assertions.

### Running Session State Tests & Workflows
```bash
# Run standalone Session State & Workflow validation suite
python session_state_runner.py

# Launch interactive Streamlit application with session state
streamlit run app.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`STREAMLIT_SESSION_STATE_GUIDE.md`](./STREAMLIT_SESSION_STATE_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_STREAMLIT_SESSION_STATE.md`](./VIDEO_SCRIPT_STREAMLIT_SESSION_STATE.md)

---

## 2.53 Automated Insight Delivery & Email Reports

Automates the last mile of analytics communication by producing structured briefings (`KPI Summary`, `Key Finding`, `Recommended Action`) and delivering them via email (`smtplib`) with secure environment credentials and non-blocking error handling.

### Core Business Problem
*"The weekly churn report is ready every Monday at 9 AM inside a Streamlit dashboard. The VP of Operations checks on Tuesdays. The CEO never opens it. By Wednesday, the analyst receives multiple Slack messages asking for numbers already computed on Monday. The analyst spends Tuesday afternoon exporting CSVs and typing summary emails instead of performing analysis."*

### Key Deliverables & Architecture
- **Structured Report Generation (`generate_report`)**:
  - Automatically synthesizes dataframes into standardized, executive-ready plaintext briefings containing:
    1. **KPI Summary**: Total Revenue, Active Customers, Average Order Value.
    2. **Key Finding**: Top performing cohort and retention insights (e.g. 4x retention for <2h support response).
    3. **Recommended Action**: Clear resource allocation guidance ($400,000 net ARR protected).
- **Secure Email Delivery Engine (`send_report_email`)**:
  - Connects to SMTP servers via Python's standard `smtplib` over TLS.
  - Zero hardcoded credentials: reads `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, and `SENDER_PASSWORD` strictly from environment variables documented in `.env.example`.
- **Non-Blocking Error Handling**:
  - Catches connection and authentication exceptions gracefully, returning diagnostic boolean tuples `(False, error_msg)` without crashing Streamlit or stopping pipeline runs.
- **Interactive Streamlit Sidebar Integration**:
  - Dedicated "Deliver Weekly Insights" drawer in `app.py`:
    - Email recipient input with address syntax validation.
    - Customizable email subject header.
    - One-click "Send Email Report" action button.
    - Progressive disclosure preview drawer displaying generated report text.
    - Instant "Download Report (TXT)" alternative for offline distribution.
- **Automated Validation Suite (`insight_delivery_runner.py`)**:
  - Validates 3-part report completeness, simulated dispatch, and exception resilience against bad credentials.

### Running Insight Delivery Tests & Reports
```bash
# Run standalone Insight Delivery validation suite
python insight_delivery_runner.py

# Launch interactive Streamlit application with email delivery
streamlit run app.py

# Run full project analytics suite (all modules)
python main.py
```

### Video Guide & Documentation
- Comprehensive engineering guide: [`INSIGHT_DELIVERY_GUIDE.md`](./INSIGHT_DELIVERY_GUIDE.md)
- Step-by-step video script: [`VIDEO_SCRIPT_INSIGHT_DELIVERY.md`](./VIDEO_SCRIPT_INSIGHT_DELIVERY.md)









