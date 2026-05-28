#!/usr/bin/env python3
"""Extract an application scenario taxonomy from a documentation page list via LLM.

Reads a JSON array of {"url", "title", "category"} from stdin.
Calls the Claude API to derive 5–8 scenario categories.

Usage:
    python3 fetch-docs-index.py --url <url> | python3 extract-taxonomy.py

Output (stdout): JSON array [{"key": "...", "label": "..."}]
Exit codes:
  0 — taxonomy extracted (5–8 categories)
  1 — LLM call failed, JSON invalid, or < 3 categories returned
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"
MIN_SCENARIOS = 3
MAX_RETRIES = 2

ANTHROPIC_MODEL = "claude-sonnet-4-6"


def _load_prompt_template() -> str:
    template_path = REFERENCES_DIR / "prompt-templates.md"
    content = template_path.read_text(encoding="utf-8")
    # Extract TAXONOMY_EXTRACTION block between ```...```
    match = re.search(r"## TAXONOMY_EXTRACTION\n\n```\n(.*?)```", content, re.DOTALL)
    if not match:
        print(
            "ERROR: TAXONOMY_EXTRACTION template not found in prompt-templates.md", file=sys.stderr
        )
        sys.exit(1)
    return match.group(1).strip()


def _build_page_summary(pages: list[dict]) -> str:
    """Build a condensed text representation of doc pages for the LLM."""
    lines = []
    seen_titles = set()
    for p in pages:
        title = (p.get("title") or "").strip()
        url = p.get("url", "")
        if not title and not url:
            continue
        # Deduplicate by title
        key = title.lower() if title else url
        if key in seen_titles:
            continue
        seen_titles.add(key)
        if title:
            lines.append(f"- {title} ({url})")
        else:
            lines.append(f"- {url}")
        if len(lines) >= 200:  # Cap to avoid token overflow
            break
    return "\n".join(lines)


def _call_llm(prompt: str) -> str:
    """Call Claude API and return the text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    import urllib.error
    import urllib.request

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["content"][0]["text"]
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        print(f"ERROR: LLM API HTTP {exc.code}: {err_body[:300]}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: LLM call failed: {exc}", file=sys.stderr)
        sys.exit(1)


def _parse_taxonomy(text: str) -> list[dict] | None:
    """Extract JSON array from LLM response. Returns None on parse failure."""
    # Try direct parse
    try:
        result = json.loads(text.strip())
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    # Try to find JSON array in the text
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _deduplicate(taxonomy: list[dict]) -> list[dict]:
    """Remove semantically identical labels (case-insensitive label dedup)."""
    seen_labels = set()
    result = []
    for item in taxonomy:
        label = item.get("label", "").strip()
        key = item.get("key", "").strip()
        if not label or not key:
            continue
        label_lower = label.lower()
        if label_lower not in seen_labels:
            seen_labels.add(label_lower)
            result.append({"key": key, "label": label})
    return result


def main():
    raw = sys.stdin.read()
    try:
        pages = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON from stdin: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(pages, list) or not pages:
        print("ERROR: stdin must be a non-empty JSON array of page objects", file=sys.stderr)
        sys.exit(1)

    print(f"Building taxonomy from {len(pages)} pages...", file=sys.stderr)
    page_summary = _build_page_summary(pages)
    template = _load_prompt_template()
    prompt = template.replace("{DOC_PAGES}", page_summary)

    taxonomy = None
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"LLM taxonomy extraction attempt {attempt}/{MAX_RETRIES}...", file=sys.stderr)
        response = _call_llm(prompt)
        taxonomy = _parse_taxonomy(response)
        if taxonomy is not None:
            break
        print(
            f"WARNING: LLM response was not valid JSON (attempt {attempt}). Retrying...",
            file=sys.stderr,
        )
        # Simplify retry prompt
        prompt = f"Fix the JSON syntax. Return ONLY a valid JSON array: {response[:500]}"

    if taxonomy is None:
        print("ERROR: LLM failed to return valid taxonomy JSON after retries", file=sys.stderr)
        sys.exit(1)

    taxonomy = _deduplicate(taxonomy)

    if len(taxonomy) < MIN_SCENARIOS:
        print(
            f"WARNING: Only {len(taxonomy)} scenarios extracted (expected ≥{MIN_SCENARIOS}). "
            "This may indicate a very flat documentation structure.",
            file=sys.stderr,
        )
        if len(taxonomy) == 0:
            print("ERROR: Zero scenarios extracted — cannot proceed", file=sys.stderr)
            sys.exit(1)

    # Ensure "general" fallback exists
    keys = {item["key"] for item in taxonomy}
    if "general" not in keys:
        taxonomy.append({"key": "general", "label": "通用"})

    print(f"Taxonomy: {len(taxonomy)} scenarios", file=sys.stderr)
    for item in taxonomy:
        print(f"  {item['key']}: {item['label']}", file=sys.stderr)

    print(json.dumps(taxonomy, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
