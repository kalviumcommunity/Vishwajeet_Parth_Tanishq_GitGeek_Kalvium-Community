# Video Presentation Script & Guide
## Assignment 2.38: SQL Business Metrics Query Design

> **Important Reminders for Submission**:
> - Ensure your face is **clearly visible** on webcam throughout the video.
> - Share your screen showing the SQL query files in `queries/`, the database schema, and `python metrics_runner.py` running in your terminal.
> - Upload the video to **Google Drive** with sharing set to **"Anyone with the link can view"**, and verify the link in an Incognito/Private window before submitting.
> - Recommended length: **3 to 5 minutes**.

---

## 🎬 Section-by-Section Speaking Script

### 1. Introduction & The Core Problem
**[What to show on screen]**: The project folder structure with the `queries/` directory, or the problem statement.

> *"Hello everyone! My name is [Your Name], and today I am presenting Assignment 2.38: SQL Business Metrics Query Design.*
>
> *In many organizations, business metrics like Monthly Revenue, Active Users, and Conversion Rates are computed independently across different Jupyter notebooks and Python scripts. Sales might calculate revenue based on paid invoices, Finance counts billed contracts, and Product counts raw transactions. The result is inconsistent KPIs, conflicting board meeting slides, and wasted time reconciling numbers.*
>
> *The solution is defining business metrics **once** in centralized, version-controlled SQL files. This establishes a **Single Source of Truth** that every analyst, dashboard, and backend service can reuse."*

---

### 2. Why SQL Metrics Beat Python Scripts (Reusability & Consistency)
**[What to show on screen]**: Open `queries/monthly_active_users.sql` and `metrics_runner.py`.

> *"Why do centralized SQL metrics beat Python script calculations?*
> 1. ***Consistency & Centralized Truth***: *When logic lives in SQL files (like `queries/monthly_active_users.sql`), every team runs the exact same query against the database engine. If a metric definition changes, updating that one SQL file updates all downstream pipelines.*
> 2. ***Database-Level Performance & Pushdown***: *Database engines use query planners, indexes, and distributed execution to aggregate millions of rows directly at the data layer, avoiding the network overhead of transferring raw rows into memory.*
> 3. ***Portability & Language Agnostic***: *SQL files can be consumed by Python via pandas, Node.js, BI tools like Tableau and Metabase, or dbt without rewriting the logic."*

---

### 3. CASE WHEN & FILTER in Aggregation (Conditional Counting)
**[What to show on screen]**: Highlight lines in `queries/monthly_active_users.sql` and `queries/conversion_funnel.sql`.

> *"Let's examine how we compute segmented and conditional metrics in a single pass using conditional aggregation.*
>
> *In `queries/monthly_active_users.sql`, we compute total active users alongside Enterprise and SMB breakdowns using the standard SQL `FILTER` clause:*
> ```sql
> COUNT(DISTINCT customer_id) FILTER (WHERE customer_type = 'Enterprise') AS enterprise_users,
> COUNT(DISTINCT customer_id) FILTER (WHERE customer_type = 'SMB') AS smb_users
> ```
>
> *Similarly, in `queries/conversion_funnel.sql`, we compute daily signup conversion rates:*
> ```sql
> COUNT(*) FILTER (WHERE u.email_verified_at IS NOT NULL) AS email_verified,
> COUNT(*) FILTER (WHERE u.first_purchase_at IS NOT NULL) AS first_purchase,
> ROUND(100.0 * COUNT(*) FILTER (WHERE u.first_purchase_at IS NOT NULL) / COUNT(*), 1) AS conversion_pct
> ```
> *In databases that don't support `FILTER`, we achieve the exact same result using `CASE WHEN`:*
> ```sql
> COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END)
> ```
> *Because SQL evaluates `NULL` values as non-countable in `COUNT()`, this enables multi-step funnel tracking and segmented breakdowns within one single scan of the table."*

---

### 4. Retention Cohort Definition
**[What to show on screen]**: Open `queries/retention_cohort.sql`.

