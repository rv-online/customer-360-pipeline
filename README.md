# Customer 360 Pipeline

Python analytics pipeline for identity stitching, customer unification, and profile-level retention metrics.

## Why This Exists

Built to mimic a lightweight customer data platform workflow where messy inputs must be stitched into analysis-ready entities.

## What This Demonstrates

- identity stitching and profile unification
- customer segmentation and retention-style summary metrics
- simple CLI workflow with deterministic JSON outputs

## Architecture

1. raw profile events are loaded and normalized
1. identity rules merge records into unified customer profiles
1. summary metrics are emitted for downstream reporting and experimentation

## Run It

```bash
python -m src.analyzer --input data/profiles.ndjson --output out/report.json
python -m unittest discover -s tests
```

## Verification

Use the CLI to generate `out/report.json` and `python -m unittest discover -s tests` for regression coverage.
