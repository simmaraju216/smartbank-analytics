# SmartBank Analytics

## Banking Data Engineering and SQL Performance Optimization

## 1. Project Overview

SmartBank Analytics is a Python-based banking analytics pipeline designed to process synthetic banking data, validate data quality, transform datasets, and optimize analytical SQL workloads.

The project demonstrates how inefficient table scans, joins, aggregations, and filtering operations can be analyzed and improved using DuckDB and Parquet.

**Project Domain:** Banking and Financial Analytics  
**Database:** DuckDB  
**Programming Language:** Python 3.12  
**Storage:** CSV and Parquet

## 2. Business Problem

Banking analytics systems process large volumes of financial transactions. Inefficient analytical queries can increase execution time and consume unnecessary computing resources.

This project addresses the following challenges:

- Inefficient table scans
- Expensive joins
- Repeated aggregations
- Filtering inefficiencies
- Data quality problems
- Duplicate records
- Incorrect analytical results
- Pipeline execution traceability

The objective is to establish a measurable performance baseline, implement SQL optimizations, validate correctness, and document performance results.

## 3. Project Objectives

1. Generate synthetic banking datasets.
2. Implement a modular data ingestion pipeline.
3. Validate schemas and business rules.
4. Identify duplicate and invalid records.
5. Transform and publish analytical datasets.
6. Store processed data in Parquet format.
7. Use DuckDB for analytical SQL workloads.
8. Identify inefficient SQL operations.
9. Develop optimized SQL queries.
10. Compare baseline and optimized query results.
11. Benchmark query execution performance.
12. Document measurable results and design decisions.

## 4. Key Features

- Synthetic banking data generation
- CSV data ingestion
- Schema validation
- Business-rule validation
- Primary-key duplicate detection
- Foreign-key validation
- Invalid-record quarantine
- Data transformation
- Parquet storage
- DuckDB analytical database
- Five baseline SQL workloads
- Five optimized SQL workloads
- SQL correctness comparison
- Execution-time benchmarking
- Execution-plan analysis
- Pipeline run tracking
- Performance reporting
- Automated testing
- Run-specific output publishing
- Database publishing rollback
- Repeatable and idempotent database publishing

## 5. Technology Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12.0 | Pipeline implementation |
| Pandas | 3.1.0 | Data processing |
| NumPy | 2.5.4 | Numerical operations |
| Faker | 40.44.0 | Synthetic data generation |
| PyArrow | 26.0.0 | Parquet storage |
| DuckDB | 2.0.0 | Analytical database |
| Pytest | 9.2.0 | Automated testing |
| Matplotlib | 3.11.2 | Visualization |
| python-dotenv | 1.2.4 | Environment configuration |
| pytz | 2026.6 | Timezone support |

These are the versions installed and verified in the development environment. Direct dependencies are listed in `requirements.txt`.

## 6. Banking Dataset

The project uses synthetic banking data.

### Dataset Tables

| Table | Description |
|---|---|
| customers | Customer information |
| branches | Bank branch information |
| accounts | Customer account information |
| merchants | Merchant information |
| cards | Card information |
| transactions | Banking transaction records |
| fraud_alerts | Synthetic transaction risk alerts |

### Current Dataset Size

| Dataset | Records |
|---|---:|
| Customers | 25,000 |
| Branches | 10 |
| Accounts | 37,500 |
| Merchants | 100 |
| Cards | 25,000 |
| Transactions | 500,000 |
| Fraud alerts | 25,000 |
| **Total** | **612,610** |

All records are synthetic and do not represent real banking customers or transactions.

### Dataset and Workload Assumptions

YottaFlex provided the project problem statement and submission guidelines but did not provide separate SQL workload files, CSV datasets, or table schema definitions.

Therefore, the Banking and Financial Analytics domain, seven synthetic banking tables, and five analytical SQL workloads were designed for this project based on the stated challenge objectives.