> *"Next, let's look at Retention Cohorts in SQL. A cohort analysis groups users by their signup or initial purchase date and tracks their return activity over subsequent months.*
>
> *In `queries/retention_cohort.sql`, we use Common Table Expressions (CTEs):*
> ```sql
> WITH first_purchase AS (
>     SELECT customer_id, DATE_TRUNC('month', MIN(transaction_date))::DATE AS cohort_month
>     FROM transactions
>     GROUP BY customer_id
> ),
> monthly_activity AS (
>     SELECT t.customer_id, fp.cohort_month, DATE_TRUNC('month', t.transaction_date)::DATE AS activity_month
>     FROM transactions t
>     JOIN first_purchase fp ON t.customer_id = fp.customer_id
> )
> SELECT cohort_month, activity_month, COUNT(DISTINCT customer_id) AS active_customers
> FROM monthly_activity
> GROUP BY cohort_month, activity_month
> ORDER BY cohort_month, activity_month;
> ```
> *The first CTE identifies each customer's acquisition cohort month. The second CTE joins back to all transactions to determine active months. Finally, grouping by `cohort_month` and `activity_month` produces the retention matrix, showing whether users acquired in March continue to return in April, May, and beyond."*

---

### 5. Rolling 7-Day Active Users (Time-Window Aggregation)
**[What to show on screen]**: Open `queries/rolling_7day_active_users.sql`.

> *"For operational health, teams frequently monitor Rolling 7-day Active Users. Rather than reporting disjoint calendar weeks, a rolling 7-day metric computes active users over any trailing 7-day sliding window.*
>
> *In `queries/rolling_7day_active_users.sql`, we perform a time-window self-join:*
> ```sql
> WITH daily_activity AS (
>     SELECT DISTINCT DATE_TRUNC('day', transaction_date)::DATE AS activity_date, customer_id
>     FROM transactions
> )
> SELECT d1.activity_date, COUNT(DISTINCT d2.customer_id) AS rolling_7d_active_users
> FROM daily_activity d1
> JOIN daily_activity d2 
>   ON d2.activity_date BETWEEN d1.activity_date - INTERVAL '6 days' AND d1.activity_date
> GROUP BY d1.activity_date
> ORDER BY d1.activity_date DESC;
> ```
> *For every calendar date `d1`, we match all active users in the prior 6 days plus the current day (`d2`), taking the `COUNT(DISTINCT)` to produce a smooth, trailing 7-day metric."*

---

### 6. Adding New Metrics Without Breaking Existing Consumers
**[What to show on screen]**: Highlight `queries/revenue_by_segment.sql`.

> *"How do we add new metrics as business requirements evolve without breaking downstream applications?*
> 1. ***Additive Column Design***: *Add new metric calculations as additional columns with descriptive aliases at the end of the `SELECT` list. Existing consumers selecting specific columns will remain completely unaffected.*
> 2. ***Semantic Aliasing***: *Always use explicit, stable column aliases (such as `monthly_revenue` or `avg_order_value`) rather than raw expression names.*
> 3. ***Modularity & SQL Views***: *Keep each metric domain in its own dedicated `.sql` file, or encapsulate them into database views. When complex logic updates internally, external consumer APIs and notebooks reading the query or view remain stable.*
> 4. ***Automated Validation Tests***: *Maintain an automated validation script like `validate_metrics()` in `metrics_runner.py` that verifies null counts, numeric bounds, and logical consistency whenever queries are updated."*

---

### 7. Execution & Validation Demonstration
**[What to show on screen]**: Run `python metrics_runner.py` in your terminal.

> *"Now, let's run the Python execution and validation script.*
>
> *[Run command]: `python metrics_runner.py`*
>
> *As you can see:*
> - *`monthly_active_users` loaded and printed without nulls.*
> - *`revenue_by_segment` successfully computed order count, monthly revenue, average order value, and revenue per customer.*
> - *`conversion_funnel` computed daily signup, verification, first purchase, and conversion percentages.*
> - *And `validate_metrics()` completed with `✓ All metrics validated`!*
>
> *Thank you!"*
