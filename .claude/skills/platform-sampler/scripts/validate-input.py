#!/usr/bin/env python3
"""Validate questions.json input format from stdin.

Usage: cat questions.json | python3 validate-input.py

Validates: JSON array, each item has id and question fields.
Output: "VALID: N questions" to stdout, errors to stderr.
"""

import json
import sys

REQUIRED_FIELDS = {"id", "question"}


def validate(data: list) -> list[str]:
    errors = []

    if not isinstance(data, list):
        return ["ERROR: Root element must be a JSON array."]

    if len(data) == 0:
        return ["ERROR: Question set is empty."]

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item [{i}]: Must be a JSON object.")
            continue
        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            errors.append(f"Item [{i}]: Missing fields: {missing}")
        elif not item["question"] or len(item["question"].strip()) < 3:
            errors.append(f"Item [{i}]: Question is empty or too short.")

    return errors


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate(data)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    print(f"VALID: {len(data)} questions ready for sampling.")
