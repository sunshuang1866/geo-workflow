#!/usr/bin/env python3
"""Parse scoring-results.json and extract actionable improvement suggestions.

Usage:
    python3 parse-suggestions.py <scoring-results-file>

Outputs a JSON array of suggestion objects to stdout.
Errors go to stderr with non-zero exit code.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import load_json


def parse_scoring_results(filepath):
    """Extract actionable suggestions from scoring results."""
    data = load_json(filepath, "scoring-results.json")

    suggestions = []
    suggestion_counter = 0

    results = data.get("results", [])
    if not results:
        print("No results found in scoring file.", file=sys.stderr)
        sys.exit(0)

    for result in results:
        question_id = result.get("question_id", "unknown")
        question = result.get("question", "")
        status = result.get("status", "")

        # Skip satisfied questions — no actionable suggestion needed
        if status == "satisfied":
            continue

        # Only process not_cited and no_official_content
        if status not in ("not_cited", "no_official_content"):
            continue

        severity = result.get("severity", "P2")
        citation_rate = result.get("citation_rate", 0.0)
        cited_count = result.get("cited_count", 0)
        total_platforms = result.get("total_platforms", 0)
        official_urls = result.get("official_urls", [])
        platforms = result.get("platforms", [])

        cited_platforms = [p["platform"] for p in platforms if p.get("cited")]
        not_cited_platforms = [p["platform"] for p in platforms if not p.get("cited")]

        if status == "not_cited":
            description = "有内容未被引用"
            if citation_rate == 0.0:
                suggestion_text = (
                    f"官方页面 {official_urls[0] if official_urls else '(未知)'} "
                    f"未被任何平台引用，需优化 SEO 可发现性（外链密度、sitemap 覆盖、结构化数据）"
                )
            else:
                suggestion_text = (
                    f"官方页面 {official_urls[0] if official_urls else '(未知)'} "
                    f"引用率仅 {citation_rate*100:.0f}%，需扩大 SEO 覆盖范围至所有主流 AI 平台"
                )
            category = "seo"
        else:  # no_official_content
            description = "官方内容缺失"
            suggestion_text = (
                f"问题「{question}」缺少官方页面，"
                f"建议在 mindspore.cn 创建对应内容页面"
            )
            category = "content"

        suggestion_counter += 1
        suggestions.append({
            "suggestion_id": f"s_{suggestion_counter:03d}",
            "question_id": question_id,
            "question": question,
            "status": status,
            "description": description,
            "severity": severity,
            "citation_rate": citation_rate,
            "cited_count": cited_count,
            "total_platforms": total_platforms,
            "cited_platforms": cited_platforms,
            "not_cited_platforms": not_cited_platforms,
            "official_urls": official_urls,
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
