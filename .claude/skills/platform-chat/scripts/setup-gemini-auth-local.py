#!/usr/bin/env python3
"""
Run this script on your LOCAL machine (not the server).

It opens a visible Chromium browser — log in to Gemini manually,
then press Enter in this terminal to save the session.

Requirements (local machine):
  pip install playwright
  playwright install chromium

Usage:
  python3 setup-gemini-auth-local.py

Output:
  gemini-storage-state.json  (in the current directory)

Then copy it to the server:
  scp gemini-storage-state.json <server>:<project>/assessments/openUBMC/.gemini-session.json
"""

import json
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

OUTPUT = "gemini-storage-state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--window-size=1280,800"])
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="zh-CN",
    )
    page = ctx.new_page()
    page.goto("https://gemini.google.com/app")

    print()
    print("=" * 60)
    print("浏览器已打开 → 请在浏览器中完成 Google 账号登录")
    print("登录完成后，回到此终端按 Enter 保存 session")
    print("=" * 60)
    input("\n登录完成后按 Enter ...")

    # Save full browser storage state (cookies + localStorage + etc.)
    ctx.storage_state(path=OUTPUT)
    browser.close()

# Convert Playwright storage state → our session format
with open(OUTPUT) as f:
    state = json.load(f)

# Extract all cookies for google domains
google_cookies = {
    c["name"]: c["value"]
    for c in state.get("cookies", [])
    if "google" in c.get("domain", "")
}

session = {
    "storage_state": OUTPUT,   # keep full state path for reference
    "cookies": google_cookies,
}
with open(OUTPUT, "w") as f:
    json.dump(state, f, indent=2)

print(f"\n✓ Session saved: {OUTPUT}")
print(f"  Cookies captured: {len(google_cookies)}")
print(f"  Keys: {list(google_cookies.keys())[:8]}...")
print()
print("下一步 — 将文件传到服务器:")
print(f"  scp {OUTPUT} <server>:<project_path>/assessments/openUBMC/.gemini-session.json")