The workloads demonstrate analytical operations involving date extraction, joins, filtering, and aggregations, followed by query optimization, correctness validation, and performance measurement.

A fixed random seed is used for synthetic data generation. Exact generated files can vary between generation dates because some timestamp values are relative to the generation date.

These project-designed workloads are an implementation of the challenge requirements, not externally supplied production workloads.

## 7. Project Architecture

```text
Synthetic Data Generator
        |
        v
    Raw CSV Files
        |
        v
    Data Ingestion
        |
        v
   Schema Validation
        |
        v
   Business Validation
        |
        v
   Duplicate Detection
        |
        v
   Valid / Rejected Data
        |
        v
   Data Transformation
        |
        v
     Parquet Storage
        |
        v
     DuckDB Database
        |
        v
   Baseline SQL Queries
        |
        v
   Optimized SQL Queries
        |
        v
   Correctness Validation
        |
        v
   Performance Benchmarking
        |
        v
     Performance Reports
```

## 8. Project Structure

```text
YottaFlex-Banking-Analytics/
|
|-- config/
|   |-- __init__.py
|   |-- settings.py
|
|-- data/
|   |-- raw/
|   |-- RUN_<run_id>/
|   |   |-- processed/
|   |   |-- rejected/
|   |-- smartbank.duckdb
|
|-- docs/
|   |-- ai_prompt_history.md
|   |-- architecture.md
|   |-- business_rules.md
|   |-- data_dictionary.md
|   |-- design_decisions.md
|   |-- query_optimization_analysis.md
|
|-- reports/
|   |-- performance/
|   |   |-- baseline_results.csv
|   |   |-- optimized_results.csv
|   |   |-- consolidated_performance_report.csv
|   |   |-- optimization_summary.md
|   |   |-- validation_benchmark.json
|   |   |-- Q1-Q5 execution plans
|   |
|   |-- pytest_output.txt
|
|-- sample_data/
|   |-- input/
|   |   |-- customers.csv
|   |   |-- branches.csv
|   |   |-- accounts.csv
|   |   |-- merchants.csv
|   |   |-- cards.csv
|   |   |-- transactions.csv
|   |   |-- fraud_alerts.csv
|   |
|   |-- output/
|   |   |-- RUN_<run_id>/
|   |       |-- processed/
|   |       |-- rejected/
|   |
|   |-- README.md
|
|-- sql/
|   |-- baseline/
|   |   |-- q1_monthly_transactions.sql
|   |   |-- q2_customer_analysis.sql
|   |   |-- q3_branch_performance.sql
|   |   |-- q4_merchant_analysis.sql
|   |   |-- q5_daily_debit_credit.sql
|   |
|   |-- optimized/
|       |-- q1_monthly_transactions.sql
|       |-- q2_customer_analysis.sql
|       |-- q3_branch_performance.sql
|       |-- q4_merchant_analysis.sql
|       |-- q5_daily_debit_credit.sql
|
|-- src/
|   |-- database/
|   |   |-- duckdb_manager.py
|   |
|   |-- generators/
|   |   |-- generate_banking_data.py
|   |
|   |-- ingestion/
|   |   |-- ingest_data.py
|   |
|   |-- monitoring/
|   |   |-- run_tracker.py
|   |
|   |-- optimization/
|   |   |-- benchmark_sql.py
|   |   |-- benchmark_optimized_sql.py
|   |   |-- benchmark_validation.py
|   |   |-- compare_queries.py
|   |   |-- consolidate_performance_reports.py
|   |
|   |-- transformation/
|   |   |-- transform_data.py
|   |
|   |-- validation/
|   |   |-- business_validator.py
|   |   |-- duplicate_handler.py
|   |   |-- schema_validator.py
|   |
|   |-- __init__.py
|   |-- main.py
|
|-- tests/
|   |-- test_business_validator.py
|   |-- test_config.py
|   |-- test_duckdb_manager.py
|   |-- test_duplicate_handler.py
|   |-- test_idempotency.py
|   |-- test_ingestion.py
|   |-- test_pipeline.py
|   |-- test_run_tracker.py
|   |-- test_schema_validator.py
|   |-- test_transformation.py
|
|-- .env.example
|-- .gitignore
|-- project_structure.txt
|-- pytest.ini
|-- requirements.txt
|-- README.md
```

