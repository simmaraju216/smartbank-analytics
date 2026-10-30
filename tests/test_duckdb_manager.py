
import duckdb
import pandas as pd
import pytest

from src.database.duckdb_manager import (
    create_analytical_tables,
    verify_database,
    TABLE_NAMES
)


# ==================================================
# FIXTURE: SAMPLE PROCESSED DATA
# ==================================================

@pytest.fixture
def sample_processed_directory(tmp_path, monkeypatch):

    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    # Create a small Parquet file for every required table.
    for table_name in TABLE_NAMES:

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "value": [100, 200, 300]
        })

        df.to_parquet(
            processed_dir / f"{table_name}.parquet",
            index=False
        )

    # Use a temporary DuckDB database.
    test_db = tmp_path / "test.duckdb"

    monkeypatch.setattr(
        "src.database.duckdb_manager.DATABASE_PATH",
        test_db
    )

    return processed_dir, test_db


# ==================================================
# TEST 1: CREATE ANALYTICAL TABLES
# ==================================================

def test_create_analytical_tables(sample_processed_directory):

    processed_dir, test_db = sample_processed_directory

    counts = create_analytical_tables(processed_dir)

    assert len(counts) == len(TABLE_NAMES)

    for table_name in TABLE_NAMES:
        assert counts[table_name] == 3

    assert test_db.exists()


# ==================================================
# TEST 2: VERIFY DATABASE
# ==================================================

def test_verify_database(sample_processed_directory):

    processed_dir, test_db = sample_processed_directory

    create_analytical_tables(processed_dir)

    counts = verify_database()

    assert len(counts) == len(TABLE_NAMES)

    for table_name in TABLE_NAMES:
        assert counts[table_name] == 3


# ==================================================
# TEST 3: MISSING PROCESSED DIRECTORY
# ==================================================

def test_missing_processed_directory_raises_error(tmp_path):

    missing_dir = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        create_analytical_tables(missing_dir)


# ==================================================
# TEST 4: MISSING PARQUET FILE
# ==================================================

def test_missing_parquet_file_raises_error(
    sample_processed_directory
):

    processed_dir, test_db = sample_processed_directory

    missing_file = processed_dir / "transactions.parquet"
    missing_file.unlink()

    with pytest.raises(FileNotFoundError):
        create_analytical_tables(processed_dir)


# ==================================================
# TEST 5: NO COMPLETE PIPELINE OUTPUT
# ==================================================

def test_get_latest_processed_directory_missing_data(
    tmp_path,
    monkeypatch
):

    from src.database.duckdb_manager import (
        get_latest_processed_directory
    )

    monkeypatch.setattr(
        "src.database.duckdb_manager.DATA_DIR",
        tmp_path
    )

    with pytest.raises(FileNotFoundError):
        get_latest_processed_directory()


# ==================================================
# TEST 6: REPEATED PUBLISHING
# ==================================================

def test_repeated_database_publishing_does_not_duplicate_records(
    sample_processed_directory
):

    processed_dir, test_db = sample_processed_directory

    # First publishing.
    first_counts = create_analytical_tables(processed_dir)

    # Change source data without changing its row count.
    updated_data = pd.DataFrame({
        "id": [1, 2, 3],
        "value": [999, 888, 777]
    })

    updated_data.to_parquet(
        processed_dir / "transactions.parquet",
        index=False
    )

    # Second publishing.
    second_counts = create_analytical_tables(processed_dir)

    # Row counts should remain unchanged.
    assert first_counts == second_counts

    # Verify that the latest source data replaced the old data.
    connection = duckdb.connect(str(test_db))

    try:

        actual_rows = connection.execute(
            "SELECT id, value FROM transactions ORDER BY id"
        ).fetchall()

        assert actual_rows == [
            (1, 999),
            (2, 888),
            (3, 777)
        ]

    finally:
        connection.close()

    # Verify final database counts.
    final_counts = verify_database()

    assert final_counts == second_counts


