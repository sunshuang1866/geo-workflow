#!/usr/bin/env python3
"""Validate scoring-engine input files (responses.json + content-labels.json).

Usage:
    python3 validate-inputs.py <responses.json> <content-labels.json>

Checks structural validity and cross-references question IDs.
Outputs validation result to stdout; errors to stderr with non-zero exit.
"""

import json
import sys


def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def validate(responses_path, labels_path):
    errors = []

    responses_data = load_json(responses_path)
    labels_data = load_json(labels_path)

    # Validate responses structure
    responses = responses_data.get("responses", [])
    if not responses:
        errors.append(f"ERROR: {responses_path} has no 'responses' array or it is empty.")

    required_response_fields = ["question_id", "platform", "response_text"]
    for i, r in enumerate(responses):
        missing = [f for f in required_response_fields if f not in r]
        if missing:
            errors.append(f"ERROR: responses[{i}] missing fields: {missing}")

    # Validate labels structure
    labels = labels_data.get("labels", [])
    if not labels:
        errors.append(f"ERROR: {labels_path} has no 'labels' array or it is empty.")

    required_label_fields = ["question_id", "content_exists"]
    for i, l in enumerate(labels):
        missing = [f for f in required_label_fields if f not in l]
        if missing:
            errors.append(f"ERROR: labels[{i}] missing fields: {missing}")

    # Cross-reference: every question_id in responses must have a label
    label_ids = {l.get("question_id") for l in labels}
    response_question_ids = {r.get("question_id") for r in responses}
    missing_labels = response_question_ids - label_ids
    if missing_labels:
        errors.append(f"ERROR: Questions in responses missing from labels: {missing_labels}")

    # Check for all-null labels
    labeled_count = sum(1 for l in labels if l.get("content_exists") is not None)
    if labels and labeled_count == 0:
        errors.append("ERROR: All content_exists values are null. Complete human labeling first.")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)

    # Summary
    print(f"Validation passed:")
    print(f"  Responses: {len(responses)} entries across {len(response_question_ids)} questions")
    print(f"  Labels: {len(labels)} entries, {labeled_count} labeled, {len(labels) - labeled_count} unlabeled")
    print(f"  Cross-reference: OK")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 validate-inputs.py <responses.json> <content-labels.json>", file=sys.stderr)
        sys.exit(1)
    validate(sys.argv[1], sys.argv[2])
