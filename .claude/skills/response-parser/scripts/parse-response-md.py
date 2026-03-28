#!/usr/bin/env python3
"""Parse a manually-collected response.md file into structured JSON.

Usage:
  python3 parse-response-md.py --input response.md --questions questions.json
  python3 parse-response-md.py --input response.md --questions questions.json --list-unmatched

Input format (response.md):
  Q:question text
  Platform: response content...

  Q：question text
  Platform：response content...

Platform aliases supported: Doubao/doubao, Qwen/qwen/千问, ChatGPT/chatgpt, DeepSeek/deepseek

Output: JSON array to stdout. Errors/warnings to stderr.
Exit 0 on success (even with warnings). Exit 1 on fatal error.
"""

import argparse
import json
import re
import sys


PLATFORM_NORM = {
    "doubao": "doubao", "Doubao": "doubao",
    "qwen": "qwen", "Qwen": "qwen", "千问": "qwen",
    "chatgpt": "chatgpt", "ChatGPT": "chatgpt",
    "deepseek": "deepseek", "DeepSeek": "deepseek",
    "perplexity": "perplexity", "Perplexity": "perplexity",
}

MODEL_MAP = {
    "doubao": "doubao-1.5-pro-32k",
    "qwen": "qwen-plus",
    "chatgpt": "gpt-4o",
    "deepseek": "deepseek-chat",
    "perplexity": "sonar",
}

# Regex for Q markers: Q: / Q： / Q；
Q_PATTERN = re.compile(r"(?m)^Q[：:；](.+)$")

# Regex for platform markers: e.g. "Doubao：" or "deepseek:"
PLAT_NAMES = "|".join(re.escape(k) for k in PLATFORM_NORM)
PLAT_PATTERN = re.compile(
    rf"(?m)^({PLAT_NAMES})[：:](.*)$"
)


def extract_citations(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s\)\]\"\'<]+", text)
    seen = set()
    result = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result


def build_question_index(questions_path: str) -> dict[str, str]:
    """Returns {question_text: question_id} and {question_id: question_text}."""
    with open(questions_path, encoding="utf-8") as f:
        questions = json.load(f)
    text_to_id = {}
    for q in questions:
        text_to_id[q["question"]] = q["id"]
    return text_to_id


def match_question_id(q_text: str, text_to_id: dict) -> str:
    """Exact match first, then substring match, then 'q_unknown'."""
    if q_text in text_to_id:
        return text_to_id[q_text]
    for text, qid in text_to_id.items():
        # Substring match: question text contains key or key contains question text
        if q_text in text or text in q_text:
            return qid
    return "q_unknown"


def parse(content: str, text_to_id: dict) -> tuple[list[dict], list[str]]:
    """Parse response.md content into a list of response dicts.

    Returns (responses, unmatched_questions).
    """
    q_matches = list(Q_PATTERN.finditer(content))
    if not q_matches:
        print("ERROR: No question markers found. Expected lines starting with 'Q:' or 'Q：'.", file=sys.stderr)
        sys.exit(1)

    responses = []
    unmatched = []

    for i, qm in enumerate(q_matches):
        q_text = qm.group(1).strip()
        block_start = qm.end()
        block_end = q_matches[i + 1].start() if i + 1 < len(q_matches) else len(content)
        block = content[block_start:block_end]

        qid = match_question_id(q_text, text_to_id)
        if qid == "q_unknown":
            unmatched.append(q_text)
            print(f"WARNING: No matching question ID for: {q_text[:60]}", file=sys.stderr)

        plat_matches = list(PLAT_PATTERN.finditer(block))
        if not plat_matches:
            print(f"WARNING: No platform responses found for question: {q_text[:40]}", file=sys.stderr)
            continue

        for j, pm in enumerate(plat_matches):
            platform_raw = pm.group(1)
            platform = PLATFORM_NORM.get(platform_raw, platform_raw.lower())
            inline_text = pm.group(2) or ""
            resp_end = plat_matches[j + 1].start() if j + 1 < len(plat_matches) else len(block)
            raw = (inline_text + "\n" + block[pm.end():resp_end]).strip()

            responses.append({
                "question_id": qid,
                "platform": platform,
                "query": q_text,
                "raw_response": raw,
                "citations": extract_citations(raw),
                "model": MODEL_MAP.get(platform, platform),
                "status": "success",
            })

    return responses, unmatched


def main():
    parser = argparse.ArgumentParser(description="Parse response.md into JSON")
    parser.add_argument("--input", required=True, help="Path to response.md")
    parser.add_argument("--questions", required=True, help="Path to questions.json")
    parser.add_argument("--list-unmatched", action="store_true",
                        help="Only print unmatched question strings to stdout")
    args = parser.parse_args()

    try:
        with open(args.input, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        text_to_id = build_question_index(args.questions)
    except FileNotFoundError:
        print(f"ERROR: questions.json not found: {args.questions}", file=sys.stderr)
        sys.exit(1)

    responses, unmatched = parse(content, text_to_id)

    if args.list_unmatched:
        for q in unmatched:
            print(q)
        return

    # Summary to stderr
    q_ids = set(r["question_id"] for r in responses)
    print(f"Parsed {len(responses)} responses across {len(q_ids)} questions", file=sys.stderr)
    for r in responses:
        print(f"  {r['question_id']} | {r['platform']:10} | {len(r['raw_response']):5} chars | {len(r['citations'])} citations", file=sys.stderr)

    print(json.dumps(responses, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
