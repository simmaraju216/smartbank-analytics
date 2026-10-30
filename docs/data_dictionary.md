# SmartBank Analytics – Data Dictionary

## 1. Overview

This document describes the data structures used in the SmartBank Analytics project.

The project uses synthetic banking data to analyze financial transactions, customer activity, branch performance, merchant payments, and fraud alerts.

The data dictionary defines:

- Table names and descriptions
- Column names and logical data types
- Primary keys and foreign keys
- Nullable and optional fields
- Business rules and relationships
- Ingestion metadata
- Transformation fields

The project contains seven main banking datasets.

## 2. Dataset Overview

| Table Name | Description | Primary Key |
|---|---|---|
| customers | Stores customer information | customer_id |
| branches | Stores bank branch information | branch_id |
| accounts | Stores customer bank accounts | account_id |
| merchants | Stores merchant information | merchant_id |
| cards | Stores customer card information | card_id |
| transactions | Stores financial transaction records | transaction_id |
| fraud_alerts | Stores transaction-related fraud alerts | alert_id |

## 3. Data Types and Conventions

The following logical data types are used throughout this document.

| Logical Type | Description | Example |
|---|---|---|
| VARCHAR | Text and identifier values | CUST000001 |
| INTEGER | Whole-number values | 25 |
| DECIMAL | Financial and numeric values | 1500.50 |
| BOOLEAN | True or false values | TRUE |
| TIMESTAMP | Date and time values | 2026-10-30T10:30:00 |
| DATE | Calendar date | 2026-10-30 |

**Important:** These are logical data types for documentation. Actual physical types may vary depending on CSV inference, Pandas, Parquet, and DuckDB.

## 4. Customers Table

### Description

The `customers` table stores basic customer information.

Each record represents one bank customer.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| customer_id | VARCHAR | Primary Key | Unique customer identifier |
| customer_name | VARCHAR | | Full name of the customer |
| email | VARCHAR | | Customer email address |
| city | VARCHAR | | Customer city |
| state | VARCHAR | | Customer state |

### Business Rules

- `customer_id` must uniquely identify each customer.
- Customer identifiers must not be null.
- Email addresses are standardized to lowercase during transformation.
- City and state values are standardized by trimming whitespace and applying title case.

### Example

| customer_id | customer_name | email | city | state |
|---|---|---|---|---|
| CUST000001 | Rahul Kumar | rahul@example.com | Hyderabad | Telangana |
| CUST000002 | Priya Sharma | priya@example.com | Visakhapatnam | Andhra Pradesh |

## 5. Branches Table

### Description

The `branches` table stores information about bank branches.

Each record represents one bank branch.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| branch_id | VARCHAR | Primary Key | Unique branch identifier |
| branch_name | VARCHAR | | Name of the bank branch |
| city | VARCHAR | | Branch city |
| state | VARCHAR | | Branch state |

### Business Rules

- `branch_id` must uniquely identify each branch.
- Branch identifiers must not be null.
- Branch information is referenced by the accounts table.

### Example

| branch_id | branch_name | city | state |
|---|---|---|---|
| BR001 | Hyderabad Main Branch | Hyderabad | Telangana |
| BR002 | Vizag Branch | Visakhapatnam | Andhra Pradesh |

## 6. Accounts Table

### Description

The `accounts` table stores bank account information.

Each record represents one customer bank account.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| account_id | VARCHAR | Primary Key | Unique bank account identifier |
| customer_id | VARCHAR | Foreign Key | Customer who owns the account |
| branch_id | VARCHAR | Foreign Key | Branch associated with the account |
| account_type | VARCHAR | | Type of bank account |
| balance | DECIMAL | | Current account balance |

### Relationships

- `customer_id` references `customers.customer_id`.
- `branch_id` references `branches.branch_id`.

### Allowed Account Types

- SAVINGS
- CURRENT
- SALARY

### Business Rules

