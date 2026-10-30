
import json

from src.monitoring.run_tracker import RunTracker


def test_run_tracker_generates_unique_ids(tmp_path):

    tracker1 = RunTracker(log_dir=str(tmp_path))
    tracker2 = RunTracker(log_dir=str(tmp_path))

    assert tracker1.run_id != tracker2.run_id


def test_run_tracker_creates_separate_log_files(tmp_path):

    tracker1 = RunTracker(log_dir=str(tmp_path))
    tracker2 = RunTracker(log_dir=str(tmp_path))

    tracker1.finish("SUCCESS")
    tracker2.finish("SUCCESS")

    log_files = list(tmp_path.glob("*.json"))

    assert len(log_files) == 2


def test_run_tracker_records_input_and_output_counts(tmp_path):

    tracker = RunTracker(log_dir=str(tmp_path))

    tracker.add_input_records(100)
    tracker.add_output_records(90)
    tracker.add_rejected_records(10)

    tracker.finish("SUCCESS")

    assert tracker.metrics["input_records"] == 100
    assert tracker.metrics["output_records"] == 90
    assert tracker.metrics["rejected_records"] == 10


def test_run_tracker_saves_errors(tmp_path):

    tracker = RunTracker(log_dir=str(tmp_path))

    tracker.add_error("Invalid transaction amount")

    tracker.finish("FAILED")

    assert tracker.metrics["status"] == "FAILED"
    assert "Invalid transaction amount" in tracker.metrics["errors"]


def test_run_tracker_log_contains_valid_json(tmp_path):

    tracker = RunTracker(log_dir=str(tmp_path))

    tracker.add_input_records(50)
    tracker.finish("SUCCESS")

    log_file = tmp_path / f"{tracker.run_id}.json"

    assert log_file.exists()

    with open(log_file, encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data["run_id"] == tracker.run_id
    assert saved_data["status"] == "SUCCESS"
    assert saved_data["input_records"] == 50


def test_run_tracker_records_execution_duration(tmp_path):

    tracker = RunTracker(log_dir=str(tmp_path))

    tracker.finish("SUCCESS")

    assert tracker.metrics["duration_seconds"] >= 0
    assert tracker.metrics["start_time"] is not None
    assert tracker.metrics["end_time"] is not None
