
-- Q3: Branch-wise Financial Performance
-- Business question:
-- Which branches handle the highest transaction volume and value?

SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    b.state,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.transaction_amount) AS total_transaction_value,
    AVG(t.transaction_amount) AS average_transaction_value
FROM branches b
LEFT JOIN accounts a
    ON b.branch_id = a.branch_id
LEFT JOIN transactions t
    ON a.account_id = t.account_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.city,
    b.state
ORDER BY
    total_transaction_value DESC;
