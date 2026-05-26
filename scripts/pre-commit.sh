#!/usr/bin/env bash
# Pre-commit hook: runs format check and lint before every git commit.
# Tests run in GitHub Actions CI on pull request. Commit is blocked if any step fails.
#
# Installed automatically by scripts/setup.sh via symlink:
#   .git/hooks/pre-commit -> scripts/pre-commit.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

fail() { echo "pre-commit: BLOCKED — $*" >&2; exit 1; }

echo "pre-commit: running checks..."

# 1. Format check (black --check does not modify files)
if command -v black &>/dev/null; then
    black --check .claude/skills/ || fail "black format check failed — run: black .claude/skills/"
else
    echo "pre-commit: WARNING: black not installed, skipping format check" >&2
fi

# 2. Lint
if command -v flake8 &>/dev/null; then
    flake8 .claude/skills/ || fail "flake8 lint failed"
else
    echo "pre-commit: WARNING: flake8 not installed, skipping lint" >&2
fi

echo "pre-commit: all checks passed."
