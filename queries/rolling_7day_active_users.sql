-- queries/rolling_7day_active_users.sql
-- Rolling 7-day active users: computes distinct active customers over a trailing 7-day sliding window
WITH daily_activity AS (
    SELECT DISTINCT
        DATE_TRUNC('day', transaction_date)::DATE as activity_date,
        customer_id
    FROM transactions
)
SELECT 
    d1.activity_date,
    COUNT(DISTINCT d2.customer_id) as rolling_7d_active_users
FROM daily_activity d1
JOIN daily_activity d2 
  ON d2.activity_date BETWEEN d1.activity_date - INTERVAL '6 days' AND d1.activity_date
GROUP BY d1.activity_date
ORDER BY d1.activity_date DESC;
