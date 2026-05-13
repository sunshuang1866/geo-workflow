#!/usr/bin/env python3
"""Fetch individual forum posts from PostgreSQL hotopic DB or Discourse API.

Primary:  PostgreSQL hotopic DB — queries discussion table (source_type='forum'),
          filters views > MIN_VIEWS, returns top FORUM_TOP_N posts sorted by views DESC.
Fallback: Discourse API — fetches topics from all active forum categories,
          applies the same views > MIN_VIEWS threshold, returns top FORUM_TOP_N.

This script handles Channel 2 of the forum path. Channel 1 (MongoDB aggregated
topics) is handled by fetch-hot-topics.py.

Usage:
    python3 fetch-forum-posts.py --community openeuler
    python3 fetch-forum-posts.py --community mindspore --api-url https://discuss.mindspore.cn
    python3 fetch-forum-posts.py --community cann --since 2024-01-01

PostgreSQL credentials:
    HOTOPIC_DB_CONFIG_JSON  — preferred, per-community JSON mapping
    HOTOPIC_DB_<COMMUNITY>_{HOST,PORT,NAME,USER,PASSWORD}
    HOTOPIC_DB_{HOST,PORT,NAME,USER,PASSWORD}

Output: JSON array to stdout, progress/errors to stderr.
  Also prints to stderr:
    TOTAL_FROM_DB={N}        (when PostgreSQL is used)
    TOTAL_FROM_DISCOURSE={N} (when Discourse API fallback is used)

Exit codes:
  0 — success (at least one post returned)
  1 — no posts fetched from any source
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


MIN_VIEWS   = 50
FORUM_TOP_N = 30

REQUIRED_DB_FIELDS = ("host", "port", "dbname", "user", "password")


def _normalize_key(community: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", community).upper()


def _load_db_config(community: str) -> dict | None:
    """Return DB config dict from env vars, or None if not configured."""
    key = community.lower()

    raw = os.environ.get("HOTOPIC_DB_CONFIG_JSON", "").strip()
    if raw:
        try:
            mapping = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"WARNING: HOTOPIC_DB_CONFIG_JSON is not valid JSON: {e}", file=sys.stderr)
            return None
        if key in mapping:
            cfg = mapping[key]
            if all(cfg.get(f) for f in REQUIRED_DB_FIELDS):
                return cfg
        return None

    ck = _normalize_key(community)
    scoped = {
        "host":     os.environ.get(f"HOTOPIC_DB_{ck}_HOST", ""),
        "port":     os.environ.get(f"HOTOPIC_DB_{ck}_PORT", ""),
        "dbname":   os.environ.get(f"HOTOPIC_DB_{ck}_NAME", ""),
        "user":     os.environ.get(f"HOTOPIC_DB_{ck}_USER", ""),
        "password": os.environ.get(f"HOTOPIC_DB_{ck}_PASSWORD", ""),
    }
    if all(scoped.values()):
        return scoped

    generic = {
        "host":     os.environ.get("HOTOPIC_DB_HOST", ""),
        "port":     os.environ.get("HOTOPIC_DB_PORT", ""),
        "dbname":   os.environ.get("HOTOPIC_DB_NAME", ""),
        "user":     os.environ.get("HOTOPIC_DB_USER", ""),
        "password": os.environ.get("HOTOPIC_DB_PASSWORD", ""),
    }
    if all(generic.values()):
        return generic

    return None


def fetch_from_db(community: str, since: str | None, limit: int | None) -> list[dict] | None:
    """Fetch forum posts from PostgreSQL hotopic DB. Returns list or None on failure."""
    try:
        import psycopg2
    except ImportError:
        print("WARNING: psycopg2 not installed, skipping DB path.", file=sys.stderr)
        return None

    cfg = _load_db_config(community)
    if not cfg:
        print("WARNING: No DB credentials found, skipping DB path.", file=sys.stderr)
        return None

    try:
        conn = psycopg2.connect(
            host=cfg["host"], port=int(cfg["port"]),
            dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"],
            connect_timeout=10,
        )
    except Exception as e:
        print(f"WARNING: DB connection failed: {e}", file=sys.stderr)
        return None

    try:
        cur = conn.cursor()
        params: list = []
        where = "source_type = 'forum' AND is_deleted = false"
        if since:
            where += " AND created_at >= %s"
            params.append(since)

        # Prefer sorting by views (field name varies across hotopic DB variants).
        rows = None
        view_candidates = ("view_num", "views", "read_num", "visit_num")
        for view_col in view_candidates:
            query = f"""
                SELECT source_id, title, url, created_at,
                       COALESCE({view_col}, 0) AS views,
                       comment_num
                FROM discussion
                WHERE {where}
                  AND COALESCE({view_col}, 0) > {MIN_VIEWS}
                ORDER BY COALESCE({view_col}, 0) DESC NULLS LAST
                LIMIT {int(limit or FORUM_TOP_N)}
            """
            try:
                cur.execute(query, params)
                rows = cur.fetchall()
                print(f"DB: using view column '{view_col}' for forum ranking", file=sys.stderr)
                break
            except Exception:
                conn.rollback()

        if rows is None:
            # No view column found — fall back to comment_num + recency ordering
            print("WARNING: No view column found; falling back to comment_num ordering.", file=sys.stderr)
            query = f"""
                SELECT source_id, title, url, created_at,
                       0 AS views,
                       comment_num
                FROM discussion
                WHERE {where}
                ORDER BY comment_num DESC NULLS LAST, created_at DESC
            """
            if limit:
                query += f" LIMIT {int(limit)}"
            try:
                cur.execute(query, params)
                rows = cur.fetchall()
            except Exception as e:
                print(f"WARNING: fallback query failed: {e}", file=sys.stderr)
                conn.close()
                return None

        if not rows:
            print(f"WARNING: DB returned 0 forum rows for '{community}' (views>{MIN_VIEWS}).", file=sys.stderr)
            return None

        results = [
            {
                "id":          row[0],
                "title":       row[1],
                "url":         row[2],
                "views":       row[4] or 0,
                "reply_count": row[5] or 0,
                "created_at":  row[3].isoformat() if row[3] else "",
                "source":      "db",
            }
            for row in rows
            if row[1] and row[2]
        ]
        print(
            f"DB: fetched {len(results)} forum posts for '{community}'"
            + (f" since {since}" if since else ""),
            file=sys.stderr,
        )
        print(f"TOTAL_FROM_DB={len(results)}", file=sys.stderr)
        conn.close()
        return results

    except Exception as e:
        print(f"WARNING: DB query failed: {e}", file=sys.stderr)
        try:
            conn.close()
        except Exception:
            pass
        return None


# ── Discourse API fallback ────────────────────────────────────────────────────

def _fetch_json(url: str) -> dict:
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


SKIP_SLUGS = {"meta", "staff", "uncategorized", "site-feedback"}


def _fetch_all_categories(base_url: str) -> list[dict]:
    try:
        data = _fetch_json(f"{base_url}/categories.json")
        cats = data.get("category_list", {}).get("categories", [])
        return [c for c in cats
                if c.get("topic_count", 0) > 0 and c.get("slug", "") not in SKIP_SLUGS]
    except Exception as e:
        print(f"WARNING: Failed to fetch categories: {e}", file=sys.stderr)
        return []


def _fetch_category_topics(base_url: str, slug: str, category_id: int) -> list[dict]:
    topics = []
    for page in range(4):
        url = f"{base_url}/c/{slug}/{category_id}/l/top.json?period=all&page={page}"
        try:
            data = _fetch_json(url)
        except Exception:
            break
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            break
        topics.extend(topic_list)
    return topics


def fetch_from_discourse(api_url: str, limit: int | None) -> list[dict]:
    """Fetch topics via Discourse API. Returns empty list on failure."""
    base_url = api_url.rstrip("/")
    categories = _fetch_all_categories(base_url)
    print(f"Discourse: discovered {len(categories)} active categories", file=sys.stderr)

    all_topics: dict = {}
    for cat in categories:
        slug = cat.get("slug", "")
        cat_id = cat.get("id")
        try:
            topics = _fetch_category_topics(base_url, slug, cat_id)
            added = sum(1 for t in topics if t["id"] not in all_topics)
            for t in topics:
                all_topics.setdefault(t["id"], t)
            print(f"  [{slug}] {added} topics added", file=sys.stderr)
        except Exception as e:
            print(f"  WARNING: Failed to fetch category '{slug}': {e}", file=sys.stderr)

    results = []
    for topic in all_topics.values():
        if topic.get("views", 0) <= MIN_VIEWS:
            continue
        results.append({
            "id":          topic.get("id"),
            "title":       topic.get("title", ""),
            "url":         "",
            "views":       topic.get("views", 0),
            "reply_count": topic.get("reply_count", 0),
            "created_at":  topic.get("created_at", ""),
            "source":      "discourse",
        })

    results.sort(key=lambda t: t["views"], reverse=True)
    total = len(results)
    if limit:
        results = results[:limit]
    print(f"Discourse: returning {len(results)} topics (pool: {total})", file=sys.stderr)
    print(f"TOTAL_FROM_DISCOURSE={total}", file=sys.stderr)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch forum posts from PostgreSQL hotopic DB or Discourse API"
    )
    parser.add_argument("--community", required=True,
                        help="Community name, e.g. openeuler, mindspore")
    parser.add_argument("--api-url", default=None,
                        help="Discourse forum base URL, used as fallback "
                             "(e.g. https://discuss.mindspore.cn)")
    parser.add_argument("--since", default=None,
                        help="Only return posts created on or after this date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of posts to return (default: top 30)")
    args = parser.parse_args()

    limit = min(args.limit or FORUM_TOP_N, FORUM_TOP_N)

    results = fetch_from_db(args.community, args.since, limit)
    if results is None:
        if args.api_url:
            print("PG unavailable, falling back to Discourse API.", file=sys.stderr)
            results = fetch_from_discourse(args.api_url, limit)
        else:
            print("PG unavailable. No --api-url provided for Discourse fallback.", file=sys.stderr)
            results = []

    if not results:
        print("ERROR: No forum posts fetched.", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(results, ensure_ascii=False, indent=2))
