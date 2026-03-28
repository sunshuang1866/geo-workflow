#!/usr/bin/env python3
"""Parse manual-questions.md and output structured JSON to stdout.

Usage: python3 parse-manual-questions.py <path-to-manual-questions.md>

Expects Markdown with H2 headers as scenario labels (了解阶段 / 使用阶段)
and list items as questions.

Output: JSON array to stdout, errors to stderr.
"""

import json
import re
import sys


def parse_manual_questions(filepath: str) -> list[dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    questions = []
    current_scenario = "未分类"
    scenario_map = {
        "了解阶段": "了解阶段",
        "了解": "了解阶段",
        "awareness": "了解阶段",
        "industry": "了解阶段",
        "使用阶段": "使用阶段",
        "使用": "使用阶段",
        "usage": "使用阶段",
    }

    for line in content.splitlines():
        line = line.strip()

        # Detect H2 headers as scenario labels
        h2_match = re.match(r"^##\s+(.+)$", line)
        if h2_match:
            header = h2_match.group(1).strip()
            for key, scenario in scenario_map.items():
                if key in header.lower() or key in header:
                    current_scenario = scenario
                    break
            continue

        # Detect list items as questions
        item_match = re.match(r"^[-*]\s+(.+)$", line)
        if item_match:
            question = item_match.group(1).strip()
            # Skip empty or too short
            if len(question) < 3:
                continue
            # Detect language
            has_cjk = bool(re.search(r"[\u4e00-\u9fff]", question))
            lang = "zh" if has_cjk else "en"
            questions.append({
                "question": question,
                "scenario": current_scenario,
                "lang": lang,
                "source": "manual",
            })

    if not questions:
        print("WARNING: No questions found in the file.", file=sys.stderr)

    return questions


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse-manual-questions.py <filepath>", file=sys.stderr)
        sys.exit(1)

    result = parse_manual_questions(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
