# SmartBank Analytics - System Architecture

## 1. Introduction

SmartBank Analytics is a modular Python-based banking data engineering and analytics system.

The system processes synthetic banking datasets through ingestion, validation, transformation, storage, and analytical processing stages.

The main objective is to build a reproducible data pipeline and demonstrate SQL performance optimization using DuckDB and Parquet.

The project focuses on data quality, analytical correctness, pipeline reliability, execution traceability, and measurable query performance.

## 2. Architecture Objectives

The architecture is designed to:

- Generate synthetic banking datasets.

- Ingest multiple CSV datasets.

- Validate data schemas and business rules.

- Identify duplicate records.

- Validate relationships between banking entities.

- Separate valid and rejected records.

- Transform raw data into analytical datasets.

- Store processed datasets in Parquet format.

- Load datasets into DuckDB.

- Execute analytical SQL workloads.

- Compare baseline and optimized query results.

- Measure query execution performance.

- Track pipeline execution metadata.

- Support repeatable pipeline execution.

- Maintain data traceability and reconciliation.

## 3. High-Level Architecture

The overall processing architecture is:

```text

                 SYNTHETIC DATA GENERATOR

                           |

                           v

                      RAW CSV FILES

                           |

                           v

                      DATA INGESTION

                           |

                           v

                     SCHEMA VALIDATION

                           |

                           v

                    BUSINESS VALIDATION

                           |

                           v

                     DUPLICATE HANDLING

                           |

                           v

                     VALIDATION RESULTS

                       /          \

                      v            v

                 VALID DATA    REJECTED DATA

                      |            |

                      v            v

                 TRANSFORMATION  QUARANTINE

                      |

                      v

                 PARQUET STORAGE

                      |

                      v

                 DUCKDB DATABASE

                      |

                      v

                BASELINE SQL QUERIES

                      |

                      v

                OPTIMIZED SQL QUERIES

                      |

                      v

               CORRECTNESS VALIDATION

                      |

                      v

               PERFORMANCE BENCHMARKING

                      |

                      v

                 PERFORMANCE REPORTS

```

## 4. Technology Architecture

| Technology | Responsibility |

|---|---|

| Python 3.12 | Main pipeline implementation |

| Pandas | Data ingestion and transformation |

| NumPy | Numerical operations |

| Faker | Synthetic banking data generation |

| PyArrow | Parquet file support |

| DuckDB | Analytical database and SQL execution |

| Pytest | Automated testing |

| Matplotlib | Performance visualization |

| python-dotenv | Environment configuration |

## 5. Data Generation Layer

**Module:** `src/generators/`

**File:** `generate_banking_data.py`

The data generation module creates synthetic banking datasets.

It generates the following entities:

- Customers

- Branches

- Accounts

- Merchants

- Cards

- Transactions

- Fraud alerts

Generated datasets are exported as CSV files.

**Output directory:** `data/raw/`

The generator supports different transaction volumes, including:

- 10,000 transactions

- 100,000 transactions

- 500,000 transactions

- 1,000,000 transactions

All generated information is synthetic and does not represent real financial records.

### Dataset and Workload Assumptions

The challenge materials received for this implementation provided the problem statement and submission guidelines, but did not include separate SQL workload files, CSV datasets, or table definitions.

Therefore, the banking domain, analytical schema, synthetic data generator, and five SQL workloads in this project were designed for the SmartBank Analytics implementation based on the challenge objectives. They are implementation assumptions, not schemas or workloads supplied by YottaFlex.

The project uses these datasets and workloads to demonstrate data engineering, validation, analytical query optimization, and performance measurement.

The generated banking records are synthetic and do not represent real production banking data.

## 6. Data Ingestion Layer

**Module:** `src/ingestion/`

**File:** `ingest_data.py`

The ingestion layer reads the generated CSV datasets and loads them into Pandas DataFrames.

Responsibilities:

- Read source CSV files.

- Load datasets into memory.

- Track source file information.

- Attach unique run identifiers.

- Record ingestion metadata.

- Prepare datasets for validation.

Each pipeline execution is associated with a unique run ID.

The ingestion metadata supports traceability by identifying the pipeline run and source file associated with the records.

## 7. Data Validation Layer

**Module:** `src/validation/`

