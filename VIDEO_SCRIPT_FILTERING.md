# Video Presentation Script: SQL Filtering, Grouping & Aggregation
## Topic: WHERE vs. HAVING Architecture & Query Design

> **Submission Video Checklist**:
> - **Webcam**: Ensure your face is **clearly visible** throughout the recording.
> - **Screen Share**: Display the SQL queries in `queries/`, the architecture guide `WHERE_VS_HAVING_GUIDE.md`, and the terminal running `python run_filtering_analysis.py`.
> - **Google Drive**: Sharing permission must be set to **"Anyone with the link can view"**.
> - **Incognito Check**: Test the Drive link in an Incognito / Private window before submitting.
> - **Target Duration**: **3 to 5 minutes**.

---

## 🎬 Word-for-Word Speaking Script

### 1. Introduction & The Core Question
**[On Screen: Display `queries/enterprise_annual_spending.sql` or `WHERE_VS_HAVING_GUIDE.md`]**

> *"Hello everyone! My name is [Your Name], and today I am presenting my submission for the SQL Filtering, Grouping & Aggregation assignment.*
>
> *Let's begin with the central question: **'Show Enterprise customers with greater than $10,000 annual spending — do you filter before or after grouping? Do you use WHERE or HAVING?'**
>
> *The answer requires understanding the separation of concerns in SQL:*
> 1. *We filter `customer_type = 'Enterprise'` **BEFORE** grouping using the **`WHERE`** clause. Why? Because `customer_type` is an attribute of the individual customer record. We want to eliminate non-enterprise rows as early as possible.*
> 2. *We filter `SUM(amount) > 10000` **AFTER** grouping using the **`HAVING`** clause. Why? Because annual spending is an **aggregate metric** across multiple purchases. That aggregate does not even exist until the rows are grouped by customer.*
>
> *This principle ensures both logical correctness and maximum query performance."*

---

### 2. WHERE vs. HAVING Distinction (When Each Applies)
**[On Screen: Open `queries/where_filtering.sql` and `queries/having_filtering.sql`]**

> *"Let's clarify the fundamental difference between `WHERE` and `HAVING`.*
>
> *The **`WHERE` clause** filters individual table rows **before** any aggregation takes place. In `queries/where_filtering.sql`, we use `WHERE` for data hygiene and scoping:*
> - *We filter `transaction_date >= DATE '2024-01-01'` to define our fiscal period.*
> - *We filter `amount > 0` to discard refunds and negative adjustments.*
> - *We filter `transaction_status = 'completed'` to exclude pending or failed payments.*
>
> *In contrast, the **`HAVING` clause** filters **groups** of rows **after** aggregation has occurred. In `queries/having_filtering.sql`:*
> - *`HAVING SUM(amount) > 10000` evaluates the total spend of the group.*
> - *`HAVING COUNT(*) >= 5` ensures we only select repeat customers with 5 or more transactions.*
>
> *You can never put an aggregate like `SUM()` in a `WHERE` clause, and you should never filter unaggregated row attributes in `HAVING` when they can be filtered in `WHERE`."*

---

### 3. GROUP BY Semantics (Changing the Aggregation Unit)
**[On Screen: Open `queries/group_by_aggregation.sql`]**

> *"Next, let's explore **GROUP BY semantics**.*
>
> *The `GROUP BY` clause fundamentally alters the granularity of your query. Before grouping, every row represents an individual transaction. After grouping by `customer_type` and `DATE_TRUNC('month', transaction_date)`, each output row represents a **distinct customer segment within a calendar month**.*
>
> *In `queries/group_by_aggregation.sql`, we apply multiple aggregate functions to this new unit of analysis:*
> - *`COUNT(DISTINCT t.customer_id)` calculates unique customer reach.*
> - *`COUNT(*)` measures total transaction frequency.*
> - *`SUM(t.amount)` computes monthly volume.*
> - *`AVG(t.amount)` calculates the average basket size.*
>
> *The SQL rule to remember: any column in the `SELECT` list that is not wrapped in an aggregate function **must** appear in the `GROUP BY` clause."*

---

### 4. Query Optimization: Why WHERE Before GROUP BY is Faster
**[On Screen: Highlight the Execution Flow diagram in `WHERE_VS_HAVING_GUIDE.md`]**

> *"From a database performance and engineering perspective, why is filtering in `WHERE` before `GROUP BY` so critical?*
>
> *Imagine a database containing 1 million transactions:*
> - *If we filter in `WHERE`, the engine uses indexes to instantly drop 90% of the rows. The `GROUP BY` engine only has to hash and sort 100,000 rows in memory.*
> - *If someone mistakenly attempted to filter row conditions in `HAVING` or didn't filter early, the engine would have to allocate memory and hash all 1 million rows before discarding them.*
>
> *Early filtering with `WHERE` reduces memory footprint, avoids disk spillover, and speeds up query execution by orders of magnitude."*

---

### 5. Percentage Share Computation (Within Groups)
**[On Screen: Open `queries/percentage_share.sql`]**

> *"Finally, let's examine **Percentage Share Computation**, which is critical for business reporting.*
>
> *In `queries/percentage_share.sql`, we compute each industry segment's revenue and its percentage contribution to total company revenue using an analytic window function:*
> ```sql
> WITH segment_totals AS (
>     SELECT c.customer_type, c.industry, SUM(t.amount) as segment_revenue
>     FROM transactions t
>     JOIN customers c ON t.customer_id = c.customer_id
>     WHERE t.transaction_date >= DATE '2024-01-01'
>       AND t.transaction_status = 'completed'
>       AND t.amount > 0
>     GROUP BY c.customer_type, c.industry
> )
> SELECT 
>     customer_type,
>     industry,
>     segment_revenue,
>     SUM(segment_revenue) OVER () as total_company_revenue,
>     ROUND(100.0 * segment_revenue / SUM(segment_revenue) OVER (), 2) as pct_of_total_revenue
> FROM segment_totals
> ORDER BY segment_revenue DESC;
> ```
> *The `SUM(segment_revenue) OVER ()` window function aggregates total revenue across all segments without collapsing individual rows, allowing us to compute percentage share cleanly in a single pass."*

---

### 6. Live Execution & Verification
**[On Screen: Switch to terminal and run `python run_filtering_analysis.py`]**

> *"Now let's execute our automated validation runner to test all queries against our live database.*
>
> *[Run command in terminal]:*
> ```bash
> python run_filtering_analysis.py
> ```
>
> *As shown in the output:*
> - *The Core Question returns 104 qualifying Enterprise customers with spend >$10k.*
> - *Task 1 successfully filters completed transactions with 0 nulls.*
> - *Task 2 produces multi-dimensional monthly segment aggregates.*
> - *Task 3 enforces both spend and transaction frequency thresholds in `HAVING`.*
> - *Task 4 executes combined row-quality and segment-threshold filters.*
> - *Task 5 ranks top segments using `RANK()`.*
> - *And our Percentage Share bonus query calculates total contribution summing to 100%.*
>
> *All test assertions have passed with zero errors! Thank you!"*
