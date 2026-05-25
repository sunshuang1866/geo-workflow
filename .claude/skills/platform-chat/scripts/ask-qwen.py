#!/usr/bin/env python3
"""
Send a single question to Qwen Chat web UI via Playwright and output a JSON response record.

Qwen requires authentication. Two auth modes are supported:
  1. Token injection (recommended): provide --session with a JSON file containing {"token": "..."}
     The token is read from localStorage["token"] in your browser's DevTools after logging in once.
  2. Password login: provide QWEN_WEB_EMAIL and QWEN_WEB_PASSWORD env vars (auto-login, no CAPTCHA).

Usage:
  # Token mode (recommended for repeated use)
  python3 ask-qwen.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --session assessments/MindSpore/.qwen-session.json \\
    --timeout 90

  # Password mode (auto-login, no session file needed)
  QWEN_WEB_EMAIL=you@example.com QWEN_WEB_PASSWORD=yourpass \\
  python3 ask-qwen.py \\
    --question "What is MindSpore?" \\
    --question-id q_001 \\
    --timeout 90

Obtain token:
  1. Log in at https://chat.qwen.ai/
  2. Open DevTools → Application → Local Storage → chat.qwen.ai
  3. Copy the value of the "token" key
  4. Save: echo '{"token":"<value>"}' > assessments/{community}/.qwen-session.json

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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.playwright_config import create_browser_context

CHROMIUM_PATH = os.path.expanduser(
    "~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"
)

# ── Selectors ──────────────────────────────────────────────────────────────────
# Auth page
SELECTOR_EMAIL        = "input[name='email']"
SELECTOR_PASSWORD     = "input[name='password']"
SELECTOR_SUBMIT       = "button.qwenchat-auth-pc-submit-button"
SELECTOR_LOGIN_BTN    = ".auth-button-ui.login"   # Log in button on home page

# Chat UI
SELECTOR_TEXTAREA     = "textarea.message-input-textarea"
SELECTOR_SEND         = "button.send-button"
SELECTOR_STOP         = "button.stop-button"        # present only during generation
SELECTOR_ASSISTANT    = ".qwen-chat-message-assistant"
SELECTOR_CITATIONS    = ".qwen-chat-message-assistant a[href]"

# Session check
API_AUTH_CHECK        = "https://chat.qwen.ai/api/v1/auths/"
AUTH_URL              = "https://chat.qwen.ai/auth"
CHAT_URL              = "https://chat.qwen.ai/"


def _load_session(session_path: str) -> str:
    """Read token from JSON session file. Returns token string."""
    with open(session_path) as f:
        data = json.load(f)
    token = data.get("token")
    if not token:
        raise ValueError(f"No 'token' key found in {session_path}")
    return token


def _inject_token(page, token: str) -> None:
    """Inject token into localStorage and reload the page."""
    page.goto(CHAT_URL, timeout=30000)
    time.sleep(2)
    page.evaluate(f'localStorage.setItem("token", {json.dumps(token)})')
    page.reload(timeout=30000)
    time.sleep(3)


def _check_logged_in(page) -> bool:
    """Return True if the current session is authenticated."""
    try:
        # If auth button is visible on homepage, we are NOT logged in
        page.wait_for_selector(SELECTOR_LOGIN_BTN, timeout=2000)
        return False
    except Exception:
        return True


def _login_with_password(page, email: str, password: str) -> bool:
    """
    Perform email/password login. Returns True on success.
    Note: the browser JS hashes the password with SHA-256 before sending —
    no client-side hashing needed here; Playwright fills the form naturally.
    """
    page.goto(AUTH_URL, timeout=30000)
    time.sleep(3)

    try:
        email_input = page.wait_for_selector(SELECTOR_EMAIL, timeout=8000)
    except Exception:
        return False

    email_input.fill(email)
    time.sleep(0.2)
    pwd_input = page.wait_for_selector(SELECTOR_PASSWORD, timeout=5000)
    pwd_input.fill(password)
    time.sleep(0.3)

    submit = page.wait_for_selector(SELECTOR_SUBMIT, timeout=5000)
    submit.click()

    # Wait for URL to leave /auth page (redirect = success)
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            url = page.url
            if "/auth" not in url:
                time.sleep(2)
                return True
        except Exception:
            # Navigation in progress — likely a successful redirect
            time.sleep(2)
            return True
        time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument(
        "--session",
        default=None,
        help="Path to .qwen-session.json with {\"token\": \"...\"}",
    )
    parser.add_argument(
        "--timeout", type=int, default=90, help="Seconds to wait for response"
    )
    parser.add_argument(
        "--screenshot-dir", default=None, help="Directory to save debug screenshots"
    )
    parser.add_argument("--min-citations", type=int, default=8, dest="min_citations",
                        help="Minimum citation count; sends a follow-up if not met")
    args = parser.parse_args()

    email    = os.environ.get("QWEN_WEB_EMAIL", "")
    password = os.environ.get("QWEN_WEB_PASSWORD", "")

    # Determine auth mode
    use_token    = bool(args.session)
    use_password = bool(email and password)

    if not use_token and not use_password:
        print(
            "AUTH_MISSING: provide --session <file> or set "
            "QWEN_WEB_EMAIL + QWEN_WEB_PASSWORD",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PW_Timeout
    except ImportError:
        print("playwright not installed", file=sys.stderr)
        sys.exit(1)

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    launch_kwargs: dict = {}
    if os.path.isfile(CHROMIUM_PATH):
        launch_kwargs["executable_path"] = CHROMIUM_PATH

    with sync_playwright() as p:
        browser, ctx, page = create_browser_context(p, launch_kwargs=launch_kwargs or None)

        def save_screenshot(label: str) -> None:
            if args.screenshot_dir:
                os.makedirs(args.screenshot_dir, exist_ok=True)
                path = os.path.join(
                    args.screenshot_dir,
                    f"debug-{args.question_id}-{label}.png",
                )
                try:
                    page.screenshot(path=path)
                    print(f"  screenshot: {path}", file=sys.stderr)
                except Exception:
                    pass

        # ── Authentication ────────────────────────────────────────────────────
        if use_token:
            try:
                token = _load_session(args.session)
            except Exception as e:
                print(f"SESSION_LOAD_ERROR: {e}", file=sys.stderr)
                browser.close()
                sys.exit(2)

            try:
                _inject_token(page, token)
            except Exception as e:
                print(f"TOKEN_INJECT_ERROR: {e}", file=sys.stderr)
                save_screenshot("token-inject-error")
                browser.close()
                sys.exit(2)

            if not _check_logged_in(page):
                print("SESSION_EXPIRED: token is invalid or expired", file=sys.stderr)
                save_screenshot("session-expired")
                browser.close()
                sys.exit(2)

        else:  # password mode
            try:
                page.goto(CHAT_URL, timeout=30000)
                time.sleep(2)
            except Exception as e:
                print(f"NAVIGATION_ERROR: {e}", file=sys.stderr)
                browser.close()
                sys.exit(1)

            ok = _login_with_password(page, email, password)
            if not ok:
                # Login function may return False even when login succeeded
                # (e.g. URL redirect timing). Check if chat UI is actually loaded.
                time.sleep(3)
                if not _check_logged_in(page):
                    save_screenshot("login-failed")
                    print(
                        "LOGIN_FAILED: check QWEN_WEB_EMAIL / QWEN_WEB_PASSWORD",
                        file=sys.stderr,
                    )
                    browser.close()
                    sys.exit(2)

        # ── Navigate to chat (ensure we are on homepage, not still on /auth) ──
        if "auth" in page.url:
            try:
                page.goto(CHAT_URL, timeout=30000)
                time.sleep(2)
            except Exception as e:
                print(f"NAVIGATION_ERROR: {e}", file=sys.stderr)
                browser.close()
                sys.exit(1)

        # ── Find textarea ─────────────────────────────────────────────────────
        try:
            textarea = page.wait_for_selector(SELECTOR_TEXTAREA, timeout=10000)
        except Exception:
            save_screenshot("no-input")
            print(
                "INPUT_NOT_FOUND: textarea selector may have changed",
                file=sys.stderr,
            )
            browser.close()
            sys.exit(3)

        # ── Type question and send ────────────────────────────────────────────
        textarea.click()
        textarea.fill(args.question)
        time.sleep(0.5)

        try:
            send_btn = page.wait_for_selector(SELECTOR_SEND, timeout=5000)
            send_btn.click()
        except Exception:
            # Fallback: press Enter
            textarea.press("Enter")

        # ── Wait for generation lifecycle ─────────────────────────────────────
        # stop-button is conditionally rendered (not just hidden)
        timed_out = False
        try:
            page.wait_for_selector(SELECTOR_STOP, timeout=15000)
        except Exception:
            # Generation may have started and finished nearly instantly
            pass

        try:
            page.wait_for_selector(
                SELECTOR_STOP,
                state="detached",
                timeout=args.timeout * 1000,
            )
        except Exception:
            timed_out = True

        time.sleep(1)

        # ── Extract response ──────────────────────────────────────────────────
        response_text = ""
        try:
            msgs = page.query_selector_all(SELECTOR_ASSISTANT)
            if msgs:
                response_text = msgs[-1].inner_text().strip()
        except Exception as e:
            print(f"RESPONSE_EXTRACT_ERROR: {e}", file=sys.stderr)

        if timed_out and not response_text:
            save_screenshot("timeout")
            result = {
                "question_id": args.question_id,
                "platform": "qwen-web",
                "query": args.question,
                "timestamp": timestamp,
                "raw_response": "",
                "citations": [],
                "model": "Qwen (web)",
                "status": "timeout",
                "error": "Response generation timed out",
            }
            print(json.dumps(result, ensure_ascii=False))
            browser.close()
            sys.exit(4)

        if not response_text:
            save_screenshot("no-response")
            print(
                "NO_RESPONSE: assistant message element not found or empty",
                file=sys.stderr,
            )
            result = {
                "question_id": args.question_id,
                "platform": "qwen-web",
                "query": args.question,
                "timestamp": timestamp,
                "raw_response": "",
                "citations": [],
                "model": "Qwen (web)",
                "status": "error",
                "error": "No assistant message found in DOM",
            }
            print(json.dumps(result, ensure_ascii=False))
            browser.close()
            sys.exit(1)

        # ── Extract citation links ────────────────────────────────────────────
        try:
            links = page.eval_on_selector_all(
                SELECTOR_CITATIONS,
                """els => [...new Set(els.map(a => a.href))].filter(h =>
                    h.startsWith('http') &&
                    !h.includes('qwen.ai') &&
                    !h.includes('aliyun') &&
                    !h.includes('alibaba')
                )""",
            )
        except Exception:
            links = []

        # Follow-up: request more citations if below threshold
        FOLLOW_UP = "请继续补充更多相关参考来源链接，要求总共包含至少8个不同的来源。"
        if len(links) < args.min_citations:
            print(f"  citations={len(links)} < {args.min_citations}, sending follow-up...", file=sys.stderr)
            seen = set(links)
            try:
                textarea = page.wait_for_selector(SELECTOR_TEXTAREA, timeout=5000)
                textarea.click()
                textarea.fill(FOLLOW_UP)
                time.sleep(0.5)
                try:
                    send_btn = page.wait_for_selector(SELECTOR_SEND, timeout=5000)
                    send_btn.click()
                except Exception:
                    textarea.press("Enter")
                try:
                    page.wait_for_selector(SELECTOR_STOP, timeout=15000)
                    page.wait_for_selector(
                        SELECTOR_STOP, state="detached", timeout=args.timeout * 1000
                    )
                except Exception:
                    pass
                time.sleep(1)
                extra_links = page.eval_on_selector_all(
                    SELECTOR_CITATIONS,
                    """els => [...new Set(els.map(a => a.href))].filter(h =>
                        h.startsWith('http') &&
                        !h.includes('qwen.ai') &&
                        !h.includes('aliyun') &&
                        !h.includes('alibaba')
                    )""",
                )
                for href in extra_links:
                    if href not in seen:
                        seen.add(href)
                        links.append(href)
            except Exception as e:
                print(f"  follow-up error: {e}", file=sys.stderr)

        result = {
            "question_id": args.question_id,
            "platform": "qwen-web",
            "query": args.question,
            "timestamp": timestamp,
            "raw_response": response_text,
            "citations": links,
            "model": "Qwen (web)",
            "status": "timeout" if timed_out else "success",
        }

        print(json.dumps(result, ensure_ascii=False))
        browser.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
