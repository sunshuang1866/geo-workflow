#!/usr/bin/env python3
"""
Inject Gemini session cookies into the community session file.
Performs a headless browser verification of the login state.

Gemini requires multiple __Secure- cookies for a valid session.
Minimum required: __Secure-1PSID
Recommended: also provide __Secure-3PSID, __Secure-1PAPISID, __Secure-3PAPISID

How to get cookies:
  1. Log in at https://gemini.google.com/ in Chrome
  2. DevTools (F12) → Application → Cookies → https://gemini.google.com
  3. Copy the values for each __Secure-* cookie listed below

Usage:
  python3 inject-gemini-session.py \\
    --community openEuler \\
    --1psid  "<__Secure-1PSID value>" \\
    --3psid  "<__Secure-3PSID value>" \\
    --1papisid "<__Secure-1PAPISID value>" \\
    --3papisid "<__Secure-3PAPISID value>"

  # Minimum (1PSID only):
  python3 inject-gemini-session.py --community openEuler --1psid "<value>"

Exit 0 = saved and verified (logged in).
Exit 1 = saved but verification failed (SESSION_EXPIRED on stderr).
"""

import argparse
import json
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--community", required=True, help="Community name, e.g. openEuler")
    parser.add_argument("--1psid", required=True, dest="psid1", help="__Secure-1PSID value")
    parser.add_argument(
        "--3psid", default=None, dest="psid3", help="__Secure-3PSID value (recommended)"
    )
    parser.add_argument("--1papisid", default=None, dest="papisid1", help="__Secure-1PAPISID value")
    parser.add_argument("--3papisid", default=None, dest="papisid3", help="__Secure-3PAPISID value")
    parser.add_argument(
        "--skip-verify", action="store_true", help="Save without browser verification"
    )
    args = parser.parse_args()

    skill_dir = os.path.dirname(__file__)
    root_dir = os.path.abspath(os.path.join(skill_dir, "..", "..", "..", ".."))
    session_path = os.path.join(root_dir, "assessments", args.community, ".gemini-session.json")
    os.makedirs(os.path.dirname(session_path), exist_ok=True)

    # Build cookie dict — only store non-None values
    cookies = {"__Secure-1PSID": args.psid1}
    if args.psid3:
        cookies["__Secure-3PSID"] = args.psid3
    if args.papisid1:
        cookies["__Secure-1PAPISID"] = args.papisid1
    if args.papisid3:
        cookies["__Secure-3PAPISID"] = args.papisid3

    state = {"cookies": cookies}
    with open(session_path, "w") as f:
        json.dump(state, f, indent=2)
    print(f"[+] Session saved: {session_path}")
    print(f"    Cookies stored: {list(cookies.keys())}")

    if args.skip_verify:
        print("SESSION_SAVED (verify skipped)")
        sys.exit(0)

    # ── Headless verification ──────────────────────────────────────────────────
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("SESSION_SAVED (playwright not available, skipping verify)", file=sys.stderr)
        sys.exit(0)

    pw_cookies = [
        {
            "name": k,
            "value": v,
            "domain": ".google.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "None",
        }
        for k, v in cookies.items()
    ]

    anti_detect = [
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--window-size=1280,800",
    ]
    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=anti_detect)
        ctx = browser.new_context(
            user_agent=ua,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        ctx.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        page = ctx.new_page()

        # Inject cookies into the browser's cookie store (domain-scoped).
        # This covers all subdomains (accounts.google.com, etc.) automatically.
        ctx.add_cookies(pw_cookies)

        page.goto("https://gemini.google.com/app", timeout=30000)
        time.sleep(5)

        # Save debug screenshot to /tmp for diagnosis
        page.screenshot(path="/tmp/gemini-verify.png")

        # Logged-in check: look for input box AND absence of "Sign in" button
        sign_in = page.query_selector('a[href*="accounts.google.com"], [aria-label*="Sign in"]')
        inp = page.query_selector("div.ql-editor[contenteditable='true']")
        url = page.url
        title = page.title()

        browser.close()

        print(f"  page url: {url}", file=sys.stderr)
        print(f"  page title: {title}", file=sys.stderr)
        print(f"  input found: {inp is not None}", file=sys.stderr)
        print(f"  sign-in found: {sign_in is not None}", file=sys.stderr)
        print(f"  screenshot: /tmp/gemini-verify.png", file=sys.stderr)

        if inp and not sign_in:
            print("SESSION_VALID: logged in, input box found")
            sys.exit(0)
        elif sign_in:
            print(
                "SESSION_EXPIRED: Sign-in button still visible — cookie may be invalid",
                file=sys.stderr,
            )
            sys.exit(1)
        else:
            print("SESSION_UNKNOWN: input box not found — page may have changed", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
