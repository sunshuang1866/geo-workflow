#!/usr/bin/env python3
"""Fetch top forum posts from a Discourse-based community forum.

Usage:
    python3 fetch-forum-posts.py --community <name> --api-url <url>
    python3 fetch-forum-posts.py --community MindSpore --api-url https://discuss.mindspore.cn
    python3 fetch-forum-posts.py --community MindSpore --api-url https://discuss.mindspore.cn --category help

Output: JSON array of posts to stdout, errors to stderr.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import urllib.parse


def fetch_json(url: str) -> dict:
    """Fetch JSON from a URL with error handling."""
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} fetching {url}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e.reason}", file=sys.stderr)
        raise


def resolve_category(base_url: str, slug: str) -> tuple[str, int] | None:
    """Resolve a category slug to (slug, id) by querying /categories.json."""
    try:
        data = fetch_json(f"{base_url}/categories.json")
        categories = data.get("category_list", {}).get("categories", [])
        for cat in categories:
            if cat.get("slug") == slug:
                return (slug, cat["id"])
        print(f"WARNING: Category slug '{slug}' not found on {base_url}.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"WARNING: Failed to fetch categories from {base_url}: {e}", file=sys.stderr)
        return None


SKIP_SLUGS = {"meta", "staff", "uncategorized", "site-feedback"}


def fetch_all_categories(base_url: str) -> list[dict]:
    """Return all active categories (topic_count > 0, skip meta/staff)."""
    try:
        data = fetch_json(f"{base_url}/categories.json")
        cats = data.get("category_list", {}).get("categories", [])
        return [
            c for c in cats
            if c.get("topic_count", 0) > 0 and c.get("slug", "") not in SKIP_SLUGS
        ]
    except Exception as e:
        print(f"WARNING: Failed to fetch categories: {e}", file=sys.stderr)
        return []


def fetch_category_topics(base_url: str, slug: str, category_id: int) -> list[dict]:
    """Fetch topics sorted by views from a specific category via /l/top endpoint."""
    topics = []
    page = 0
    while True:
        url = f"{base_url}/c/{slug}/{category_id}/l/top.json?period=all&page={page}"
        data = fetch_json(url)
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            break
        topics.extend(topic_list)
        page += 1
        if page > 3:
            break
    return topics


def normalize_topic(topic: dict) -> dict:
    """Extract relevant fields from a Discourse topic object."""
    return {
        "id": topic.get("id"),
        "title": topic.get("title", ""),
        "views": topic.get("views", 0),
        "reply_count": topic.get("reply_count", 0),
        "like_count": topic.get("like_count", 0),
        "posts_count": topic.get("posts_count", 0),
        "category_id": topic.get("category_id"),
        "tags": topic.get("tags", []),
        "has_accepted_answer": topic.get("has_accepted_answer", False),
        "pinned": topic.get("pinned", False),
        "closed": topic.get("closed", False),
        "created_at": topic.get("created_at", ""),
        "last_posted_at": topic.get("last_posted_at", ""),
    }


def fetch_posts(community: str, api_url: str,
                category: str | None = None,
                limit: int | None = None) -> list[dict]:
    """Fetch forum topics, deduplicate, and sort by relevance score."""
    base_url = api_url.rstrip("/")

    all_topics = {}  # id → topic, for dedup

    if category:
        # Single category mode: resolve slug → id, fetch views-sorted topics
        resolved = resolve_category(base_url, category)
        if resolved:
            slug, cat_id = resolved
            try:
                topics = fetch_category_topics(base_url, slug, cat_id)
                for t in topics:
                    all_topics[t["id"]] = t
                print(f"Fetched {len(topics)} topics from category '{slug}'", file=sys.stderr)
            except Exception as e:
                print(f"WARNING: Failed to fetch category '{slug}': {e}", file=sys.stderr)
    else:
        # Global mode: fetch all active categories, collect views-sorted topics from each,
        # merge and deduplicate — gives a complete pool sorted by views across all categories.
        categories = fetch_all_categories(base_url)
        print(f"Discovered {len(categories)} active categories", file=sys.stderr)
        for cat in categories:
            slug = cat.get("slug", "")
            cat_id = cat.get("id")
            try:
                topics = fetch_category_topics(base_url, slug, cat_id)
                added = 0
                for t in topics:
                    if t["id"] not in all_topics:
                        all_topics[t["id"]] = t
                        added += 1
                print(f"  [{slug}] {added} topics added ({len(topics)} fetched)", file=sys.stderr)
            except Exception as e:
                print(f"  WARNING: Failed to fetch category '{slug}': {e}", file=sys.stderr)

    if not all_topics:
        print("ERROR: No topics fetched from any source.", file=sys.stderr)
        sys.exit(1)

    # Normalize, filter low-traffic topics
    results = []
    for topic in all_topics.values():
        normalized = normalize_topic(topic)
        if normalized["views"] <= 50:
            continue
        results.append(normalized)

    results.sort(key=lambda t: t["views"], reverse=True)
    total = len(results)
    if limit is not None and limit > 0:
        results = results[:limit]
    print(f"Returning {len(results)} topics (total pool: {total})", file=sys.stderr)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch forum posts from Discourse")
    parser.add_argument("--community", required=True, help="Community name")
    parser.add_argument("--api-url", required=True, help="Forum base URL (e.g., https://discuss.mindspore.cn)")
    parser.add_argument("--category", default=None,
                        help="Category slug to filter (auto-resolves ID via /categories.json)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of topics to return (proportional quota from DB)")
    args = parser.parse_args()

    posts = fetch_posts(args.community, args.api_url, args.category, args.limit)
    print(json.dumps(posts, ensure_ascii=False, indent=2))
