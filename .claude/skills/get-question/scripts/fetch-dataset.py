#!/usr/bin/env python3
"""
Fetch hot topic discussions from datastat.osinfra.cn API.

Two data sources are supported:
  mail   — queries fact_{community}_mail_topic via static access-token (no login needed)
  issue  — queries dws_{community}_contribute via cookie/token login

Usage:
    # Mail (static access-token, no login):
    python3 fetch-dataset.py --community mindspore --source mail --since 2024-01-01

    # Issue (requires login credentials):
    python3 fetch-dataset.py --community mindspore --source issue --since 2024-01-01 \
        --email user@example.com --password <password>

    # Issue via env vars:
    DATASTAT_EMAIL=user@example.com DATASTAT_PASSWORD=xxx \
    python3 fetch-dataset.py --community mindspore --source issue --since 2024-01-01

Output: JSON array to stdout, progress/errors to stderr.

Exit codes:
  0 — success
  1 — missing required arguments
  2 — auth failed (login or token invalid)
"""

import argparse
import json
import os
import sys
import time

import requests


API_BASE        = "https://beta.datastat.osinfra.cn/server/customization"
LOGIN_URL       = "https://id.datastat.osinfra.cn/oneid/login"
ACCESS_TOKEN    = "jvMe0-mMVNXp4k_OkmpdHPByVuyCpMgCLoGV3Hm61ps"
CLIENT_ID       = "682e93df3c292532ad012ff7"
PAGE_SIZE       = 100


# ── Auth ──────────────────────────────────────────────────────────────────────

def login(email: str, password: str) -> tuple[str, str]:
    """Login to datastat and return (cookie_string, token).

    The login endpoint sets a _U_T_ cookie that is used as the bearer token
    for subsequent API requests.
    """
    try:
        resp = requests.post(
            LOGIN_URL,
            headers={"Referer": "https://id.datastat.osinfra.cn/"},
            json={
                "permission": "sigRead",
                "account": email,
                "client_id": CLIENT_ID,
                "accept_term": 0,
                "password": password,
            },
            timeout=30,
        )
        resp.raise_for_status()
        cookie_str = ""
        token = ""
        for k, v in resp.cookies.items():
            cookie_str += f"{k}={v};"
            if k == "_U_T_":
                token = v
        if not token:
            print("LOGIN_FAILED: _U_T_ token not found in response cookies", file=sys.stderr)
            sys.exit(2)
        print("Login successful.", file=sys.stderr)
        return cookie_str, token
    except SystemExit:
        raise
    except Exception as e:
        print(f"LOGIN_FAILED: {e}", file=sys.stderr)
        sys.exit(2)


# ── API query ─────────────────────────────────────────────────────────────────

def _query_page(community: str, table: str, dims: list, filters: list,
                page: int, headers: dict) -> list:
    """Fetch a single page from the datastat detail API."""
    url = f"{API_BASE}/{community}/detail/v2"
    payload = {
        "community": community,
        "dim": dims,
        "name": table,
        "page": page,
        "page_size": PAGE_SIZE,
        "filters": filters,
        "conditonsLogic": "AND",
        "order_field": "created_at",
        "order_dir": "ASC",
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        data = resp.json()
        code = data.get("code")
        if code in (401, 403):
            print(f"AUTH_FAILED: API returned code={code}", file=sys.stderr)
            sys.exit(2)
        if code == 429:
            print("Rate limited, retrying in 2s...", file=sys.stderr)
            time.sleep(2)
            return _query_page(community, table, dims, filters, page, headers)
        return data.get("data") or []
    except SystemExit:
        raise
    except Exception as e:
        print(f"WARNING: page {page} query failed: {e}", file=sys.stderr)
        return []


def _fetch_all(community: str, table: str, dims: list, filters: list,
               headers: dict) -> list:
    """Paginate through all pages and return combined records."""
    all_records = []
    page = 1
    while True:
        records = _query_page(community, table, dims, filters, page, headers)
        if not records:
            break
        all_records.extend(records)
        print(f"  page {page}: {len(records)} records fetched", file=sys.stderr)
        if len(records) < PAGE_SIZE:
            break
        page += 1
    return all_records


# ── Source-specific fetch ─────────────────────────────────────────────────────

def fetch_mail(community: str, since: str | None, limit: int | None = None) -> list:
    """Fetch mailing list topics using static access-token (no login required).

    limit: cap the returned list to this many records.
    """
    headers = {"access-token": ACCESS_TOKEN}
    table = f"fact_{community}_mail_topic"
    dims = [
        "uuid", "title", "created_at", "last_update_time",
        "url", "author", "list_name", "tags",
    ]
    filters = []
    if since:
        filters.append({"column": "created_at", "operator": ">=", "value": since})

    print(f"Fetching mail topics for '{community}' from {table}...", file=sys.stderr)
    records = _fetch_all(community, table, dims, filters, headers)

    results = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "source_type": "mail",
            "created_at": r.get("created_at", ""),
            "last_update_time": r.get("last_update_time", ""),
            "author": r.get("author", ""),
            "list_name": r.get("list_name", ""),
            "tags": r.get("tags") or [],
        }
        for r in records
        if r.get("title") and r.get("url")
    ]

    if limit is not None and limit > 0:
        results = results[:limit]
        print(f"  limit applied: returning {len(results)} records", file=sys.stderr)

    return results


