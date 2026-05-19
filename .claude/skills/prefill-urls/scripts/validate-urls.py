#!/usr/bin/env python3
"""Batch HTTP reachability check for a list of URLs.

Usage:
    python3 validate-urls.py '["https://...", "https://..."]'

Input:  JSON array of URLs (first CLI argument)
Output: JSON object {"url": true/false} to stdout
        true  = HTTP 2xx or 3xx
        false = connection error, timeout, or 4xx/5xx

Exit codes:
  0 — completed (even if some URLs failed)
  1 — bad input (not valid JSON array)
"""

import json
import sys
import urllib.request
import urllib.error


TIMEOUT = 8


def check_url(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "geo-prefill-urls/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as e:
        return e.code < 400
    except Exception:
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-urls.py '[\"url1\", \"url2\"]'", file=sys.stderr)
        sys.exit(1)

    try:
        urls = json.loads(sys.argv[1])
        if not isinstance(urls, list):
            raise ValueError("expected JSON array")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: invalid input — {e}", file=sys.stderr)
        sys.exit(1)

    results = {}
    for i, url in enumerate(urls, 1):
        ok = check_url(url)
        results[url] = ok
        status = "OK" if ok else "FAIL"
        print(f"[{i}/{len(urls)}] {status}  {url}", file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
