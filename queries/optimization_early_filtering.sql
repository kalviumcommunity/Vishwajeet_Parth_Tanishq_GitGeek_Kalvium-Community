-- queries/optimization_early_filtering.sql
-- Module: Query Optimization - Early Filtering: Apply WHERE Before JOIN
-- Inefficient: Joins entire 50k transactions table before filtering
-- Optimized: Filters 10k rows in derived subquery before joining to customers

SELECT 
    t.transaction_id,
    t.amount,
    c.customer_name,
    c.country
FROM (
    SELECT 
        transaction_id, 
        customer_id, 
        amount 
    FROM warehouse_transactions 
    WHERE transaction_year = 2024
) t
JOIN customers_expanded c ON t.customer_id = c.customer_id;
