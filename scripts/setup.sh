#!/usr/bin/env bash
# Initialize geo-workflow development environment.
# Run once after cloning, or after a fresh Python environment is created.
#
# Usage:
#   bash scripts/setup.sh
#
# Exit codes:
#   0 — setup complete
#   1 — critical step failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

log()  { echo "[setup] $*"; }
fail() { echo "[setup] ERROR: $*" >&2; exit 1; }

cd "${REPO_ROOT}"

# ── 1. Python deps ────────────────────────────────────────────────────────────
log "Installing Python dependencies..."
pip3 install -r requirements.txt || fail "pip3 install failed — check requirements.txt"

# ── 2. Playwright browser ─────────────────────────────────────────────────────
log "Installing Playwright Chromium browser..."
python3 -m playwright install chromium || fail "playwright install chromium failed"

# ── 3. Playwright system libraries ───────────────────────────────────────────
# Required on RPM-based systems (openEuler, Fedora, RHEL).
# Symptom when missing: libnspr4.so: cannot open shared object file
log "Installing Playwright system dependencies..."
if command -v dnf &>/dev/null; then
    sudo dnf install -y nss nspr atk cups-libs libdrm mesa-libgbm \
        pango alsa-lib gtk3 libXcomposite libXdamage libXrandr \
        libgbm xdg-utils 2>/dev/null || {
        echo "[setup] WARNING: dnf install incomplete — Chromium may fail to launch" >&2
        echo "[setup] Run manually: sudo dnf install -y nss nspr" >&2
    }
elif command -v apt-get &>/dev/null; then
    python3 -m playwright install-deps chromium 2>/dev/null || {
        echo "[setup] WARNING: install-deps incomplete — Chromium may fail to launch" >&2
    }
else
    echo "[setup] WARNING: unknown package manager — install Playwright system deps manually" >&2
    echo "[setup] See: https://playwright.dev/python/docs/browsers#install-system-dependencies" >&2
fi

# ── 4. Env file ───────────────────────────────────────────────────────────────
if [[ ! -f .env ]]; then
    log "Creating .env from .env.example..."
    cp .env.example .env
    echo "[setup] WARNING: .env created but credentials are empty — fill in before running." >&2
else
    log ".env already exists — skipping copy."
fi

# ── 5. Git pre-commit hook ────────────────────────────────────────────────────
if [[ -d .git ]]; then
    log "Installing pre-commit hook..."
    ln -sf "$(pwd)/scripts/pre-commit.sh" .git/hooks/pre-commit
    chmod +x scripts/pre-commit.sh
    log "pre-commit hook installed: .git/hooks/pre-commit → scripts/pre-commit.sh"
else
    echo "[setup] WARNING: not a git repository — skipping pre-commit hook install" >&2
fi

# ── 6. Validate ───────────────────────────────────────────────────────────────
log "Running environment validation..."
bash scripts/validate-env.sh || true   # warn only, don't block setup completion

log "Setup complete."
