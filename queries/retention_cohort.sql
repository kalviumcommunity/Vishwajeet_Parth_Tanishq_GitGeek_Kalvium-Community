-- queries/retention_cohort.sql
-- Retention cohort definition: groups customers by initial purchase month and tracks return activity over subsequent months
WITH first_purchase AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(transaction_date))::DATE as cohort_month
    FROM transactions
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT 
        t.customer_id,
        fp.cohort_month,
        DATE_TRUNC('month', t.transaction_date)::DATE as activity_month
    FROM transactions t
    JOIN first_purchase fp ON t.customer_id = fp.customer_id
)
SELECT 
    cohort_month,
    activity_month,
    COUNT(DISTINCT customer_id) as active_customers
FROM monthly_activity
GROUP BY cohort_month, activity_month
ORDER BY cohort_month ASC, activity_month ASC;
