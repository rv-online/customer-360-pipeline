import json
import unittest
from pathlib import Path

from src.analyzer import build_report, run


class AnalyzerTests(unittest.TestCase):
    def test_build_report_counts_records(self) -> None:
        report = build_report([
            {"customer_id": "c_101", "segment": "growth", "lifetime_value": 1240, "active_days": 18},
            {"customer_id": "c_102", "segment": "enterprise", "lifetime_value": 7120, "active_days": 89},
        ])
        self.assertEqual(report["record_count"], 2)

    def test_run_writes_output(self) -> None:
        output_path = Path("out/test-report.json")
        report = run(Path("data/profiles.ndjson"), output_path)
        on_disk = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(report["record_count"], 4)
        self.assertIn("segments", on_disk)


if __name__ == "__main__":
    unittest.main()
