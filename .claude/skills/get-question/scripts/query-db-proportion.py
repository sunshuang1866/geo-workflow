#!/usr/bin/env python3
"""
Query the community-hot-topic MongoDB (or hotopic PostgreSQL fallback)
to get per-channel counts for a community, then compute proportional
question quotas.

Usage:
    python3 query-db-proportion.py --community cann --target 100

Output: JSON to stdout
  {
    "community": "cann",
    "target": 100,
    "counts":  {"forum": 126, "mail": 0, "question_issue": 0},
    "quotas":  {"forum": 100, "mail": 0, "question_issue": 0},
    "pg_channel_status": {
      "forum":          {"count": 45,  "available": true},
      "mail":           {"count": 0,   "available": false},
      "question_issue": {"count": 0,   "available": false}
    }
  }

Strategy:
  1. Query PostgreSQL for channel inventory (forum/mail/issue) — non-fatal.
  2. Query MongoDB for accurate consult-filtered forum count — non-fatal.
  3. Combine: MongoDB forum count overrides PG forum count when available;
     mail/question_issue always come from PostgreSQL.

Channels with count=0 are excluded from quota allocation (quota=0).

Exit codes:
  0 — success
  1 — community not found in config or DB connection failed
"""

import argparse
import json
import os
import re
import sys
import urllib.parse

try:
    import psycopg2
except ImportError:
    psycopg2 = None  # type: ignore


REQUIRED_DB_FIELDS = ("host", "port", "dbname", "user", "password")

# Source type keywords (mirrors fetch-forum-posts.py)
_CONSULT_BRACKETS = frozenset(["question", "bug"])
_EXCLUDE_BRACKETS = frozenset(["requirement", "req", "task", "rfc", "roadmap", "documentation", "doc"])


def _classify_source(source: dict) -> str:
    src_type = (source.get("type") or "").lower()
    if src_type == "forum":
        return "consult"
    title = (source.get("title") or "").lower()
    url   = (source.get("url") or "").lower()
    m = re.match(r"\[([^\]|]+)", title)
    if m:
        bracket = m.group(1).strip().lower()
        if any(k in bracket for k in _CONSULT_BRACKETS):
            return "consult"
        if any(k in bracket for k in _EXCLUDE_BRACKETS):
            return "exclude"
        return "consult"
    if "/forum/" in url or "hiascend.com/forum" in url:
        return "consult"
    return "consult"


def _dominant_source_type(sources: list) -> str:
    """Among consult-classified sources, return dominant type: 'forum' or 'issue'."""
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


def _passes_consult_filter(sources: list) -> bool:
    if not sources:
        return False
    classifications = [_classify_source(s) for s in sources]
    consult_n = classifications.count("consult")
    exclude_n = classifications.count("exclude")
    if exclude_n == 0:
        return True
    if consult_n == 0:
        return False
    return consult_n / len(classifications) >= 0.5


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


def query_counts_mongodb(community: str) -> dict | None:
    """Count consult-filtered topics from MongoDB. Returns {"forum": N} or None."""
    try:
        from pymongo import MongoClient  # type: ignore
    except ImportError:
        print("WARNING: pymongo not installed, skipping MongoDB count.", file=sys.stderr)
        return None

    cfg = _load_mongo_config()
    if not cfg:
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
        print(f"WARNING: No MongoDB collections for '{community}'", file=sys.stderr)
        return None

    forum_count = 0
    issue_count = 0

    def _tally(sources: list) -> None:
        nonlocal forum_count, issue_count
        if not _passes_consult_filter(sources):
            return
        dom = _dominant_source_type(sources)
        if dom == "issue":
            issue_count += 1
        else:
            forum_count += 1

    if hot_col in existing_cols:
        for doc in db[hot_col].find({}, {"sources": 1}):
            _tally(doc.get("sources", []))

    if nothot_col in existing_cols:
        doc = db[nothot_col].find_one({}, {"topics": 1})
        if doc:
            for topic in doc.get("topics", []):
                _tally(topic.get("sources", []))

    total = forum_count + issue_count
    print(
        f"MongoDB counts for '{comm_key}': "
        f"forum={forum_count}, question_issue={issue_count}, total={total}",
        file=sys.stderr,
    )
    return {"forum": forum_count, "question_issue": issue_count}