def fetch_issue(community: str, since: str | None, email: str, password: str,
                question_only: bool = False, limit: int | None = None) -> list:
    """Fetch issues using cookie/token login auth.

    question_only: if True, only return issues whose title contains [Question] or [question].
    limit: cap the returned list to this many records (applied after filtering).
    """
    cookie, token = login(email, password)
    headers = {"Cookie": cookie, "token": token}
    table = f"dws_{community}_contribute"
    dims = ["title", "html_url", "created_at", "state", "labels"]
    filters = []
    if since:
        filters.append({"column": "created_at", "operator": ">=", "value": since})

    print(f"Fetching issues for '{community}' from {table}...", file=sys.stderr)
    records = _fetch_all(community, table, dims, filters, headers)

    results = [
        {
            "title": r.get("title", ""),
            "url": r.get("html_url", ""),
            "source_type": "issue",
            "created_at": r.get("created_at", ""),
            "state": r.get("state", ""),
            "labels": r.get("labels") or [],
        }
        for r in records
        if r.get("title") and r.get("html_url")
    ]

    if question_only:
        before = len(results)
        results = [r for r in results if "[question]" in r["title"].lower()]
        print(f"  question_only filter: {before} → {len(results)} records", file=sys.stderr)

    if limit is not None and limit > 0:
        results = results[:limit]
        print(f"  limit applied: returning {len(results)} records", file=sys.stderr)

    return results


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch hot topic discussions from datastat.osinfra.cn"
    )
    parser.add_argument(
        "--community", required=True,
        help="Community name, e.g. mindspore, openeuler, cann"
    )
    parser.add_argument(
        "--since", default=None,
        help="Only return records created on or after this date (YYYY-MM-DD), e.g. 2024-01-01"
    )
    parser.add_argument(
        "--source", required=True, choices=["mail", "issue"],
        help="Data source: mail or issue"
    )
    parser.add_argument(
        "--email", default=None,
        help="Login email for issue source (or set DATASTAT_EMAIL env var)"
    )
    parser.add_argument(
        "--password", default=None,
        help="Login password for issue source (or set DATASTAT_PASSWORD env var)"
    )
    parser.add_argument(
        "--question-only", action="store_true", default=False,
        help="(issue only) Filter to titles containing [Question] or [question]"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Maximum number of records to return (proportional quota from DB)"
    )
    args = parser.parse_args()

    if args.source == "issue":
        email = args.email or os.environ.get("DATASTAT_EMAIL")
        password = args.password or os.environ.get("DATASTAT_PASSWORD")
        if not email or not password:
            print(
                "ERROR: --email and --password (or DATASTAT_EMAIL / DATASTAT_PASSWORD env vars) "
                "are required for --source issue",
                file=sys.stderr,
            )
            sys.exit(1)
        results = fetch_issue(args.community, args.since, email, password,
                              question_only=args.question_only, limit=args.limit)
    else:
        results = fetch_mail(args.community, args.since, limit=args.limit)

    print(f"Total: {len(results)} records", file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))