The validation layer contains separate modules for schema validation, business validation, and duplicate handling.

### 7.1 Schema Validation

**File:** `schema_validator.py`

Responsibilities:

- Verify required columns.

- Check expected data types.

- Identify missing required values.

- Validate primary-key fields.

- Detect duplicate primary keys.

### 7.2 Business Validation

**File:** `business_validator.py`

Responsibilities:

- Validate transaction amounts.

- Validate transaction types.

- Validate transaction statuses.

- Validate transaction timestamps.

- Check account relationships.

- Check merchant relationships.

- Check card relationships.

- Validate fraud alert information.

- Validate risk scores.

### 7.3 Duplicate Handling

**File:** `duplicate_handler.py`

Responsibilities:

- Identify duplicate primary keys.

- Retain the first occurrence.

- Reject subsequent duplicate records.

- Record rejection reasons.

- Preserve rejected records for investigation.

### 7.4 Validation Output

The validation process separates records into:

- Valid records.

- Rejected records.

Rejected records are retained separately rather than silently discarded.

This allows invalid data to be inspected and traced to its source.

## 8. Data Transformation Layer

**Module:** `src/transformation/`

**File:** `transform_data.py`

The transformation layer prepares validated records for analytical processing.

Responsibilities:

- Standardize column names.

- Normalize customer email addresses.

- Standardize customer city and state values.

- Convert transaction amounts into numeric values.

- Parse transaction timestamps.

- Standardize transaction timestamps to UTC.

- Generate transaction date.

- Generate transaction month.

- Generate transaction year.

- Derive debit amounts.

- Derive credit amounts.

### Derived Transaction Attributes

| Attribute | Description |

|---|---|

| transaction_date | Date derived from transaction timestamp |

| transaction_month | Transaction month |

| transaction_year | Transaction year |

| debit_amount | Derived debit transaction amount |

| credit_amount | Derived credit transaction amount |

These attributes support downstream analytical workloads.

## 9. Data Storage and Publishing Layer

The data publishing process is implemented as part of the main pipeline.

**Module:** `src/`

**File:** `main.py`

The publishing process stores validated and transformed datasets in Parquet format.

### Storage Locations

| Storage Location | Purpose |

|---|---|

| `data/raw/` | Original generated CSV files |

| `data/<run_id>/processed/` | Run-specific validated and transformed datasets |

| `data/<run_id>/rejected/` | Run-specific rejected records and validation details |

| `data/smartbank.duckdb` | Local analytical database |

### Safe Publishing Process

The pipeline uses a temporary directory before publishing final run-specific output.

The publishing process:

1. Creates a temporary output directory.

2. Writes processed Parquet datasets.

3. Writes rejected datasets when available.

4. Verifies expected output files.

5. Checks that the final run directory does not already exist.

6. Renames the temporary directory to the final run-specific directory.

7. Removes the temporary directory if publishing fails.

This approach helps prevent incomplete output from being treated as a successfully published run.

Each run has a separate output directory, preserving previous run results.

### Why Parquet?

Parquet is a columnar storage format suitable for analytical workloads.

Benefits include:

- Efficient column-based access.

- Compression support.

- Reduced unnecessary data reading.

- Compatibility with analytical query engines.

## 10. Analytical Database Layer

**Module:** `src/database/`

**File:** `duckdb_manager.py`

DuckDB provides the analytical database used for SQL workload execution and benchmarking.

Responsibilities:

- Read processed Parquet datasets.

- Load datasets into analytical tables.

- Maintain the local analytical database.

- Execute analytical SQL workloads.

- Support query performance measurement.

- Verify analytical table record counts.

**Database location:** `data/smartbank.duckdb`

### Analytical Tables

| Table | Description |

|---|---|

| customers | Customer information |

| branches | Branch information |

| accounts | Account information |

| merchants | Merchant information |

| cards | Card information |

| transactions | Transaction information |

| fraud_alerts | Fraud alert information |

The database contains seven analytical tables representing the banking entities generated by the data pipeline.

### Transactional Database Publishing and Recovery

DuckDB publishing is performed inside a database transaction. The publisher validates that all seven required processed Parquet files are present before modifying the database, then replaces the analytical tables and commits only after all table loads complete.

If a table load fails, the transaction is rolled back so that the previously published database contents remain available. An automated test uses an invalid Parquet input to verify that a failed publish does not replace the existing database contents.

