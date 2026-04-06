#!/usr/bin/env python3
"""
Send a single question to DeepSeek web UI via Playwright and output a JSON response record.

DeepSeek supports two auth modes:
  1. Cookie injection (recommended): provide --session with a JSON file containing ds_session_id
  2. Password login: provide DEEPSEEK_WEB_EMAIL and DEEPSEEK_WEB_PASSWORD env vars

Usage:
  # Cookie mode (use inject-deepseek.py first to create the session file)
  python3 ask-deepseek.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --session assessments/MindSpore/.deepseek-session.json \\
    --timeout 90

  # Password mode (auto-login, no session file needed)
  DEEPSEEK_WEB_EMAIL=you@example.com DEEPSEEK_WEB_PASSWORD=yourpass \\
  python3 ask-deepseek.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --timeout 90

Stdout: single JSON object (responses.json compatible)
Stderr: error messages only

Exit codes:
  0 — success
  2 — session expired / login failed
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

# ── Selectors ──────────────────────────────────────────────────────────────────
# Sign-in page
SELECTOR_EMAIL    = "input.ds-input__input[type='text']"  # stable ds- prefix
SELECTOR_PASSWORD = "input[type='password']"
SELECTOR_LOGIN_BTN = "button.ds-basic-button--primary"    # "Log in"

# Chat UI (CSS module hashes can drift across deployments; update if UI breaks)
SELECTOR_TEXTAREA     = "textarea"                         # only one textarea on page
SELECTOR_SEND_BTN     = "._7436101"                       # sendButton CSS class
SELECTOR_SEND_ACTIVE  = "._7436101:not(.bcc55ca1)"        # sendButton when not disabled
SELECTOR_STOP_BTN     = "._7436101.bcc55ca1"              # sendButton in "stop" state
SELECTOR_ASST_MSG     = "._4f9bf79"                       # assistantMessage container
SELECTOR_CITATIONS    = "._4f9bf79 a[href]"               # links inside response

# Fallback selector using CSS variable in style attribute (more stable)
SELECTOR_ASST_MSG_STABLE = "div[style*='--assistant-last-margin-bottom']"


def _make_empty_result(question_id, question, status, error=""):
    return {
        "question_id": question_id,
        "platform": "deepseek-web",
        "query": question,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "raw_response": "",
        "citations": [],
        "model": "DeepSeek (web)",
        "status": status,
        **({"error": error} if error else {}),
    }


def _do_login(page, email, password, timeout_ms=30000):
    """Fill sign-in form and wait for redirect to chat. Returns True on success."""
    from playwright.sync_api import TimeoutError as PW_Timeout

    try:
        page.wait_for_selector(SELECTOR_EMAIL, timeout=10000)
        page.fill(SELECTOR_EMAIL, email)
        page.fill(SELECTOR_PASSWORD, password)
        btn = page.wait_for_selector(SELECTOR_LOGIN_BTN, timeout=5000)
        btn.click()
        # Wait for redirect away from sign_in
        page.wait_for_url(lambda u: "/sign_in" not in u, timeout=timeout_ms)
        time.sleep(2)
        return True
    except PW_Timeout:
        return False
    except Exception as e:
        print(f"LOGIN_ERROR: {e}", file=sys.stderr)
        return False


def _wait_for_response(page, timeout_sec):
    """
    Wait for DeepSeek to finish generating.
    Strategy:
      1. Poll until a new assistant message appears in the DOM.
      2. Then poll text content until stable for 3 consecutive checks (2-second intervals).
      Timeout aborts both phases.
    Returns (text, timed_out:bool)
    """
    deadline = time.time() + timeout_sec
    prev_text = None
    stable_count = 0

    # Phase 1: wait for at least one assistant message to appear
    while time.time() < deadline:
        msgs = (
            page.query_selector_all(SELECTOR_ASST_MSG)
            or page.query_selector_all(SELECTOR_ASST_MSG_STABLE)
        )
        if msgs:
            break
        time.sleep(1)
    else:
        return "", True

    # Phase 2: wait for text to stabilize
    while time.time() < deadline:
        msgs = (
            page.query_selector_all(SELECTOR_ASST_MSG)
            or page.query_selector_all(SELECTOR_ASST_MSG_STABLE)
        )
        current_text = msgs[-1].inner_text().strip() if msgs else ""
        if current_text == prev_text and current_text:
            stable_count += 1
            if stable_count >= 3:
                return current_text, False
        else:
            stable_count = 0
        prev_text = current_text
        time.sleep(2)

    # Return whatever we have, even if timed out
    return prev_text or "", True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--question-id", required=True, dest="question_id")
    parser.add_argument("--session", default=None,
                        help="Path to .deepseek-session.json (cookie auth)")
    parser.add_argument("--timeout", type=int, default=90,
                        help="Seconds to wait for response")
    parser.add_argument("--screenshot-dir", default=None,
                        help="Directory to save debug screenshots")
    parser.add_argument("--min-citations", type=int, default=8, dest="min_citations",
                        help="Minimum citation count; sends a follow-up if not met")
    args = parser.parse_args()

    email    = os.environ.get("DEEPSEEK_WEB_EMAIL")
    password = os.environ.get("DEEPSEEK_WEB_PASSWORD")

    # Must have at least one auth method
    has_session = args.session and os.path.isfile(args.session)
    has_creds   = bool(email and password)

    if not has_session and not has_creds:
        msg = (
            "No auth: provide --session <file> (cookie auth) "
            "or set DEEPSEEK_WEB_EMAIL + DEEPSEEK_WEB_PASSWORD env vars."
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("playwright not installed — run: pip3 install playwright && python3 -m playwright install chromium",
              file=sys.stderr)
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

        # Build context with optional storage_state (cookie file)
        ctx_kwargs = dict(
            user_agent=UA,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        if has_session:
            ctx_kwargs["storage_state"] = args.session

        ctx = browser.new_context(**ctx_kwargs)
        ctx.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        page = ctx.new_page()

        # Navigate
        try:
            page.goto("https://chat.deepseek.com/", timeout=30000)
            time.sleep(2)
        except Exception as e:
            print(f"NAVIGATION_ERROR: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # Handle login if login form is visible (URL may or may not contain /sign_in)
        login_form_visible = page.query_selector(SELECTOR_EMAIL) is not None
        if login_form_visible:
            if has_creds:
                print("  Logging in with email/password ...", file=sys.stderr)
                if not _do_login(page, email, password):
                    save_screenshot("login-failed")
                    print("LOGIN_FAILED: check credentials or CAPTCHA", file=sys.stderr)
                    browser.close()
                    sys.exit(2)
            else:
                save_screenshot("session-expired")
                print("SESSION_EXPIRED: cookie auth failed and no credentials provided",
                      file=sys.stderr)
                browser.close()
                sys.exit(2)

        # Find chat textarea
        try:
            textarea = page.wait_for_selector(SELECTOR_TEXTAREA, timeout=15000)
        except PW_Timeout:
            save_screenshot("no-input")
            print("INPUT_NOT_FOUND: textarea selector may have changed", file=sys.stderr)
            browser.close()
            sys.exit(3)

        # Type question and submit via Enter key
        textarea.click()
        textarea.fill(args.question)
        time.sleep(0.5)

        # Click send button if available; fall back to Enter key
        try:
            btn = page.wait_for_selector(SELECTOR_SEND_ACTIVE, timeout=3000)
            btn.click()
        except PW_Timeout:
            textarea.press("Enter")

        # Wait for response
        response_text, timed_out = _wait_for_response(page, args.timeout)

        if timed_out and not response_text:
            save_screenshot("timeout")
            result = _make_empty_result(
                args.question_id, args.question, "timeout",
                "Response generation timed out"
            )
            result["timestamp"] = timestamp
            print(json.dumps(result, ensure_ascii=False))
            browser.close()
            sys.exit(4)

        # Extract citations
        try:
            links = page.eval_on_selector_all(
                SELECTOR_CITATIONS
                if page.query_selector(SELECTOR_ASST_MSG) else
                SELECTOR_ASST_MSG_STABLE + " a[href]",
                "els => els.map(a => a.href).filter(h => h.startsWith('http'))",
            )
        except Exception:
            links = []

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
                textarea = page.wait_for_selector(SELECTOR_TEXTAREA, timeout=5000)
                textarea.click()
                textarea.fill(FOLLOW_UP)
                time.sleep(0.5)
                try:
                    send_btn = page.wait_for_selector(SELECTOR_SEND_ACTIVE, timeout=5000)
                    send_btn.click()
                except PW_Timeout:
                    textarea.press("Enter")
                _wait_for_response(page, args.timeout)
                try:
                    all_links = page.eval_on_selector_all(
                        SELECTOR_CITATIONS
                        if page.query_selector(SELECTOR_ASST_MSG)
                        else SELECTOR_ASST_MSG_STABLE + " a[href]",
                        "els => els.map(a => a.href).filter(h => h.startsWith('http'))",
                    )
                    for href in all_links:
                        if href not in seen:
                            seen.add(href)
                            citations.append(href)
                except Exception:
                    pass
            except Exception as e:
                print(f"  follow-up error: {e}", file=sys.stderr)

        result = {
            "question_id": args.question_id,
            "platform": "deepseek-web",
            "query": args.question,
            "timestamp": timestamp,
            "raw_response": response_text,
            "citations": citations,
            "model": "DeepSeek (web)",
            "status": "timeout" if timed_out else "success",
        }

        print(json.dumps(result, ensure_ascii=False))
        browser.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
