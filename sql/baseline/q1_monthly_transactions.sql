
SELECT
    MAKE_DATE(
        EXTRACT(
            YEAR FROM transaction_timestamp AT TIME ZONE 'UTC'
        )::INTEGER,
        EXTRACT(
            MONTH FROM transaction_timestamp AT TIME ZONE 'UTC'
        )::INTEGER,
        1
    )::TIMESTAMP AS transaction_month,

    transaction_type,
    transaction_status,

    COUNT(transaction_id) AS total_transactions,

    SUM(transaction_amount) AS total_transaction_value,

    AVG(transaction_amount) AS average_transaction_value

FROM transactions

GROUP BY
    1, 2, 3

ORDER BY
    1, 2, 3;
