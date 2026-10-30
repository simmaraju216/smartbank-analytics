
-- Q5: Daily Debit and Credit Summary
-- Business question:
-- What are the daily debit and credit totals?

SELECT
    CAST(transaction_timestamp AS DATE) AS transaction_date,
    transaction_status,
    COUNT(transaction_id) AS total_transactions,
    SUM(debit_amount) AS total_debit_amount,
    SUM(credit_amount) AS total_credit_amount,
    SUM(transaction_amount) AS total_transaction_amount
FROM transactions
GROUP BY
    CAST(transaction_timestamp AS DATE),
    transaction_status
ORDER BY
    transaction_date,
    transaction_status;
