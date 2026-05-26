#!/usr/bin/env python3
"""Add a comment to an existing Issue on GitHub or GitCode.

Usage:
    python3 comment-issue.py --owner <owner> --repo <repo> --platform github|gitcode \
                              --issue-number <number> --body '<markdown>' [--dry-run] [--token <token>]

In dry-run mode, prints the comment payload to stdout without calling the API.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import resolve_platform_token

GITHUB_API = "https://api.github.com"
GITCODE_API = "https://api.gitcode.com/api/v5"


def _post(url: str, body: dict, headers: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def comment_github(
    owner: str, repo: str, issue_number: str, body: str, token: str, dry_run: bool
) -> dict:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if dry_run:
        return {
            "mode": "dry-run",
            "issue_number": issue_number,
            "body": body[:200] + ("..." if len(body) > 200 else ""),
        }

    return _post(url, {"body": body}, headers)


def comment_gitcode(
    owner: str, repo: str, issue_number: str, body: str, token: str, dry_run: bool
) -> dict:
    url = f"{GITCODE_API}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {"Content-Type": "application/json", "private-token": token}

    if dry_run:
        return {
            "mode": "dry-run",
            "issue_number": issue_number,
            "body": body[:200] + ("..." if len(body) > 200 else ""),
        }

    payload = {"access_token": token, "body": body}
    return _post(url, payload, headers)


def main():
    parser = argparse.ArgumentParser(description="Comment on an existing Issue")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--platform", choices=["github", "gitcode"], default=None)
    parser.add_argument(
        "--issue-number", required=True, help="Issue number (GitHub) or Issue number/ID (GitCode)"
    )
    parser.add_argument("--body", required=True, help="Comment body in Markdown")
    parser.add_argument("--token", default=None, help="API token (overrides env)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Resolve platform + token
    platform, token = resolve_platform_token(args.platform, args.token)

    if not token and not args.dry_run:
        print(
            "ERROR: No API token found. Set GITHUB_TOKEN or GITCODE_TOKEN in .env.", file=sys.stderr
        )
        sys.exit(1)

    try:
        if platform == "github":
            result = comment_github(
                args.owner, args.repo, args.issue_number, args.body, token, args.dry_run
            )
            comment_url = result.get("html_url", "")
        else:
            result = comment_gitcode(
                args.owner, args.repo, args.issue_number, args.body, token, args.dry_run
            )
            comment_url = result.get("html_url", "")

        if args.dry_run:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(
                json.dumps(
                    {
                        "status": "commented",
                        "issue_number": args.issue_number,
                        "comment_url": comment_url,
                        "comment_id": result.get("id", ""),
                    },
                    ensure_ascii=False,
                )
            )

    except urllib.error.HTTPError as e:
        body_err = ""
        try:
            body_err = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        print(f"ERROR: HTTP {e.code}: {body_err[:300]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
