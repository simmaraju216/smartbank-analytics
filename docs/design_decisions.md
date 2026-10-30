# SmartBank Analytics - Design Decisions

## 1. Project Architecture

The project uses a modular Python-based data analytics pipeline.

Main stages:

1. Synthetic data generation
2. Data ingestion
3. Schema validation
4. Business validation
5. Duplicate handling
6. Data transformation
7. Parquet storage
8. DuckDB analytics
9. SQL optimization and benchmarking
10. Performance reporting

## 2. Technology Selection

| Technology | Purpose | Reason |
|---|---|---|
| Python | Pipeline implementation | Simple and modular |
| Pandas | Data processing | Data cleaning and transformation |
| NumPy | Numerical operations | Efficient numerical processing |
| Faker | Synthetic data generation | Generate realistic sample banking records |
| PyArrow | Parquet support | Columnar analytical storage |
| DuckDB | Analytical database | Local analytical SQL execution |
| Pytest | Testing | Automated validation |
| Matplotlib | Reporting | Performance visualization |
| python-dotenv | Configuration | Environment-based configuration |

## 3. Banking Domain Selection

Banking and financial analytics was selected as the business domain.

The dataset includes:

- Customers
- Branches
- Accounts
- Merchants
- Cards
- Transactions
- Fraud alerts

The domain supports analytical workloads involving financial transactions, customer activity, branch performance, merchant payments, and debit/credit summaries.

The records are synthetic and do not represent real customer or financial information.

## 4. Storage Design

### Raw data

Original generated CSV files are stored under:

data/raw/

### Processed data

Validated and transformed datasets are stored in Parquet format under run-specific directories.

### Rejected data

Invalid records are stored separately for traceability and investigation.

### Analytical database

DuckDB is used to query the processed datasets and support performance comparisons.

## 5. Data Validation Decisions

Validation is performed in multiple stages:

- Schema validation checks required columns and data types.
- Primary-key validation identifies duplicate records.
- Business validation checks required values and domain rules.
- Foreign-key validation checks relationships between banking entities.
- Invalid records are rejected with reasons.

The pipeline preserves rejected records separately rather than silently discarding them.

## 6. Duplicate Handling

Duplicate primary-key records are identified during processing.

The first occurrence is retained, and subsequent duplicate records are rejected with a duplicate reason.

This helps prevent duplicate records from affecting analytical totals.

## 7. Timezone Decision

The transformation pipeline converts transaction timestamps to UTC for standardized analytical processing.

The DuckDB database session uses Asia/Calcutta (IST).

During Q5 validation, the precomputed UTC transaction_date produced different calendar dates from the baseline query's IST date calculation.

The final Q5 query preserves the baseline's IST business-day definition to ensure identical results.

Future improvements should introduce an explicit business-date column calculated using the selected reporting timezone.

## 8. Idempotency and Run Tracking

Each pipeline execution receives a unique run_id.

Run tracking records:

- Run ID
- Start timestamp
- End timestamp
- Execution status
- Input record count
- Output record count
- Rejected record count
- Errors
- Execution duration

Run-specific output directories help keep processing results traceable.

The current run tracker provides execution-level traceability. Reprocessing the same input safely without creating duplicate published data should continue to be verified through dedicated idempotency tests.

## 9. SQL Optimization Decisions

Five baseline analytical queries were compared with optimized versions.

Optimization techniques included:

- Reusing precomputed transaction year and month attributes.
- Pre-aggregating customer transactions before joining customer details.
- Pre-aggregating account transactions before joining branch details.
- Filtering and aggregating successful merchant transactions before joining merchant details.

Q5 preserves the baseline date conversion because the earlier UTC date attribute did not match the IST business-day definition.

## 10. Performance Measurement Decisions

Each benchmark includes:

- One warm-up execution
- Three measured executions
- Median execution time
- Average execution time
- Saved execution plan

Median execution time is used for the consolidated comparison.

Performance results are treated as local experimental measurements rather than guaranteed production improvements.

## 11. Future Improvements

- Increase benchmark repetitions.
- Test larger datasets.
- Add timezone-consistent business-date attributes.
- Strengthen safe retry and idempotent publishing tests.
- Add more detailed pipeline observability.
- Evaluate incremental processing.
- Improve automated reconciliation and performance reporting.

## 12. Conclusion

The design prioritizes modularity, data quality, traceability, reproducibility, and analytical correctness.

The pipeline combines Python, Pandas, Parquet, and DuckDB to demonstrate a reproducible banking analytics workflow with measurable SQL performance experiments.
