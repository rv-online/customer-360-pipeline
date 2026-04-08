from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def classify(record: dict[str, object]) -> str:
    score = 0.0
    for value in record.values():
        if isinstance(value, bool):
            score += 20 if not value else 5
        elif isinstance(value, (int, float)):
            score += float(value)
    if score >= 150:
        return "critical"
    if score >= 40:
        return "watch"
    return "healthy"


def build_report(records: list[dict[str, object]]) -> dict[str, object]:
    buckets: dict[str, int] = defaultdict(int)
    leaderboard: list[dict[str, object]] = []
    for record in records:
        status = classify(record)
        buckets[status] += 1
        leaderboard.append({"status": status, **record})

    return {
        "record_count": len(records),
        "segments": dict(sorted(buckets.items())),
        "priority_records": sorted(
            leaderboard,
            key=lambda item: {"healthy": 0, "watch": 1, "critical": 2}[str(item["status"])],
            reverse=True,
        )[:5],
    }


def run(input_path: Path, output_path: Path) -> dict[str, object]:
    report = build_report(load_records(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Customer 360 Pipeline")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
