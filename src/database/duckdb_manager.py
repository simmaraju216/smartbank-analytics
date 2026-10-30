
import duckdb

from pathlib import Path

from config.settings import PROJECT_ROOT, DUCKDB_PATH


# ==================================================
# CONFIGURATION
# ==================================================

DATA_DIR = PROJECT_ROOT / "data"

DATABASE_PATH = DUCKDB_PATH

TABLE_NAMES = [
    "customers",
    "branches",
    "accounts",
    "merchants",
    "cards",
    "transactions",
    "fraud_alerts"
]


# ==================================================
# FIND LATEST PIPELINE OUTPUT
# ==================================================

def get_latest_processed_directory():

    run_directories = sorted(
        DATA_DIR.glob("RUN_*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    for run_directory in run_directories:

        processed_directory = run_directory / "processed"

        if not processed_directory.is_dir():
            continue

        required_files = [
            processed_directory / f"{name}.parquet"
            for name in TABLE_NAMES
        ]

        if all(file.is_file() for file in required_files):
            return processed_directory

    raise FileNotFoundError(
        "No complete pipeline output found. "
        "Run the banking pipeline first."
    )


# ==================================================
# CONNECT TO DUCKDB
# ==================================================

def get_connection():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return duckdb.connect(str(DATABASE_PATH))


# ==================================================
# VALIDATE INPUT FILES
# ==================================================

def validate_processed_files(processed_directory):

    missing_files = [
        processed_directory / f"{table_name}.parquet"
        for table_name in TABLE_NAMES
        if not (
            processed_directory / f"{table_name}.parquet"
        ).is_file()
    ]

    if missing_files:

        missing_names = [
            file.name for file in missing_files
        ]

        raise FileNotFoundError(
            f"Missing required Parquet files: {missing_names}"
        )


# ==================================================
# CREATE ANALYTICAL TABLES
# ==================================================

def create_analytical_tables(processed_directory=None):

    if processed_directory is None:
        processed_directory = get_latest_processed_directory()

    processed_directory = Path(processed_directory)

    if not processed_directory.is_dir():
        raise FileNotFoundError(
            f"Processed directory not found: {processed_directory}"
        )

    # Validate all files before modifying the database.
    validate_processed_files(processed_directory)

    connection = get_connection()

    table_counts = {}

    try:

        print("\nSMARTBANK DUCKDB DATABASE")
        print("=" * 60)

        print(f"Database: {DATABASE_PATH}")
        print(f"Source:   {processed_directory}")

        # Start an atomic publishing transaction.
        connection.execute("BEGIN TRANSACTION")

        try:

            for table_name in TABLE_NAMES:

                parquet_file = (
                    processed_directory / f"{table_name}.parquet"
                )

                connection.execute(
                    f"""
                    CREATE OR REPLACE TABLE {table_name} AS
                    SELECT *
                    FROM read_parquet(?)
                    """,
                    [str(parquet_file)]
                )

                count = connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]

                table_counts[table_name] = count

            # Commit only after all tables are published.
            connection.execute("COMMIT")

        except Exception:

            # Roll back all table replacements on failure.
            connection.execute("ROLLBACK")

            raise

        for table_name, count in table_counts.items():

            print(
                f"{table_name:<20} {count:>12,} records"
            )

        print("\nALL ANALYTICAL TABLES PUBLISHED SUCCESSFULLY")

        return table_counts

    finally:
        connection.close()


# ==================================================
# VERIFY DATABASE
# ==================================================

def verify_database():

    connection = get_connection()

    try:

        print("\nDATABASE VERIFICATION")
        print("=" * 60)

        tables = connection.execute(
            "SHOW TABLES"
        ).fetchall()

        database_counts = {}

        for (table_name,) in tables:

            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            database_counts[table_name] = count

            print(
                f"{table_name:<20} {count:>12,} records"
            )

        missing_tables = (
            set(TABLE_NAMES) - set(database_counts)
        )

        if missing_tables:

            raise RuntimeError(
                f"Missing analytical tables: {sorted(missing_tables)}"
            )

        print("\nDATABASE VERIFICATION SUCCESSFUL")

        return database_counts

    finally:
        connection.close()


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    create_analytical_tables()

    verify_database()