Generated Python cache files, virtual environments, local databases, and large generated datasets are excluded from the public source repository. The sample input and selected sample output are retained for reproducibility.

## 9. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/simmaraju216/smartbank-analytics.git
cd YottaFlex-Banking-Analytics
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Review `.env.example` and create a local `.env` file.

Example configuration:

```env
PROJECT_NAME=SmartBankAnalytics
RANDOM_SEED=42
DATA_SIZE=10000
DUCKDB_PATH=data/smartbank.duckdb
LOG_LEVEL=INFO
```

Do not commit passwords, API keys, or other secrets.

## 10. Generate Synthetic Banking Data

Generate 500,000 transactions:

```bash
python -m src.generators.generate_banking_data --transactions 500000
```

Generate a smaller dataset for testing:

```bash
python -m src.generators.generate_banking_data --transactions 10000
```

The generator also supports other configurable transaction volumes.

Generated CSV files are stored under:

```text
data/raw/
```

The configured random seed supports repeatable pseudo-random data generation. Generated timestamps may vary depending on the generation date.

## 11. Run the Data Pipeline

Execute:

```bash
python -m src.main
```

The pipeline performs:

1. Data ingestion
2. Schema validation
3. Business validation
4. Duplicate handling
5. Foreign-key validation
6. Data transformation
7. Valid and rejected record publishing
8. Run tracking and reconciliation

Run details are recorded under:

```text
logs/
```

Processed and rejected datasets are stored in run-specific directories:

```text
data/<run_id>/processed/
data/<run_id>/rejected/
```

Each execution receives a unique run ID to support traceability.

### Run the Pipeline Using the Sample Dataset

```powershell
python -c "from src.main import run_pipeline; result = run_pipeline(input_dir='sample_data/input', output_dir='sample_data/output'); print(result['metrics'])"
```

### Latest Recorded Full Pipeline Execution

| Metric | Records |
|---|---:|
| Input records | 612,610 |
| Output records | 612,610 |
| Rejected records | 0 |
| Errors | 0 |
| Execution time | 6.943 seconds |
| Status | SUCCESS |

Run ID:

```text
RUN_20261030_143804_73745c37
```

The corresponding run report is stored in the local `logs/` directory.

This is a recorded full-dataset execution; it is separate from the latest sample pipeline run and should be treated as historical execution evidence.

## 12. Load Data into DuckDB

Execute:

```bash
python -m src.database.duckdb_manager
```

The analytical database is stored at:

```text
data/smartbank.duckdb
```

The database contains seven analytical tables:

- customers
- branches
- accounts
- merchants
- cards
- transactions
- fraud_alerts

The database manager loads the latest processed Parquet datasets and verifies table record counts.

Database publishing uses a transaction. If publishing fails, the transaction is rolled back so previously published table contents remain available.

Repeated publishing replaces analytical tables rather than appending duplicate rows. This supports repeatable publishing, but does not maintain historical database snapshots.

## 13. SQL Performance Optimization

Five analytical SQL workloads were implemented based on the challenge objectives.

| Query | Business Question |
|---|---|
| Q1 | What is the monthly transaction volume and value? |
| Q2 | What is the transaction activity of each customer? |
| Q3 | What is the financial performance of each branch? |
| Q4 | What is the successful payment performance of each merchant? |
| Q5 | What are the daily debit and credit totals? |

### Baseline SQL Queries

```text
sql/baseline/
```

### Optimized SQL Queries

