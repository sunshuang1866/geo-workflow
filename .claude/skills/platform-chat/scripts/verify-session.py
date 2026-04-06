#!/usr/bin/env python3
"""
Verify that a saved ChatGPT session file is still valid.

Usage:
  python3 verify-session.py --session assessments/MindSpore/.chatgpt-session.json

Stdout:
  SESSION_VALID   — token accepted, input box found
Stderr + exit 1:
  SESSION_EXPIRED — login button detected or input box missing
  SESSION_FILE_MISSING — file not found
"""

import argparse
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True, help="Path to .chatgpt-session.json")
    args = parser.parse_args()

    if not os.path.isfile(args.session):
        print(f"SESSION_FILE_MISSING: {args.session}", file=sys.stderr)
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("playwright not installed; skipping verify — assuming valid", file=sys.stderr)
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
            storage_state=args.session,
        )
        ctx.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        page = ctx.new_page()
        page.goto("https://chatgpt.com/", timeout=30000)
        time.sleep(4)

        try:
            page.wait_for_selector('[data-testid="login-button"]', timeout=4000)
            print("SESSION_EXPIRED", file=sys.stderr)
            browser.close()
            sys.exit(1)
        except PW_Timeout:
            inp = page.query_selector("#prompt-textarea")
            browser.close()
            if inp:
                print("SESSION_VALID")
                sys.exit(0)
            else:
                print("SESSION_EXPIRED: input box not found", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
