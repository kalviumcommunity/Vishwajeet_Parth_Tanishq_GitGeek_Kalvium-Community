-- queries/optimization_cte_structuring.sql
-- Module: Query Optimization - CTEs: Structuring Complex Queries for Readability
-- Transforms deeply nested spaghetti subqueries into named logical steps

WITH recent_transactions AS (
    -- Step 1: Filter to relevant recent timeframe (2024 onwards) and project needed columns
    SELECT 
        customer_id, 
        amount, 
        transaction_date 
    FROM warehouse_transactions 
    WHERE transaction_date >= DATE '2024-01-01'
),
customer_summary AS (
    -- Step 2: Aggregate metric summaries per customer
    SELECT 
        customer_id, 
        COUNT(*) as transaction_count, 
        ROUND(SUM(amount), 2) as total_spent 
    FROM recent_transactions 
    GROUP BY customer_id
)
-- Step 3: Join to dimension table and apply high-value customer business filter
SELECT 
    cs.customer_id, 
    c.customer_name, 
    c.country,
    c.tier,
    cs.transaction_count, 
    cs.total_spent 
FROM customer_summary cs 
JOIN customers_expanded c ON cs.customer_id = c.customer_id 
WHERE cs.total_spent > 3000
ORDER BY cs.total_spent DESC;
