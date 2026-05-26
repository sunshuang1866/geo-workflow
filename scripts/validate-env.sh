#!/usr/bin/env bash
# Validate that the geo-workflow environment is ready to run.
# Checks: .env completeness, Python deps importable, Playwright Chromium present.
#
# Usage:
#   bash scripts/validate-env.sh
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

PASS=0
FAIL=1
overall=0

check() {
    local label="$1"
    local ok="$2"
    local fix="${3:-}"
    if [[ "${ok}" == "0" ]]; then
        echo "  ✓ ${label}"
    else
        echo "  ✗ ${label}" >&2
        [[ -n "${fix}" ]] && echo "    FIX: ${fix}" >&2
        overall=1
    fi
}

# ── Load .env ─────────────────────────────────────────────────────────────────
if [[ -f .env ]]; then
    # shellcheck disable=SC1091
    # Redirect stderr: JSON values in .env (HOTOPIC_DB_CONFIG_JSON) cause harmless bash parse warnings
    set -a; source .env 2>/dev/null || true; set +a
fi

echo "geo-workflow environment check"
echo "────────────────────────────────"

# ── 1. .env file ──────────────────────────────────────────────────────────────
[[ -f .env ]] && env_ok=0 || env_ok=1
check ".env file exists" "${env_ok}" "cp .env.example .env  then fill in credentials"

# ── 2. Required workflow variables ────────────────────────────────────────────
for var in GEO_COMMUNITY GEO_COMMUNITY_DIR GEO_REPO_URL; do
    val="${!var:-}"
    [[ -n "${val}" ]] && var_ok=0 || var_ok=1
    check "env: ${var}=${val:-<unset>}" "${var_ok}" "Set ${var} in .env"
done

# ── 3. Python deps ────────────────────────────────────────────────────────────
for pkg in playwright psycopg2 pymongo; do
    python3 -c "import ${pkg}" 2>/dev/null && pkg_ok=0 || pkg_ok=1
    check "python: ${pkg} importable" "${pkg_ok}" "pip3 install -r requirements.txt"
done

# ── 4. Playwright Chromium binary ─────────────────────────────────────────────
chromium_path=$(find "${HOME}/.cache/ms-playwright" -name "chrome" -type f 2>/dev/null | head -1)
[[ -n "${chromium_path}" ]] && chr_ok=0 || chr_ok=1
check "Playwright Chromium binary" "${chr_ok}" "python3 -m playwright install chromium"

# ── 5. Playwright system libs (libnspr4 / libnss) ─────────────────────────────
if [[ -n "${chromium_path}" ]]; then
    ldd "${chromium_path}" 2>/dev/null | grep -q "not found" && libs_ok=1 || libs_ok=0
    check "Playwright system libraries (ldd clean)" "${libs_ok}" \
        "sudo dnf install -y nss nspr  # or: bash scripts/setup.sh"
fi

echo "────────────────────────────────"
if [[ "${overall}" -eq 0 ]]; then
    echo "All checks passed."
else
    echo "One or more checks failed — see FIX hints above." >&2
fi

exit "${overall}"
