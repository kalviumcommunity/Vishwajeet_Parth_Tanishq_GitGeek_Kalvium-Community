-- queries/task2_orphaned_orders.sql
-- Task 2B: Orders with NO matching customer (identifies orphaned records requiring data investigation)
SELECT 
    o.order_id, 
    o.customer_id, 
    o.order_date 
FROM orders o 
LEFT JOIN customers c ON o.customer_id = c.customer_id 
WHERE c.customer_id IS NULL 
ORDER BY o.order_date;