- Every account must have a valid customer reference.
- Every account must have a valid branch reference.
- `account_id` must be unique.
- Account balances are stored as numeric values.

### Example

| account_id | customer_id | branch_id | account_type | balance |
|---|---|---|---|---:|
| ACC000001 | CUST000001 | BR001 | SAVINGS | 25000.50 |
| ACC000002 | CUST000002 | BR002 | CURRENT | 50000.00 |

## 7. Merchants Table

### Description

The `merchants` table stores information about merchants participating in financial transactions.

Each record represents one merchant.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| merchant_id | VARCHAR | Primary Key | Unique merchant identifier |
| merchant_name | VARCHAR | | Name of the merchant |
| category | VARCHAR | | Merchant business category |

### Business Rules

- `merchant_id` must uniquely identify each merchant.
- Merchant identifiers must not be null.
- Merchant records are referenced by transactions.
- Merchant information supports payment and merchant performance analysis.

### Example

| merchant_id | merchant_name | category |
|---|---|---|
| MER000001 | ABC Supermarket | Retail |
| MER000002 | City Restaurant | Food |

## 8. Cards Table

### Description

The `cards` table stores customer debit and credit card information.

Each record represents one payment card.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| card_id | VARCHAR | Primary Key | Unique card identifier |
| customer_id | VARCHAR | Foreign Key | Customer associated with the card |
| card_type | VARCHAR | | Type of payment card |
| card_status | VARCHAR | | Current card status |

### Relationships

- `customer_id` references `customers.customer_id`.

### Allowed Card Types

- DEBIT
- CREDIT

### Allowed Card Statuses

- ACTIVE
- BLOCKED

### Business Rules

- `card_id` must uniquely identify each card.
- Every card must reference a valid customer.
- Card status must represent an accepted status.
- Card information is used for card transaction analysis.

### Example

| card_id | customer_id | card_type | card_status |
|---|---|---|---|
| CARD000001 | CUST000001 | DEBIT | ACTIVE |
| CARD000002 | CUST000002 | CREDIT | BLOCKED |

## 9. Transactions Table

### Description

The `transactions` table is the central fact table of the SmartBank Analytics project.

It stores financial activities performed through bank accounts, including payments, withdrawals, deposits, and transfers.

Each record represents one financial transaction.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| transaction_id | VARCHAR | Primary Key | Unique transaction identifier |
| account_id | VARCHAR | Foreign Key | Account associated with the transaction |
| merchant_id | VARCHAR | Foreign Key / Nullable | Merchant associated with the transaction |
| card_id | VARCHAR | Foreign Key / Nullable | Payment card associated with the transaction |
| transaction_type | VARCHAR | | Type of financial transaction |
| transaction_amount | DECIMAL | | Transaction amount |
| transaction_status | VARCHAR | | Current transaction status |
| transaction_timestamp | TIMESTAMP | | Date and time when transaction occurred |

### Relationships

- `account_id` references `accounts.account_id`.
- `merchant_id` references `merchants.merchant_id` when provided.
- `card_id` references `cards.card_id` when provided.

### Optional Fields

The following fields can contain null values:

- `merchant_id`
- `card_id`

These fields are optional because not every financial transaction involves a merchant or payment card.

### Transaction Types

The generator supports multiple transaction types, including:

- ATM_WITHDRAWAL
- DEBIT_CARD
- CREDIT_CARD
- UPI
- NEFT
- RTGS
- IMPS
- CASH_DEPOSIT

### Transaction Statuses

- SUCCESS
- FAILED
- PENDING
- REVERSED

### Business Rules

- `transaction_id` must uniquely identify each transaction.
- `account_id` must reference an existing account.
- `merchant_id` must reference an existing merchant when provided.
- `card_id` must reference an existing card when provided.
- Transaction amounts must be numeric and greater than zero.
- Transaction timestamps must be valid.
- Transaction types and statuses must follow the accepted values defined by the validation logic.

