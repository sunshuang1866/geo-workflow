#!/usr/bin/env python3
"""Fetch and parse a community documentation index page into a flat list of pages.

Supports three formats, auto-detected:
  - sitemap.xml  → XML <loc> tags
  - JSON         → parsed directly as array or object with url/title keys
  - HTML         → BeautifulSoup <a> tag extraction

Usage:
    python3 fetch-docs-index.py --url https://docs.openeuler.org/sitemap.xml
    python3 fetch-docs-index.py --url https://docs.openeuler.org/

Output (stdout): JSON array of {"url": "...", "title": "...", "category": ""}
Exit codes:
  0 — success, at least one page found
  1 — URL unreachable, parse failure, or no pages extracted
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

TIMEOUT = 15
USER_AGENT = "geo-classify-scenarios/1.0"

# sitemap.xml namespace
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def _fetch(url: str) -> tuple[str, str]:
    """Return (body_text, content_type). Raises on non-200."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                raise urllib.error.HTTPError(url, resp.status, "Non-200", {}, None)
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8", errors="replace")
            return body, content_type
    except urllib.error.HTTPError as exc:
        print(f"ERROR: HTTP {exc.code} fetching {url}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"ERROR: Cannot reach {url}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Unexpected error fetching {url}: {exc}", file=sys.stderr)
        sys.exit(1)


def _detect_format(url: str, content_type: str, body: str) -> str:
    """Return 'sitemap', 'json', or 'html'."""
    url_lower = url.lower()
    if url_lower.endswith(".xml") or "sitemap" in url_lower:
        return "sitemap"
    if "application/json" in content_type or "text/json" in content_type:
        return "json"
    # Peek at body content
    stripped = body.lstrip()
    if stripped.startswith(("<?xml", "<urlset", "<sitemapindex")):
        return "sitemap"
    if stripped.startswith(("[", "{")):
        return "json"
    return "html"


def _parse_sitemap(body: str, base_url: str) -> list[dict]:
    """Extract pages from sitemap.xml. Falls through child sitemaps one level."""
    pages = []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        # Fallback: regex extraction
        locs = re.findall(r"<loc>(https?://[^<]+)</loc>", body)
        return [{"url": u.strip(), "title": "", "category": ""} for u in locs]

    tag = root.tag
    # Sitemap index → fetch child sitemaps (first only to avoid explosion)
    if "sitemapindex" in tag:
        child_locs = [
            elem.text.strip()
            for elem in root.iter()
            if elem.tag.endswith("}loc") or elem.tag == "loc"
        ]
        if child_locs:
            child_body, _ = _fetch(child_locs[0])
            pages.extend(_parse_sitemap(child_body, child_locs[0]))
        return pages

    for url_elem in root.iter():
        local = url_elem.tag.split("}")[-1] if "}" in url_elem.tag else url_elem.tag
        if local == "loc" and url_elem.text:
            pages.append({"url": url_elem.text.strip(), "title": "", "category": ""})

    return pages


def _parse_json(body: str) -> list[dict]:
    """Parse JSON body into page list."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        print(f"ERROR: JSON parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    pages = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                pages.append({"url": item, "title": "", "category": ""})
            elif isinstance(item, dict):
                pages.append(
                    {
                        "url": item.get("url") or item.get("loc") or "",
                        "title": item.get("title") or item.get("name") or "",
                        "category": item.get("category") or "",
                    }
                )
    elif isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, str):
                pages.append({"url": val, "title": key, "category": ""})
            elif isinstance(val, dict):
                pages.append(
                    {
                        "url": val.get("url") or val.get("loc") or "",
                        "title": val.get("title") or key,
                        "category": val.get("category") or "",
                    }
                )
    return [p for p in pages if p["url"]]


def _parse_html(body: str, base_url: str) -> list[dict]:
    """Extract <a href> links from HTML using regex (no external deps)."""
    # Extract title from <title> tag for category context
    title_match = re.search(r"<title[^>]*>([^<]+)</title>", body, re.IGNORECASE)
    page_title = title_match.group(1).strip() if title_match else ""

    # Find all anchor tags with href and text
    anchor_pattern = re.compile(
        r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL
    )
    pages = []
    seen = set()
    parsed_base = urlparse(base_url)

    for href, inner_html in anchor_pattern.findall(body):
        href = href.strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        # Resolve relative URLs
        if href.startswith("http"):
            full_url = href
        else:
            full_url = urljoin(base_url, href)

        # Only keep same-domain links
        parsed = urlparse(full_url)
        if parsed.netloc != parsed_base.netloc:
            continue

        if full_url in seen:
            continue
        seen.add(full_url)

        # Clean link text
        text = re.sub(r"<[^>]+>", "", inner_html).strip()
        pages.append({"url": full_url, "title": text or "", "category": page_title})

    return pages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Documentation index URL")
    args = parser.parse_args()

    url = args.url.rstrip("/")
    print(f"Fetching docs index: {url}", file=sys.stderr)

    body, content_type = _fetch(url)
    fmt = _detect_format(url, content_type, body)
    print(f"Detected format: {fmt}", file=sys.stderr)

    if fmt == "sitemap":
        pages = _parse_sitemap(body, url)
    elif fmt == "json":
        pages = _parse_json(body)
    else:
        pages = _parse_html(body, url)

    # Filter empty URLs
    pages = [p for p in pages if p.get("url")]

    if not pages:
        print(f"ERROR: No pages extracted from {url}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(pages)} pages", file=sys.stderr)
    print(json.dumps(pages, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
