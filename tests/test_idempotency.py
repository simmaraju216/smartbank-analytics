
from pathlib import Path

from src.main import run_pipeline
from src.monitoring.run_tracker import RunTracker
from tests.test_pipeline import create_sample_datasets


def test_repeated_pipeline_runs_are_isolated(tmp_path):

    first_data = create_sample_datasets()
    second_data = create_sample_datasets()

    first_tracker = RunTracker(
        log_dir=str(tmp_path / "logs")
    )

    second_tracker = RunTracker(
        log_dir=str(tmp_path / "logs")
    )

    first_result = run_pipeline(
        datasets=first_data,
        tracker=first_tracker,
        output_dir=str(tmp_path / "data")
    )

    second_result = run_pipeline(
        datasets=second_data,
        tracker=second_tracker,
        output_dir=str(tmp_path / "data")
    )

    first_output = Path(first_result["output_dir"])
    second_output = Path(second_result["output_dir"])

    assert first_result["status"] == "SUCCESS"
    assert second_result["status"] == "SUCCESS"

    assert first_tracker.run_id != second_tracker.run_id

    assert first_output != second_output

    assert (first_output / "processed" / "transactions.parquet").exists()

    assert (second_output / "processed" / "transactions.parquet").exists()

    assert len(first_result["processed"]["transactions"]) == 2
    assert len(second_result["processed"]["transactions"]) == 2

    assert first_output.exists()
    assert second_output.exists()
