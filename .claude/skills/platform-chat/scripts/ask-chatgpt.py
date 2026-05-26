#!/usr/bin/env python3
"""
Send a single question to ChatGPT web UI via Playwright and output a JSON response record.

Usage:
  python3 ask-chatgpt.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --session output/MindSpore/.chatgpt-session.json \\
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.playwright_config import create_browser_context

SELECTOR_INPUT = "#prompt-textarea"
SELECTOR_SEND = 'button[data-testid="send-button"]'

# ChatGPT has used several different aria-labels / test-ids across UI versions.
# Tried in order; first match wins.
SELECTORS_STOP = [
    'button[data-testid="stop-button"]',
    'button[aria-label="Stop streaming"]',
    'button[aria-label="Stop generating"]',
]

SELECTOR_LOGIN = '[data-testid="login-button"]'
SELECTOR_RESPONSE = '[data-message-author-role="assistant"]'
SELECTOR_CITATIONS = '[data-message-author-role="assistant"] a[href]'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--session", required=True, help="Path to .chatgpt-session.json")
    parser.add_argument("--timeout", type=int, default=90, help="Seconds to wait for response")
    parser.add_argument(
        "--screenshot-dir", default=None, help="Directory to save debug screenshots"
    )
    parser.add_argument(
        "--min-citations",
        type=int,
        default=8,
        dest="min_citations",
        help="Minimum citation count; sends a follow-up if not met",
    )
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

    # ------------------------------------------------------------------ helpers

    def save_screenshot(label):
        if args.screenshot_dir:
            os.makedirs(args.screenshot_dir, exist_ok=True)
            path = os.path.join(args.screenshot_dir, f"debug-{args.question_id}-{label}.png")
            try:
                page.screenshot(path=path)
                print(f"  screenshot: {path}", file=sys.stderr)
            except Exception:
                pass

    def fill_input(el, text: str) -> None:
        """Fill the ChatGPT input box (contenteditable div).
        Tries fill() first; falls back to click + keyboard.type() if fill()
        doesn't trigger React's synthetic events.
        """
        try:
            el.click()
            el.fill(text)
            # Verify content landed
            val = el.inner_text().strip()
            if val:
                return
        except Exception:
            pass
        # Fallback: clear and type char-by-char via keyboard
        el.click()
        page.keyboard.key("Control+a")
        page.keyboard.press("Delete")
        time.sleep(0.2)
        page.keyboard.type(text, delay=20)

    def submit_question() -> None:
        """Click the send button, or press Enter if the button is not found."""
        try:
            btn = page.wait_for_selector(SELECTOR_SEND, timeout=5000)
            btn.click()
        except PW_Timeout:
            page.keyboard.press("Enter")

    def wait_for_generation(timeout_ms: int) -> bool:
        """Wait for ChatGPT to finish streaming. Returns True = completed normally."""
        # Strategy 1: wait for a stop-button to appear, then disappear.
        for stop_sel in SELECTORS_STOP:
            try:
                page.wait_for_selector(stop_sel, timeout=10_000)
                print(f"  [gen] stop button found: {stop_sel}", file=sys.stderr)
                try:
                    page.wait_for_selector(stop_sel, state="detached", timeout=timeout_ms)
                    return True
                except PW_Timeout:
                    return False  # streaming did not finish in time
            except PW_Timeout:
                continue  # this selector never appeared, try next

        # Strategy 2: no stop button appeared (selectors may have changed again).
        # Fall back to waiting for the send button to become re-enabled.
        print(
            "  [gen] stop button not found; falling back to send-button re-enable check",
            file=sys.stderr,
        )
        try:
            # Send button is disabled / replaced during streaming; re-appears when done.
            page.wait_for_function(
                f"""() => {{
                    const btn = document.querySelector('{SELECTOR_SEND}');
                    return btn && !btn.disabled;
                }}""",
                timeout=timeout_ms,
            )
            time.sleep(1)
            return True
        except PW_Timeout:
            return False

    def extract_citations() -> list:
        """Return deduplicated HTTP/HTTPS citation links from all assistant messages."""
        try:
            links = page.eval_on_selector_all(
                SELECTOR_CITATIONS,
                "els => els.map(a => a.href)",
            )
        except Exception:
            links = []
        seen = set()
        result = []
        for href in links:
            if (
                href
                and href.startswith("http")
                and href not in seen
                and not href.startswith("https://chatgpt.com")  # skip internal nav links
            ):
                seen.add(href)
                result.append(href)
        return result

    # ------------------------------------------------------------------ load token

    try:
        with open(args.session) as f:
            sess_data = json.load(f)
    except Exception as e:
        print(f"SESSION_READ_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    # Support both formats:
    #   new: {"token": "..."}
    #   legacy: {"cookies": [{"name": "__Secure-next-auth.session-token", "value": "..."}]}
    token_value = None
    if "token" in sess_data:
        token_value = sess_data["token"]
    elif "cookies" in sess_data:
        for c in sess_data.get("cookies", []):
            if c.get("name") == "__Secure-next-auth.session-token":
                token_value = c.get("value")
                break

    if not token_value:
        print("SESSION_TOKEN_MISSING: no token found in session file", file=sys.stderr)
        sys.exit(2)

    # ------------------------------------------------------------------ browser

    with sync_playwright() as p:
        browser, ctx, page = create_browser_context(p)

        try:
            # Inject token via extra request header — bypasses CDP __Secure- cookie
            # restriction in Playwright 1.x. NextAuth.js reads Cookie header server-side.
            page.set_extra_http_headers(
                {"Cookie": f"__Secure-next-auth.session-token={token_value}"}
            )
            page.goto("https://chatgpt.com/", timeout=30000)
            time.sleep(3)
        except Exception as e:
            print(f"NAVIGATION_ERROR: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # --- login check ---
        try:
            page.wait_for_selector(SELECTOR_LOGIN, timeout=3000)
            print("SESSION_EXPIRED: login button visible", file=sys.stderr)
            save_screenshot("session-expired")
            browser.close()
            sys.exit(2)
        except PW_Timeout:
            pass  # login button absent → session appears valid

        # --- locate input ---
        try:
            textarea = page.wait_for_selector(SELECTOR_INPUT, timeout=10000)
        except PW_Timeout:
            save_screenshot("no-input")
            print("INPUT_NOT_FOUND: selector may have changed — check screenshot", file=sys.stderr)
            browser.close()
            sys.exit(3)

        # --- ask the question ---
        fill_input(textarea, args.question)
        time.sleep(0.5)
        submit_question()

        # --- wait for answer ---
        timed_out = not wait_for_generation(args.timeout * 1000)

        # After the stop button disappears, React may still be rendering.
        # Wait until aria-busy clears and text is non-empty (max 10 s).
        try:
            page.wait_for_function(
                """() => {
                    const msgs = document.querySelectorAll('[data-message-author-role="assistant"]');
                    if (!msgs.length) return false;
                    const last = msgs[msgs.length - 1];
                    return !last.querySelector('[aria-busy="true"]')
                        && last.innerText.trim().length > 0;
                }""",
                timeout=10_000,
            )
        except Exception:
            pass  # fallback: extract whatever is rendered
        time.sleep(1)

        if timed_out:
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
            # partial response received despite timeout — continue

        # --- extract response ---
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
        citations = extract_citations()

        # --- follow-up if too few citations ---
        FOLLOW_UP = "请继续补充更多相关参考来源链接，要求总共包含至少8个不同的来源。"
        if len(citations) < args.min_citations:
            print(
                f"  citations={len(citations)} < {args.min_citations}, sending follow-up...",
                file=sys.stderr,
            )
            try:
                textarea = page.wait_for_selector(SELECTOR_INPUT, timeout=5000)
                fill_input(textarea, FOLLOW_UP)
                time.sleep(0.5)
                submit_question()
                wait_for_generation(args.timeout * 1000)
                try:
                    page.wait_for_function(
                        """() => {
                            const msgs = document.querySelectorAll('[data-message-author-role="assistant"]');
                            if (!msgs.length) return false;
                            const last = msgs[msgs.length - 1];
                            return !last.querySelector('[aria-busy="true"]')
                                && last.innerText.trim().length > 0;
                        }""",
                        timeout=10_000,
                    )
                except Exception:
                    pass
                time.sleep(1)
                citations = extract_citations()
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
