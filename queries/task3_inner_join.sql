-- queries/task3_inner_join.sql
-- Task 3A: INNER JOIN (keeps matched rows only: customers who have placed orders)
SELECT 
    c.customer_id, 
    o.order_id, 
    o.order_amount 
FROM customers c 
INNER JOIN orders o ON c.customer_id = o.customer_id;