# ==================================================
# TEST 7: DATABASE ROLLBACK ON PUBLISHING FAILURE
# ==================================================

def test_database_publishing_rolls_back_on_failure(
    sample_processed_directory,
    monkeypatch
):

    processed_dir, test_db = sample_processed_directory

    # First publish the original data.
    create_analytical_tables(processed_dir)

    # Save existing transaction records.
    connection = duckdb.connect(str(test_db))

    try:

        original_rows = connection.execute(
            "SELECT id, value FROM transactions ORDER BY id"
        ).fetchall()

    finally:
        connection.close()

    # Wrapper that simulates a failure during publishing.
    class FailingConnection:

        def __init__(self, connection):
            self.connection = connection

        def execute(self, query, parameters=None):

            if "CREATE OR REPLACE TABLE transactions" in query:
                raise RuntimeError(
                    "Simulated publishing failure"
                )

            if parameters is None:
                return self.connection.execute(query)

            return self.connection.execute(query, parameters)

        def close(self):
            self.connection.close()

    # Replace the database manager's connection factory.
    monkeypatch.setattr(
        "src.database.duckdb_manager.get_connection",
        lambda: FailingConnection(
            duckdb.connect(str(test_db))
        )
    )

    # Publishing should fail and trigger transaction rollback.
    with pytest.raises(
        RuntimeError,
        match="Simulated publishing failure"
    ):

        create_analytical_tables(processed_dir)

    # Verify that the previous database contents remain unchanged.
    connection = duckdb.connect(str(test_db))

    try:

        final_rows = connection.execute(
            "SELECT id, value FROM transactions ORDER BY id"
        ).fetchall()

        assert final_rows == original_rows

    finally:
        connection.close()

# ==================================================
# TEST 8: REPEATED PUBLISHING WITH IDENTICAL INPUT
# ==================================================

def test_repeated_identical_publishing_is_idempotent(
    sample_processed_directory
):

    processed_dir, test_db = sample_processed_directory

    # First publishing.
    first_counts = create_analytical_tables(processed_dir)

    connection = duckdb.connect(str(test_db))

    try:
        first_rows = {}

        for table_name in TABLE_NAMES:
            first_rows[table_name] = connection.execute(
                f"SELECT * FROM {table_name} ORDER BY id"
            ).fetchall()

    finally:
        connection.close()

    # Second publishing using exactly the same Parquet files.
    second_counts = create_analytical_tables(processed_dir)

    connection = duckdb.connect(str(test_db))

    try:
        second_rows = {}

        for table_name in TABLE_NAMES:
            second_rows[table_name] = connection.execute(
                f"SELECT * FROM {table_name} ORDER BY id"
            ).fetchall()

    finally:
        connection.close()

    # Verify that repeated publishing does not change counts.
    assert first_counts == second_counts

    # Verify that all seven tables retain identical records.
    assert first_rows == second_rows

    # Verify expected record counts.
    for table_name in TABLE_NAMES:
        assert second_counts[table_name] == 3

# ==================================================
# TEST 9: INVALID PARQUET FILE PRESERVES DATABASE
# ==================================================

def test_invalid_parquet_file_preserves_existing_database(
    sample_processed_directory
):
    processed_dir, test_db = sample_processed_directory

    # First publish valid data.
    original_counts = create_analytical_tables(processed_dir)

    connection = duckdb.connect(str(test_db))

    try:
        original_rows = connection.execute(
            "SELECT * FROM transactions ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    # Corrupt the transactions Parquet file.
    transactions_file = processed_dir / "transactions.parquet"
    transactions_file.write_bytes(b"invalid parquet content")

    # Publishing should fail.
    with pytest.raises(Exception):
        create_analytical_tables(processed_dir)

    # Verify that the previous database contents remain unchanged.
    connection = duckdb.connect(str(test_db))

    try:
        final_rows = connection.execute(
            "SELECT * FROM transactions ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    assert final_rows == original_rows

    # Verify all existing table counts remain unchanged.
    final_counts = verify_database()

    assert final_counts == original_counts
