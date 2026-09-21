-- queries/where_filtering.sql
-- Filter data quality issues BEFORE grouping
SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'  -- Date range filter: restricts to current fiscal year
  AND amount > 0                              -- Remove refunds: ensures negative charges don't distort gross volume
  AND transaction_status = 'completed'        -- Valid transactions only: excludes abandoned, pending, or failed payments
GROUP BY customer_id
ORDER BY annual_revenue DESC;
