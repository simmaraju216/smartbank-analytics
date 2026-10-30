# SmartBank Analytics – Business Rules

## 1. Introduction

This document defines the business rules and data quality requirements used in the SmartBank Analytics project.

The project uses synthetic banking and financial data to demonstrate a reliable analytical data pipeline.

The pipeline processes customer information, bank accounts, branches, merchants, payment cards, financial transactions, and fraud alerts.

These rules help ensure that the processed data is accurate, consistent, traceable, and suitable for analytical queries.

## 2. Business Objectives

The main objectives of the business rules are:

- Maintain accurate banking records.
- Prevent invalid financial transactions from entering analytical datasets.
- Maintain referential integrity between related tables.
- Identify and handle duplicate records.
- Standardize customer and transaction data.
- Preserve rejected records for investigation.
- Support reliable financial reporting.
- Make pipeline executions reproducible and traceable.

## 3. Customer Rules

The customers table stores customer information.

### Rules

1. Every customer must have a unique `customer_id`.
2. `customer_id` must not be null.
3. Customer names must be available.
4. Email values should be standardized to lowercase.
5. Leading and trailing whitespace should be removed from email values.
6. City and state values should be standardized by trimming whitespace and applying title case.
7. Duplicate customer identifiers must be identified and handled.

### Expected Outcome

Customer records should contain consistent identifiers and standardized descriptive information.

## 4. Branch Rules

The branches table stores bank branch information.

### Rules

1. Every branch must have a unique `branch_id`.
2. `branch_id` must not be null.
3. Branch names must be available.
4. Branch city and state information should be available.
5. Every account must reference an existing branch.

### Expected Outcome

Every processed account should be associated with a valid branch.

## 5. Account Rules

The accounts table stores bank account information.

### Rules

1. Every account must have a unique `account_id`.
2. `account_id` must not be null.
3. Every account must reference an existing customer.
4. Every account must reference an existing branch.
5. Account balance must be numeric.
6. Account type must follow the accepted values defined by the generator and validation logic.
7. Duplicate account identifiers must be handled.

### Referential Integrity

- `accounts.customer_id` must exist in `customers.customer_id`.
- `accounts.branch_id` must exist in `branches.branch_id`.

### Expected Outcome

Every valid account must be connected to an existing customer and branch.

## 6. Merchant Rules

The merchants table stores merchant information.

### Rules

1. Every merchant must have a unique `merchant_id`.
2. `merchant_id` must not be null.
3. Merchant names must be available.
4. Merchant categories should describe the merchant's business type.
5. Transactions containing a merchant identifier must reference an existing merchant.

### Expected Outcome

Merchant information should be consistent and usable for payment analysis.

## 7. Card Rules

The cards table stores payment card information.

### Rules

1. Every card must have a unique `card_id`.
2. `card_id` must not be null.
3. Every card must reference an existing customer.
4. Card type must follow the accepted values defined by the generator and validation logic.
5. Card status must follow the accepted values defined by the generator and validation logic.
6. Duplicate card identifiers must be handled.

### Referential Integrity

`cards.customer_id` must exist in `customers.customer_id`.

### Expected Outcome

Every processed card must be associated with a valid customer.

## 8. Transaction Rules

The transactions table is the main financial fact table.

It stores withdrawals, deposits, payments, and other financial activities.

### 8.1 Transaction Identifier

1. Every transaction must have a unique `transaction_id`.
2. `transaction_id` must not be null.
3. Duplicate transaction identifiers must be identified.
4. The first valid occurrence is retained by the current duplicate-handling logic.

### 8.2 Account Reference

1. Every transaction must reference an existing account.
2. `account_id` must not be null.
3. Transactions with missing or invalid account references must be rejected.

### 8.3 Merchant Reference

1. `merchant_id` is optional.
2. If `merchant_id` is provided, it must reference an existing merchant.
3. A missing merchant identifier is acceptable for transactions that do not involve a merchant.

### 8.4 Card Reference

