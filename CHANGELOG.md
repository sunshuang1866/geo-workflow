## 0.2.0 - 2026-05-26

### Features
- Add GitHub Actions CI pipeline: lint, format, and full test suite gate on PR/push to main
- Add dev toolchain scripts: `setup.sh` (installs deps + pre-commit hook), `validate-env.sh` (checks required env vars)
- Add comprehensive test suite: unit tests for scoring logic, URL matching, threshold boundary, and stdout/stderr protocol compliance
- Add `pyproject.toml` with pytest + coverage config (≥70% required), and `.flake8` config

### Fixes
- Fix citation threshold: `citation_rate >= 0.9` → `>= 0.75` to match PRD specification
- Fix stdout/stderr protocol violations in `score-urls.py`, `validate-inputs.py`, `generate-report.py`, `validate-questions.py` — all progress text now routes to stderr, stdout reserved for JSON only
- Remove unused `import json` from `validate-inputs.py`
- Auto-format 27 files with black (line-length 100)

### Documentation
- Add acceptance criteria (验收标准) to all 6 Epics in PRD
- Reorganize docs into `docs/design/` subdirectory
- Update README: CI gate flow, directory structure, setup steps, `output/` path references
- Update AGENT.md: add `validate-env.sh` prerequisite step, `output/` path references
- Rename data directory references `assessments/` → `output/` across all skill docs and scripts
