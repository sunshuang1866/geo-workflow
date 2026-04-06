#!/usr/bin/env python3
"""
Send a single question to ChatGPT web UI via Playwright and output a JSON response record.

Usage:
  python3 ask-chatgpt.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --session assessments/MindSpore/.chatgpt-session.json \\
    --timeout 90

Stdout: single JSON object (responses.json compatible)
Stderr: error messages only

Exit codes:
  0 — success
  2 — session expired
  3 — UI changed (input box not found)
  4 — timeout
  1 — other error
"""

import argparse
import json
import os
import sys
import time


ANTI_DETECT_ARGS = [
    "--no-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--window-size=1280,800",
]
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Selector definitions (kept in one place for easy update)
SELECTOR_INPUT = "#prompt-textarea"
SELECTOR_SEND = 'button[data-testid="send-button"]'
SELECTOR_STOP = 'button[aria-label="Stop streaming"]'
SELECTOR_LOGIN = '[data-testid="login-button"]'
SELECTOR_RESPONSE = '[data-message-author-role="assistant"]'
SELECTOR_CITATIONS = '[data-message-author-role="assistant"] a[href]'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--session", required=True, help="Path to .chatgpt-session.json")
    parser.add_argument("--timeout", type=int, default=90, help="Seconds to wait for response")
    parser.add_argument("--screenshot-dir", default=None, help="Directory to save debug screenshots")
    parser.add_argument("--min-citations", type=int, default=8, dest="min_citations",
                        help="Minimum citation count; sends a follow-up if not met")
    args = parser.parse_args()

    if not os.path.isfile(args.session):
        print(f"SESSION_FILE_MISSING: {args.session}", file=sys.stderr)
        sys.exit(2)

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("playwright not installed", file=sys.stderr)
        sys.exit(1)

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def save_screenshot(label):
        if args.screenshot_dir:
            os.makedirs(args.screenshot_dir, exist_ok=True)
            path = os.path.join(args.screenshot_dir, f"debug-{args.question_id}-{label}.png")
            try:
                page.screenshot(path=path)
                print(f"  screenshot: {path}", file=sys.stderr)
            except Exception:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ANTI_DETECT_ARGS)
        ctx = browser.new_context(
            user_agent=UA,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            storage_state=args.session,
        )
        ctx.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        page = ctx.new_page()

        try:
            page.goto("https://chatgpt.com/", timeout=30000)
            time.sleep(3)
        except Exception as e:
            print(f"NAVIGATION_ERROR: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # Check login
        try:
            page.wait_for_selector(SELECTOR_LOGIN, timeout=3000)
            print("SESSION_EXPIRED", file=sys.stderr)
            browser.close()
            sys.exit(2)
        except PW_Timeout:
            pass  # logged in

        # Find input box
        try:
            textarea = page.wait_for_selector(SELECTOR_INPUT, timeout=10000)
        except PW_Timeout:
            save_screenshot("no-input")
            print("INPUT_NOT_FOUND: input box selector may have changed", file=sys.stderr)
            browser.close()
            sys.exit(3)

        # Type question
        textarea.click()
        textarea.fill(args.question)
        time.sleep(0.5)

        # Send
        try:
            btn = page.wait_for_selector(SELECTOR_SEND, timeout=5000)
            btn.click()
        except PW_Timeout:
            textarea.press("Enter")

        # Wait for generation to complete
        timed_out = False
        try:
            page.wait_for_selector(SELECTOR_STOP, timeout=15000)
            page.wait_for_selector(SELECTOR_STOP, state="detached", timeout=args.timeout * 1000)
        except PW_Timeout:
            timed_out = True

        time.sleep(1)

        if timed_out:
            # Check if there's any content anyway
            msgs = page.query_selector_all(SELECTOR_RESPONSE)
            if not msgs:
                save_screenshot("timeout")
                result = {
                    "question_id": args.question_id,
                    "platform": "chatgpt-web",
                    "query": args.question,
                    "timestamp": timestamp,
                    "raw_response": "",
                    "citations": [],
                    "model": "ChatGPT (web)",
                    "status": "timeout",
                    "error": "Response generation timed out",
                }
                print(json.dumps(result, ensure_ascii=False))
                browser.close()
                sys.exit(4)

        # Extract response
        msgs = page.query_selector_all(SELECTOR_RESPONSE)
        if not msgs:
            save_screenshot("no-response")
            result = {
                "question_id": args.question_id,
                "platform": "chatgpt-web",
                "query": args.question,
                "timestamp": timestamp,
                "raw_response": "",
                "citations": [],
                "model": "ChatGPT (web)",
                "status": "error",
                "error": "No assistant message found in DOM",
            }
            print(json.dumps(result, ensure_ascii=False))
            browser.close()
            sys.exit(1)

        response_text = msgs[-1].inner_text().strip()

        # Extract citation links
        try:
            links = page.eval_on_selector_all(
                SELECTOR_CITATIONS,
                "els => els.map(a => a.href).filter(h => h.startsWith('http'))",
            )
        except Exception:
            links = []

        # Deduplicate citations preserving order
        seen = set()
        citations = []
        for href in links:
            if href not in seen:
                seen.add(href)
                citations.append(href)

        # Follow-up: request more citations if below threshold
        FOLLOW_UP = "请继续补充更多相关参考来源链接，要求总共包含至少8个不同的来源。"
        if len(citations) < args.min_citations:
            print(f"  citations={len(citations)} < {args.min_citations}, sending follow-up...", file=sys.stderr)
            try:
                textarea = page.wait_for_selector(SELECTOR_INPUT, timeout=5000)
                textarea.click()
                textarea.fill(FOLLOW_UP)
                time.sleep(0.5)
                try:
                    btn = page.wait_for_selector(SELECTOR_SEND, timeout=5000)
                    btn.click()
                except PW_Timeout:
                    textarea.press("Enter")
                try:
                    page.wait_for_selector(SELECTOR_STOP, timeout=15000)
                    page.wait_for_selector(SELECTOR_STOP, state="detached", timeout=args.timeout * 1000)
                except PW_Timeout:
                    pass
                time.sleep(1)
                extra_links = page.eval_on_selector_all(
                    SELECTOR_CITATIONS,
                    "els => els.map(a => a.href).filter(h => h.startsWith('http'))",
                )
                for href in extra_links:
                    if href not in seen:
                        seen.add(href)
                        citations.append(href)
            except Exception as e:
                print(f"  follow-up error: {e}", file=sys.stderr)

        result = {
            "question_id": args.question_id,
            "platform": "chatgpt-web",
            "query": args.question,
            "timestamp": timestamp,
            "raw_response": response_text,
            "citations": citations,
            "model": "ChatGPT (web)",
            "status": "success",
        }

        print(json.dumps(result, ensure_ascii=False))
        browser.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
