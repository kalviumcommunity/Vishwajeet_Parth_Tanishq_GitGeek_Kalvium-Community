-- queries/task3_left_join.sql
-- Task 3B: LEFT JOIN (keeps all customers from left table, matches orders from right where present)
SELECT 
    c.customer_id, 
    o.order_id, 
    o.order_amount 
FROM customers c 
LEFT JOIN orders o ON c.customer_id = o.customer_id;
