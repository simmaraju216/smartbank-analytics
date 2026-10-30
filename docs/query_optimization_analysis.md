# SmartBank Analytics - SQL Query Optimization Analysis

## 1. Objective

The objective of this analysis is to identify inefficient analytical SQL operations in the SmartBank banking dataset and evaluate optimization techniques.

The analysis focuses on:

- Table scans
- Joins
- Aggregations
- Filtering
- Repeated calculations
- Query execution time

Five analytical workloads were evaluated using DuckDB and synthetic banking data containing 500,000 transactions.

## 2. Benchmark Methodology

### Environment

- Database: DuckDB
- Storage format: Parquet
- Transaction records: 500,000
- Benchmark repetitions: 3 measured executions per query
- Performance metric: Median execution time
- Correctness validation: Baseline and optimized result comparison

### Measurement approach

Each query was executed using the baseline and optimized SQL versions.

The benchmark process:

1. Executes a warm-up query.
2. Executes the query three times.
3. Records execution times.
4. Calculates median and average execution time.
5. Saves the execution plan.
6. Compares baseline and optimized performance.

### Improvement calculation

Improvement percentage is calculated as:

Improvement (%) = ((Baseline Time - Optimized Time) / Baseline Time) * 100

A positive value indicates a lower measured execution time for the optimized version.

## 3. Q1 - Monthly Transaction Analysis

### Business question

What is the monthly transaction volume and value by transaction type and status?

### Baseline approach

The baseline query extracts the year and month from transaction_timestamp during query execution.

It groups transactions by:

- Transaction month
- Transaction type
- Transaction status

### Optimization technique

The transformation pipeline already generates:

- transaction_year
- transaction_month

The optimized query uses these precomputed columns instead of repeatedly extracting year and month from the timestamp.

### Expected benefit

- Reduces repeated date-part extraction.
- Reuses transformed analytical attributes.
- Simplifies grouping expressions.

### Correctness result

- Baseline rows: 416
- Optimized rows: 416
- Result comparison: PASS

## 4. Q2 - Customer Transaction Analysis

### Business question

What is the transaction activity and financial performance of each customer?

### Baseline approach

The baseline query joins customers, accounts, and transactions before calculating customer-level aggregates.

### Optimization technique

The optimized query pre-aggregates transaction information by customer through the account relationship before joining the customer details.

### Expected benefit

- Reduces the number of transaction rows entering later joins.
- Performs aggregation before joining customer details.
- Reduces unnecessary processing in the final join stage.

### Correctness result

- Baseline rows: 25,000
- Optimized rows: 25,000
- Result comparison: PASS

## 5. Q3 - Branch Financial Performance

### Business question

What is the financial transaction performance of each branch?

### Baseline approach

The baseline query joins branches, accounts, and transactions before calculating branch-level aggregates.

### Optimization technique

The optimized query first aggregates transaction information by account.

It then joins the aggregated results with accounts and branches.

### Expected benefit

- Reduces transaction-level rows before joining branch details.
- Separates transaction aggregation from dimensional joins.
- Can reduce the volume of data processed by later joins.

### Correctness result

- Baseline rows: 10
- Optimized rows: 10
- Result comparison: PASS

## 6. Q4 - Merchant Payment Analysis

### Business question

What is the successful payment volume and value for each merchant?

### Baseline approach

The baseline query joins merchants and transactions, filters successful transactions, and calculates merchant-level aggregates.

### Optimization technique

The optimized query:

1. Filters successful transactions.
2. Excludes transactions without a merchant ID.
3. Aggregates transaction metrics by merchant ID, transaction type, and transaction status.
4. Joins the aggregated results with merchant details.

### Expected benefit

- Reduces the number of rows entering the merchant join.
- Performs aggregation before joining merchant details.
- Separates transaction metrics from merchant descriptive attributes.

### Correctness result

- Baseline rows: 300
- Optimized rows: 300
- Result comparison: PASS

## 7. Q5 - Daily Debit and Credit Summary

### Business question

What are the daily debit and credit totals?

### Baseline approach

The baseline query converts transaction_timestamp into a date using:

CAST(transaction_timestamp AS DATE)

It groups the records by transaction date and transaction status.

### Optimization investigation

An initial optimized version used the precomputed transaction_date column.

However, correctness validation identified a timezone difference:

- The transformation pipeline generated transaction_date using UTC.
- DuckDB used Asia/Calcutta as its session timezone.
- The two approaches produced different calendar dates for some transactions.

The optimized query was therefore changed to preserve the baseline date calculation and IST business-day definition.

### Final correctness result

- Baseline rows: 1,464
- Optimized rows: 1,464
- Result comparison: PASS

### Performance interpretation

The final optimized query uses the same date conversion logic as the baseline.

Although the measured optimized median was lower, this difference cannot currently be attributed to a distinct SQL optimization.

Further controlled benchmarking is required before claiming a Q5 optimization.

## 8. Consolidated Performance Results

| Query | Baseline (sec) | Optimized (sec) | Measured improvement |
|---|---:|---:|---:|
| Q1 Monthly transactions | 0.036705 | 0.011514 | 68.63% |
| Q2 Customer analysis | 0.092689 | 0.062242 | 32.85% |
| Q3 Branch performance | 0.046677 | 0.030332 | 35.02% |
| Q4 Merchant analysis | 0.015918 | 0.011917 | 25.14% |
| Q5 Daily debit/credit | 0.020430 | 0.017314 | 15.25% |

### Performance observations

- Q1 recorded the highest measured improvement at 68.63%.
- Q2 recorded a measured improvement of 32.85%.
- Q3 recorded a measured improvement of 35.02%.
- Q4 recorded a measured improvement of 25.14%.
- Q5 recorded a lower median execution time, but no distinct SQL optimization has yet been established.

These results are local experimental measurements based on three repetitions. They should not be interpreted as guaranteed production performance.

## 9. Correctness Validation Summary

| Query | Baseline rows | Optimized rows | Status |
|---|---:|---:|---|
| Q1 | 416 | 416 | PASS |
| Q2 | 25,000 | 25,000 | PASS |
| Q3 | 10 | 10 | PASS |
| Q4 | 300 | 300 | PASS |
| Q5 | 1,464 | 1,464 | PASS |

All five query comparisons passed using the existing numeric tolerance and result comparison logic.

## 10. Limitations and Future Improvements

The current benchmark has several limitations:

- Only three measured executions were used per query.
- Results may be affected by caching and system activity.
- Measurements represent one local environment.
- Q5 needs a timezone-consistent precomputed date column before it can benefit from date precomputation.
- Larger datasets should be tested to evaluate scalability.
- Additional repeated benchmark rounds would provide more reliable performance estimates.

Future work:

1. Increase benchmark repetitions.
2. Test with one million or more transactions.
3. Compare execution plans before and after optimization.
4. Evaluate partitioning and predicate pushdown.
5. Establish a consistent business timezone for daily and monthly reporting.
6. Reconcile query outputs after every optimization.

## 11. Conclusion

The SmartBank Analytics project evaluated five banking analytical SQL workloads.

Four queries use identifiable SQL optimization techniques involving precomputed date attributes and pre-aggregation before joins.

All five optimized queries passed correctness validation.

The benchmark recorded lower median execution times for all five queries. However, the Q5 timing difference requires further investigation because its final SQL logic is equivalent to the baseline.

The results demonstrate the importance of combining performance measurement with business-result correctness and timezone consistency.
