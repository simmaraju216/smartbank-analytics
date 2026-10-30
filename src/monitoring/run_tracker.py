
import json
import os
import uuid

from datetime import datetime, timezone


class RunTracker:

    def __init__(self, log_dir="logs"):

        self.log_dir = log_dir

        os.makedirs(self.log_dir, exist_ok=True)

        self.run_id = (
            "RUN_" + datetime.now(timezone.utc).strftime(
                "%Y%m%d_%H%M%S"
            ) + "_" + uuid.uuid4().hex[:8]
        )

        self.start_time = datetime.now(timezone.utc)

        self.metrics = {
            "run_id": self.run_id,
            "status": "RUNNING",
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "input_records": 0,
            "output_records": 0,
            "rejected_records": 0,
            "errors": []
        }

    def add_input_records(self, count):
        self.metrics["input_records"] += count

    def add_output_records(self, count):
        self.metrics["output_records"] += count

    def add_rejected_records(self, count):
        self.metrics["rejected_records"] += count

    def add_error(self, error):
        self.metrics["errors"].append(str(error))

    def finish(self, status="SUCCESS"):

        end_time = datetime.now(timezone.utc)

        self.metrics["end_time"] = end_time.isoformat()

        self.metrics["duration_seconds"] = round(
            (end_time - self.start_time).total_seconds(),
            3
        )

        self.metrics["status"] = status

        self.save()

    def save(self):

        file_path = os.path.join(
            self.log_dir,
            f"{self.run_id}.json"
        )

        with open(file_path, "w", encoding="utf-8") as file:

            json.dump(
                self.metrics,
                file,
                indent=4
            )

        print(f"Run report saved: {file_path}")