### Example

| transaction_id | account_id | merchant_id | card_id | transaction_type | transaction_amount | transaction_status |
|---|---|---|---|---|---:|---|
| TXN000001 | ACC000001 | MER000001 | CARD000001 | UPI | 1500.00 | SUCCESS |
| TXN000002 | ACC000002 | NULL | NULL | CASH_DEPOSIT | 5000.00 | SUCCESS |

## 10. Fraud Alerts Table

### Description

The `fraud_alerts` table stores alerts associated with financial transactions.

Each record represents one generated fraud alert.

**Important:** These are synthetic fraud alerts. An alert does not necessarily mean that a transaction is confirmed fraudulent.

### Schema

| Column Name | Logical Data Type | Key | Description |
|---|---|---|---|
| alert_id | VARCHAR | Primary Key | Unique fraud alert identifier |
| transaction_id | VARCHAR | Foreign Key | Transaction associated with the alert |
| alert_type | VARCHAR | | Category of fraud alert |
| risk_score | DECIMAL | | Numerical risk score |

### Relationships

- `transaction_id` references `transactions.transaction_id`.

### Business Rules

- `alert_id` must uniquely identify each alert.
- Every alert must reference an existing transaction.
- Risk scores must be numeric.
- Risk scores must be between 0 and 1, inclusive.
- Alert types must follow the accepted values defined by the validation logic.

### Example

| alert_id | transaction_id | alert_type | risk_score |
|---|---|---|---:|
| ALERT000001 | TXN000001 | HIGH_VALUE | 0.92 |
| ALERT000002 | TXN000002 | UNUSUAL_ACTIVITY | 0.75 |

## 11. Entity Relationship Overview

The following relationships describe how the seven tables are connected.

| Parent Table | Parent Key | Child Table | Foreign Key | Relationship |
|---|---|---|---|---|
| customers | customer_id | accounts | customer_id | One-to-many |
| branches | branch_id | accounts | branch_id | One-to-many |
| customers | customer_id | cards | customer_id | One-to-many |
| accounts | account_id | transactions | account_id | One-to-many |
| merchants | merchant_id | transactions | merchant_id | One-to-many, optional on transaction |
| cards | card_id | transactions | card_id | One-to-many, optional on transaction |
| transactions | transaction_id | fraud_alerts | transaction_id | One-to-many |

### Relationship Diagram

```text
                    CUSTOMERS
                    /       \
                   /         \
             ACCOUNTS        CARDS
                 |             |
                 |             |
                 +------ TRANSACTIONS ------ MERCHANTS
                            |
                            |
                       FRAUD_ALERTS

                    BRANCHES
                        |
                        |
                     ACCOUNTS
```

## 12. Data Grain

Data grain defines what one record represents in each table.

| Table | Data Grain |
|---|---|
| customers | One record per customer |
| branches | One record per branch |
| accounts | One record per bank account |
| merchants | One record per merchant |
| cards | One record per payment card |
| transactions | One record per financial transaction |
| fraud_alerts | One record per generated fraud alert |

The transactions table is the primary analytical fact table.

The remaining tables provide descriptive information used for joins and aggregations.

## 13. Ingestion Metadata

During ingestion, the pipeline adds metadata columns to identify where records originated and which execution processed them.

| Column Name | Logical Data Type | Description |
|---|---|---|
| run_id | VARCHAR | Unique identifier for the pipeline execution |
| source_file | VARCHAR | Name of the source CSV file |
| ingested_at | TIMESTAMP | UTC timestamp when the record was ingested |

These fields improve traceability and support debugging, auditing, and pipeline monitoring.

The metadata allows records to be associated with a particular execution and source file.

## 14. Transformation Fields

The transformation stage adds analytical fields to the transactions dataset.

