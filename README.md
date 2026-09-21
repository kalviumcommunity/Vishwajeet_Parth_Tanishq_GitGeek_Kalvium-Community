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


