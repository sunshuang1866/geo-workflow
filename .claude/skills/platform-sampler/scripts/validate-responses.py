#!/usr/bin/env python3
"""Validate responses collection from stdin.

Usage: cat responses.json | python3 validate-responses.py

Validates: JSON array, each item has required fields, checks completeness.
Output: "VALID" to stdout, warnings/errors to stderr.
"""

import json
import sys

REQUIRED_FIELDS = {"question_id", "platform", "query", "timestamp", "raw_response", "status"}


def validate(data: list) -> list[str]:
    errors = []

    if not isinstance(data, list):
        return ["ERROR: Root element must be a JSON array."]

    if len(data) == 0:
        return ["ERROR: Response collection is empty."]

    error_count = 0
    empty_count = 0

    for i, item in enumerate(data):
        prefix = f"Item [{i}]"

        if not isinstance(item, dict):
            errors.append(f"{prefix}: Must be a JSON object.")
            continue

        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            errors.append(f"{prefix}: Missing fields: {missing}")
            continue

        if item.get("status") == "error":
            error_count += 1
        elif item.get("status") == "empty" or not item.get("raw_response"):
            empty_count += 1

    # Check coverage
    question_ids = set(item.get("question_id") for item in data if isinstance(item, dict))
    platforms = set(item.get("platform") for item in data if isinstance(item, dict))

    expected_total = len(question_ids) * len(platforms)
    actual_total = len(data)

    if actual_total < expected_total:
        errors.append(
            f"WARNING: Expected {expected_total} responses "
            f"({len(question_ids)} questions x {len(platforms)} platforms), "
            f"got {actual_total}. Some combinations may be missing."
        )

    if error_count > 0:
        pct = error_count / actual_total * 100
        msg = f"WARNING: {error_count}/{actual_total} responses ({pct:.0f}%) are errors."
        if pct > 50:
            msg += " Check API tokens and network connectivity."
        errors.append(msg)

    if empty_count > 0:
        errors.append(f"WARNING: {empty_count} responses have empty content.")

    return errors


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate(data)
    real_errors = [e for e in errors if not e.startswith("WARNING")]
    warnings = [e for e in errors if e.startswith("WARNING")]

    for w in warnings:
        print(w, file=sys.stderr)

    if real_errors:
        for e in real_errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    question_ids = set(item.get("question_id") for item in data if isinstance(item, dict))
    platforms = set(item.get("platform") for item in data if isinstance(item, dict))
    print(f"VALID: {len(data)} responses ({len(question_ids)} questions x {len(platforms)} platforms).")
