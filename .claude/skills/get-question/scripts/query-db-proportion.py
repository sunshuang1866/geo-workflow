#!/usr/bin/env python3
"""
Query the hotopic database to get per-channel counts for a community,
then compute proportional question quotas.

Usage:
    python3 query-db-proportion.py --community openeuler --target 100

Output: JSON to stdout
  {
    "community": "openeuler",
    "target": 100,
    "counts":  {"forum": 762, "mail": 29, "question_issue": 15},
    "quotas":  {"forum": 85,  "mail": 3,  "question_issue": 12}
  }

Channels with count=0 are excluded from allocation (quota=0).

Exit codes:
  0 — success
  1 — community not found in config or DB connection failed
"""

import argparse
import json
import os
import re
import sys

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)


REQUIRED_DB_FIELDS = ("host", "port", "dbname", "user", "password")


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


def query_counts(community: str) -> dict:
    key = community.lower()
    cfg = load_db_config(community)
    try:
        conn = psycopg2.connect(
            host=cfg["host"], port=int(cfg["port"]),
            dbname=cfg["dbname"], user=cfg["user"], password=cfg["password"],
            connect_timeout=10,
        )
    except Exception as e:
        print(f"ERROR: DB connection failed for '{community}': {e}", file=sys.stderr)
        sys.exit(1)

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM discussion WHERE is_deleted = False AND source_type = 'forum'")
    forum_total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM discussion WHERE is_deleted = False AND source_type = 'mail'")
    mail_total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM discussion
        WHERE is_deleted = False
          AND source_type = 'issue'
          AND LOWER(title) LIKE '%[question]%'
    """)
    question_total = cur.fetchone()[0]

    conn.close()

    print(
        f"DB counts for '{key}': forum={forum_total}, mail={mail_total}, "
        f"question_issue={question_total}",
        file=sys.stderr,
    )
    return {"forum": forum_total, "mail": mail_total, "question_issue": question_total}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query hotopic DB channel counts and compute question quotas"
    )
    parser.add_argument("--community", required=True,
                        help="Community name, e.g. openeuler, mindspore")
    parser.add_argument("--target", type=int, required=True,
                        help="Total number of questions to allocate across channels")
    args = parser.parse_args()

    counts = query_counts(args.community)
    quotas = compute_quotas(counts, args.target)

    result = {
        "community": args.community.lower(),
        "target": args.target,
        "counts": counts,
        "quotas": quotas,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
