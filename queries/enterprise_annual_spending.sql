-- queries/enterprise_annual_spending.sql
-- Answers the core architectural question:
-- "Show Enterprise customers with >$10k annual spending:
--  - Filter customer_type = 'Enterprise' BEFORE grouping in WHERE (row-level attribute)
--  - Filter SUM(amount) > 10000 AFTER grouping in HAVING (aggregate metric)

SELECT 
    c.customer_id,
    c.name as customer_name,
    c.customer_type,
    SUM(t.amount) as annual_spending,
    COUNT(*) as completed_transactions
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE c.customer_type = 'Enterprise'               -- WHERE: filters row attributes BEFORE grouping
  AND t.transaction_date >= DATE '2024-01-01'       -- WHERE: restricts analysis date range
  AND t.transaction_status = 'completed'            -- WHERE: removes pending/failed records
  AND t.amount > 0                                  -- WHERE: eliminates refunds/zero amounts
GROUP BY c.customer_id, c.name, c.customer_type
HAVING SUM(t.amount) > 10000                        -- HAVING: filters aggregate results AFTER grouping
ORDER BY annual_spending DESC;
