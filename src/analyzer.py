from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import median
from typing import Iterable


REQUIRED_FIELDS = {"customer_id", "segment", "lifetime_value", "active_days"}


@dataclass(frozen=True)
class CustomerProfile:
    customer_id: str
    segment: str
    lifetime_value: float
    active_days: int


@dataclass(frozen=True)
class ProfileScore:
    customer_id: str
    segment: str
    lifetime_value: float
    active_days: int
    value_band: str
    health: str
    engagement_score: int
    churn_risk: int
    reason: str


@dataclass(frozen=True)
class Customer360Report:
    record_count: int
    unique_customer_count: int
    segment_counts: dict[str, int]
    value_band_counts: dict[str, int]
    health_counts: dict[str, int]
    avg_lifetime_value: float
    median_active_days: float
    total_lifetime_value: float
    top_segment_by_value: str | None
    concentration: dict[str, float]
    customer_revenue_share: dict[str, float]
    priority_customers: list[ProfileScore]
    segment_profiles: dict[str, dict[str, float]]
    operational_notes: list[str]
    report_version: str = "v2"


def parse_profile(record: dict[str, object]) -> CustomerProfile:
    missing = REQUIRED_FIELDS.difference(record)
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")

    lifetime_value = float(record["lifetime_value"])
    active_days = int(record["active_days"])
    if lifetime_value < 0:
        raise ValueError("lifetime_value must be non-negative")
    if active_days < 0:
        raise ValueError("active_days must be non-negative")

    return CustomerProfile(
        customer_id=str(record["customer_id"]).strip(),
        segment=str(record["segment"]).strip(),
        lifetime_value=lifetime_value,
        active_days=active_days,
    )


def load_records(path: Path) -> list[CustomerProfile]:
    return [
        parse_profile(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def value_band(lifetime_value: float) -> str:
    if lifetime_value >= 5000:
        return "enterprise"
    if lifetime_value >= 1000:
        return "growth"
    return "self-serve"


def health_label(profile: CustomerProfile) -> str:
    if profile.lifetime_value >= 5000 and profile.active_days >= 60:
        return "champion"
    if profile.active_days >= 30:
        return "stable"
    if profile.active_days >= 10:
        return "watch"
    return "at-risk"


def engagement_score(profile: CustomerProfile) -> int:
    score = int(profile.lifetime_value / 100) + profile.active_days
    if profile.segment == "enterprise":
        score += 20
    elif profile.segment == "growth":
        score += 10
    return score


def churn_risk(profile: CustomerProfile) -> int:
    risk = 100 - min(60, profile.active_days * 2) - min(40, int(profile.lifetime_value / 250))
    if profile.segment == "self-serve":
        risk += 10
    return max(0, min(100, risk))


def score_profile(profile: CustomerProfile) -> ProfileScore:
    risk = churn_risk(profile)
    score = engagement_score(profile)
    band = value_band(profile.lifetime_value)
    label = health_label(profile)
    if risk >= 80:
        reason = "low tenure and low realized value"
    elif risk >= 55:
        reason = "moderate inactivity or weak expansion"
    else:
        reason = "strong retention and value posture"
    return ProfileScore(
        customer_id=profile.customer_id,
        segment=profile.segment,
        lifetime_value=profile.lifetime_value,
        active_days=profile.active_days,
        value_band=band,
        health=label,
        engagement_score=score,
        churn_risk=risk,
        reason=reason,
    )


def _coerce_profile(record: CustomerProfile | dict[str, object]) -> CustomerProfile:
    if isinstance(record, CustomerProfile):
        return record
    return parse_profile(record)


def build_report(records: Iterable[CustomerProfile | dict[str, object]]) -> Customer360Report:
    profiles = [_coerce_profile(record) for record in records]
    scored = [score_profile(profile) for profile in profiles]
    segment_counts = Counter(profile.segment for profile in profiles)
    value_band_counts = Counter(score.value_band for score in scored)
    health_counts = Counter(score.health for score in scored)
    total_ltv = round(sum(profile.lifetime_value for profile in profiles), 2)

    by_segment_value = defaultdict(float)
    by_segment_days = defaultdict(float)
    for profile in profiles:
        by_segment_value[profile.segment] += profile.lifetime_value
        by_segment_days[profile.segment] += profile.active_days

    sorted_by_ltv = sorted(scored, key=lambda item: item.lifetime_value, reverse=True)
    top_segment = max(by_segment_value, key=by_segment_value.get, default=None)
    concentration_top1 = round((sorted_by_ltv[0].lifetime_value / total_ltv) if total_ltv else 0.0, 4)
    concentration_top2 = round((sum(item.lifetime_value for item in sorted_by_ltv[:2]) / total_ltv) if total_ltv else 0.0, 4)

    segment_profiles = {
        segment: {
            "customers": segment_counts[segment],
            "avg_lifetime_value": round(by_segment_value[segment] / segment_counts[segment], 2),
            "avg_active_days": round(by_segment_days[segment] / segment_counts[segment], 2),
        }
        for segment in sorted(segment_counts)
    }

    priority_customers = sorted(
        scored,
        key=lambda item: (item.churn_risk, item.engagement_score, item.lifetime_value),
        reverse=True,
    )[:5]

    operational_notes = [
        f"{len(priority_customers)} customers surfaced for proactive outreach",
        f"{len([item for item in scored if item.health == 'at-risk'])} customers are at-risk",
        f"top two customers represent {round(concentration_top2 * 100, 1)}% of total value",
    ]

    return Customer360Report(
        record_count=len(profiles),
        unique_customer_count=len({profile.customer_id for profile in profiles}),
        segment_counts=dict(sorted(segment_counts.items())),
        value_band_counts=dict(sorted(value_band_counts.items())),
        health_counts=dict(sorted(health_counts.items())),
        avg_lifetime_value=round(total_ltv / len(profiles), 2) if profiles else 0.0,
        median_active_days=median(profile.active_days for profile in profiles) if profiles else 0.0,
        total_lifetime_value=total_ltv,
        top_segment_by_value=top_segment,
        concentration={"top_customer_share": concentration_top1, "top_two_customer_share": concentration_top2},
        customer_revenue_share={
            score.customer_id: round(score.lifetime_value / total_ltv, 4) if total_ltv else 0.0
            for score in sorted_by_ltv
        },
        priority_customers=priority_customers,
        segment_profiles=segment_profiles,
        operational_notes=operational_notes,
    )


def run(input_path: Path, output_path: Path) -> dict[str, object]:
    report = build_report(load_records(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return asdict(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Customer 360 Pipeline")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
