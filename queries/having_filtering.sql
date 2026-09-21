-- queries/having_filtering.sql
-- Filter GROUPS after aggregation
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 10000                      -- HAVING filters groups: requires aggregate annual spend > $10,000
  AND COUNT(*) >= 5                             -- Only customers with 5+ repeat purchases
ORDER BY annual_revenue DESC;
