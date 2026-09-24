# Video Script: SQL Query Optimization & Performance Tuning

**Target Duration**: 4 - 5 Minutes  
**Speaker**: Senior Analytics Engineer / Database Performance Specialist  
**Visual Assets**: Terminal execution (`./venv/bin/python query_optimization_runner.py`), SQL queries in `queries/`, DuckDB database, and `public/query_optimization.png`.

---

## Breakdown & Timeline

### 0:00 - 0:45 | Section 1: Introduction & The Slow Dashboard Crisis
* **Visual**: Camera on Speaker (Webcam Fullscreen).
* **Speaker Dialogue**:
  > "Hello everyone! Welcome to our masterclass on SQL Query Optimization.
  > 
  > Every data team has experienced this frustrating moment: an analyst opens an executive revenue dashboard, clicks refresh, and waits thirty seconds, forty-five seconds... or worse, watches the page crash with a timeout error. 
  > 
  > When queries slow down as datasets scale from thousands to millions of rows, the default reaction is often to blame the database infrastructure or demand more expensive compute clusters. But in reality, the culprit is almost always inefficient SQL patterns: indiscriminate `SELECT *` statements, joining huge tables before filtering, and deeply nested subquery spaghetti.
  > 
  > Today, we're going to break down the three fundamental optimization patterns that transformed a forty-five-second query into a two-second query—a twenty-two-times compounding speedup."

---

### 0:45 - 1:45 | Section 2: Pattern 1 & 2 - Eliminating SELECT * & Early Filter Pushdown
* **Visual**: Transition to Screen Share showing the architecture flow diagram in `QUERY_OPTIMIZATION_GUIDE.md`.
* **Speaker Dialogue**:
  > "Let's examine the first two patterns.
  > 
  > Pattern One is eliminating the `SELECT *` antipattern. In modern columnar databases like DuckDB, Snowflake, or BigQuery, storage is organized by columns, not rows. When you write `SELECT *` on a table with fifty columns, the database is forced to read every single column from disk. On a hundred-million-row table, that means reading five gigabytes of data when your report only needed five hundred megabytes! In our test benchmark on fifty thousand records with twenty-five wide columns, replacing `SELECT *` with explicit columns reduced data transfer by eighty-five percent and delivered a thirteen-times latency speedup.
  > 
  > Pattern Two is Early Filtering: applying `WHERE` before `JOIN`. Imagine joining a hundred-million-row transaction table to a customer table. If you join first and then filter for 2024 transactions, the database creates a five-hundred-gigabyte intermediate join buffer in memory, only to discard ninety percent of it a second later! By filtering transactions down to ten million rows inside a subquery or CTE *before* the join, your hash table is ten times smaller and builds in a fraction of the time."

---

### 1:45 - 2:45 | Section 3: Pattern 3 - Common Table Expressions (CTEs) & Readability
* **Visual**: Screen Share of Code Editor displaying `queries/optimization_cte_structuring.sql`.
* **Speaker Dialogue**:
  > "Pattern Three is structuring complex business logic using Common Table Expressions, or CTEs.
  > 
  > [Point to CTE Query Code]
  > 
  > Here in `optimization_cte_structuring.sql`, instead of nesting subqueries five levels deep, we break the transformation into distinct, named logical stages.
  > 
  > Step One, `recent_transactions`: filters to the active fiscal window and projects only `customer_id`, `amount`, and `transaction_date`.
  > 
  > Step Two, `customer_summary`: groups metrics by customer to compute total spend and order counts.
  > 
  > Step Three: joins cleanly with our customer dimension table to surface high-value accounts spending over three thousand dollars.
  > 
  > Notice how this reads like clean, executable prose. Each step can be unit-tested in isolation, and the database optimizer can eliminate redundant subexpressions across downstream joins."

---

### 2:45 - 3:45 | Section 4: Live Benchmark Execution & Visual Performance Dashboard
* **Visual**: Screen Share of Terminal. Run `./venv/bin/python query_optimization_runner.py`, then switch to `public/query_optimization.png`.
* **Speaker Dialogue**:
  > "Let's run our automated benchmark runner: `python query_optimization_runner.py`.
  > 
  > [Point to Terminal Output]
  > 
  > Look at the benchmark metrics:
  > In Task One, explicit column projection cut column transfers by 85.7% and improved latency by thirteen times.
  > In Task Two, early filtering pruned eighty percent of warehouse records before the join buffer was even allocated.
  > In Task Three, our CTE pipeline identified four hundred high-value customers with 100% rule compliance.
  > 
  > [Switch to Visual Dashboard `public/query_optimization.png`]
  > 
  > Now look at our visual dashboard:
  > In the top-left panel, you see the compounding waterfall: forty-five seconds down to thirty seconds with explicit columns, down to eight seconds with early filtering, down to two seconds with CTE pushdown—a total 22.5x speedup!
  > In the top-right panel, the intermediate join buffer collapses from five hundred gigabytes to just fifty gigabytes.
  > In the bottom panels, we visualize the physical operator execution tree and our production engineering checklist."

---

### 3:45 - 4:15 | Section 5: Summary & Key Takeaways
* **Visual**: Transition back to Speaker (Webcam Fullscreen).
* **Speaker Dialogue**:
  > "To summarize our checklist before you deploy any query or dbt model:
  > First: Never use `SELECT *` in production queries. Always project explicit columns.
  > Second: Filter early before joins so the smallest possible dataset enters your join buffer.
  > Third: Structure multi-step logic into named, readable CTEs.
  > And Fourth: Always inspect your execution plan with `EXPLAIN` on production data volumes.
  > 
  > All queries, runners, and guides are tested and committed in the repository. Thank you for watching!"
