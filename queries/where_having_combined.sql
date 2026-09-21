-- queries/where_having_combined.sql
-- Real-world: filter data quality AND aggregate thresholds
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'      -- WHERE: restricts to valid transaction timeframe
  AND t.transaction_status = 'completed'           -- WHERE: data quality check (completed only)
  AND t.amount > 0                                 -- WHERE: logical validity check (positive order amounts)
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100       -- HAVING: segment volume threshold (statistically viable segments)
  AND SUM(t.amount) > 100000                       -- HAVING: business revenue threshold ($100k+ total spend)
ORDER BY segment_revenue DESC;
