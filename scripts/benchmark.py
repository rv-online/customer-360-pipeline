from __future__ import annotations

import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyzer import run


def main() -> None:
    input_path = Path("data/profiles.ndjson")
    output_path = Path("out/benchmark-report.json")
    iterations = 500
    started = time.perf_counter()
    last_report = None
    for _ in range(iterations):
        last_report = run(input_path, output_path)
    elapsed_ms = (time.perf_counter() - started) * 1000
    payload = {
        "iterations": iterations,
        "elapsed_ms": round(elapsed_ms, 2),
        "reports_per_second": round(iterations / (elapsed_ms / 1000), 2),
        "last_report": {
            "record_count": last_report["record_count"],
            "top_segment_by_value": last_report["top_segment_by_value"],
            "priority_customer": last_report["priority_customers"][0]["customer_id"] if last_report["priority_customers"] else None,
        },
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
