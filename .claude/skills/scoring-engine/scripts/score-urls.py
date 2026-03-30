#!/usr/bin/env python3
"""
score-urls.py — Re-score responses.json against questions.json using exact URL matching only.

Usage:
  python3 score-urls.py <responses_json> <questions_json> <output_scoring_json>

Exact URL matching with normalization:
  - Lowercase
  - Strip trailing slashes
  - Treat http:// and https:// as equivalent (normalize to https://)
  - Strip www. prefix

No domain-level matching: domain-only checks produce false positives when all
official URLs share a single domain (e.g. mindspore.cn).
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def normalize_url(url: str) -> str:
    url = url.strip().lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    url = url.rstrip('/')
    return url


def is_cited(response_text: str, official_urls: list[str]) -> tuple[bool, list[str]]:
    """Return (cited, matched_urls). Exact normalized match only."""
    text_lower = response_text.lower()
    matched = []
    for url in official_urls:
        if not url:
            continue
        norm = normalize_url(url)
        if norm in text_lower:
            matched.append(url)
    return bool(matched), matched


def load_json(path: str, label: str):
    p = Path(path)
    if not p.exists():
        print(f"ERROR: {label} not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {label}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) != 4:
        print("Usage: score-urls.py <responses_json> <questions_json> <output_scoring_json>",
              file=sys.stderr)
        sys.exit(1)

    responses_path, questions_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    responses_data = load_json(responses_path, "responses.json")
    questions_data = load_json(questions_path, "questions.json")

    # Build question lookup: id -> {official_urls, question}
    q_lookup = {}
    for q in questions_data.get("questions", []):
        q_lookup[q["id"]] = q

    # responses.json may be a bare array or {"responses": [...]}
    raw_responses = responses_data if isinstance(responses_data, list) else responses_data.get("responses", [])

    # Group responses by question_id
    by_question: dict[str, list] = {}
    for resp in raw_responses:
        qid = resp["question_id"]
        by_question.setdefault(qid, []).append(resp)

    results = []
    status_counts = {"satisfied": 0, "not_cited": 0, "no_official_content": 0}

    for qid, responses in sorted(by_question.items()):
        q = q_lookup.get(qid)
        if not q:
            print(f"WARNING: {qid} not found in questions.json, skipping", file=sys.stderr)
            continue

        official_urls = [u for u in q.get("official_urls", []) if u]  # filter empty strings

        if not official_urls:
            # No official content
            platform_records = [
                {"platform": r["platform"], "cited": False, "matched_urls": []}
                for r in responses
            ]
            results.append({
                "question_id": qid,
                "question": q["question"],
                "official_urls": [],
                "status": "no_official_content",
                "description": "官方内容缺失",
                "severity": "P1",
                "citation_rate": 0.0,
                "cited_count": 0,
                "total_platforms": len(responses),
                "platforms": platform_records,
            })
            status_counts["no_official_content"] += 1
            continue

        # Exact URL matching per platform
        platform_records = []
        cited_count = 0
        for r in responses:
            cited, matched = is_cited(r.get("response_text", r.get("raw_response", "")), official_urls)
            if cited:
                cited_count += 1
            platform_records.append({
                "platform": r["platform"],
                "cited": cited,
                "matched_urls": matched,
            })

        total = len(responses)
        citation_rate = cited_count / total if total > 0 else 0.0

        if citation_rate >= 0.9:
            status, description, severity = "satisfied", "引用了官方内容", "OK"
            status_counts["satisfied"] += 1
        else:
            status, description, severity = "not_cited", "有内容未被引用", "P0"
            status_counts["not_cited"] += 1

        results.append({
            "question_id": qid,
            "question": q["question"],
            "official_urls": official_urls,
            "status": status,
            "description": description,
            "severity": severity,
            "citation_rate": round(citation_rate, 4),
            "cited_count": cited_count,
            "total_platforms": total,
            "platforms": platform_records,
        })

    # Sort: P0 first, then P1, then OK
    severity_order = {"P0": 0, "P1": 1, "OK": 2}
    results.sort(key=lambda r: (severity_order.get(r["severity"], 9), r["question_id"]))

    output = {
        "metadata": {
            "scored_at": datetime.now(timezone.utc).isoformat(),
            "total_questions": len(results),
            "total_platforms": len({r["platform"] for resp_list in by_question.values() for r in resp_list}),
            "citation_threshold": 0.9,
            "match_mode": "exact_url",
        },
        "results": results,
        "summary": {
            "by_status": status_counts,
            "by_severity": {
                "P0": status_counts["not_cited"],
                "P1": status_counts["no_official_content"],
                "OK": status_counts["satisfied"],
            },
        },
    }

    Path(output_path).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(results)
    print(f"Scoring complete (exact_url match only):")
    print(f"  Questions scored: {total}")
    print(f"  引用了官方内容 (OK):  {status_counts['satisfied']} ({status_counts['satisfied']/total*100:.0f}%)")
    print(f"  有内容未被引用 (P0):  {status_counts['not_cited']} ({status_counts['not_cited']/total*100:.0f}%)")
    print(f"  官方内容缺失  (P1):   {status_counts['no_official_content']} ({status_counts['no_official_content']/total*100:.0f}%)")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
