# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Rules

1. Before writing any code, describe your approach and wait for approval.

2. If the requirements I give you are ambiguous, ask clarifying questions before writing any code.

3. After you finish writing any code, list the edge cases and suggest test cases to cover them.

4. If a task requires changes to more than 3 files, stop and break it into smaller tasks first.

5. When there's a bug, start by writing a test that reproduces it, then fix it until the test passes.

6. Every time I correct you, reflect on what you did wrong and come up with a plan to never make the same mistake again.

7. Before every git commit, you MUST run `/release-skills` first to update CHANGELOG.md. Do not commit without updating the changelog.

8. When creating new skills, you MUST use `/skill-creator` to scaffold and structure the skill. After creation, verify the new skill conforms to the agentskills.io spec (correct SKILL.md frontmatter, directory structure, procedural instructions).

9. At the start of every new conversation, IMMEDIATELY read `CLAUDE-RESUME.md` to restore project context, current status, and pending TODOs before doing anything else.

10. After completing any task that changes project state (file creation/modification, TODO completion, new decisions, architecture changes), you MUST update `CLAUDE-RESUME.md` accordingly — keep the "Current Status", "TODO", and "Recent Changes" sections accurate and up to date.

11. Do NOT just agree with my ideas. Think independently, challenge assumptions, and proactively suggest better alternatives or broader perspectives when you see an opportunity.

---

## Code Standards

