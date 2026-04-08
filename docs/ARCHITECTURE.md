# Architecture

## Goal

This repo models a customer 360 pipeline that turns compact profile events into a higher-signal decision support report for growth, retention, and account planning.

## Flow

1. NDJSON profile records are parsed into typed customer profiles.
2. Profiles are scored into value bands, health labels, and churn risk.
3. The report layer aggregates segment concentration, customer value shares, and outreach candidates.
4. The CLI writes a single JSON artifact that can be fed into dashboards, review meetings, or experimentation analysis.

## Design Tradeoffs

- The pipeline stays in-memory so the scoring behavior is easy to inspect and test.
- The report favors explainability over a black-box ML model because a portfolio repo should make the reasoning visible.
- A richer report object is better than a flat dict because it keeps the business and operational views aligned.

## Operational Notes

- The report is deterministic for the bundled data set.
- The JSON output is intended to be the contract for downstream consumers.
- If the input schema grows, the parser should fail fast instead of guessing.
