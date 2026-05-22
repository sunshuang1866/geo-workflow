#!/usr/bin/env python3
"""Validate scoring-engine input files (responses.json + questions.json).

Usage:
    python3 validate-inputs.py <responses.json> <questions.json>

Checks structural validity and cross-references question IDs.
Outputs validation result to stdout; errors to stderr with non-zero exit.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import load_json


def validate(responses_path, questions_path):
    errors = []

    responses_data = load_json(responses_path)
    questions_data = load_json(questions_path)

    # Validate responses structure
    responses = responses_data.get("responses", [])
    if not responses:
        errors.append(f"ERROR: {responses_path} has no 'responses' array or it is empty.")

    required_response_fields = ["question_id", "platform", "response_text"]
    for i, r in enumerate(responses):
        missing = [f for f in required_response_fields if f not in r]
        if missing:
            errors.append(f"ERROR: responses[{i}] missing fields: {missing}")

    # Validate questions structure
    questions = questions_data.get("questions", [])
    if not questions:
        errors.append(f"ERROR: {questions_path} has no 'questions' array or it is empty.")

    for i, q in enumerate(questions):
        if "id" not in q:
            errors.append(f"ERROR: questions[{i}] missing 'id' field")
        if "official_urls" not in q:
            errors.append(f"ERROR: questions[{i}] missing 'official_urls' field")

    # Cross-reference: every question_id in responses must have a matching question
    question_ids = {q.get("id") for q in questions}
    response_question_ids = {r.get("question_id") for r in responses}
    missing_questions = response_question_ids - question_ids
    if missing_questions:
        errors.append(f"ERROR: Questions in responses missing from questions.json: {missing_questions}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)

    # Summary
    labeled_count = sum(1 for q in questions if q.get("official_urls"))
    print(f"Validation passed:")
    print(f"  Responses: {len(responses)} entries across {len(response_question_ids)} questions")
    print(f"  Questions: {len(questions)} total, {labeled_count} with official_urls, {len(questions) - labeled_count} without")
    print(f"  Cross-reference: OK")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 validate-inputs.py <responses.json> <questions.json>", file=sys.stderr)
        sys.exit(1)
    validate(sys.argv[1], sys.argv[2])
