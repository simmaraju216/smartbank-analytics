
-- Q4: Merchant Payment Analysis
-- Business question:
-- Which merchants receive the highest payment volume?

SELECT
    m.merchant_id,
    m.merchant_name,
    m.category,
    t.transaction_type,
    t.transaction_status,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.transaction_amount) AS total_payment_value,
    AVG(t.transaction_amount) AS average_payment_value
FROM merchants m
INNER JOIN transactions t
    ON m.merchant_id = t.merchant_id
WHERE
    t.transaction_status = 'SUCCESS'
GROUP BY
    m.merchant_id,
    m.merchant_name,
    m.category,
    t.transaction_type,
    t.transaction_status
ORDER BY
    total_payment_value DESC;
