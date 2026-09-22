-- queries/task3_full_outer_join.sql
-- Task 3C: FULL OUTER JOIN (keeps all records from both sides, matching where keys align)
SELECT 
    c.customer_id, 
    o.order_id, 
    o.order_amount 
FROM customers c 
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
