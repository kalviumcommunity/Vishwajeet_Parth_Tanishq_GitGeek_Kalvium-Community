-- queries/optimization_select_star_antipattern.sql
-- Module: Query Optimization - Eliminating SELECT * Antipattern
-- Inefficient vs Explicit Column Selection Comparison

-- [INEFFICIENT PATTERN]:
-- SELECT * 
-- FROM warehouse_transactions t 
-- JOIN customers_expanded c ON t.customer_id = c.customer_id 
-- WHERE t.transaction_year = 2024;
-- Cost: Reads all 35 columns (JSON payloads, addresses, user agents, notes)

-- [OPTIMIZED PATTERN]:
-- Explicit column selection: reads only the 5 required analytical columns
SELECT 
    t.transaction_id,
    t.customer_id,
    t.amount,
    c.customer_name,
    c.country
FROM warehouse_transactions t
JOIN customers_expanded c ON t.customer_id = c.customer_id
WHERE t.transaction_year = 2024;
