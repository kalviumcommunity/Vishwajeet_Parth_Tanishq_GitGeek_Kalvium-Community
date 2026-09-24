-- queries/optimization_benchmark_comparison.sql
-- Module: Query Optimization - Comprehensive Analytical Dashboard Query
-- Combines Explicit Columns + Early Filter Pushdown + CTE Architecture

WITH filtered_orders AS (
    -- Early filter: Prune 80% of rows (only completed transactions from 2024)
    -- Column projection: Only 4 columns out of 25 wide warehouse columns
    SELECT 
        transaction_id,
        customer_id,
        amount,
        channel
    FROM warehouse_transactions
    WHERE transaction_year = 2024
      AND status = 'completed'
),
customer_metrics AS (
    -- Aggregate by customer and sales channel
    SELECT 
        customer_id,
        channel,
        COUNT(transaction_id) as orders_count,
        ROUND(SUM(amount), 2) as channel_revenue,
        ROUND(AVG(amount), 2) as avg_order_value
    FROM filtered_orders
    GROUP BY customer_id, channel
)
-- Final join with dimension table for reporting
SELECT 
    cm.customer_id,
    c.customer_name,
    c.region,
    c.tier,
    cm.channel,
    cm.orders_count,
    cm.channel_revenue,
    cm.avg_order_value
FROM customer_metrics cm
JOIN customers_expanded c ON cm.customer_id = c.customer_id
WHERE cm.channel_revenue >= 2000
ORDER BY cm.channel_revenue DESC;