1. `card_id` is optional.
2. If `card_id` is provided, it must reference an existing card.
3. A missing card identifier is acceptable for transactions that do not involve a payment card.

### 8.5 Transaction Amount

1. Transaction amounts must be numeric.
2. Transaction amounts must be greater than zero.
3. Null transaction amounts are invalid.
4. Non-numeric transaction amounts must be rejected.
5. Invalid financial amounts must not be included in analytical calculations.

### 8.6 Transaction Type

The transaction type must be one of the accepted values defined in the validation logic.

The current generator supports:

- ATM_WITHDRAWAL
- DEBIT_CARD
- CREDIT_CARD
- UPI
- NEFT
- RTGS
- IMPS
- CASH_DEPOSIT

Unknown transaction types must be rejected.

### 8.7 Transaction Status

The transaction status must be one of the accepted values defined in the validation logic.

The current generator supports:

- SUCCESS
- FAILED
- PENDING
- REVERSED

Unknown transaction statuses must be rejected.

### 8.8 Transaction Timestamp

1. Every transaction must have a valid timestamp.
2. Invalid timestamp values must be rejected.
3. Transaction timestamps are standardized to UTC during transformation.
4. UTC timestamps are used to derive analytical year, month, and date fields.

### Expected Outcome

Only transactions that pass the applicable schema, business, duplicate, null, and reference checks should enter the valid processed dataset.

## 9. Debit and Credit Classification Rules

The transformation stage creates two analytical fields:

- `debit_amount`
- `credit_amount`

### Debit Classification

The following transaction types are classified as debit:

- ATM_WITHDRAWAL
- DEBIT_CARD
- UPI
- NEFT
- RTGS
- IMPS

For these transaction types:

`debit_amount = transaction_amount`

### Credit Classification

The following transaction type is classified as credit:

- CASH_DEPOSIT

For this transaction type:

`credit_amount = transaction_amount`

### Other Transaction Types

Transaction types not included in either classification receive zero in the corresponding analytical amount fields.

### Example

| Transaction Type | Amount | Debit Amount | Credit Amount |
|---|---:|---:|---:|
| ATM_WITHDRAWAL | 1000 | 1000 | 0 |
| UPI | 500 | 500 | 0 |
| CASH_DEPOSIT | 2000 | 0 | 2000 |
| CREDIT_CARD | 1500 | 0 | 0 |

**Note:** This classification follows the current project transformation logic. It is an analytical classification and should not be interpreted as a complete accounting ledger.

## 10. Fraud Alert Rules

The fraud_alerts table stores generated alerts associated with transactions.

### Rules

1. Every alert must have a unique `alert_id`.
2. `alert_id` must not be null.
3. Every alert must reference an existing transaction.
4. Risk scores must be numeric.
5. Risk scores must be between 0 and 1, inclusive.
6. Invalid risk scores must be rejected.
7. Alert types must follow the accepted values defined in the validation logic.
8. Duplicate alert identifiers must be handled.

### Important Business Interpretation

Fraud alerts represent generated risk indicators.

An alert does not automatically confirm that a transaction is fraudulent.

Further investigation is required before classifying a transaction as confirmed fraud.

## 11. Primary Key Rules

Every main table must have a unique primary key.

| Table | Primary Key |
|---|---|
| customers | customer_id |
| branches | branch_id |
| accounts | account_id |
| merchants | merchant_id |
| cards | card_id |
| transactions | transaction_id |
| fraud_alerts | alert_id |

### Rules

- Primary key values must not be null.
- Duplicate primary key values must be identified.
- The current duplicate handler retains the first occurrence.
- Subsequent duplicate records are moved to the rejected dataset with a rejection reason.

## 12. Foreign Key Rules

Foreign key validation ensures that child records reference existing parent records.

| Child Table | Foreign Key | Parent Table | Parent Key |
|---|---|---|---|
| accounts | customer_id | customers | customer_id |
| accounts | branch_id | branches | branch_id |
| cards | customer_id | customers | customer_id |
| transactions | account_id | accounts | account_id |
| transactions | merchant_id | merchants | merchant_id |
| transactions | card_id | cards | card_id |
| fraud_alerts | transaction_id | transactions | transaction_id |

