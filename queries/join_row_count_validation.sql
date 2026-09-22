-- queries/join_row_count_validation.sql
-- Bonus Query: Validates row counts and distinct keys across source tables and the joined result
SELECT 
    'customers' as entity, 
    COUNT(DISTINCT customer_id) as distinct_keys, 
    COUNT(*) as total_rows 
FROM customers 
UNION ALL 
SELECT 
    'orders', 
    COUNT(DISTINCT customer_id), 
    COUNT(*) 
FROM orders 
UNION ALL 
SELECT 
    'joined (customers LEFT JOIN orders)', 
    COUNT(DISTINCT c.customer_id), 
    COUNT(*) 
FROM customers c 
LEFT JOIN orders o ON c.customer_id = o.customer_id;
