#!/usr/bin/env python3
"""
Preflight check for platform-chat skill.
Verifies: playwright importable, Chromium binary exists, session file present.

Exit 0 = all checks passed.
Exit 1 = one or more checks failed (details on stderr).
"""

import sys
import os
import importlib.util


def check(label, ok, fix=""):
    icon = "✓" if ok else "✗"
    print(f"  {icon} {label}", file=sys.stdout if ok else sys.stderr)
    if not ok and fix:
        print(f"    FIX: {fix}", file=sys.stderr)
    return ok


all_ok = True

# 1. playwright importable
pw_ok = importlib.util.find_spec("playwright") is not None
all_ok &= check(
    "playwright installed",
    pw_ok,
    "pip3 install playwright",
)

# 2. Chromium binary
chromium_path = None
candidate_dirs = [
    os.path.expanduser("~/.cache/ms-playwright"),
]
for base in candidate_dirs:
    if os.path.isdir(base):
        for root, dirs, files in os.walk(base):
            if "chrome" in files:
                chromium_path = os.path.join(root, "chrome")
                break
    if chromium_path:
        break

all_ok &= check(
    f"Chromium binary: {chromium_path or 'NOT FOUND'}",
    chromium_path is not None,
    "python3 -m playwright install chromium",
)

# 3. Session file: look in output/*/.chatgpt-session.json
session_found = False
asses_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assessments")
if os.path.isdir(asses_dir):
    for community in os.listdir(asses_dir):
        sess = os.path.join(asses_dir, community, ".chatgpt-session.json")
        if os.path.isfile(sess):
            session_found = True
            break

all_ok &= check(
    "ChatGPT session file found",
    session_found,
    "python3 .claude/skills/platform-chat/scripts/inject-token.py --token <TOKEN> --community <NAME>",
)

if all_ok:
    print("PREFLIGHT_OK")
    sys.exit(0)
else:
    print("PREFLIGHT_FAILED", file=sys.stderr)
    sys.exit(1)
