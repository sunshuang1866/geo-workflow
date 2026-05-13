#!/usr/bin/env python3
"""Fetch filtered aggregated topics from community-hot-topic MongoDB.

Each topic in MongoDB clusters similar posts from the community's forum,
issue tracker, and maillist. Sources within each topic are classified and
excluded sources are stripped; topics with no remaining sources are dropped.
Surviving topics are sorted by remaining source count (descending).

Keep:    type=forum, [Question], [咨询], [问题] (and variants), no-bracket
Exclude: [Req], [Task], [RFC], [Roadmap], [Doc], [Bug] (and variants)

Usage:
    python3 fetch-hot-topics.py --community cann
    python3 fetch-hot-topics.py --community openeuler --limit 50

MongoDB credentials (all required):
    MONGODB_HOST, MONGODB_PORT, MONGODB_USER, MONGODB_PASSWORD
    MONGODB_DBNAME  (default: community-hot-topic)
    MONGODB_TLS     (default: true)

Output: JSON array to stdout, progress/errors to stderr.
  Also prints to stderr:
    TOTAL_FROM_MONGODB={N}
    MONGO_SOURCE_TYPES={"forum":N,"issue":N,"maillist":N}

Exit codes:
  0 — success (at least one topic returned)
  1 — no topics fetched (MongoDB unavailable or no passing topics)
"""

import argparse
import json
import os
import re
import sys
import urllib.parse


_CONSULT_BRACKETS = frozenset(["question", "咨询", "问题"])
_EXCLUDE_BRACKETS = frozenset(["requirement", "req", "task", "rfc", "roadmap",
                                "documentation", "doc", "bug"])


def _load_mongo_config() -> dict | None:
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

    Keep:    type=forum; [Question]/[咨询]/[问题] and variants; no bracket
    Exclude: [Req]/[Task]/[RFC]/[Roadmap]/[Doc]/[Bug] and variants
    """
    src_type = (source.get("type") or "").lower()
    if src_type == "forum":
        return "consult"

    title = (source.get("title") or "").lower()
    url   = (source.get("url") or "").lower()

    # Extract bracket prefix: "[Question|问题咨询]: ..." → "question"
    m = re.match(r"\[([^\]|]+)", title)
    if m:
        bracket = m.group(1).strip().lower()
        if any(k in bracket for k in _CONSULT_BRACKETS):
            return "consult"
        if any(k in bracket for k in _EXCLUDE_BRACKETS):
            return "exclude"
        # Unknown bracket → consult (err on the side of inclusion)
        return "consult"

    if "/forum/" in url or "hiascend.com/forum" in url:
        return "consult"

    # No bracket, no forum URL → consult (plain user post)
    return "consult"


def fetch_topics(community: str, limit: int | None) -> list[dict] | None:
    """Fetch topics from MongoDB, filter at source level, sort by remaining count.

    For each topic:
      - Classify each source as consult or exclude
      - Strip excluded sources from the count
      - Drop topics whose remaining_count == 0
    Then sort all surviving topics by remaining_count DESC.
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

    comm_key   = community.lower()
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

    if hot_col in existing_cols:
        for doc in db[hot_col].find():
            raw_topics.append({
                "title":           doc.get("title", ""),
                "sources":         doc.get("sources", []),
                "source_collection": "hot_topic",
            })

    if nothot_col in existing_cols:
        doc = db[nothot_col].find_one()
        if doc:
            for topic in doc.get("topics", []):
                raw_topics.append({
                    "title":           topic.get("title", ""),
                    "sources":         topic.get("sources", []),
                    "source_collection": "not_hot_topic",
                })

    print(f"MongoDB: {len(raw_topics)} raw topics for '{community}'", file=sys.stderr)

    # Source-level filter: strip excluded sources, drop topics with nothing left
    scored: list[dict] = []
    for topic in raw_topics:
        sources = topic.get("sources", [])
        classifications = [_classify_source(s) for s in sources]
        remaining_count = classifications.count("consult")
        exclude_count   = classifications.count("exclude")
        if remaining_count == 0:
            continue
        scored.append({**topic,
                       "remaining_count": remaining_count,
                       "exclude_count":   exclude_count,
                       "total_count":     len(sources)})

    dropped = len(raw_topics) - len(scored)
    print(f"MongoDB: {len(scored)} topics after source filter ({dropped} dropped)", file=sys.stderr)
    print(f"TOTAL_FROM_MONGODB={len(scored)}", file=sys.stderr)

    # Count source type distribution across all raw topics (informational)
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

    if not scored:
        return None

    # Sort by remaining_count DESC (no collection priority)
    scored.sort(key=lambda t: t["remaining_count"], reverse=True)

    if limit:
        scored = scored[:int(limit)]

    results = []
    for t in scored:
        sources = t["sources"]
        first_url = next((s.get("url", "") for s in sources if s.get("url")), "")
        results.append({
            "id":                None,
            "title":             t["title"],
            "url":               first_url,
            "views":             0,
            "reply_count":       len(sources),
            "created_at":        "",
            "source":            "mongodb",
            "source_collection": t["source_collection"],
            "consult_count":     t["remaining_count"],
            "exclude_count":     t["exclude_count"],
            "total_count":       t["total_count"],
        })
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch filtered aggregated topics from community-hot-topic MongoDB"
    )
    parser.add_argument("--community", required=True,
                        help="Community name, e.g. cann, openeuler, mindspore")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of topics to return (default: all passing topics)")
    args = parser.parse_args()

    results = fetch_topics(args.community, args.limit)
    if not results:
        print("ERROR: No topics fetched from MongoDB.", file=sys.stderr)
        sys.exit(1)

    print(f"fetch-hot-topics: returning {len(results)} topics.", file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))
