# CLAUDE-RESUME.md

Session resume file for Claude Code. Read this at the start of every new conversation to restore context.

> **Keep this file up to date**: After any task that changes project state, update the relevant sections below.

## Project Overview

GEO (Generative Engine Optimization) Search Assessment — a system that automatically evaluates how well an open-source community (initially MindSpore) is represented across mainstream AI search platforms, then generates actionable improvement suggestions.

**Core workflow**: Define questions → Sample AI platforms → Score & diagnose → Output suggestions

**Design doc**: See `README.md` + `AGENT.md` for the current executable specification.

## Architecture

The system is a **skill chain orchestrated by AGENT.md**, not a web application. Pure CLI-driven via Claude Code.

3-step pipeline + issue creation, each step is a separate skill:

1. **get-question** — Incrementally append new questions to existing `questions.json`; never overwrites. Deduplicates new candidates against existing questions. Preserves `official_urls`/`notes`.
2. **platform-sampler** — Call 4 AI platform APIs with questions, collect responses
3. **scoring-engine** — Multi-layer evaluation (content completeness + citation accuracy + optional fact coverage), cross-platform pattern analysis, catalog-based suggestion matching (72-item GEO catalog), generate P0-P2 improvement suggestions with execution roadmap
4. **issue-creator** — Auto-create GitCode Issues from improvement suggestions

Data flows as JSON between skills, with Markdown output for human review.

## Step 1 Design (get-question) — AGREED

Question sources: manual input + 4 selectable auto-generation paths (`paths` param: `forum`, `issue`, `maillist`, `website`, `all`)

- **Manual input**: Community operators write questions in `manual-questions.md` (Markdown), skill auto-parses to structured JSON. No YAML needed.
- **Path 1 (PRIMARY): Forum usage question extraction (使用阶段)** — Fetch top topics from MindSpore Discourse forum (`https://discuss.mindspore.cn`) via API. Fetches from 问题求助 Help + MindSpore Lite categories + global top. LLM rewrites titles to search questions, filters pure bugs. Forum + issues are the primary question source.
- **Path 2 (PRIMARY): Repo issue question extraction (使用阶段)** — Fetch issues from GitCode (`https://gitcode.com/mindspore/mindspore/issues`) via API (`api.gitcode.com/api/v5`). Requires `GITCODE_TOKEN`. Sorted by comments, LLM rewrites to search questions. No LLM fallback — skip if no token.
- **Path 3: Maillist (SIG) question extraction (使用阶段)** — Two-step: MagicAPI fetches SIG list → HyperKitty API fetches email archives from mailweb.mindspore.cn. Active lists: dev(71), tsc(53), discuss(49), infra(8). LLM filters/rewrites to search questions.
- **Path 4: Website search keywords (使用阶段)** — Calls official website's internal search hot-words API (`WEBSITE_SEARCH_URL`, must be provided by community ops). Filters navigation/brand terms. LLM rewrites raw search terms into natural language questions. No fallback — skip if `WEBSITE_SEARCH_URL` not set. Optional auth via `WEBSITE_SEARCH_TOKEN`.
Merge (manual + selected paths) → semantic dedup → classify → output `questions.json` + `questions.md`.

Priority: manual > forum (path1) / issue (path2) > multi-source > single-source.

**Quantity**: 30-40 questions for MVP (adjustable based on results).

**Output format**: `questions.json` (machine) + `questions.md` (human readable). Bilingual zh/en.

## Design Doc Structure

Current docs focus:

- **总览**: 系统架构 + 执行步骤(1-4) + 总体开发路线 + 待讨论问题汇总
- **第一部分(一~五)**: 主流 AI 搜索平台分析 — 平台分类、优先级、API 可用性、MVP 结论
- **第二部分(六~九)**: 关键词定义策略 — 手动输入(Markdown)、自动生成(3 paths)、合并去重、技术要点
- **第三部分(十~十四)**: 评分体系与输出规范（待讨论）— 评分指标、GEO 评分体系、改进建议、Excel 导出、技术方案