| Column Name | Logical Data Type | Description |
|---|---|---|
| transaction_date | DATE | Date derived from the transaction timestamp using UTC |
| transaction_month | INTEGER | Month number derived from the transaction timestamp using UTC |
| transaction_year | INTEGER | Year derived from the transaction timestamp using UTC |
| debit_amount | DECIMAL | Transaction amount classified as debit; otherwise zero |
| credit_amount | DECIMAL | Transaction amount classified as credit; otherwise zero |

### Debit Classification

The current transformation logic classifies the following transaction types as debit:

- ATM_WITHDRAWAL
- DEBIT_CARD
- UPI
- NEFT
- RTGS
- IMPS

### Credit Classification

The current transformation logic classifies:

- CASH_DEPOSIT

as credit.

Other transaction types receive zero in these classification fields unless included in the transformation rules.

### Timestamp Standardization

Transaction timestamps are parsed and standardized to UTC during transformation.

The `transaction_date`, `transaction_month`, and `transaction_year` fields are derived using UTC.

The daily Q5 baseline and optimized SQL comparison preserve the existing DuckDB session-date behavior instead of assuming that the SQL date cast is equivalent to the UTC-derived transformation date.

## 15. Data Quality Rules

The pipeline applies validation rules to maintain data quality.

| Validation Category | Rule |
|---|---|
| Schema validation | Required columns must exist |
| Primary key validation | Primary keys must not be null |
| Duplicate validation | Duplicate primary-key records are identified |
| Numeric validation | Financial amounts must be numeric |
| Transaction validation | Transaction amounts must be greater than zero |
| Status validation | Transaction status must be an accepted value |
| Foreign key validation | Referenced parent records must exist |
| Timestamp validation | Transaction timestamps must be valid |
| Risk score validation | Risk score must be between 0 and 1 |
| Null validation | Required fields must not contain null values |

## 16. Duplicate Handling

Duplicate records are identified using the primary key of each table.

The current duplicate-handling logic:

1. Identifies duplicate primary-key values.
2. Retains the first occurrence.
3. Rejects subsequent duplicate records.
4. Records the rejection reason.
5. Preserves rejected records for traceability.

Duplicate records are not silently included in the final analytical dataset.

## 17. Rejected Data

Records that fail validation are stored separately from valid processed data.

The rejected dataset supports investigation and debugging.

Rejection reasons may include:

- Missing required values
- Invalid transaction amount
- Invalid transaction status
- Invalid transaction timestamp
- Missing foreign key reference
- Duplicate primary key
- Invalid fraud risk score

Rejected records should retain their original identifying information and ingestion metadata wherever available.

## 18. Storage and Analytical Database

The project uses the following storage components:

| Component | Purpose |
|---|---|
| CSV | Synthetic source data |
| Pandas DataFrame | Data ingestion and validation |
| Parquet | Processed analytical data |
| DuckDB | Analytical query execution |
| JSON | Pipeline run metadata and execution logs |

Parquet is used for efficient analytical storage.

DuckDB provides SQL-based analysis and supports baseline versus optimized query benchmarking.

## 19. Dataset Scale

The current synthetic dataset contains the following records:

| Table | Record Count |
|---|---:|
| customers | 25,000 |
| branches | 10 |
| accounts | 37,500 |
| merchants | 100 |
| cards | 25,000 |
| transactions | 500,000 |
| fraud_alerts | 25,000 |
| **Total** | **612,610** |

These counts describe the current generated dataset and may change when the generator is executed with a different transaction count.

## 20. Conclusion

This data dictionary provides a reference for the SmartBank Analytics data model.

It documents the seven banking datasets, their relationships, data grain, logical data types, business rules, and analytical transformation fields.

The documentation supports:

- Understanding the banking data model
- Designing reliable ingestion and validation
- Maintaining referential integrity
- Building reproducible analytical SQL workloads
- Investigating rejected records
- Supporting future scalability and maintenance

The data dictionary should be updated whenever the generator, schema definitions, validation rules, or transformation logic change.