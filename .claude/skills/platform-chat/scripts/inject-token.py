#!/usr/bin/env python3
"""
Inject a ChatGPT __Secure-next-auth.session-token into the community session file.
Also performs a headless browser verification of the token validity.

Usage:
  python3 inject-token.py --token <TOKEN> --community <NAME>

Exit 0 = token saved and verified valid.
Exit 1 = token saved but verification failed (SESSION_EXPIRED on stderr).
"""

import argparse
import json
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="__Secure-next-auth.session-token value")
    parser.add_argument("--community", required=True, help="Community name, e.g. MindSpore")
    parser.add_argument(
        "--skip-verify", action="store_true", help="Save token without browser verify"
    )
    args = parser.parse_args()

    skill_dir = os.path.dirname(__file__)
    root_dir = os.path.abspath(os.path.join(skill_dir, "..", "..", "..", ".."))
    session_path = os.path.join(root_dir, "assessments", args.community, ".chatgpt-session.json")
    os.makedirs(os.path.dirname(session_path), exist_ok=True)

    # Store only the raw token value — add_cookies() is used at runtime
    # (storage_state initialization rejects __Secure- cookies without a URL context)
    state = {"token": args.token}

    with open(session_path, "w") as f:
        json.dump(state, f, indent=2)
    print(f"[+] Session saved: {session_path}")

    if args.skip_verify:
        print("SESSION_SAVED (verify skipped)")
        sys.exit(0)

    # Verify with headless browser
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("SESSION_SAVED (playwright not available, skipping verify)", file=sys.stderr)
        sys.exit(0)

    anti_detect = [
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--window-size=1280,800",
    ]
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=anti_detect)
        ctx = browser.new_context(
            user_agent=ua,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        ctx.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        page = ctx.new_page()
        # Use extra HTTP headers instead of add_cookies — Playwright 1.x rejects
        # __Secure- prefixed cookies via CDP setCookies; header injection is equivalent
        # because NextAuth.js reads the Cookie header server-side.
        page.set_extra_http_headers({"Cookie": f"__Secure-next-auth.session-token={args.token}"})
        page.goto("https://chatgpt.com/", timeout=30000)
        time.sleep(4)

        try:
            page.wait_for_selector('[data-testid="login-button"]', timeout=4000)
            print("SESSION_EXPIRED: login button still visible", file=sys.stderr)
            browser.close()
            sys.exit(1)
        except PW_Timeout:
            inp = page.query_selector("#prompt-textarea")
            if inp:
                print("SESSION_VALID")
                browser.close()
                sys.exit(0)
            else:
                print("SESSION_UNKNOWN: input box not found, page may be loading", file=sys.stderr)
                browser.close()
                sys.exit(1)


if __name__ == "__main__":
    main()
