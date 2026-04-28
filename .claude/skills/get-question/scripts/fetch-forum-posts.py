#!/usr/bin/env python3
"""Fetch forum topics for a community from two complementary sources.

Channel 1 — MongoDB community-hot-topic (always tried first, non-fatal):
  Reads {community}_hot_topic + {community}_not_hot_topic, applies consult-filter,
  returns ALL passing aggregated topics (each topic = cluster of similar forum/issue posts).
  No view threshold applied here — MongoDB topics are already curated/clustered.

Channel 2 — PostgreSQL hotopic DB / Discourse API (always tried, non-fatal):
  Returns individual forum posts with views > {MIN_VIEWS}, sorted DESC, capped at {FORUM_TOP_N}.
  PostgreSQL is tried first; Discourse API is the fallback.

Both channel results are combined and returned.
LLM-level deduplication happens downstream (Step 8 in SKILL.md).

Usage:
    python3 fetch-forum-posts.py --community cann --limit 72
    python3 fetch-forum-posts.py --community mindspore --api-url https://discuss.mindspore.cn
    python3 fetch-forum-posts.py --community cann --since 2024-01-01

MongoDB credentials (channel 1):
    MONGODB_HOST, MONGODB_PORT, MONGODB_USER, MONGODB_PASSWORD
    MONGODB_DBNAME  (default: community-hot-topic)
    MONGODB_TLS     (default: true)

PostgreSQL credentials (channel 2):
    HOTOPIC_DB_CONFIG_JSON  — preferred, per-community JSON mapping
    HOTOPIC_DB_<COMMUNITY>_{HOST,PORT,NAME,USER,PASSWORD}
    HOTOPIC_DB_{HOST,PORT,NAME,USER,PASSWORD}

Output: JSON array to stdout, progress/errors to stderr.
Exit codes:
  0 — success (at least one topic returned)
  1 — no topics fetched from any source
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


# Forum-specific constants
MIN_VIEWS    = 50   # minimum views threshold for PG/Discourse channel
FORUM_TOP_N  = 30   # maximum posts from PG/Discourse channel


# ── MongoDB config loading + consult filter ─────────────────────────────────

# Source type keywords for consult/exclude classification
_CONSULT_BRACKETS = frozenset(["question", "bug"])
_EXCLUDE_BRACKETS = frozenset(["requirement", "req", "task", "rfc", "roadmap", "documentation", "doc"])


def _load_mongo_config() -> dict | None:
    """Return MongoDB config dict from env vars, or None if not configured."""
    host     = os.environ.get("MONGODB_HOST", "").strip()
    port     = os.environ.get("MONGODB_PORT", "").strip()
    user     = os.environ.get("MONGODB_USER", "").strip()
    password = os.environ.get("MONGODB_PASSWORD", "").strip()
    dbname   = os.environ.get("MONGODB_DBNAME", "community-hot-topic").strip()
    tls      = os.environ.get("MONGODB_TLS", "true").strip().lower() not in ("false", "0", "no")
    if host and port and user and password:
        return {"host": host, "port": port, "user": user,
                "password": password, "dbname": dbname, "tls": tls}
    return None


def _classify_source(source: dict) -> str:
    """Classify a topic source as 'consult' or 'exclude'.

    Consult: Forum (type=forum), Question, Bug  →  kept
    Exclude: Requirement/Req, Task, RFC, Roadmap, Documentation/Doc  →  dropped
    Untagged issues (no bracket in title) → treated as consult.
    """
    src_type = (source.get("type") or "").lower()
    if src_type == "forum":
        return "consult"

    title = (source.get("title") or "").lower()
    url   = (source.get("url") or "").lower()

    # Extract bracket prefix from issue title: "[Question|问题咨询]: ..."
    m = re.match(r"\[([^\]|]+)", title)
    if m:
        bracket = m.group(1).strip().lower()
        if any(k in bracket for k in _CONSULT_BRACKETS):
            return "consult"
        if any(k in bracket for k in _EXCLUDE_BRACKETS):
            return "exclude"
        # Unknown bracket type → consult
        return "consult"

    # No bracket: forum URL → consult
    if "/forum/" in url or "hiascend.com/forum" in url:
        return "consult"

    # Untagged issue without bracket → treat as consult (plain user bug/question)
    return "consult"


def _apply_consult_filter(topics: list[dict]) -> list[dict]:
    """Filter topics by consult-source ratio.

    Keep:    all sources are consult types (Question/Bug/Forum)
    Discard: all sources are exclude types (Req/Task/RFC/Doc)
    Mixed:   keep if consult_count / total >= 0.5, else discard
    """
    kept = []
    for topic in topics:
        sources = topic.get("sources", [])
        if not sources:
            continue
        classifications = [_classify_source(s) for s in sources]
        consult_n = classifications.count("consult")
        exclude_n = classifications.count("exclude")
        total = len(classifications)

        if exclude_n == 0:                             # pure consult
            kept.append(topic)
        elif consult_n == 0:                           # pure exclude → drop
            pass
        elif consult_n / total >= 0.5:                 # mixed ≥50% consult → keep
            kept.append(topic)
    return kept


def _dominant_source_type(sources: list[dict]) -> str:
    """Among consult-classified sources, determine dominant type: 'forum' or 'issue'.

    Returns 'forum' if forum sources >= issue sources, else 'issue'.
    'issue' covers both issue-type and untagged no-bracket sources.
    """
    forum_n = 0
    issue_n = 0
    for s in sources:
        if _classify_source(s) != "consult":
            continue
        src_type = (s.get("type") or "").lower()
        if src_type == "forum":
            forum_n += 1
        else:
            issue_n += 1
    return "issue" if issue_n > forum_n else "forum"


def _source_type_counts(sources: list[dict]) -> dict:
    """Count consult-classified sources by type: {"forum": N, "issue": M}."""
    forum_n = 0
    issue_n = 0
    for s in sources:
        if _classify_source(s) != "consult":
            continue
        src_type = (s.get("type") or "").lower()
        if src_type == "forum":
            forum_n += 1
        else:
            issue_n += 1
    return {"forum": forum_n, "issue": issue_n}


def fetch_from_mongodb(community: str, limit: int | None) -> list[dict] | None:
    """Fetch consult-filtered topics from MongoDB community-hot-topic DB.

    Reads {community}_hot_topic (individual docs) and
    {community}_not_hot_topic (single doc with 'topics' array).
    Applies consult filter, sorts hot_topic first by 'order', then not_hot_topic.
    Returns list or None on failure.
    """
    try:
        from pymongo import MongoClient  # type: ignore
    except ImportError:
        print("WARNING: pymongo not installed, skipping MongoDB path.", file=sys.stderr)
        return None

    cfg = _load_mongo_config()
    if not cfg:
        print("WARNING: No MongoDB credentials found, skipping MongoDB path.", file=sys.stderr)
        return None

    try:
        pwd = urllib.parse.quote(cfg["password"], safe="")
        tls_params = "&tls=true&tlsAllowInvalidCertificates=true" if cfg["tls"] else ""
        uri = (f"mongodb://{cfg['user']}:{pwd}@{cfg['host']}:{cfg['port']}/"
               f"?authSource=admin{tls_params}")
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        db = client[cfg["dbname"]]
    except Exception as e:
        print(f"WARNING: MongoDB connection failed: {e}", file=sys.stderr)
        return None

    comm_key = community.lower()
    hot_col    = f"{comm_key}_hot_topic"
    nothot_col = f"{comm_key}_not_hot_topic"

    try:
        existing_cols = set(db.list_collection_names())
    except Exception as e:
        print(f"WARNING: MongoDB list_collections failed: {e}", file=sys.stderr)
        return None

    if hot_col not in existing_cols and nothot_col not in existing_cols:
        print(f"WARNING: No MongoDB collections found for '{community}' "
              f"(tried: {hot_col}, {nothot_col})", file=sys.stderr)
        return None

    raw_topics: list[dict] = []

    # 1. hot_topic: each document is one topic cluster
    if hot_col in existing_cols:
        for doc in db[hot_col].find():
            raw_topics.append({
                "title":       doc.get("title", ""),
                "sources":     doc.get("sources", []),
                "_collection": "hot_topic",
                "_order":      int(doc.get("order") or 9999),
            })

    # 2. not_hot_topic: single document with a 'topics' array
    if nothot_col in existing_cols:
        doc = db[nothot_col].find_one()
        if doc:
            for i, topic in enumerate(doc.get("topics", [])):
                raw_topics.append({
                    "title":       topic.get("title", ""),
                    "sources":     topic.get("sources", []),
                    "_collection": "not_hot_topic",
                    "_order":      i,
                })

    print(f"MongoDB: {len(raw_topics)} raw topics for '{community}'", file=sys.stderr)

    # Apply consult filter
    filtered = _apply_consult_filter(raw_topics)
    print(f"MongoDB: {len(filtered)} topics after consult filter "
          f"({len(raw_topics)-len(filtered)} dropped)", file=sys.stderr)
    print(f"TOTAL_FROM_MONGODB={len(filtered)}", file=sys.stderr)

    # Count source type distribution across all raw topics (before filter)
    type_dist: dict[str, int] = {"forum": 0, "issue": 0, "maillist": 0}
    for topic in raw_topics:
        for s in topic.get("sources", []):
            raw_type = (s.get("type") or "").lower()
            url = (s.get("url") or "").lower()
            if raw_type == "forum" or (not raw_type and "/forum/" in url):
                type_dist["forum"] += 1
            elif raw_type == "maillist" or (not raw_type and "maillist" in url):
                type_dist["maillist"] += 1
            else:
                type_dist["issue"] += 1
    print(f"MONGO_SOURCE_TYPES={json.dumps(type_dist)}", file=sys.stderr)

    if not filtered:
        return None

    # Sort: hot_topic (by order ASC) first, then not_hot_topic
    filtered.sort(key=lambda t: (0 if t["_collection"] == "hot_topic" else 1, t["_order"]))

    if limit:
        filtered = filtered[:int(limit)]

    results = []
    for t in filtered:
        sources = t["sources"]
        sources = t["sources"]
        first_url = next((s.get("url", "") for s in sources if s.get("url")), "")
        classifications = [_classify_source(s) for s in sources]
        consult_n = classifications.count("consult")
        exclude_n = classifications.count("exclude")
        results.append({
            "id":          None,
            "title":       t["title"],
            "url":         first_url,
            "views":       0,
            "reply_count": len(sources),
            "created_at":  "",
            "source":      "mongodb",
            "source_collection": t["_collection"],
            "consult_count": consult_n,
            "exclude_count": exclude_n,
            "total_count":   len(sources),
        })
    return results


# ── PostgreSQL DB credential loading (mirrors query-db-proportion.py) ─────────

REQUIRED_DB_FIELDS = ("host", "port", "dbname", "user", "password")


def _normalize_key(community: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", community).upper()


def _load_db_config(community: str) -> dict | None:
    """Return DB config dict, or None if no credentials configured."""
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


# ── DB fetch path ─────────────────────────────────────────────────────────────

def fetch_from_db(community: str, since: str | None, limit: int | None) -> list[dict] | None:
    """Fetch forum posts from hotopic DB. Returns list or None on failure."""
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
                "id": row[0],
                "title": row[1],
                "url": row[2],
                "views": row[4] or 0,
                "reply_count": row[5] or 0,
                "created_at": row[3].isoformat() if row[3] else "",
                "source": "db",
            }
            for row in rows
            if row[1] and row[2]
        ]
        print(
            f"DB: fetched {len(results)} forum posts for '{community}'"
            + (f" since {since}" if since else ""),
            file=sys.stderr,
        )
        # Report to stderr so get-question skill can read total
        print(f"TOTAL_FROM_DB={len(results)}", file=sys.stderr)
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


def _normalize_discourse_topic(topic: dict) -> dict:
    return {
        "id": topic.get("id"),
        "title": topic.get("title", ""),
        "url": "",
        "views": topic.get("views", 0),
        "reply_count": topic.get("reply_count", 0),
        "created_at": topic.get("created_at", ""),
        "source": "discourse",
    }


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
        norm = _normalize_discourse_topic(topic)
        if norm["views"] <= 50:
            continue
        results.append(norm)

    results.sort(key=lambda t: t["views"], reverse=True)
    total = len(results)
    if limit:
        results = results[:limit]
    print(f"Discourse: returning {len(results)} topics (pool: {total})", file=sys.stderr)
    print(f"TOTAL_FROM_DISCOURSE={total}", file=sys.stderr)
    return results


# ── Entry point ───────────────────────────────────────────────────────────────

def fetch_posts(community: str, api_url: str | None,
                since: str | None, limit: int | None) -> list[dict]:
    """Fetch topics from BOTH channels and combine.

    Channel 1 — MongoDB: all consult-filtered aggregated topics (non-fatal).
    Channel 2 — PG/Discourse: top {FORUM_TOP_N} individual forum posts (views>{MIN_VIEWS}).
    """
    # Channel 1: MongoDB (all consult-filtered aggregated topics)
    mongo_results = fetch_from_mongodb(community, limit=None)
    if mongo_results is None:
        mongo_results = []
        print("Channel 1 (MongoDB): unavailable.", file=sys.stderr)
    else:
        print(f"Channel 1 (MongoDB): {len(mongo_results)} aggregated topics.", file=sys.stderr)

    # Channel 2: PostgreSQL forum (views>{MIN_VIEWS}, top {FORUM_TOP_N})
    forum_limit = min(limit or FORUM_TOP_N, FORUM_TOP_N)
    pg_results = fetch_from_db(community, since, forum_limit)
    if pg_results is None:
        pg_results = []
        if api_url:
            print(f"Channel 2 (PG): unavailable, falling back to Discourse API.", file=sys.stderr)
            disc = fetch_from_discourse(api_url, forum_limit)
            if disc:
                pg_results = disc
        else:
            print("Channel 2 (PG): unavailable. No --api-url provided for Discourse fallback.",
                  file=sys.stderr)
    else:
        print(f"Channel 2 (PG forum): {len(pg_results)} posts (views>{MIN_VIEWS}).", file=sys.stderr)

    combined = mongo_results + pg_results
    if not combined:
        print("ERROR: No topics fetched from either channel.", file=sys.stderr)
        sys.exit(1)

    # Apply overall limit if given (MongoDB topics take priority in ordering)
    if limit and len(combined) > limit:
        combined = combined[:limit]

    print(
        f"source=combined mongo={len(mongo_results)} forum_pg={len(pg_results)} "
        f"total={len(combined)}",
        file=sys.stderr,
    )
    return combined


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch forum posts from hotopic DB (primary) or Discourse API (fallback)"
    )
    parser.add_argument("--community", required=True, help="Community name, e.g. cann, mindspore")
    parser.add_argument("--api-url", default=None,
                        help="Discourse forum base URL, used only as fallback "
                             "(e.g. https://discuss.mindspore.cn)")
    parser.add_argument("--category", default=None,
                        help="(Discourse fallback only) Category slug to filter")
    parser.add_argument("--since", default=None,
                        help="Only return posts created on or after this date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of posts to return")
    args = parser.parse_args()

    posts = fetch_posts(args.community, args.api_url, args.since, args.limit)
    print(json.dumps(posts, ensure_ascii=False, indent=2))
