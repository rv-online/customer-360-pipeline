import json
import unittest
from pathlib import Path

from src.analyzer import build_report, load_records, run


class AnalyzerTests(unittest.TestCase):
    def test_build_report_counts_records(self) -> None:
        report = build_report([
            {"customer_id": "c_101", "segment": "growth", "lifetime_value": 1240, "active_days": 18},
            {"customer_id": "c_102", "segment": "enterprise", "lifetime_value": 7120, "active_days": 89},
        ])
        self.assertEqual(report.record_count, 2)
        self.assertEqual(report.top_segment_by_value, "enterprise")
        self.assertEqual(report.health_counts["champion"], 1)
        self.assertEqual(report.concentration["top_two_customer_share"], 1.0)

    def test_load_records_parses_profiles(self) -> None:
        records = load_records(Path("data/profiles.ndjson"))
        self.assertEqual(len(records), 4)
        self.assertEqual(records[0].customer_id, "c_101")

    def test_run_writes_output(self) -> None:
        output_path = Path("out/test-report.json")
        report = run(Path("data/profiles.ndjson"), output_path)
        on_disk = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(report["record_count"], 4)
        self.assertIn("segment_counts", on_disk)
        self.assertEqual(on_disk["priority_customers"][0]["customer_id"], "c_104")
        self.assertIn("operational_notes", on_disk)


if __name__ == "__main__":
    unittest.main()