已删除的节: 定期更新机制(原九)、中英文双语方案(原十)

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Development rules (11 rules) |
| `AGENT.md` | Workflow orchestrator (periodic re-check entry point) |
| `CLAUDE-RESUME.md` | Session recovery (this file) |
| `README.md` | Usage rules for developers |
| `.env.example` | API token template (6 platforms) |
| `.gitignore` | Excludes `.env` from git |
| `assessments/` | Community assessment data root |
| `assessments/MindSpore/` | MindSpore community data (questions, labels, runs) |

## Skills Created

| Skill | Directory | Status |
|-------|-----------|--------|
| get-question | `.claude/skills/get-question/` | ✅ Complete |
| platform-sampler | `.claude/skills/platform-sampler/` | ✅ Complete |
| scoring-engine | `.claude/skills/scoring-engine/` | ✅ Complete |
| issue-creator | `.claude/skills/issue-creator/` | ✅ Complete |
| assessment-report | `.claude/skills/assessment-report/` | ✅ Complete |
| ~~improvement-advisor~~ | merged into scoring-engine (2026-03-19) | ❌ Deleted |

### get-question
- 8-step procedure: Load config → Parse manual → Path 1 (forum) → Path 2 (issue) → Path 3 (maillist/SIG) → Path 4 (website search keywords) → Merge & dedup → Output
- Maillist path: two-step flow — (1) MagicAPI fetches SIG list → extracts mailing_list addresses, (2) HyperKitty API fetches email archives from mailweb.mindspore.cn → thread subjects + email content. Active lists: dev(71), tsc(53), discuss(49), infra(8).
- Forum: all content types included (technical, events, blogs, announcements) — views are relevance filter, not content type
- Forum endpoint: `/c/{slug}/{id}/l/top.json?period=all` (views-sorted, not latest activity)
- Scripts: `parse-manual-questions.py`, `fetch-forum-posts.py`, `fetch-repo-issues.py`, `fetch-sig-info.py`, `validate-questions.py`
- References: `forum-api-spec.md`, `gitcode-api-spec.md`, `sig-api-spec.md`
- Assets: `questions-template.md`

### platform-sampler
- 5-step procedure: Load config → Load questions → Sample platforms → Post-process (LLM metadata extraction) → Validate & output
- Scripts: `sample-platform.py`, `validate-input.py`, `validate-responses.py`
- References: `platform-rate-limits.md`
- Assets: `responses-template.md`
- Post-processing extracts: mentions_community, community_description, competitors_mentioned, recommendation_position, citations_to_official

### scoring-engine
- 5-step procedure: Validate inputs → URL match scoring → Cross-platform aggregation → Match GEO catalog suggestions → Compile output
- Scripts: `validate-inputs.py`, `compile-report.py`
- References: `suggestion-rules.md`, `geo-suggestions-catalog.md`
- Pure URL string matching (exact URL + domain-level), no LLM evaluation
- Scoring is question-level: Step 2 does per-platform binary match (cited/not_cited), Step 3 aggregates with 90% threshold
- citation_rate = cited_platforms / total_platforms; ≥90% → "引用了官方内容" (OK), <90% → "有内容未被引用" (P0), no official URLs → "官方内容缺失" (P1)
- 72-item GEO suggestion catalog, matched by status (not_cited → SEO suggestions, no_official_content → content creation)
- Output: `scoring-results.json` only

