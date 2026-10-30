
-- Q2: Customer Transaction Analysis
-- Business question:
-- Which customers generate the highest transaction activity?

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.transaction_amount) AS total_transaction_value,
    AVG(t.transaction_amount) AS average_transaction_value
FROM customers c
LEFT JOIN accounts a
    ON c.customer_id = a.customer_id
LEFT JOIN transactions t
    ON a.account_id = t.account_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.city,
    c.state
ORDER BY
    total_transaction_value DESC;
