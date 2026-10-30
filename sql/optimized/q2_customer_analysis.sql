WITH customer_transactions AS (
    SELECT
        a.customer_id,
        COUNT(t.transaction_id) AS total_transactions,
        SUM(t.transaction_amount) AS total_transaction_value,
        AVG(t.transaction_amount) AS average_transaction_value
    FROM accounts a
    INNER JOIN transactions t
        ON a.account_id = t.account_id
    GROUP BY a.customer_id
)

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    COALESCE(ct.total_transactions, 0) AS total_transactions,
    ct.total_transaction_value,
    ct.average_transaction_value

FROM customers c

LEFT JOIN customer_transactions ct
    ON c.customer_id = ct.customer_id

ORDER BY total_transaction_value DESC;