### Rules

1. Required foreign key values must not be null.
2. Every provided foreign key must match an existing parent key.
3. Optional merchant and card references are checked only when provided.
4. Records with invalid references must be rejected.
5. Parent records must be validated before dependent records are processed.

## 13. Duplicate Handling Rules

Duplicate records can affect financial reporting and analytical accuracy.

The project identifies duplicates using the primary key of each table.

### Processing Steps

1. Read the source dataset.
2. Identify duplicate primary key values.
3. Retain the first occurrence.
4. Identify subsequent duplicate records.
5. Assign a rejection reason.
6. Store rejected records separately.
7. Continue processing valid records.

### Rejection Reason Example

`DUPLICATE_transaction_id`

The duplicate handler must preserve sufficient information to identify the rejected source record.

## 14. Data Validation Rules

The pipeline applies multiple validation stages.

| Validation Stage | Description |
|---|---|
| Schema validation | Checks required columns and expected schema |
| Primary key validation | Checks missing primary key values |
| Duplicate validation | Identifies repeated primary key values |
| Null validation | Checks required fields |
| Numeric validation | Checks numeric values |
| Business validation | Checks transaction and fraud business rules |
| Foreign key validation | Checks parent-child relationships |
| Timestamp validation | Checks valid transaction timestamps |

### Validation Outcome

Each record should be classified as either:

- Valid record
- Rejected record

Rejected records should have a meaningful rejection reason.

## 15. Rejected Record Rules

Invalid records must not silently disappear from the pipeline.

### Rules

1. Records that fail validation must be separated from valid records.
2. Rejected records should preserve their original values.
3. Rejected records should retain available ingestion metadata.
4. Each rejected record should have a rejection reason.
5. Rejected records should be stored separately.
6. Rejected record counts must be included in pipeline execution metrics.

### Example Rejection Reasons

| Rejection Reason | Description |
|---|---|
| MISSING_REQUIRED_VALUE | Required field is missing |
| DUPLICATE_transaction_id | Duplicate transaction identifier |
| INVALID_TRANSACTION_AMOUNT | Amount is invalid |
| INVALID_TRANSACTION_STATUS | Unsupported transaction status |
| INVALID_TRANSACTION_TYPE | Unsupported transaction type |
| INVALID_TRANSACTION_TIMESTAMP | Invalid timestamp |
| INVALID_ACCOUNT_REFERENCE | Account does not exist |
| INVALID_MERCHANT_REFERENCE | Merchant does not exist |
| INVALID_CARD_REFERENCE | Card does not exist |
| INVALID_FRAUD_RISK_SCORE | Risk score outside the permitted range |

These examples describe rejection categories; the exact reason strings should remain consistent with the implemented validation functions.

## 16. Date and Time Rules

The project uses UTC as the standard timezone for transaction timestamp transformation.

### Rules

1. Transaction timestamps are parsed into datetime values.
2. Valid timestamps are standardized to UTC.
3. `transaction_date` is derived from the UTC timestamp.
4. `transaction_month` is derived from the UTC timestamp.
5. `transaction_year` is derived from the UTC timestamp.
6. The ingestion timestamp is recorded in UTC.

### Analytical Consideration

The daily transaction SQL workload uses DuckDB's session timezone when casting the timestamp to a date.

Therefore, the daily baseline and optimized queries preserve the same date semantics to ensure result correctness.

The UTC-derived transformation date and DuckDB session-date result should not be treated as interchangeable without explicit timezone conversion.

## 17. Pipeline Execution and Monitoring Rules

Every pipeline execution must be identifiable and traceable.

### Run Identifier

Each execution receives a unique `run_id`.

Example:

`RUN_20261030_125609_3f4fa8be`

### Execution Metadata

The pipeline tracker records:

- Run identifier
- Execution start time
- Execution end time
- Execution status
- Input record count
- Output record count
- Rejected record count
- Error information
- Execution duration

### Execution Status

