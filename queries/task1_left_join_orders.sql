-- queries/task1_left_join_orders.sql
-- Task 1: All customers with their orders (retains customers without orders, expands for multi-order customers)
SELECT 
    c.customer_id, 
    c.customer_type, 
    COUNT(DISTINCT o.order_id) as order_count, 
    SUM(o.order_amount) as total_spent 
FROM customers c 
LEFT JOIN orders o ON c.customer_id = o.customer_id 
GROUP BY c.customer_id, c.customer_type 
ORDER BY total_spent DESC NULLS LAST;
