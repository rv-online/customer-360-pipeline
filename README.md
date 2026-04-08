# Customer 360 Pipeline

Python analytics project for customer profile unification. It packages a small but reviewable workflow with deterministic scoring, JSON outputs, and unit tests.

## What It Shows

- identity stitching, segmentation, and retention-style KPIs
- clear ingestion and summarization logic
- CLI entrypoint and test coverage

## Run

```bash
python -m src.analyzer --input data/profiles.ndjson --output out/report.json
```

## Test

```bash
python -m unittest discover -s tests
```
