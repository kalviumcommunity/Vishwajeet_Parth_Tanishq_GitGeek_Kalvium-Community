-- queries/multi_key_join.sql
-- Bonus Query: Demonstrating Multi-Key Join to prevent Cartesian explosion when single key is non-unique
SELECT 
    c.customer_id,
    c.customer_type,
    o.order_id,
    o.order_date,
    o.order_amount
FROM customers c
INNER JOIN orders o 
    ON c.customer_id = o.customer_id 
   AND c.customer_type = o.customer_type
WHERE o.order_amount > 1000
ORDER BY o.order_amount DESC;
