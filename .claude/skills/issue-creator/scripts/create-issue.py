#!/usr/bin/env python3
"""Create an Issue on GitHub or GitCode from a JSON payload.

Usage:
    python3 create-issue.py --owner <owner> --repo <repo> --platform github|gitcode \\
                            --payload '<json>' [--dry-run] [--token <token>]

Platform auto-detection:
    If --platform is omitted, looks for GITHUB_TOKEN first, then GITCODE_TOKEN.

Label fallback:
    If the API returns 403 or 422 due to label errors, retries without labels and
    logs a warning. Does NOT abort.

In dry-run mode, prints the payload to stdout without calling the API.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


GITHUB_API  = "https://api.github.com"
GITCODE_API = "https://api.gitcode.com/api/v5"


# ── helpers ──────────────────────────────────────────────────────────────────

def _is_label_error(http_err: urllib.error.HTTPError) -> bool:
    """Return True when the error is caused by non-existent or forbidden labels."""
    if http_err.code not in (403, 422):
        return False
    try:
        body = http_err.read().decode("utf-8", errors="replace")
        return "label" in body.lower()
    except Exception:
        return False


def _post(url: str, body: dict, headers: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ── GitHub ────────────────────────────────────────────────────────────────────

def create_github(owner: str, repo: str, title: str, body: str,
                  labels: list, token: str, dry_run: bool) -> dict:
    url     = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization":        f"Bearer {token}",
        "Accept":               "application/vnd.github+json",
        "Content-Type":         "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if dry_run:
        return {"mode": "dry-run", "title": title, "labels": labels,
                "body": body[:200] + ("..." if len(body) > 200 else "")}

    payload = {"title": title, "body": body, "labels": labels}
    try:
        return _post(url, payload, headers)
    except urllib.error.HTTPError as e:
        if _is_label_error(e):
            print("WARNING: Labels not applied (insufficient permission or labels not found). "
                  "Retrying without labels.", file=sys.stderr)
            payload_no_labels = {"title": title, "body": body}
            result = _post(url, payload_no_labels, headers)
            result["_labels_applied"] = False
            return result
        raise


# ── GitCode ───────────────────────────────────────────────────────────────────

def create_gitcode(owner: str, repo: str, title: str, body: str,
                   labels: list, token: str, dry_run: bool) -> dict:
    url     = f"{GITCODE_API}/repos/{owner}/{repo}/issues"
    headers = {"Content-Type": "application/json", "private-token": token}
    labels_str = ",".join(labels)

    if dry_run:
        return {"mode": "dry-run", "title": title, "labels": labels_str,
                "body": body[:200] + ("..." if len(body) > 200 else "")}

    payload = {"access_token": token, "repo": repo,
               "title": title, "body": body, "labels": labels_str}
    try:
        return _post(url, payload, headers)
    except urllib.error.HTTPError as e:
        if _is_label_error(e):
            print("WARNING: Labels not applied (insufficient permission or labels not found). "
                  "Retrying without labels.", file=sys.stderr)
            payload_no_labels = {"access_token": token, "repo": repo,
                                 "title": title, "body": body}
            result = _post(url, payload_no_labels, headers)
            result["_labels_applied"] = False
            return result
        raise


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Create an Issue on GitHub or GitCode")
    parser.add_argument("--owner",    required=True)
    parser.add_argument("--repo",     required=True)
    parser.add_argument("--platform", choices=["github", "gitcode"], default=None,
                        help="Target platform. Auto-detected from available tokens if omitted.")
    parser.add_argument("--payload",  required=True, help="JSON: {title, body, labels}")
    parser.add_argument("--token",    default=None,  help="API token (overrides env)")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    # Parse payload
    try:
        issue = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON payload: {e}", file=sys.stderr)
        sys.exit(1)

    title  = issue.get("title", "")
    body   = issue.get("body",  "")
    labels = issue.get("labels", [])
    if isinstance(labels, str):                         # tolerate comma-string input
        labels = [l.strip() for l in labels.split(",") if l.strip()]
    if not title:
        print("ERROR: Issue title is required", file=sys.stderr)
        sys.exit(1)

    # Resolve platform + token
    platform = args.platform
    token    = args.token

    if not token:
        gh_token  = os.environ.get("GITHUB_TOKEN", "")
        gc_token  = os.environ.get("GITCODE_TOKEN", "")
        if platform == "github":
            token = gh_token
        elif platform == "gitcode":
            token = gc_token
        else:
            # auto-detect: prefer GitHub if token present
            if gh_token:
                platform, token = "github",  gh_token
            elif gc_token:
                platform, token = "gitcode", gc_token

    if not token and not args.dry_run:
        print("ERROR: No API token found. Set GITHUB_TOKEN or GITCODE_TOKEN in .env.",
              file=sys.stderr)
        sys.exit(1)

    platform = platform or "github"     # fallback for dry-run with no token

    # Create issue
    try:
        if platform == "github":
            result = create_github(args.owner, args.repo, title, body,
                                   labels, token, args.dry_run)
            issue_url = result.get("html_url",
                        f"https://github.com/{args.owner}/{args.repo}/issues/{result.get('number','?')}")
        else:
            result = create_gitcode(args.owner, args.repo, title, body,
                                    labels, token, args.dry_run)
            issue_url = result.get("html_url",
                        f"https://gitcode.com/{args.owner}/{args.repo}/issues/{result.get('number','?')}")

        labels_applied = result.get("_labels_applied", True)
        if args.dry_run:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "status":         "created",
                "url":            issue_url,
                "number":         result.get("number", ""),
                "title":          title,
                "labels_applied": labels_applied,
            }, ensure_ascii=False))

    except urllib.error.HTTPError as e:
        body_err = ""
        try:
            body_err = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        print(f"ERROR: HTTP {e.code}: {body_err[:300]}", file=sys.stderr)
        if e.code == 403:
            print("HINT: Check that your token has 'issues:write' (GitHub) or "
                  "'write_issues' (GitCode) scope.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