```text
sql/optimized/
```

### Optimization Techniques

**Q1 - Monthly Transaction Analysis**

Uses precomputed transaction year and month attributes instead of repeatedly extracting them from timestamps.

**Q2 - Customer Analysis**

Pre-aggregates transaction information by customer before joining customer details.

**Q3 - Branch Performance**

Pre-aggregates transaction information by account before joining account and branch details.

**Q4 - Merchant Analysis**

Filters successful transactions and aggregates merchant transaction metrics before joining merchant details.

**Q5 - Daily Debit and Credit Summary**

Preserves the baseline IST date calculation to maintain identical business-day results. No distinct SQL rewrite is claimed for this query.

## 14. SQL Correctness Validation

Run:

```bash
python -m src.optimization.compare_queries
```

### Validation Results

| Query | Baseline Rows | Optimized Rows | Status |
|---|---:|---:|---|
| Q1 | 416 | 416 | PASS |
| Q2 | 25,000 | 25,000 | PASS |
| Q3 | 10 | 10 | PASS |
| Q4 | 300 | 300 | PASS |
| Q5 | 1,464 | 1,464 | PASS |

**All five baseline and optimized query comparisons passed.**

The comparison checks result structure, row counts, keys, and numeric values within the configured tolerance.

## 15. SQL Performance Benchmarking

### Run Baseline Benchmarks

```bash
python -m src.optimization.benchmark_sql
```

### Run Optimized Benchmarks

```bash
python -m src.optimization.benchmark_optimized_sql
```

### Generate Consolidated Performance Report

```bash
python -m src.optimization.consolidate_performance_reports
```

### Benchmark Methodology

- Database: DuckDB
- Transaction records: 500,000
- Warm-up executions: 1 per query
- Measured executions: 3 per query
- Performance metric: Median execution time
- Execution plans: Saved for analysis

### Performance Results

| Query | Baseline (sec) | Optimized (sec) | Measured Improvement |
|---|---:|---:|---:|
| Q1 - Monthly transactions | 0.036705 | 0.011514 | 68.63% |
| Q2 - Customer analysis | 0.092689 | 0.062242 | 32.85% |
| Q3 - Branch performance | 0.046677 | 0.030332 | 35.02% |
| Q4 - Merchant analysis | 0.015918 | 0.011917 | 25.14% |
| Q5 - Daily debit/credit | 0.020430 | 0.017314 | 15.25% |

**Interpretation:** Q1-Q4 use identifiable SQL optimization techniques. Q5 recorded a lower median execution time, but its final SQL uses the same date conversion as the baseline. Its timing difference is an observed benchmark result, not a proven SQL optimization.

These are local experimental measurements based on three repetitions, not production performance guarantees. Caching and background system activity may affect timings.

### Key Findings

- Q1 recorded the highest measured improvement at 68.63%.
- Q2 improved by 32.85%.
- Q3 improved by 35.02%.
- Q4 improved by 25.14%.
- Q5 recorded a 15.25% lower median time without a distinct SQL rewrite.

### Performance Report Locations

```text
reports/performance/
    |
    |-- baseline_results.csv
    |-- optimized_results.csv
    |-- consolidated_performance_report.csv
    |-- optimization_summary.md
    |-- validation_benchmark.json
    |-- Q1-Q5 baseline execution plans
    |-- Q1-Q5 optimized execution plans
```

## 16. Run Automated Tests

Execute:

```bash
python -m pytest tests/ -v
```

The automated test suite covers:

- CSV data ingestion
- Ingestion metadata and run tracking
- Missing input directory and required files
- Malformed CSV handling
- Empty dataset ingestion
- Schema validation
- Business-rule validation
- Duplicate handling
- Null primary-key handling
- Foreign-key validation
- Data transformation
- Pipeline execution
- Failure handling
- Temporary output cleanup
- DuckDB publishing
- Repeatable database publishing
- Identical-input idempotency
- Database publishing rollback
- Invalid Parquet file recovery
- Pipeline run isolation
- Record reconciliation

