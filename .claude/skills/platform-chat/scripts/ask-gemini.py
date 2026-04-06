#!/usr/bin/env python3
"""
Send a single question to Gemini web UI via Playwright and output a JSON response record.

Gemini allows anonymous (unauthenticated) usage — no session file is required.
Each invocation opens a fresh browser context and a new conversation.

Usage:
  python3 ask-gemini.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --timeout 90

Stdout: single JSON object (responses.json compatible)
Stderr: error messages only

Exit codes:
  0 — success
  3 — UI changed (input box not found)
  4 — timeout
  1 — other error
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs, unquote


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

# ── Selectors ──────────────────────────────────────────────────────────────────
# Quill rich-text editor (must use keyboard.type(), not fill())
SELECTOR_INPUT = "div.ql-editor[contenteditable='true']"

# Send button: hidden/disabled until text is typed; enabled after
SELECTOR_SEND_ENABLED = "button[aria-label='Send message']:not([aria-disabled='true'])"

# Generation lifecycle signals
SELECTOR_GENERATION_START = "pending-response"
SELECTOR_GENERATION_END   = "pending-response"   # wait state="detached"

# Response container (directly accessible in regular DOM, no shadow pierce needed)
# Use textContent (not innerText) — layout-based innerText is truncated
JS_GET_RESPONSE = """
() => {
    const mr = document.querySelector('model-response');
    if (!mr) return null;
    let text = mr.textContent || '';
    // Strip leading 'Gemini said' label
    if (text.startsWith(' Gemini said ')) text = text.slice(' Gemini said '.length);
    else if (text.startsWith('Gemini said')) text = text.slice('Gemini said'.length);
    return text.trim();
}
"""

# Citation links: Gemini wraps source URLs as Google search redirects
# href = "https://www.google.com/search?q=<encoded_actual_url>"
JS_GET_CITATIONS = """
() => {
    const mr = document.querySelector('model-response');
    if (!mr) return [];
    const hrefs = Array.from(mr.querySelectorAll('a[href]')).map(a => a.href);
    const results = [];
    const seen = new Set();
    for (const href of hrefs) {
        // Unwrap Google search redirect: ?q=<actual_url>
        if (href.includes('google.com/search?q=')) {
            try {
                const url = new URL(href);
                const q = url.searchParams.get('q') || '';
                if (q.startsWith('http') && !seen.has(q)) {
                    seen.add(q);
                    results.push(q);
                }
            } catch (_) {}
        } else if (href.startsWith('http') && !href.includes('google.com') &&
                   !href.includes('gstatic.com') && !href.includes('gemini.google')) {
            if (!seen.has(href)) {
                seen.add(href);
                results.push(href);
            }
        }
    }
    return results;
}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--timeout", type=int, default=90, help="Seconds to wait for response")
    parser.add_argument("--screenshot-dir", default=None, help="Directory to save debug screenshots")
    parser.add_argument("--min-citations", type=int, default=8, dest="min_citations",
                        help="Minimum citation count; sends a follow-up if not met")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("playwright not installed", file=sys.stderr)
        sys.exit(1)

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ANTI_DETECT_ARGS)
        ctx = browser.new_context(
            user_agent=UA,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        ctx.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        page = ctx.new_page()

        def save_screenshot(label):
            if args.screenshot_dir:
                os.makedirs(args.screenshot_dir, exist_ok=True)
                path = os.path.join(args.screenshot_dir, f"debug-{args.question_id}-{label}.png")
                try:
                    page.screenshot(path=path)
                    print(f"  screenshot: {path}", file=sys.stderr)
                except Exception:
                    pass

        # ── Navigate ──────────────────────────────────────────────────────────
        try:
            page.goto("https://gemini.google.com/app", timeout=30000)
            time.sleep(3)
        except Exception as e:
            print(f"NAVIGATION_ERROR: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # ── Find input box ────────────────────────────────────────────────────
        try:
            editor = page.wait_for_selector(SELECTOR_INPUT, timeout=10000)
        except PW_Timeout:
            save_screenshot("no-input")
            print("INPUT_NOT_FOUND: Quill editor selector may have changed", file=sys.stderr)
            browser.close()
            sys.exit(3)

        # ── Type question (must use keyboard.type, not fill) ──────────────────
        editor.click()
        time.sleep(0.3)
        page.keyboard.type(args.question)
        time.sleep(0.5)

        # ── Click send (button is hidden until text is typed) ─────────────────
        try:
            send_btn = page.wait_for_selector(SELECTOR_SEND_ENABLED, timeout=5000)
            send_btn.click()
        except PW_Timeout:
            save_screenshot("send-button-not-found")
            print("SEND_BUTTON_NOT_FOUND: send button selector may have changed", file=sys.stderr)
            browser.close()
            sys.exit(3)

        # ── Wait for generation lifecycle ─────────────────────────────────────
        timed_out = False
        try:
            page.wait_for_selector(SELECTOR_GENERATION_START, timeout=15000)
        except PW_Timeout:
            # Generation may have already started and finished
            pass

        try:
            page.wait_for_selector(
                SELECTOR_GENERATION_END,
                state="detached",
                timeout=args.timeout * 1000,
            )
        except PW_Timeout:
            timed_out = True

        time.sleep(1)

        # ── Extract response ──────────────────────────────────────────────────
        response_text = ""
        try:
            response_text = page.evaluate(JS_GET_RESPONSE) or ""
        except Exception as e:
            print(f"RESPONSE_EXTRACT_ERROR: {e}", file=sys.stderr)

        if timed_out and not response_text:
            save_screenshot("timeout")
            result = {
                "question_id": args.question_id,
                "platform": "gemini-web",
                "query": args.question,
                "timestamp": timestamp,
                "raw_response": "",
                "citations": [],
                "model": "Gemini (web)",
                "status": "timeout",
                "error": "Response generation timed out",
            }
            print(json.dumps(result, ensure_ascii=False))
            browser.close()
            sys.exit(4)

        if not response_text:
            save_screenshot("no-response")
            print("NO_RESPONSE: model-response element not found or empty", file=sys.stderr)
            result = {
                "question_id": args.question_id,
                "platform": "gemini-web",
                "query": args.question,
                "timestamp": timestamp,
                "raw_response": "",
                "citations": [],
                "model": "Gemini (web)",
                "status": "error",
                "error": "model-response element not found or empty",
            }
            print(json.dumps(result, ensure_ascii=False))
            browser.close()
            sys.exit(1)

        # ── Extract citations ─────────────────────────────────────────────────
        try:
            citations = page.evaluate(JS_GET_CITATIONS) or []
        except Exception:
            citations = []

        # Follow-up: request more citations if below threshold
        FOLLOW_UP = "请继续补充更多相关参考来源链接，要求总共包含至少8个不同的来源。"
        if len(citations) < args.min_citations:
            print(f"  citations={len(citations)} < {args.min_citations}, sending follow-up...", file=sys.stderr)
            seen = set(citations)
            try:
                editor = page.wait_for_selector(SELECTOR_INPUT, timeout=5000)
                editor.click()
                time.sleep(0.3)
                page.keyboard.type(FOLLOW_UP)
                time.sleep(0.5)
                send_btn = page.wait_for_selector(SELECTOR_SEND_ENABLED, timeout=5000)
                send_btn.click()
                try:
                    page.wait_for_selector(SELECTOR_GENERATION_START, timeout=15000)
                except PW_Timeout:
                    pass
                try:
                    page.wait_for_selector(
                        SELECTOR_GENERATION_END,
                        state="detached",
                        timeout=args.timeout * 1000,
                    )
                except PW_Timeout:
                    pass
                time.sleep(1)
                extra_citations = page.evaluate(JS_GET_CITATIONS) or []
                for href in extra_citations:
                    if href not in seen:
                        seen.add(href)
                        citations.append(href)
            except Exception as e:
                print(f"  follow-up error: {e}", file=sys.stderr)

        result = {
            "question_id": args.question_id,
            "platform": "gemini-web",
            "query": args.question,
            "timestamp": timestamp,
            "raw_response": response_text,
            "citations": citations,
            "model": "Gemini (web)",
            "status": "timeout" if timed_out else "success",
        }

        print(json.dumps(result, ensure_ascii=False))
        browser.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