This protects the database publishing step from a partially completed table refresh. It does not provide historical table snapshots or incremental merge processing; the current implementation replaces the seven analytical tables from a selected processed run.

## 11. SQL Analytics and Optimization Layer

**Module:** `src/optimization/`

This layer evaluates baseline analytical queries and their optimized versions.

The project contains five analytical workloads.

### Q1 - Monthly Transaction Analysis

**Business question:**

What is the monthly transaction volume and value by transaction type and status?

**Optimization:**

Uses precomputed transaction year and month attributes instead of repeatedly extracting them from timestamps.

### Q2 - Customer Transaction Analysis

**Business question:**

What is the transaction activity and financial performance of each customer?

**Optimization:**

Pre-aggregates transaction information by customer before joining customer details.

This reduces the amount of transaction-level data involved in the subsequent customer join.

### Q3 - Branch Financial Performance

**Business question:**

What is the transaction performance of each bank branch?

**Optimization:**

Pre-aggregates transaction information by account before joining account and branch details.

### Q4 - Merchant Payment Analysis

**Business question:**

What is the successful payment volume and value for each merchant?

**Optimization:**

Filters successful transactions and pre-aggregates merchant transaction metrics before joining merchant details.

### Q5 - Daily Debit and Credit Summary

**Business question:**

What are the daily debit and credit totals?

**Final implementation:**

Preserves the baseline IST date calculation to maintain identical business-day results.

The final Q5 SQL does not introduce a distinct query rewrite. Its lower measured execution time is documented as an observed benchmark result rather than a proven optimization.

## 12. SQL Correctness Validation

**File:** `src/optimization/compare_queries.py`

The correctness validation module compares baseline and optimized SQL results.

Validation includes:

- Column consistency.

- Result row counts.

- Business key consistency.

- Numeric value comparison.

- Configured numeric tolerance.

### Current Validation Results

| Query | Baseline Rows | Optimized Rows | Result |

|---|---:|---:|---|

| Q1 | 416 | 416 | PASS |

| Q2 | 25,000 | 25,000 | PASS |

| Q3 | 10 | 10 | PASS |

| Q4 | 300 | 300 | PASS |

| Q5 | 1,464 | 1,464 | PASS |

All five optimized queries passed correctness validation.

## 13. Performance Benchmarking Layer

The benchmarking layer measures the execution performance of baseline and optimized SQL queries.

### Baseline Benchmark

**File:** `src/optimization/benchmark_sql.py`

Responsibilities:

- Execute baseline SQL queries.

- Perform warm-up execution.

- Measure query execution times.

- Calculate median and average times.

- Save execution plans.

- Generate baseline benchmark results.

### Optimized Benchmark

**File:** `src/optimization/benchmark_optimized_sql.py`

Responsibilities:

- Execute optimized SQL queries.

- Perform warm-up execution.

- Measure query execution times.

- Calculate median and average times.

- Save optimized execution plans.

- Generate optimized benchmark results.

### Performance Consolidation

**File:** `src/optimization/consolidate_performance_reports.py`

Responsibilities:

- Read baseline benchmark results.

- Read optimized benchmark results.

- Compare execution times.

- Calculate improvement percentages.

- Generate a consolidated performance report.

### Benchmark Configuration

- Database: DuckDB

- Transaction records: 500,000

- Warm-up executions: 1 per query

- Measured executions: 3 per query

- Comparison metric: Median execution time

### Current Performance Results

| Query | Baseline (sec) | Optimized (sec) | Measured Difference |

|---|---:|---:|---:|

| Q1 | 0.036705 | 0.011514 | 68.63% |

| Q2 | 0.092689 | 0.062242 | 32.85% |

| Q3 | 0.046677 | 0.030332 | 35.02% |

| Q4 | 0.015918 | 0.011917 | 25.14% |

| Q5 | 0.020430 | 0.017314 | 15.25% |

These are local experimental measurements based on three repetitions, not production performance guarantees.

Q5's final SQL uses the same date conversion as the baseline. Its lower measured median should not be interpreted as a proven SQL optimization.

### Performance Report Locations

Performance reports and execution plans are stored under:

`reports/performance/`

Important artifacts include:

- `baseline_results.csv`