### Latest Test Results

The complete automated test suite was executed successfully.

| Metric | Result |
|---|---:|
| Python version | 3.12.0 |
| Total tests | 83 |
| Passed | 83 |
| Failed | 0 |
| Execution time | 3.09 seconds |

**All 83 automated tests passed in 3.09 seconds.**

Test execution evidence is available in:

```text
reports/pytest_output.txt
```

Dependency verification:

```bash
python -m pip check
```

Verified result:

```text
No broken requirements found.
```

SQL correctness validation is performed separately through the query comparison module.

## 17. Timezone Handling

The transformation pipeline standardizes transaction timestamps to UTC.

The DuckDB database session uses:

```text
Asia/Calcutta (IST)
```

During Q5 validation, the precomputed UTC transaction date produced different calendar dates from the baseline query's IST date calculation.

The final Q5 query preserves the baseline's IST business-day definition to ensure correctness.

A timezone-consistent precomputed business-date column is a future improvement.

## 18. Documentation

| Document | Description |
|---|---|
| `docs/architecture.md` | Pipeline architecture |
| `docs/data_dictionary.md` | Dataset tables and columns |
| `docs/business_rules.md` | Data validation and business rules |
| `docs/query_optimization_analysis.md` | Detailed SQL optimization analysis |
| `docs/design_decisions.md` | Architecture and technical decisions |
| `docs/ai_prompt_history.md` | AI-assisted development history |
| `reports/performance/optimization_summary.md` | Performance results and findings |
| `sample_data/README.md` | Sample dataset and reproduction instructions |

## 19. Limitations and Future Improvements

Current limitations and possible improvements include:

- Increase benchmark repetitions.
- Test larger datasets.
- Improve timezone-consistent business-date handling.
- Expand automated reconciliation.
- Evaluate incremental loading and cross-run deduplication.
- Expand retry and interrupted-run recovery testing.
- Improve pipeline observability.
- Evaluate additional query optimization techniques.
- Expand negative test scenarios for late-arriving data and other edge cases where not yet covered.

These limitations are documented to distinguish implemented functionality from future improvements.

## 20. Conclusion

SmartBank Analytics demonstrates a reproducible banking data engineering and analytics workflow.

The project combines synthetic data generation, data validation, transformation, Parquet storage, DuckDB analytics, SQL correctness testing, and performance benchmarking.

All five optimized query outputs passed correctness validation, and all five recorded lower median execution times in the current local benchmark. Q5's timing difference is not claimed as a proven SQL optimization.

The project emphasizes measurable performance analysis, analytical correctness, data quality, and traceable pipeline execution.

## 21. AI Assistance and Transparency

AI tools were used as development assistants for:

- Understanding the challenge requirements.
- Planning the banking analytics architecture.
- Selecting the banking analytics domain.
- Designing synthetic banking datasets.
- Reviewing SQL optimization approaches.
- Debugging Python and DuckDB errors.
- Designing automated tests.
- Improving project documentation.

AI assistance supported development and problem-solving. The developer reviewed, tested, and validated the implementation and is responsible for understanding the code, dependencies, design decisions, and limitations.

The AI prompt history is maintained in:

```text
docs/ai_prompt_history.md
```

**Prompt history completeness:** The current prompt-history document organizes representative prompts and major prompt categories. It must be reconciled with the actual prompts submitted during development, including relevant follow-up prompts and prompts submitted to other AI tools, before submission. It should not be described as exhaustive until that review is complete.

AI responses are optional according to the submission FAQ.

The developer remains responsible for explaining and defending the final implementation during evaluation.

---

**Project:** SmartBank Analytics  
**Domain:** Banking and Financial Analytics  
**Database:** DuckDB  
**Language:** Python 3.12  
**Storage:** CSV and Parquet