The pipeline should report whether execution completed successfully or failed.

### Traceability

The `run_id`, `source_file`, and `ingested_at` metadata fields help connect processed records to their source and execution.

## 18. Idempotency and Rerun Rules

The pipeline should support safe reruns.

### Expected Behavior

1. Each execution receives a unique run identifier.
2. Execution output is associated with its run identifier.
3. Previous run outputs should not be accidentally overwritten by a new run.
4. Reprocessing the same source should produce deterministic business results when the source and processing logic are unchanged.
5. Duplicate records within an input dataset must be handled consistently.
6. Execution metadata should make individual runs traceable.

### Important Consideration

Run-specific output directories support execution isolation. They do not, by themselves, guarantee idempotent publishing to every downstream target.

Target-table replacement, merge, and retry behavior should be tested separately.

## 19. Analytical Reporting Rules

The project supports five analytical SQL workloads.

### Q1: Monthly Transaction Analysis

Purpose:

- Calculate monthly transaction volume.
- Calculate total transaction value.
- Calculate average transaction amount.
- Analyze results by transaction type and status.

### Q2: Customer Transaction Analysis

Purpose:

- Analyze transaction activity by customer.
- Calculate customer transaction counts.
- Calculate customer transaction values.
- Identify high-activity customers.

### Q3: Branch Financial Performance

Purpose:

- Analyze financial activity by branch.
- Calculate branch transaction counts.
- Calculate branch transaction values.
- Compare branch-level performance.

### Q4: Merchant Payment Analysis

Purpose:

- Analyze successful merchant transactions.
- Calculate merchant payment counts.
- Calculate total and average payment values.
- Compare merchant activity.

### Q5: Daily Debit and Credit Analysis

Purpose:

- Calculate daily transaction counts.
- Calculate debit amounts.
- Calculate credit amounts.
- Calculate total transaction amounts.
- Group results by transaction status.

## 20. Data Reconciliation Rules

Reconciliation checks ensure that pipeline processing accounts for input records.

### Basic Reconciliation

For each table:

`Input Records = Valid Output Records + Rejected Records`

This equation applies when every input record is classified exactly once.

### Reconciliation Metrics

The pipeline should report:

- Total input records
- Total valid output records
- Total rejected records
- Difference between expected and actual counts

### Expected Outcome

The reconciliation difference should be zero for a successfully classified dataset.

Any mismatch should be investigated before publishing analytical results.

## 21. Performance and Optimization Rules

The project compares baseline SQL queries with optimized SQL queries.

### Rules

1. Baseline and optimized queries must return equivalent results.
2. Query execution times must be measured using the same database and dataset.
3. Warm-up executions should be performed before measured runs.
4. Multiple executions should be used to reduce timing noise.
5. Median execution time should be used for comparison.
6. Query execution plans should be retained for analysis.
7. Performance improvements must be reported using measured results.
8. Faster execution alone is not proof of correctness.

### Performance Calculation

Improvement percentage:

`((Baseline Time - Optimized Time) / Baseline Time) * 100`

A positive percentage means the optimized query had a lower measured execution time.

## 22. Important Limitations and Assumptions

The project uses synthetic banking data.

Therefore:

- Customer and account information does not represent real bank customers.
- Fraud alerts are generated indicators, not confirmed fraud cases.
- Debit and credit classification follows the implemented transformation rules.
- The current data model is designed for analytical demonstration.
- It is not a complete banking core system or accounting ledger.
- Performance measurements depend on hardware, caching, DuckDB configuration, and dataset size.
- Business rules must be updated whenever the implemented generator or validation logic changes.

## 23. Conclusion

These business rules define how SmartBank Analytics processes, validates, transforms, and analyzes synthetic banking data.

They help maintain:

- Data consistency
- Referential integrity
- Financial data quality
- Duplicate control
- Rejected record traceability
- Reliable pipeline execution
- Correct analytical results
- Reproducible performance comparisons

The business rules serve as a reference for developers, reviewers, and future maintainers of the SmartBank Analytics project.