def normalize_community_key(community: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", community).upper()


def _load_json_config(key: str) -> dict | None:
    raw = os.environ.get(key, "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: {key} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"ERROR: {key} must be a JSON object", file=sys.stderr)
        sys.exit(1)
    return data


def _validate_db_config(cfg: dict, source: str) -> dict:
    missing = [k for k in REQUIRED_DB_FIELDS if not cfg.get(k)]
    if missing:
        print(
            f"ERROR: Incomplete DB config from {source}. Missing fields: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return cfg


def load_db_config(community: str) -> dict:
    """Load DB credentials from env/secret sources.

    Supported sources in priority order:
    1) HOTOPIC_DB_CONFIG_JSON: per-community JSON mapping
       e.g. {"openeuler": {"host":...,"port":...,"dbname":...,"user":...,"password":...}}
    2) HOTOPIC_DB_<COMMUNITY>_{HOST,PORT,NAME,USER,PASSWORD}
       where <COMMUNITY> is uppercased and non-alnum replaced by '_'
    3) HOTOPIC_DB_{HOST,PORT,NAME,USER,PASSWORD}: single-community fallback
    """
    key = community.lower()

    json_cfg = _load_json_config("HOTOPIC_DB_CONFIG_JSON")
    if json_cfg:
        if key in json_cfg:
            return _validate_db_config(json_cfg[key], "HOTOPIC_DB_CONFIG_JSON")
        print(
            f"ERROR: community '{community}' not found in HOTOPIC_DB_CONFIG_JSON",
            file=sys.stderr,
        )
        sys.exit(1)

    ck = normalize_community_key(community)
    scoped = {
        "host": os.environ.get(f"HOTOPIC_DB_{ck}_HOST", ""),
        "port": os.environ.get(f"HOTOPIC_DB_{ck}_PORT", ""),
        "dbname": os.environ.get(f"HOTOPIC_DB_{ck}_NAME", ""),
        "user": os.environ.get(f"HOTOPIC_DB_{ck}_USER", ""),
        "password": os.environ.get(f"HOTOPIC_DB_{ck}_PASSWORD", ""),
    }
    if any(scoped.values()):
        return _validate_db_config(scoped, f"HOTOPIC_DB_{ck}_*")

    generic = {
        "host": os.environ.get("HOTOPIC_DB_HOST", ""),
        "port": os.environ.get("HOTOPIC_DB_PORT", ""),
        "dbname": os.environ.get("HOTOPIC_DB_NAME", ""),
        "user": os.environ.get("HOTOPIC_DB_USER", ""),
        "password": os.environ.get("HOTOPIC_DB_PASSWORD", ""),
    }
    if any(generic.values()):
        return _validate_db_config(generic, "HOTOPIC_DB_*")

    print(
        "ERROR: No DB credentials found. Configure HOTOPIC_DB_CONFIG_JSON "
        "or HOTOPIC_DB_<COMMUNITY>_* or HOTOPIC_DB_* env vars.",
        file=sys.stderr,
    )
    sys.exit(1)


def compute_quotas(counts: dict, target: int) -> dict:
    """Proportional allocation; channels with count=0 get quota=0.
    Rounding remainder goes to the channel with the largest fractional part.
    """
    active = {ch: cnt for ch, cnt in counts.items() if cnt > 0}
    if not active:
        return {ch: 0 for ch in counts}

    total = sum(active.values())
    raw = {ch: target * cnt / total for ch, cnt in active.items()}
    floored = {ch: int(v) for ch, v in raw.items()}
    remainder = target - sum(floored.values())

    by_frac = sorted(active, key=lambda ch: raw[ch] - floored[ch], reverse=True)
    for i in range(remainder):
        floored[by_frac[i % len(by_frac)]] += 1

    return {ch: floored.get(ch, 0) for ch in counts}


def query_counts_postgresql(community: str) -> dict | None:
    """Query PostgreSQL hotopic DB for per-channel counts.

    Returns {"forum": N, "mail": N, "question_issue": N} or None if unavailable.
    Never exits — all failures are non-fatal (warnings only).
    """
    if psycopg2 is None:
        print("WARNING: psycopg2 not installed, skipping PostgreSQL channel check.",
              file=sys.stderr)
        return None

    try:
        cfg = load_db_config(community)
    except SystemExit:
        return None  # No PG credentials configured

    try:
        conn = psycopg2.connect(
            host=cfg["host"], port=int(cfg["port"]),
            dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"],
            connect_timeout=10,
        )
    except Exception as e:
        print(f"WARNING: PostgreSQL unavailable for '{community}': {e}", file=sys.stderr)
        return None

    cur = conn.cursor()
    key = community.lower()

    cur.execute("SELECT COUNT(*) FROM discussion WHERE is_deleted = False AND source_type = 'forum'")
    forum_total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM discussion WHERE is_deleted = False AND source_type = 'mail'")
    mail_total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM discussion
        WHERE is_deleted = False
          AND source_type = 'issue'
          AND LOWER(title) LIKE '%[question%'
    """)
    question_total = cur.fetchone()[0]

    conn.close()

    print(
        f"PG counts for '{key}': forum={forum_total}, mail={mail_total}, "
        f"question_issue={question_total}",
        file=sys.stderr,
    )
    return {"forum": forum_total, "mail": mail_total, "question_issue": question_total}


def query_counts(community: str) -> tuple[dict, dict]:
    """Return (counts, pg_channel_status).

    Strategy:
      1. Query PostgreSQL for channel inventory (forum/mail/issue) — non-fatal.
      2. Query MongoDB for accurate consult-filtered forum count — non-fatal.
      3. Combine: MongoDB forum count overrides PG forum count when available;
         mail/question_issue always come from PostgreSQL.

    counts:            allocation dict passed to compute_quotas()
    pg_channel_status: raw PostgreSQL counts keyed by channel name,
                       or {} if PostgreSQL is unavailable
    """
    # Step 1: PostgreSQL — channel inventory (non-fatal)
    pg_raw = query_counts_postgresql(community) or {}

    # Step 2: MongoDB — accurate forum count with consult-filter (non-fatal)
    mongo_counts = query_counts_mongodb(community)

    if mongo_counts is not None:
        forum_count  = mongo_counts.get("forum", 0)
        issue_count  = mongo_counts.get("question_issue", 0)
        forum_source = "mongodb"
    elif pg_raw:
        forum_count  = pg_raw.get("forum", 0)
        issue_count  = 0  # PG issue count handled separately below
        forum_source = "postgresql"
    else:
        forum_count  = 0
        issue_count  = 0
        forum_source = "unavailable"
        print("WARNING: Both MongoDB and PostgreSQL unavailable; forum count=0.",
              file=sys.stderr)

    # For issue quota: MongoDB value takes priority; PG fills in if MongoDB
    # returned 0 issue count (e.g., community has no issue-type topics in Mongo)
    if mongo_counts is not None and issue_count == 0:
        pg_issue = pg_raw.get("question_issue", 0)
        if pg_issue > 0:
            issue_count = pg_issue
            print(f"MongoDB question_issue=0; using PostgreSQL question_issue={pg_issue}",
                  file=sys.stderr)

    counts = {
        "forum":          forum_count,
        "mail":           pg_raw.get("mail", 0),
        "question_issue": issue_count,
    }

    pg_channel_status = {
        ch: {"count": cnt, "available": cnt > 0}
        for ch, cnt in pg_raw.items()
    }

    print(
        f"Combined counts for '{community.lower()}': {counts} "
        f"(forum_source={forum_source})",
        file=sys.stderr,
    )
    return counts, pg_channel_status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query hotopic DB channel counts and compute question quotas"
    )
    parser.add_argument("--community", required=True,
                        help="Community name, e.g. openeuler, mindspore")
    parser.add_argument("--target", type=int, required=True,
                        help="Total number of questions to allocate across channels")
    args = parser.parse_args()

    counts, pg_channel_status = query_counts(args.community)
    quotas = compute_quotas(counts, args.target)

    result = {
        "community": args.community.lower(),
        "target": args.target,
        "counts": counts,
        "quotas": quotas,
        "pg_channel_status": pg_channel_status,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
