WITH successful_merchant_transactions AS (
    SELECT
        merchant_id,
        transaction_type,
        transaction_status,
        COUNT(transaction_id) AS total_transactions,
        SUM(transaction_amount) AS total_payment_value,
        AVG(transaction_amount) AS average_payment_value
    FROM transactions
    WHERE transaction_status = 'SUCCESS'
      AND merchant_id IS NOT NULL
    GROUP BY
        merchant_id,
        transaction_type,
        transaction_status
)
SELECT
    m.merchant_id,
    m.merchant_name,
    m.category,
    t.transaction_type,
    t.transaction_status,
    t.total_transactions,
    t.total_payment_value,
    t.average_payment_value
FROM successful_merchant_transactions t
INNER JOIN merchants m
    ON t.merchant_id = m.merchant_id
ORDER BY total_payment_value DESC;
