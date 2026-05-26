#!/usr/bin/env python3
"""Expand a website URL into Chinese and English variants.

Detects existing /zh/ or /en/ path segments and produces both variants.
If no i18n structure is detected, exits with code 1 (caller keeps URL as-is).

Usage:
    python3 expand-i18n-urls.py "https://docs.example.com/zh/install"
    python3 expand-i18n-urls.py "https://docs.example.com/docs/install"

Output (stdout): JSON array of expanded URLs, e.g.:
    ["https://docs.example.com/zh/install", "https://docs.example.com/en/install"]

Exit codes:
  0 — i18n variants produced
  1 — no i18n structure detected (no expansion needed)
"""

import json
import re
import sys

# Patterns that indicate i18n path structure
_ZH_PATTERNS = ["/zh/", "/zh-cn/", "/zh_cn/", "/chinese/"]
_EN_PATTERNS = ["/en/", "/en-us/", "/en_us/", "/english/"]

# Query-parameter i18n (e.g. ?lang=zh)
_LANG_PARAM = re.compile(r"([?&]lang=)(zh[-_]?(?:cn)?|en[-_]?(?:us)?)", re.IGNORECASE)


def _replace_path_segment(url: str, old_segs: list[str], new_seg: str) -> str:
    for seg in old_segs:
        if seg in url:
            return url.replace(seg, new_seg, 1)
    return url


def expand(url: str) -> list[str] | None:
    url_lower = url.lower()

    # Path-based i18n
    for zh in _ZH_PATTERNS:
        if zh in url_lower:
            en_url = _replace_path_segment(url, _ZH_PATTERNS, "/en/")
            return [url, en_url]

    for en in _EN_PATTERNS:
        if en in url_lower:
            zh_url = _replace_path_segment(url, _EN_PATTERNS, "/zh/")
            return [zh_url, url]

    # Query-param i18n
    m = _LANG_PARAM.search(url)
    if m:
        prefix = m.group(1)
        lang_val = m.group(2).lower()
        if lang_val.startswith("zh"):
            en_url = _LANG_PARAM.sub(lambda _: prefix + "en", url)
            return [url, en_url]
        else:
            zh_url = _LANG_PARAM.sub(lambda _: prefix + "zh", url)
            return [zh_url, url]

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: expand-i18n-urls.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1].strip()
    result = expand(url)

    if result is None:
        print(f"No i18n structure detected in: {url}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