### issue-creator
- 7-step procedure: Load config → Parse scoring results → LLM enrich & group → Match issue-map → Create new issues → Update/resolve existing → Save & summary
- Scripts: `parse-suggestions.py`, `create-issue.py`, `comment-issue.py`
- References: `gitcode-api-spec.md`
- Assets: `issue-template.md`
- Supports dry-run mode, outputs `created-issues.json`
- Status-based matching: `not_cited`→SEO suggestions, `no_official_content`→content creation; `satisfied` triggers resolution comment
- Issue-map match key: `question_ids` overlap only (status excluded, so status changes don't create duplicate issues)
- `citation_rate` displayed in all issue bodies and update comments
- LLM generates: `phenomenon_type`, `content_judgment`, `phenomenon_detail`, `causal_chain`, `action_items`, `cross_platform_section`

## Current Status

- **Phase**: All 5 pipeline skills created and simplified. AGENT.md is 6 steps (0-5): init → sample → score → issue → report → finalize. assessment-tracker.md and tracking-log.md removed from workflow.
- **Directory structure**: Community data lives under `assessments/{community}/`. Typo `asssessments` fixed to `assessments` on 2026-03-28.
- **MindSpore**: `assessments/MindSpore/` — has `questions.json` (with official_urls merged in), `questions.md`. Ready for first full pipeline run.
- **issue-creator skill**: Updated SKILL.md (community/version_label inputs, richer LLM prompt with causal_chain/cross_platform_section/action_items) and issue-template.md (matches real-world issue.md format)
- **Branch**: `main`
- **Last updated**: 2026-03-26

## TODO

- [x] Create get-question skill using `/skill-creator`
- [x] Create platform-sampler skill using `/skill-creator`
- [x] Create scoring-engine skill (design agreed, needs `/skill-creator`)
- [x] Create issue-creator skill
- [x] ~~Create improvement-advisor skill~~ (merged into scoring-engine 2026-03-19)
- [x] Create AGENT.md to orchestrate the full workflow
- [ ] Discuss 第一部分 (主流 AI 搜索平台分析) with user
- [x] Create `content-labels.json` template (human labels: official_urls per question)
- [ ] Design scoring LLM Prompt template (待设计 3.3)

## Recent Changes

| Date | Change |
|------|--------|
| 2026-04-02 | Generated assessment-report for openEuler run `2026-04-02` (first run, prev_report=none). 50 questions all `not_cited` P0, grouped into 5 improvement action categories: 补充专题文档(24q)、添加结构化数据(16q)、优化SEO元数据(22q)、重构内容结构(5q)、针对特定平台提交收录(4q). All 50 questions linked to GitHub Issues #15-#27. Output: `assessments/openEuler/2026-04-02/assessment-report.json` + `assessment-report.md`. |
| 2026-04-02 | Ran issue-creator for openEuler run `2026-04-02` with exclusion set `{q_041..q_059, q_061, q_062, q_064..q_068, q_076}` (none present in current 50-question scope, filter no-op). Generated `scoring-results.issue-filtered.json`. LLM grouped 50 `not_cited` P0 suggestions into 13 semantic groups (g_001..g_013). issue-map.json was absent → all 13 → `to_create`. Created 13 live GitHub Issues (#15–#27) on `opensourceways/geo-workflow`. Saved `assessments/openEuler/issue-map.json` (13 entries) and `assessments/openEuler/2026-04-02/created-issues.json`. |
| 2026-04-02 | Re-ran assessment-report generation for openEuler `2026-04-02` with explicit exclusion set `{q_041..q_059, q_061, q_062, q_064..q_068, q_076}` using filtered input `assessments/openEuler/2026-04-02/scoring-results.filtered.json`. Validation showed these IDs were not present in current scoring/results scope, so output question set remained unchanged (`total_questions=50`, `not_cited=50`, excluded IDs found in report = none). |
| 2026-04-02 | Re-generated `assessments/openEuler/2026-04-02/assessment-report.json` and `assessments/openEuler/2026-04-02/assessment-report.md` after finalizing 3-platform issue-map updates. Report metadata now points to `prev_report=none` (no historical baseline found), totals remain `50` questions with `P0/not_cited=50`, `P1/no_official_content=0`, `OK/satisfied=0`, and trend summary remains first-run (`new=50`). |
| 2026-04-02 | Ran issue-creator on openEuler run `2026-04-02` using the updated 3-platform scoring baseline (`deepseek,qwen,gemini`) in **dry-run** mode. Match result against `assessments/openEuler/issue-map.json`: `to_create=0`, `to_update=6`, `to_resolve=0`. Wrote `assessments/openEuler/2026-04-02/created-issues.json` with 6 simulated update comments and updated `issue-map.json` citation fields to 3-platform values (notably `g_004` and `g_006` citation_rate to `0.3333`). |
| 2026-04-02 | Re-ran scoring-engine for openEuler run `2026-04-02` with platform scope restricted to `deepseek,qwen,gemini` (excluded `chatgpt,doubao`) per user request. Generated `responses.3p.json`, `scoring-results.raw.3p.json`, `scoring-results.3p.json`, and finalized canonical `scoring-results.json` with merged summary schema: `by_status={satisfied:0, not_cited:50, no_official_content:0}`, `by_severity={P0:50, P1:0, OK:0}`, `citation_rate_distribution={0.0:48, 0.3:2}`, `total_platforms=3`. Re-synced `assessments/openEuler/questions.md` official links column from `questions.json`, and cleaned one accidental empty URL item in `q_012` of `questions.json`. |
| 2026-04-02 | Ran assessment-report for openEuler run `2026-04-02` using `scoring-results.json` + `questions.json` + `issue-map.json` (first baseline with `prev_report=none`). Generated `assessments/openEuler/2026-04-02/assessment-report.json` and `assessments/openEuler/2026-04-02/assessment-report.md`. Summary: total 50 questions, `not_cited`=50 (P0), `no_official_content`=0, `satisfied`=0, trend counts `new`=50. |
| 2026-04-02 | Ran scoring-engine for openEuler using `assessments/openEuler/2026-04-02/responses.json` + `assessments/openEuler/questions.json`. Because responses used `raw_response`, generated compatibility file `responses.normalized.json` (adds `response_text`) to pass validator, then produced `scoring-results.raw.json` and final `scoring-results.json`. Result summary: 50/50 scored, `not_cited`=50, `satisfied`=0, `no_official_content`=0; citation rate distribution `0.0=48`, `0.2=2`; compiled suggestions count=45. Synced official URLs into `assessments/openEuler/questions.md` (50 questions with official links). |
| 2026-04-02 | Ran platform-sampler for openEuler with range `q001-q040` (expanded to `q_001..q_040`, `q_036` missing and skipped). Merge result in `assessments/openEuler/2026-04-02/responses.json`: 250 responses (50 questions x 5 platforms), 147 success / 103 errors; validator warns 41% errors and 2 empty responses. Requested-slice quality (`q_001..q_040`): 39 questions, 195 responses, deepseek 39/39, qwen 39/39, gemini 37/39, chatgpt 0/39, doubao 0/39. |
| 2026-04-02 | Fixed platform-sampler compatibility: `sample-platform.py` now supports `{PLATFORM}_MODEL` env override, Gemini defaults switched to OpenAI-compatible `https://www.packyapi.com/v1` + `gemini-2.5-pro`, and citation extraction trims trailing backticks. Updated `.env` Gemini settings accordingly, then re-ran openEuler sampler in `append` mode for `q_060,q_063,q_070,q_071,q_073,q_074,q_077,q_078,q_079,q_080,q_081` on `deepseek,qwen,gemini` (q_072 missing as before). Post-rerun result: 55 total responses with 32 success / 23 errors (error ratio reduced from 65% to 42%). |
| 2026-04-02 | Ran platform-sampler for openEuler with filtered IDs `q_060,q_063,q_070,q_071,q_073,q_074,q_077,q_078,q_079,q_080,q_081` (requested range included missing `q_072`, skipped by warning). Output written to `assessments/openEuler/2026-04-02/responses.json` with 55 responses (11 questions x 5 platforms), 19 success / 36 errors (65% errors warning). |
| 2026-04-01 | Implemented `.claude/skills/platform-sampler/scripts/run-sampler.py` as the concrete batch entry for multi-question x multi-platform sampling (grouped parallel questions, sequential per-platform calls, per-question flush, append/new_run merge by `(question_id, platform)`) and documented usage in platform-sampler SKILL.md. |
| 2026-04-01 | AGENT.md Step 5 enhanced with issue activity consistency validation: when Step 3 runs, `created-issues.json` must exist and its activity counts must match `run-meta.json.summary` (`issues_created/updated/resolved`); mismatch now marked as `partial_success` with warning and re-run hint `steps=3,4,5`. |
| 2026-04-01 | Housekeeping cleanup: fixed `assessments/MindSpore/2026-03-31/run-meta.json` community_dir path, removed stale `docs/` and `openUBMC` references from README/CLAUDE-RESUME, and deleted tracked Python cache file with `.gitignore` rules for `__pycache__/`, `*.pyc`, `.claude/settings.local.json`. |
| 2026-03-10 | Initialized repository with design doc |
| 2026-03-10 | Installed release-skills and skill-creator to `.claude/skills/` |
| 2026-03-10 | Configured CLAUDE.md development rules (rules 1-11) |
| 2026-03-10 | Created CLAUDE-RESUME.md for session context recovery |
| 2026-03-10 | Created README.md with usage rules |
| 2026-03-10 | Released v0.1.0 |
| 2026-03-10 | Agreed on total architecture: skill chain + AGENT.md orchestration |
| 2026-03-10 | Agreed on Step 1 design: 3 paths + manual input, human review checkpoint, feedback loop |
| 2026-03-10 | Changed target community from openEuler to MindSpore (competitors: TensorFlow/PyTorch) |
| 2026-03-10 | Revised 第二部分: manual input via Markdown, auto-generation aligned with 3 paths |
| 2026-03-10 | MVP platforms expanded to 5: +豆包(火山引擎) +Qwen(阿里云百炼), scoring weights TBD |
| 2026-03-10 | Created `.env.example` (6 platform API keys) and `.gitignore` |
| 2026-03-10 | Created get-question skill (8 steps, 4 scripts, follows agentskills.io spec) |
| 2026-03-10 | Path 2 simplified: removed Issue extraction, forum posts only |
| 2026-03-10 | Created platform-sampler skill (5 steps, 3 scripts, follows agentskills.io spec) |
| 2026-03-12 | Analyzed Q8-Q10 (official FAQ) across 5 AI platforms, identified critical issues |
| 2026-03-12 | Created GEO-Improvement-Report-Q8-Q10.md with root cause analysis and optimization roadmap |
| 2026-03-12 | Added universal GEO recommendations (5.1-5.7) to improvement report |
| 2026-03-12 | Created improvement-advisor skill (7 steps, 2 scripts, 2 references, 1 asset template) |
| 2026-03-12 | 设计文档重新排版：执行步骤合并为三步，MVP 平台调整为 4 个（移除 Perplexity） |
| 2026-03-12 | get-question: Forum→Path 1 (primary), Industry→Path 2, AI reverse→Path 3. Added `paths` selector. |
| 2026-03-12 | fetch-forum-posts.py: Implemented Discourse API integration (discuss.mindspore.cn), no longer placeholder |
| 2026-03-12 | forum-api-spec.md: Updated with real Discourse endpoints, categories, and topic object schema |
| 2026-03-12 | Design doc 步骤一: Reordered paths, forum as primary, added path selectability |
| 2026-03-12 | Added Path 2 (issue): GitCode repo issue extraction via api.gitcode.com (requires GITCODE_TOKEN) |
| 2026-03-12 | Created fetch-repo-issues.py and references/gitcode-api-spec.md |
| 2026-03-12 | Now 4 paths: forum, issue, industry, ai_reverse (was 3) |
| 2026-03-16 | Removed Path 4 (ai_reverse): circular reasoning risk, replaced by real data sources only |
| 2026-03-16 | Fixed forum fetch endpoint to /l/top.json (views-sorted) instead of latest activity |
| 2026-03-16 | Removed QUESTION_CATEGORY_IDS filter: all forum content types now included |
| 2026-03-16 | Added SKILL_DIR variable to SKILL.md Step 1 to fix script path resolution |
| 2026-03-16 | Added GitCode token pre-validation (curl) before running fetch-repo-issues.py |
| 2026-03-12 | Scoring design agreed: two-layer (content completeness + citation accuracy), 5 phenomena (A-E) |
| 2026-03-12 | official_urls = human pre-labeled, citation ratio = source-level, human spot-check 20% |
| 2026-03-12 | Issue auto-creation = separate skill (issue-creator), not inside scoring-engine |
| 2026-03-12 | Pipeline expanded to 4 steps: get-question → platform-sampler → scoring-engine → issue-creator |
| 2026-03-12 | Ran scoring-engine on Q1,Q4,Q5,Q7,Q9,Q10 (28 pairs). Output: scoring-results.json + suggestions.md |
| 2026-03-13 | Created GEO-Improvement-Report-Q8-Q10.md: analyzed Q8-Q10 against official FAQ sources, identified P0 issues |
| 2026-03-13 | Created GEO-Improvement-Report-Q4-Q7.md: analyzed Q4-Q7 (activities, contribution, PyTorch migration, v2.8.0 features) |
| 2026-03-13 | Created GEO-Improvement-Report-Q1-Q3.md: analyzed Q1-Q3 (install, version cadence, data sharding), completed full Q1-Q10 analysis |
| 2026-03-17 | Added maillist path (Path 3) to get-question: fetches SIG data from mindspore.cn/sig via official APIs |
| 2026-03-24 | Added website search keyword path (Path 4) to get-question: calls official website's internal search hot-words API, filtered by navigation/brand terms, LLM rewrites to natural language questions. Industry shifted to Path 5. Now 5 paths total. |
| 2026-03-17 | Created fetch-sig-info.py: Step 1 MagicAPI→SIG mailing lists, Step 2 HyperKitty API→email archives |
| 2026-03-17 | Discovered mindspore.cn/sig data sources: MagicAPI, Meeting API, HyperKitty (Mailman 3), Etherpad, OBS |
| 2026-03-17 | get-question now 9 steps (was 8), 4 paths: forum, issue, maillist, industry |
| 2026-03-26 | responses.json repaired twice: fixed raw text blocks for q_037 (lines 711-856) and q_032 (lines 626-935), now 53 total entries |
| 2026-03-26 | Added multi-platform data: q_032 now has 4 entries (qwen/kimi/doubao/chatgpt), q_037 has 4 entries |
| 2026-03-26 | Added s_011 to issues-draft.md: SIG page discoverability (C-type, P0), cross-platform meeting time inconsistency |
| 2026-03-26 | Updated issue-creator SKILL.md: community/version_label inputs, richer LLM prompt, ASCII causal chain, cross-platform table |
| 2026-03-26 | Updated issue-creator issue-template.md: matches real-world issue.md format (phenomenon_type, causal_chain, action_items) |
| 2026-03-28 | Created AGENT.md: 5-step workflow orchestrator (init → sample → score → issue create/update → tracking log), versioned runs/ storage, issue-map.json for dedup, OpenClaw compatible |
| 2026-03-28 | Updated issue-creator SKILL.md: added Steps 4-7 (issue-map matching, create new, comment existing, save map), new inputs issue_map_file/run_date |
| 2026-03-28 | Created comment-issue.py: appends comments to existing GitHub/GitCode Issues (supports both platforms, dry-run mode) |
| 2026-03-28 | Created scripts/generate-tracking-entry.py: compares two scoring-results.json, outputs Markdown tracking log entry with overview, changes table, issue activity |
| 2026-03-28 | Updated gitcode-api-spec.md: added issue comment API endpoint documentation |
| 2026-03-28 | Created WORKFLOW.md: operator guide covering prerequisites, first run, periodic re-check, directory structure, file reference, OpenClaw integration, FAQ |
| 2026-03-28 | Updated README.md: added link to WORKFLOW.md |
| 2026-03-28 | Severity priority remapping: B→P0, C→P0, E→P1, A→P2 (was A→P0, B→P1). Updated WORKFLOW.md, scoring-engine SKILL.md (Steps 2+6), suggestion-rules.md, CLAUDE-RESUME.md |
| 2026-03-28 | accuracy_score hidden from output: remains internal for D-type severity判定, removed from scoring-results.json and suggestion objects |
| 2026-03-28 | Added assessment-tracker.md: question-level priority & suggestion tracking table, updated per workflow run. AGENT.md now 7 steps (was 6), new Step 3 before issue creation |
| 2026-03-28 | Created scripts/update-tracker.py: parses existing tracker, appends new rows, regroups by priority, marks digested suggestions |
| 2026-03-28 | Fixed directory typo: `asssessments` → `assessments`. All paths now use `assessments/{community}/` |
| 2026-03-28 | Created `.env.example` with 6 API key placeholders |
| 2026-03-28 | Updated README.md, AGENT.md, CLAUDE-RESUME.md to match actual directory structure. Removed references to non-existent files (VERSION, CHANGELOG.md, WORKFLOW.md, INPUT.md) |
| 2026-03-30 | Removed `approved-questions.json`: `questions.json` is now source of truth. AGENT.md Step 0 detects changes and requires `accept_question_update=true` to proceed. |
| 2026-03-30 | AGENT.md: added `steps` param (select steps by number or name), `scope` param (`all`/`p0`/IDs), `accept_question_update` param. Added `update_questions` special step. Each step now has a name label. |
| 2026-03-30 | Removed `suggestions.md` output from scoring-engine and all workflow docs. Removed 人工抽检评分 step from first-run flow. Scoring output is `scoring-results.json` only. |
| 2026-03-30 | scoring-engine rewritten: pure URL string matching (exact + domain), no LLM. Three statuses replace A-E phenomena: `引用了官方内容`(OK), `有内容未被引用`(P0), `官方内容缺失`(P1). 5 steps down from 8. |
| 2026-03-30 | issue-creator updated: citation_type→status, A-E→new statuses in LLM prompt; citation_rate shown in issue body and comments; issue-map match key is question_ids only; to_resolve list for satisfied questions; Step 6 adds content-labels.json update prompt for no_official_content questions. |
| 2026-03-30 | Removed assessment-tracker.md and tracking-log.md from workflow. AGENT.md steps reduced from 7 to 5 (removed tracker Step 3 and log Step 5, renumbered). Issue history now lives in GitCode/GitHub Issue comments only. |
| 2026-03-30 | Created assessment-report skill: 6-step procedure, generates assessment-report.json + assessment-report.md per run. Grouped by phenomenon (no_official_content/not_cited/satisfied) with per-platform ✅/❌/— indicators and Issue metadata. Integrated into AGENT.md as Step 4 (report). |
| 2026-03-30 | Added Gemini to platform-sampler. All platform BASE_URL + API_KEY now in .env. Script auto-loads .env, removed --api-key/--base-url CLI args. |
| 2026-03-30 | Removed Path 5 (Industry) from get-question. |
| 2026-03-30 | platform-sampler: added `community` param, removed `questions_file`/`output_dir`. Paths auto-resolved from community dir. |
| 2026-03-30 | Merged content-labels.json into questions.json. questions.json is now single source of truth with official_urls/notes/official_domains. content-labels.json no longer used. AGENT.md, scoring-engine, issue-creator, assessment-report all updated to read from questions.json. MindSpore questions.json migrated to new object format with all official_urls merged in. |

## Key Decisions

- Architecture is skill chain + AGENT.md, NOT web app (FastAPI/frontend deferred to Phase 3)
- Target community: MindSpore (AI computing framework, competitors: TensorFlow/PyTorch/PaddlePaddle/JAX)
- Data format: JSON between skills, Markdown for human review
- Manual questions: write in `manual-questions.md` (Markdown), skill auto-converts to JSON
- Community data path: `assessments/{community}/` (e.g. `assessments/MindSpore/`)
- `approved-questions.json` removed: `questions.json` is the source of truth. AGENT.md Step 0 diffs against the last run's snapshot; if changed, aborts unless `accept_question_update=true` is set.
- AGENT.md supports `steps` (select which steps to run), `scope` (which questions to sample: `all`/`p0`/IDs), `accept_question_update` parameters.
- New skills must use `/skill-creator` and conform to agentskills.io spec
- MVP platforms (5): ChatGPT + DeepSeek + 豆包 + Qwen + Gemini
- API tokens stored in `.env`, template in `.env.example`
- Forum (Discourse API) is primary question source; all 4 paths selectable via `paths` param (forum, issue, maillist, website)
- Path 4 (AI reverse extraction) permanently removed — circular reasoning risk; real data only
- Forum includes all content types (not filtered by category type); views = relevance signal
- Forum URL: https://discuss.mindspore.cn/ (Discourse, public API, no auth needed)
- MVP question count: 30-40 (adjustable)
- No official doc directory as data source for now
- Pipeline is 4 execution steps: get-question → platform-sampler → scoring-engine → issue-creator
- Scoring uses two-layer model: Layer 1 = content completeness (human pre-labeled), Layer 2 = citation accuracy (LLM)
- Three statuses: `引用了官方内容` (OK), `有内容未被引用` (P0), `官方内容缺失` (P1) — replaces old A-E phenomenon codes
- `official_urls` per question is human pre-labeled directly in `questions.json` (empty array = no official content). `content-labels.json` is retired.
- Scoring is pure URL string matching (exact + domain-level), no LLM, no human spot-check
- Issue auto-creation is a separate skill (issue-creator), uses same GITCODE_TOKEN
- assessment-report skill generates per-question report (JSON + Markdown) after issue-creator; groups by phenomenon category with per-platform indicators (✅/❌/—) and Issue URL + iteration count
