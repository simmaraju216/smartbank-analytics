WITH transaction_by_account AS (
    SELECT
        account_id,
        COUNT(transaction_id) AS transaction_count,
        SUM(transaction_amount) AS transaction_value
    FROM transactions
    GROUP BY account_id
)
SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    b.state,
    SUM(COALESCE(ta.transaction_count, 0)) AS total_transactions,
    SUM(ta.transaction_value) AS total_transaction_value,
    CASE
        WHEN SUM(COALESCE(ta.transaction_count, 0)) = 0 THEN NULL
        ELSE SUM(ta.transaction_value) / SUM(ta.transaction_count)
    END AS average_transaction_value
FROM branches b
LEFT JOIN accounts a
    ON b.branch_id = a.branch_id
LEFT JOIN transaction_by_account ta
    ON a.account_id = ta.account_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.city,
    b.state
ORDER BY total_transaction_value DESC;