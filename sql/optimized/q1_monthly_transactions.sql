
SELECT
    CAST(
        MAKE_DATE(transaction_year, transaction_month, 1)
        AS TIMESTAMP
    ) AS transaction_month,
    transaction_type,
    transaction_status,
    COUNT(transaction_id) AS total_transactions,
    SUM(transaction_amount) AS total_transaction_value,
    AVG(transaction_amount) AS average_transaction_value
FROM transactions
GROUP BY
    transaction_year,
    transaction_month,
    transaction_type,
    transaction_status
ORDER BY
    transaction_year,
    transaction_month,
    transaction_type,
    transaction_status;
