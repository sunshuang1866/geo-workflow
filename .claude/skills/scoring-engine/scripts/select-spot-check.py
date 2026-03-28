#!/usr/bin/env python3
"""Select a stratified sample of scoring results for human spot-check.

Usage:
    python3 select-spot-check.py <scoring-results.json> [--ratio 0.2]

Outputs a Markdown checklist of (question_id, platform) pairs to review,
sampling proportionally from each severity level (~20% default).
"""

import argparse
import json
import math
import random
import sys


def select_sample(filepath, ratio):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    results = data.get("results", [])
    if not results:
        print("No results to sample.", file=sys.stderr)
        sys.exit(0)

    # Group by severity
    by_severity = {}
    for r in results:
        sev = r.get("severity", "unknown")
        by_severity.setdefault(sev, []).append(r)

    # Stratified sampling
    selected = []
    for sev, items in sorted(by_severity.items()):
        n = max(1, math.ceil(len(items) * ratio))
        sampled = random.sample(items, min(n, len(items)))
        selected.extend(sampled)

    # Output as Markdown checklist
    print(f"# Spot-Check Sample ({len(selected)}/{len(results)} pairs, {ratio:.0%} target)\n")
    print(f"Review each pair below. Mark corrections in `scoring-calibration.md`.\n")

    current_sev = None
    for r in sorted(selected, key=lambda x: (x.get("severity", ""), x.get("question_id", ""))):
        sev = r.get("severity", "unknown")
        if sev != current_sev:
            print(f"\n## {sev}\n")
            current_sev = sev
        qid = r.get("question_id", "?")
        platform = r.get("platform", "?")
        ct = r.get("citation_type", "?")
        score = r.get("accuracy_score", "?")
        ratio_val = r.get("official_source_ratio", "?")
        print(f"- [ ] **{qid}** × {platform} — Type {ct}, Score {score}, Ratio {ratio_val}")

    print(f"\n---\nTotal: {len(selected)} pairs to review")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select spot-check sample")
    parser.add_argument("scoring_results", help="Path to scoring-results.json")
    parser.add_argument("--ratio", type=float, default=0.2, help="Sampling ratio (default: 0.2)")
    args = parser.parse_args()
    select_sample(args.scoring_results, args.ratio)