> All code development MUST comply with these standards. Full specifications: [docs/CLEAN_CODE.md](docs/CLEAN_CODE.md) · [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

### stdout / stderr Protocol (CRITICAL — never violate)

- **stdout**: pure JSON only (array or object). NEVER mix in progress text — it breaks downstream parsing.
- **stderr**: all human-readable output (progress, warnings, errors).
- **stderr prefix convention**:
  - `ERROR: <message>` → fatal, immediately followed by `sys.exit(1)`
  - `WARNING: <message>` → non-fatal, log and continue (degraded mode)
  - no prefix → normal progress info
- **Exit codes**: `0` = success, `1` = failure. No other values.

```python
# ✅ Correct
print(f"WARNING: DB connection failed: {e}", file=sys.stderr)   # non-fatal
print(f"ERROR: questions.json not found: {path}", file=sys.stderr)
sys.exit(1)                                                      # fatal
print(json.dumps(results, ensure_ascii=False, indent=2))        # stdout: JSON only

# ❌ Wrong — progress text in stdout corrupts JSON output
print(f"Fetching {url}...")
print(json.dumps(results))
```

### Error Handling

- No bare `except:` — always specify the exception type.
- Prefer specific types: `urllib.error.HTTPError`, `urllib.error.URLError`, `json.JSONDecodeError`, `psycopg2.Error`.
- Error messages MUST include context (URL, file path, parameter value).
- Distinguish fatal vs degradable: missing file → `ERROR:` + `sys.exit(1)`; network timeout → `WARNING:` + `return None`.

```python
# ✅ Specific exception + context + graceful degradation
try:
    conn = psycopg2.connect(host=cfg["host"], ...)
except Exception as e:
    print(f"WARNING: DB connection failed: {e}", file=sys.stderr)
    return None  # caller falls back to Discourse API

# ❌ Swallowing exceptions
try:
    result = call_api(url)
except:
    result = {}
```

### Script Structure

- Every script MUST have: module-level docstring (purpose + Usage + Exit codes) + `main()` function + `if __name__ == "__main__"` guard.
- Script filenames: kebab-case verb phrases (e.g. `fetch-forum-posts.py`, `score-urls.py`).
- Functions: ≤ 30 lines, single responsibility. Private helpers prefixed with `_`.
- Module-level constants: `UPPER_SNAKE_CASE` (e.g. `MIN_VIEWS = 50`).
- Reusable utilities go in `_shared/utils.py` — never re-implement `load_json`, `resolve_platform_token`, etc.

```python
# ✅ Standard script header
"""Score responses against official URLs using exact URL matching.

Usage:
    python3 score-urls.py <responses_json> <questions_json> <output_json>

Exit codes:
  0 — scoring complete
  1 — missing input file or invalid JSON
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import load_json

def main():
    ...

if __name__ == "__main__":
    main()
```

### Naming

- Functions: start with a verb (`fetch_from_db`, `normalize_url`, `_load_db_config`).
- No abbreviations: `citation_rate` not `cr`, `platform_records` not `precs`.
- Environment variables: use `os.environ.get()` with explicit missing check — never `os.environ[key]`.

```python
# ✅ Explicit missing check
community = os.environ.get("GEO_COMMUNITY", "")
if not community:
    print("ERROR: GEO_COMMUNITY not set in .env", file=sys.stderr)
    sys.exit(1)
```

### Security

- NEVER hardcode tokens, passwords, or API keys. Read all credentials from environment variables.
- `.env` must NOT be committed. `.env.example` is the template.

### Skill Design Rules

- Every Skill MUST declare its inputs, outputs, and required env vars in `SKILL.md` Prerequisites.
- `SKILL.md` body MUST stay ≤ 500 lines — move large rule sets to `references/`.
- Every Skill MUST support a `dry_run` parameter — no write operations when `dry_run=true`.
- Skill logic MUST be idempotent — re-running must not create duplicates (use `issue-map.json` append-or-update pattern).
- Do NOT manually edit `CLAUDE-RESUME.md` or `CHANGELOG.md` — they are auto-maintained.

### Commit Standards

- Follow Conventional Commits: `<type>(<scope>): <description>`
- Scope = skill name or `agent` / `shared` / `project`.
- One commit = one logical change.

---

## Pre-Commit Checklist

Run these checks before every commit. Do not skip.

```bash
# Format
black .claude/skills/

# Lint
flake8 .claude/skills/ --max-line-length=100

# Tests + coverage (fails if coverage drops below 70%)
python3 -m pytest

# Verify stdout is valid JSON (spot-check any modified script)
python3 <script> [args] 2>/dev/null | python3 -m json.tool

# Verify dry_run works (for skills that write to GitHub/GitCode)
python3 <script> --dry-run [args]
```

---

## Observability

> Full guide: [docs/OBSERVABILITY_GUIDE.md](docs/OBSERVABILITY_GUIDE.md)

After every pipeline run, check these signals before reporting completion:

**1. Run status** — read `{community_dir}/{date}/run-meta.json`:
- `"status": "success"` → OK
- `"status": "partial_success"` → Issue activity mismatch; re-run `steps=3,4,5`
- `"status": "failed"` → check `run.log` or Claude Code stderr for root cause
- `"skipped_platforms": [...]` → one or more sampling platforms failed; check session credentials

**2. Scoring sanity** — read `scoring-results.json`:
```bash
python3 -c "
import json; data = json.load(open('{path}/scoring-results.json'))
s = data['summary']['by_severity']; total = sum(s.values())
print(f'OK={s[\"OK\"]}/{total}  P0={s[\"P0\"]}  P1={s[\"P1\"]}')
"
```

**3. Issue consistency** — if Step 3 ran, verify `created-issues.json` exists and `run-meta.json` summary counters match its activity log.

**Common failure patterns and fixes:**

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `libnspr4.so: cannot open shared object file` | Playwright missing system libs | `playwright install-deps chromium` or `sudo dnf install -y nss nspr` |
| All `citation_rate = 0.0` | `official_urls` empty in `questions.json` | Run `/prefill-urls` or fill manually |
| `ERROR: HTTP 403` on issue creation | Token missing `issues:write` scope | Regenerate token with correct scope |
| `questions.json has changed` abort | Question set changed since last run | Re-run with `accept_question_update=true` |
| `partial_success` in run-meta | Issue count mismatch | Re-run `steps=3,4,5` |

---

## Full Specification References

- [docs/CLEAN_CODE.md](docs/CLEAN_CODE.md) — Naming, stdout/stderr protocol, error handling, formatting rules
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — Skill design, branching, commit standards, environment setup
- [docs/OBSERVABILITY_GUIDE.md](docs/OBSERVABILITY_GUIDE.md) — Run output interpretation, multi-run trend analysis, troubleshooting
