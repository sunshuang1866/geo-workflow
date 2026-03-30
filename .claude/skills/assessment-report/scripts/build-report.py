#!/usr/bin/env python3
"""
build-report.py — Merge scoring-results.json, content-labels.json, and issue-map.json
into a unified per-question record list.

Usage:
  python3 build-report.py <scoring_file> <labels_file> <issue_map_file>

Outputs JSON array to stdout. Each element is a per-question record.
Exits 1 on error.
"""

import json
import sys
from pathlib import Path

PLATFORM_DISPLAY = {
    "doubao": "豆包",
    "qwen": "Qwen",
    "chatgpt": "ChatGPT",
    "deepseek": "DeepSeek",
}

STATUS_TO_CATEGORY = {
    "no_official_content": "no_official_content",
    "not_cited": "not_cited",
    "satisfied": "satisfied",
}


def load_json(path, label):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse {label}: {e}", file=sys.stderr)
        sys.exit(1)


def build_issue_lookup(issue_map):
    """Build {question_id -> issue record} from issue-map.json."""
    lookup = {}
    if not issue_map:
        return lookup
    for suggestion_id, entry in issue_map.get("issues", {}).items():
        for qid in entry.get("question_ids", []):
            if qid not in lookup:
                lookup[qid] = {
                    "issue_url": entry.get("issue_url"),
                    "issue_number": entry.get("issue_number"),
                    "issue_created_at": entry.get("created_at"),
                    "issue_iterations": _count_iterations(entry),
                }
    return lookup


def _count_iterations(entry):
    """Estimate iteration count from issue-map entry."""
    created = entry.get("created_at", "")
    last_updated = entry.get("last_updated_run", "")
    if created and last_updated and created != last_updated:
        return 2  # At least one update after creation
    return 1


def build_platform_record(platform_data, has_official_content):
    """Build per-platform dict with cited bool and indicator."""
    cited = platform_data.get("cited", False)
    if not has_official_content:
        indicator = "—"
    elif cited:
        indicator = "✅"
    else:
        indicator = "❌"
    return {
        "cited": cited,
        "indicator": indicator,
        "match_type": platform_data.get("match_type"),
        "matched_urls": platform_data.get("matched_urls", []),
    }


def main():
    if len(sys.argv) < 4:
        print("Usage: build-report.py <scoring_file> <labels_file> <issue_map_file>",
              file=sys.stderr)
        sys.exit(1)

    scoring_file, labels_file, issue_map_file = sys.argv[1], sys.argv[2], sys.argv[3]

    scoring = load_json(scoring_file, "scoring-results.json")
    if not scoring:
        print(f"ERROR: {scoring_file} not found or empty", file=sys.stderr)
        sys.exit(1)

    labels_data = load_json(labels_file, "content-labels.json") or {"labels": []}
    issue_map = load_json(issue_map_file, "issue-map.json") or {"issues": {}}

    # Build labels lookup
    labels_lookup = {
        entry["question_id"]: entry
        for entry in labels_data.get("labels", [])
    }

    # Build issue lookup
    issue_lookup = build_issue_lookup(issue_map)

    records = []
    for result in scoring.get("results", []):
        qid = result["question_id"]
        status = result.get("status", "satisfied")
        has_official = status != "no_official_content"

        label_entry = labels_lookup.get(qid, {})
        official_urls = label_entry.get("official_urls", [])

        # Build per-platform records
        platforms_raw = result.get("platforms", [])
        platforms = {}
        for p in platforms_raw:
            name = p.get("platform", "unknown")
            display = PLATFORM_DISPLAY.get(name, name)
            platforms[name] = {
                "display_name": display,
                **build_platform_record(p, has_official),
            }

        # Issue data
        issue_info = issue_lookup.get(qid, {})

        record = {
            "question_id": qid,
            "question": result.get("question", ""),
            "official_urls": official_urls,
            "status": status,
            "description": result.get("description", ""),
            "severity": result.get("severity", "OK"),
            "citation_rate": result.get("citation_rate"),
            "cited_count": result.get("cited_count"),
            "total_platforms": result.get("total_platforms"),
            "platforms": platforms,
            "issue_url": issue_info.get("issue_url"),
            "issue_number": issue_info.get("issue_number"),
            "issue_created_at": issue_info.get("issue_created_at"),
            "issue_iterations": issue_info.get("issue_iterations"),
        }
        records.append(record)

    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
