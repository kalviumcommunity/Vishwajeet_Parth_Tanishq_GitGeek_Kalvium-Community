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
│   └── styles.css
├── queries/
│   ├── monthly_active_users.sql
│   ├── revenue_by_segment.sql
│   ├── conversion_funnel.sql
│   ├── retention_cohort.sql
│   └── rolling_7day_active_users.sql
├── data/
│   ├── demo.json
│   └── business_metrics.duckdb
├── init_db.py
├── metrics_runner.py
├── main.py
├── requirements.txt
├── VIDEO_SCRIPT.md
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