- `optimized_results.csv`

- `consolidated_performance_report.csv`

- `optimization_summary.md`

- Baseline Q1–Q5 execution plans

- Optimized Q1–Q5 execution plans

- `validation_benchmark.json`

## 14. Monitoring and Run Tracking Layer

**Module:** `src/monitoring/`

**File:** `run_tracker.py`

The monitoring layer provides execution-level traceability.

Each pipeline run generates a unique identifier.

Tracked information includes:

- Run ID

- Start timestamp

- End timestamp

- Execution status

- Input record count

- Output record count

- Rejected record count

- Errors

- Execution duration

Run metadata is stored as JSON files under `logs/`.

This information helps identify pipeline failures, monitor execution, and review record reconciliation.

## 15. Testing Architecture

The project uses Pytest for automated testing.

The test suite covers:

- Configuration loading.

- Data ingestion and pipeline execution.

- Schema validation.

- Business validation.

- Duplicate handling.

- Data transformation.

- Failure handling.

- Temporary output cleanup.

- Run tracking.

- DuckDB publishing.

- Repeatable database publishing.

- Pipeline run isolation.

SQL correctness validation is performed separately through the query comparison module.

### Current Automated Test Results

| Metric | Result |

|---|---:|

| Total tests | 83 |

| Passed | 83 |

| Failed | 0 |

| Execution time | 3.09 seconds |

All 83 automated tests passed in the latest recorded test execution.

## 16. Data Quality and Reconciliation

Data quality is maintained through schema validation, business validation, duplicate detection, and foreign-key checks.

Invalid records are separated from valid records and retained for investigation.

The pipeline records input, output, and rejected record counts to support reconciliation.

Run-specific directories provide traceability for individual pipeline executions.

The latest successful pipeline execution recorded:

| Metric | Records |

|---|---:|

| Input records | 612,610 |

| Output records | 612,610 |

| Rejected records | 0 |

The seven DuckDB analytical tables were verified against the processed dataset counts.

## 17. Timezone Architecture

The transformation pipeline standardizes transaction timestamps to UTC.

The DuckDB database session uses the `Asia/Calcutta` timezone.

During Q5 correctness validation, the precomputed UTC transaction date produced different calendar dates from the baseline IST date calculation.

The final Q5 implementation preserves the baseline IST business-day definition.

A timezone-consistent precomputed business-date attribute is a future improvement.

## 18. End-to-End Execution Flow

The complete project execution sequence is:

1. Generate synthetic banking datasets.

2. Execute the ingestion module.

3. Validate dataset schemas.

4. Apply business validation rules.

5. Detect and handle duplicates.

6. Transform valid datasets.

7. Publish valid and rejected datasets.

8. Store processed datasets in Parquet format.

9. Load processed data into DuckDB.

10. Execute baseline SQL benchmarks.

11. Execute optimized SQL benchmarks.

12. Compare baseline and optimized query results.

13. Consolidate performance results.

14. Review reports and execution plans.

15. Execute automated tests.

## 19. Reliability and Future Improvements

Current implementation features include:

- Unique run identifiers.

- Run-specific output directories.

- Temporary-directory-based output publishing.

- Protection against overwriting an existing run directory.

- Failure status and error recording.

- Separate rejected-record storage.

- Repeatable DuckDB table publishing.

- Automated tests for publishing failures and repeat execution.

Future architecture improvements include:

- More advanced retry and recovery handling.

- Incremental data ingestion.

- More detailed monitoring.

- Improved automated reconciliation.

- Timezone-consistent business-date attributes.

- Larger-scale performance testing.

- Additional query optimization techniques.

## 20. Conclusion

The SmartBank Analytics architecture separates banking data engineering responsibilities into modular components.

The system demonstrates synthetic data generation, data ingestion, validation, transformation, Parquet storage, DuckDB analytics, SQL correctness validation, and performance benchmarking.

The architecture prioritizes reproducibility, data quality, traceability, analytical correctness, and measurable query performance.

The implementation provides a foundation for evaluating analytical SQL workloads and demonstrating practical data engineering and query optimization techniques.

---

**Project:** SmartBank Analytics  

**Domain:** Banking and Financial Analytics  

**Database:** DuckDB  

**Programming Language:** Python 3.12  

**Storage:** CSV and Parquet