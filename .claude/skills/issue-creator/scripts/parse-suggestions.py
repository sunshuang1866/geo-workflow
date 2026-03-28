#!/usr/bin/env python3
"""Parse scoring-results.json and extract actionable improvement suggestions.

Usage:
    python3 parse-suggestions.py <scoring-results-file>

Outputs a JSON array of suggestion objects to stdout.
Errors go to stderr with non-zero exit code.
"""

import json
import sys


def parse_scoring_results(filepath):
    """Extract actionable suggestions from scoring results."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    suggestions = []
    suggestion_counter = 0

    # Support two formats:
    # 1. Top-level "results" array with per-question scoring
    # 2. Top-level "suggestions" array (pre-extracted)
    results = data.get("results", [])
    if not results and "suggestions" in data:
        # Already extracted — pass through with validation
        for s in data["suggestions"]:
            required = ["suggestion_id", "question_id", "citation_type", "severity", "suggestion_text"]
            missing = [k for k in required if k not in s]
            if missing:
                print(f"WARNING: Suggestion missing fields {missing}, skipping", file=sys.stderr)
                continue
            suggestions.append(s)
        json.dump(suggestions, sys.stdout, ensure_ascii=False, indent=2)
        return

    for result in results:
        question_id = result.get("question_id", "unknown")
        question = result.get("question", "")
        phenomena = result.get("phenomena", [])

        for phenom in phenomena:
            citation_type = phenom.get("type", "")
            # Skip type D (high ratio) — that's a positive outcome, not actionable
            if citation_type == "D":
                continue

            severity = phenom.get("severity", "P2")
            affected_platforms = phenom.get("affected_platforms", [])
            suggestion_text = phenom.get("suggestion", "")
            category = phenom.get("category", "general")

            if not suggestion_text:
                continue

            suggestion_counter += 1
            suggestions.append({
                "suggestion_id": f"s_{suggestion_counter:03d}",
                "question_id": question_id,
                "question": question,
                "citation_type": citation_type,
                "severity": severity,
                "affected_platforms": affected_platforms,
                "suggestion_text": suggestion_text,
                "category": category,
            })

    if not suggestions:
        print("No actionable suggestions found. All scores are healthy.", file=sys.stderr)
        sys.exit(0)

    json.dump(suggestions, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse-suggestions.py <scoring-results.json>", file=sys.stderr)
        sys.exit(1)
    parse_scoring_results(sys.argv[1])
