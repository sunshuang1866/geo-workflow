#!/usr/bin/env python3
"""Discover pages from a website sitemap and score them against a keyword query.

Usage:
    python3 discover-docs.py --base-url https://openubmc.org --query "固件升级 HPM" --limit 2

Tries in order:
  1. {base_url}/sitemap.xml
  2. {base_url}/sitemap_index.xml
  3. {base_url}/docs/sitemap.xml

Output (stdout): JSON array of matched page URLs.

Exit codes:
  0 — at least one result
  1 — sitemap not found or no matching pages
"""

import argparse
import json
import re
import sys
import urllib.request

TIMEOUT = 10


def fetch(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "geo-prefill-urls/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8", errors="replace")
    except Exception:
        pass
    return None


def parse_urls(xml: str) -> list[str]:
    return re.findall(r"<loc>(https?://[^<]+)</loc>", xml)


def score(url: str, keywords: list[str]) -> int:
    url_lower = url.lower()
    return sum(1 for kw in keywords if kw.lower() in url_lower)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    keywords = [k.strip() for k in args.query.split() if k.strip()]

    # Try sitemaps in priority order
    sitemap_xml = None
    for path in ["/sitemap.xml", "/sitemap_index.xml", "/docs/sitemap.xml"]:
        content = fetch(base + path)
        if content and "<loc>" in content:
            sitemap_xml = content
            print(f"Found sitemap: {base + path}", file=sys.stderr)
            break

    if not sitemap_xml:
        print(f"No sitemap found at {base}", file=sys.stderr)
        sys.exit(1)

    # If sitemap index, fetch first child sitemap
    child_sitemaps = re.findall(r"<sitemap>.*?<loc>(https?://[^<]+)</loc>", sitemap_xml, re.DOTALL)
    if child_sitemaps:
        content = fetch(child_sitemaps[0])
        if content:
            sitemap_xml += content

    all_urls = parse_urls(sitemap_xml)
    print(f"Sitemap: {len(all_urls)} pages", file=sys.stderr)

    if not all_urls:
        sys.exit(1)

    # Score and rank
    scored = [(score(u, keywords), u) for u in all_urls]
    scored = [(s, u) for s, u in scored if s > 0]
    scored.sort(key=lambda x: x[0], reverse=True)

    results = [u for _, u in scored[: args.limit]]
    if not results:
        print(f"No pages matched keywords: {keywords}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
