-- queries/percentage_share.sql
-- Bonus Query: Computes percentage share of total revenue within groups
WITH segment_totals AS (
    SELECT 
        c.customer_type,
        c.industry,
        SUM(t.amount) as segment_revenue,
        COUNT(DISTINCT t.customer_id) as customer_count
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    WHERE t.transaction_date >= DATE '2024-01-01'
      AND t.transaction_status = 'completed'
      AND t.amount > 0
    GROUP BY c.customer_type, c.industry
)
SELECT 
    customer_type,
    industry,
    customer_count,
    segment_revenue,
    SUM(segment_revenue) OVER () as total_company_revenue,
    ROUND(100.0 * segment_revenue / SUM(segment_revenue) OVER (), 2) as pct_of_total_revenue
FROM segment_totals
ORDER BY segment_revenue DESC;
