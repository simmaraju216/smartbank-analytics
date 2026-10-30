# SmartBank Analytics - Sample Data

## Purpose

This directory contains a small synthetic banking dataset for demonstrating the SmartBank Analytics data pipeline.

The sample dataset is separate from the larger generated datasets under `data/raw/`.

## Sample Input

Location: `sample_data/input/`

| Dataset | Records |
|---|---:|
| customers.csv | 100 |
| branches.csv | 10 |
| accounts.csv | 350 |
| merchants.csv | 100 |
| cards.csv | 100 |
| transactions.csv | 1,000 |
| fraud_alerts.csv | 50 |
| **Total** | **1,710** |

## Sample Output

Location: `sample_data/output/`

The retained successful sample run is:

`RUN_20261030_162257_8130076e/`

It contains seven processed Parquet files under the `processed/` directory.

The run produced 1,710 processed records and zero rejected records. No rejected Parquet files were generated because there were no rejected records.

## Reproduce the Sample

Run these commands from the project root.

### 1. Generate sample input

```powershell
python -m src.generators.generate_banking_data --transactions 1000 --customers 100 --seed 42 --output-dir sample_data/input
```

### 2. Execute the pipeline

```powershell
python -c "from src.main import run_pipeline; result = run_pipeline(input_dir='sample_data/input', output_dir='sample_data/output'); print(result['status'])"
```

The pipeline creates a new run-specific directory. It does not overwrite an existing run directory.

## Data Characteristics

- All records are synthetic.
- Customer and transaction identifiers are generated using the configured seed and record sequence.
- The sample contains customers, branches, accounts, merchants, cards, transactions, and fraud alerts.
- Fraud alerts represent synthetic risk alerts, not confirmed fraud cases.
- Transaction timestamps are generated within the preceding year.

## Verified Sample Execution

| Metric | Result |
|---|---:|
| Input records | 1,710 |
| Processed records | 1,710 |
| Rejected records | 0 |
| Errors | 0 |
| Pipeline status | SUCCESS |
| Duration | 0.266 seconds |

### Record Reconciliation

```text
Input = Processed + Rejected

1,710 = 1,710 + 0
```

## Important Notes

- The sample dataset is intended for quick setup and demonstration.
- Performance benchmarking uses a larger synthetic dataset.
- Performance results are documented separately under `reports/performance/`.
- Because timestamps use a moving date window, regenerating the dataset later may not produce byte-for-byte identical files.