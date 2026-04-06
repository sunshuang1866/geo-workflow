#!/usr/bin/env python3
"""Validate questions JSON from stdin.

Usage: cat questions.json | python3 validate-questions.py

Accepts two input formats:
  - Object wrapper: {"community": ..., "questions": [{...}, ...]}
  - Flat array:     [{...}, ...]

Validates:
- Each item has required fields: id, question
- id follows pattern q_NNN
- No duplicate ids
- Total count within target range (warning if outside; range read from .env:
    GEO_QUESTION_TARGET_MIN  default 30
    GEO_QUESTION_TARGET_MAX  default 40)

Output: "VALID: N questions passed validation." to stdout on success,
        errors to stderr on failure (exit 1).
"""

import json
import re
import sys
from pathlib import Path


def load_env(env_path: str = ".env") -> dict:
    env: dict[str, str] = {}
    try:
        for line in Path(env_path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env


env = load_env()
TARGET_MIN = int(env.get("GEO_QUESTION_TARGET_MIN", 30))
TARGET_MAX = int(env.get("GEO_QUESTION_TARGET_MAX", 40))

REQUIRED_FIELDS = {"id", "question"}


def validate(data: list) -> list[str]:
    errors = []

    if not isinstance(data, list):
        return ["ERROR: Root element must be a JSON array or an object with a 'questions' key."]

    seen_ids = set()
    for i, item in enumerate(data):
        prefix = f"Item [{i}]"

        if not isinstance(item, dict):
            errors.append(f"{prefix}: Must be a JSON object.")
            continue

        # Check required fields
        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            errors.append(f"{prefix}: Missing fields: {missing}")
            continue

        # Validate id
        qid = item["id"]
        if not re.match(r"^q_\d{3}$", qid):
            errors.append(f"{prefix}: id '{qid}' must match pattern q_NNN (e.g., q_001).")
        if qid in seen_ids:
            errors.append(f"{prefix}: Duplicate id '{qid}'.")
        seen_ids.add(qid)

        # Validate question is non-empty
        if not item["question"] or len(item["question"].strip()) < 3:
            errors.append(f"{prefix}: Question is empty or too short.")

    # Count warnings
    total = len(data)
    if total < TARGET_MIN:
        errors.append(f"WARNING: Only {total} questions. Target is {TARGET_MIN}-{TARGET_MAX}.")
    elif total > TARGET_MAX:
        errors.append(f"WARNING: {total} questions exceeds target of {TARGET_MIN}-{TARGET_MAX}.")

    return errors


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Accept both object wrapper and flat array
    if isinstance(parsed, dict):
        data = parsed.get("questions")
        if data is None:
            print("ERROR: Object has no 'questions' key.", file=sys.stderr)
            sys.exit(1)
    else:
        data = parsed

    errors = validate(data)
    if errors:
        # Separate actual errors from warnings
        real_errors = [e for e in errors if not e.startswith("WARNING")]
        warnings = [e for e in errors if e.startswith("WARNING")]

        for w in warnings:
            print(w, file=sys.stderr)

        if real_errors:
            for e in real_errors:
                print(e, file=sys.stderr)
            sys.exit(1)

    print(f"VALID: {len(data)} questions passed validation.")
