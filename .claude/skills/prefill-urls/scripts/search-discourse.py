#!/usr/bin/env python3
"""Search a Discourse forum and return the top matching topic URLs.

Usage:
    python3 search-discourse.py --base-url https://discuss.openubmc.cn --query "QEMU 仿真 调试" --limit 2

Output (stdout): JSON array of topic URLs, e.g.:
    ["https://discuss.openubmc.cn/t/qemu-bmc/123", "https://discuss.openubmc.cn/t/qemu-debug/456"]

Exit codes:
  0 — at least one result found
  1 — no results or API error
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

TIMEOUT = 10


def search(base_url: str, query: str, limit: int) -> list[str]:
    base_url = base_url.rstrip("/")
    encoded = urllib.parse.quote(query)
    url = f"{base_url}/search.json?q={encoded}"

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "geo-prefill-urls/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                print(f"ERROR: HTTP {resp.status} from {url}", file=sys.stderr)
                return []
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return []

    topics = data.get("topics", [])
    if not topics:
        # fall back to posts
        posts = data.get("posts", [])
        topic_ids = []
        seen = set()
        for p in posts:
            tid = p.get("topic_id")
            if tid and tid not in seen:
                seen.add(tid)
                slug = p.get("topic_slug", str(tid))
                topic_ids.append(f"{base_url}/t/{slug}/{tid}")
        return topic_ids[:limit]

    results = []
    for t in topics[:limit]:
        slug = t.get("slug", "")
        tid = t.get("id", "")
        if slug and tid:
            results.append(f"{base_url}/t/{slug}/{tid}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()

    results = search(args.base_url, args.query, args.limit)
    if not results:
        print(f"No results for: {args.query}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
