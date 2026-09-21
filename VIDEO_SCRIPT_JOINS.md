# Video Presentation Script: SQL Joins & Multi-Table Analysis
## Module 2.40: Mastering Relational Joins & Data Lineage

> **Submission Video Checklist**:
> - **Webcam**: Ensure your face is **clearly visible** throughout the recording.
> - **Screen Share**: Display the SQL queries in `queries/`, the documentation `JOIN_STRATEGY_DOCUMENTATION.md`, and the terminal running `python joins_runner.py`.
> - **Google Drive**: Sharing permission must be set to **"Anyone with the link can view"**.
> - **Incognito Check**: Test the Drive link in an Incognito / Private window before submitting.
> - **Target Duration**: **3 to 5 minutes**.

---

## 🎬 Word-for-Word Speaking Script

### 1. Introduction & The Core Problem
**[On Screen: Display `JOIN_STRATEGY_DOCUMENTATION.md` or the database schema]**

> *"Hello everyone! My name is [Your Name], and today I am presenting Assignment 2.40: SQL Joins and Multi-Table Analysis.*
>
> *In relational database analysis, combining data across tables is daily work. But every analyst has encountered the mystery: you join 1,000 customers to 5,000 orders and end up with 5,500 rows. Why 5,500? Did the join create accidental duplicate rows? Are customers missing orders? Or did orders lack matching customers?*
>
> *Without systematic join validation, data corruption goes undetected into production dashboards. In this project, we implement three core join types, validate row counts before and after merging, detect unmatched and orphaned keys, and audit multi-table lineage."*

---

### 2. INNER vs. LEFT vs. FULL OUTER JOIN (Concrete Examples)
**[On Screen: Highlight queries `task3_inner_join.sql`, `task3_left_join.sql`, and `task3_full_outer_join.sql`]**

> *"Let's examine the three primary join types using our dataset:*
>
> 1. ***INNER JOIN***: *Keeps only matched rows where keys exist in both tables. In our data, `INNER JOIN` produces **464 rows** — representing only customers who have placed valid orders.*
> 2. ***LEFT JOIN***: *Keeps all rows from the left table (`customers`), matching order details where available and filling with `NULL` where absent. This yields **504 rows** (the 464 matched orders plus 40 inactive customers).*
> 3. ***FULL OUTER JOIN***: *Preserves every row from both tables. It yields **519 rows**.*
>
> *Notice the exact mathematical identity:*
> $$\text{FULL OUTER (519)} = \text{INNER (464)} + \text{Unmatched Customers (40)} + \text{Orphaned Orders (15)}$$
> *Every single record is accounted for without silent loss."*

---

### 3. Importance of Row Count Validation (Preventing Silent Errors)
**[On Screen: Open `queries/task1_left_join_orders.sql` and `queries/join_row_count_validation.sql`]**

> *"Why is row count validation so essential?*
>
> *When performing a 1-to-many join, row counts expand. In Task 1, joining 220 customers to orders expands to 504 rows before aggregation — a 129% increase because active customers placed 2 to 3 orders each.*
>
> *If an analyst mistakenly assumed a 1-to-1 relationship and calculated average spend across raw joined rows without grouping, the average would be severely distorted by multi-order customers!*
>
> *Row count validation before and after joining confirms whether multiplication is expected business reality or accidental Cartesian fan-out."*

---

### 4. Detecting Unmatched Keys & Orphaned Records
**[On Screen: Open `queries/task2_unmatched_customers.sql` and `queries/task2_orphaned_orders.sql`]**

> *"How do we detect broken data relationships? We use `LEFT JOIN` combined with `WHERE ... IS NULL`:*
>
> 1. *In `task2_unmatched_customers.sql`, we query `WHERE o.order_id IS NULL` to find customers who never made a purchase. We found 40 inactive customers (18.2% of our user base) — perfect for targeted reactivation campaigns.*
> 2. *In `task2_orphaned_orders.sql`, we query `orders LEFT JOIN customers WHERE c.customer_id IS NULL`. We uncovered 15 orphaned orders referencing customer ID 9999.*
>
> *Orphaned records signal critical data pipeline bugs — like deleted user accounts or unlinked guest checkouts — that must be caught before financial reporting."*

---

### 5. Multi-Key Joining & Join Order Impact
**[On Screen: Open `queries/multi_key_join.sql` and `queries/task4_multi_table_join.sql`]**

> *"Two advanced considerations are critical in production:*
>
> 1. ***Multi-Key Joining***: *When joining on non-unique keys, a single key join creates a Cartesian product explosion. In `queries/multi_key_join.sql`, we join on composite keys: `c.customer_id = o.customer_id AND c.customer_type = o.customer_type`, guaranteeing strict 1-to-1 key alignment.*
> 2. ***Join Order Impact***: *In `queries/task4_multi_table_join.sql`, we chain 4 tables: `customers -> orders -> order_items -> products`. We place `customers` on the left and chain `LEFT JOIN`s throughout. If you accidentally place an `INNER JOIN` in the middle of a `LEFT JOIN` pipeline, any missing child record will silently drop the parent customer! Maintaining `LEFT JOIN` preserves full entity lineage."*

---

### 6. Live Execution & Verification
**[On Screen: Switch to terminal and run `python joins_runner.py`]**

> *"Now let's run our automated validation script `python joins_runner.py`.*
>
> *[Run command in terminal]:*
> ```bash
> python joins_runner.py
> ```
>
> *As you can see:*
> - *Task 1 confirms row count expansion from 220 customers to 504 raw joined rows.*
> - *Task 2 detects 40 customers with no orders and 15 orphaned orders.*
> - *Task 3 confirms our row count relationships: INNER (464) <= LEFT (504) <= FULL (519).*
> - *Task 4 validates line totals against direct order item aggregates with exactly $0.00 difference!*
> - *And Task 5 outputs our complete join architecture strategy.*
>
> *All tests pass with zero errors! Thank you!"*
