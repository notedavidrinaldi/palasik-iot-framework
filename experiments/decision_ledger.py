#!/usr/bin/env python3
"""Tools untuk analisis file decision log PALASIK (format JSONL)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from statistics import mean
from typing import Iterable

from pathlib import Path


def iter_records(path: Path) -> Iterable[dict]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            # abaikan baris rusak agar analisis tetap jalan
            continue


def summarize_records(records: Iterable[dict]) -> dict:
    total = 0
    by_decision = Counter()
    challenge = Counter()
    trust = []
    unique_policies = set()

    for rec in records:
        total += 1
        decision = str(rec.get("decision", "DENY")).upper()
        by_decision[decision] += 1
        unique_policies.add(rec.get("policy_name", "unknown"))

        if "challenge" in rec and rec["challenge"] is not None:
            challenge[rec["challenge"]] += 1

        try:
            trust.append(float(rec.get("trust_score")))
        except (TypeError, ValueError):
            pass

    return {
        "total_events": total,
        "decision_counts": dict(by_decision),
        "challenge_counts": dict(challenge),
        "unique_policies": sorted(unique_policies),
        "trust_min": min(trust) if trust else None,
        "trust_max": max(trust) if trust else None,
        "trust_mean": mean(trust) if trust else None,
    }


def as_text(summary: dict) -> str:
    lines = [
        f"Total events: {summary['total_events']}",
        "Decision counts:",
    ]

    for key, value in sorted(summary["decision_counts"].items()):
        lines.append(f"  - {key}: {value}")

    if summary["challenge_counts"]:
        lines.append("Challenge states:")
        for key, value in sorted(summary["challenge_counts"].items()):
            lines.append(f"  - {key}: {value}")

    lines.append(f"Policies: {', '.join(summary['unique_policies']) or 'n/a'}")

    if summary["trust_mean"] is not None:
        lines.append(f"Trust min/mean/max: {summary['trust_min']:.3f} / {summary['trust_mean']:.3f} / {summary['trust_max']:.3f}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="PALASIK Decision Ledger Analyzer")
    parser.add_argument("ledger", type=Path, help="Path ke file JSONL decision log")
    parser.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args()

    summary = summarize_records(iter_records(args.ledger))
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(as_text(summary))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
