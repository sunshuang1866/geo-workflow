# AGENT.md — GEO Search Assessment Workflow

This file orchestrates the full GEO assessment pipeline. It is designed for both manual invocation via Claude Code and future automated triggering via OpenClaw.

## Inputs (caller must provide)

| Input | Required | Description |
|-------|----------|-------------|
| `community_dir` | Yes | Path to community directory, e.g. `packages/assessments/MindSpore/` |
| `repo_url` | Yes | Target repo for issue creation, e.g. `https://gitcode.com/mindspore/mindspore-portal/` |
| `version_label` | No | Round label, e.g. `V4`. Default: auto-increment from latest `runs/` subdirectory |
| `dry_run` | No | If `true`, skip actual issue creation. Default: `false` |

## Prerequisites (must exist before running)

| File | Location | Description |
|------|----------|-------------|
| `approved-questions.json` | `{community_dir}/` | Manually curated and frozen question set |
| `content-labels.json` | `{community_dir}/` | Human pre-labeled content existence per question |
| `.env` | project root | API tokens for platforms and issue creation |

## Workflow

### Step 0: Initialize Run Directory

1. Determine today's date as `YYYY-MM-DD` (e.g. `2026-03-28`).
2. Create `{community_dir}/runs/{date}/` directory.
3. Copy `{community_dir}/approved-questions.json` to `{community_dir}/runs/{date}/questions.json`.
4. Copy `{community_dir}/content-labels.json` to `{community_dir}/runs/{date}/content-labels.json`.
5. If `version_label` is not provided, derive it: count existing `runs/` subdirectories + 1, format as `V{n}`.
6. Record run metadata:
   ```json
   {
     "run_date": "2026-03-28",
     "version_label": "V4",
     "community_dir": "packages/assessments/MindSpore/",
     "repo_url": "https://gitcode.com/mindspore/mindspore-portal/",
     "dry_run": false,
     "started_at": "2026-03-28T10:00:00Z"
   }
   ```
   Write to `{community_dir}/runs/{date}/run-meta.json`.

### Step 1: Platform Sampling

1. Invoke `/platform-sampler` with:
   - `questions.json` path: `{community_dir}/runs/{date}/questions.json`
   - Output directory: `{community_dir}/runs/{date}/`
2. The skill reads `.env` for platform API tokens, samples all available platforms, and produces:
   - `{community_dir}/runs/{date}/responses.json`
   - `{community_dir}/runs/{date}/responses.md`
3. If a platform API fails, the skill logs the error and continues. Check `responses.md` coverage matrix for gaps.
4. Verify output: `responses.json` must exist and contain at least 1 response per question.

### Step 2: Scoring

1. Invoke `/scoring-engine` with:
   - `responses.json` path: `{community_dir}/runs/{date}/responses.json`
   - `content-labels.json` path: `{community_dir}/runs/{date}/content-labels.json`
   - Output directory: `{community_dir}/runs/{date}/`
2. If `{community_dir}/runs/{date}/scoring-calibration.md` exists (from prior human review), it is automatically picked up as prompt context.
3. The skill produces:
   - `{community_dir}/runs/{date}/scoring-results.json`
   - `{community_dir}/runs/{date}/suggestions.md`
4. Verify output: `scoring-results.json` must exist and contain `results` array.

### Step 3: Update Assessment Tracker

Update the question-level tracking table that records priority and suggestion history across runs.

1. Read `{community_dir}/assessment-tracker.md` (create with header if not exists).
2. Read `{community_dir}/runs/{date}/scoring-results.json` for this run's results and suggestions.
3. Read `{community_dir}/issue-map.json` (if exists) for issue associations.
4. Update the tracker with this run's data:
   - Input: `{community_dir}/runs/{date}/scoring-results.json`
   - Tracker: `{community_dir}/assessment-tracker.md`
   - Issue map: `{community_dir}/issue-map.json` (if exists)
   - Version: `{version_label}`, Date: `{date}`
5. The update logic:
   - For each question, determines the current highest priority across all platforms.
   - Appends a new row under each question's table with this run's data.
   - Compares with the previous row to compute trend: `↑` (priority lowered/improved), `→` (unchanged), `↓` (priority raised/worsened), `NEW` (first appearance).
   - Marks suggestions from the previous row that no longer appear as `✅已消化`.
   - Moves questions between priority sections if their current priority changed.
   - Maps phenomenon letters to Chinese labels: A→官网无内容, B→有内容未引用, C→引用错误信息, D→引用正确, E→官网引用比例低.
6. Write the updated `assessment-tracker.md` back to `{community_dir}/`.

### Step 4: Issue Creation / Update

This step uses `{community_dir}/issue-map.json` to determine whether to create new issues or append comments to existing ones.

1. Read `{community_dir}/issue-map.json` (create empty `{"issues": {}}` if not exists).
2. Read `{community_dir}/runs/{date}/scoring-results.json` and extract suggestions.
3. For each suggestion group:
   - **Match key**: Use `suggestion_id` or the combination of `question_ids` + `citation_type` to look up in `issue-map.json`.
   - **If match found** (issue already exists):
     - The issue is still relevant: append a **comment** to the existing issue via API with this run's updated scoring data (score change, current status, date).
     - Comment format:
       ```
       ## GEO 复检更新 — {date}

       **版本**: {version_label}
       **评分变化**: {old_score} → {new_score}
       **严重级别**: {old_severity} → {new_severity}
       **影响平台**: {platforms}

       ### 本次发现
       {brief_findings}

       ---
       > 此评论由 GEO Search Assessment 系统自动生成
       ```
     - If the issue was previously P0 and is now OK/P2, add a note suggesting the issue may be ready to close.
   - **If no match** (new issue):
     - Invoke `/issue-creator` with:
       - `input_file`: `{community_dir}/runs/{date}/scoring-results.json`
       - `repo_url`: from caller input
       - `community`: derived from `community_dir` name
       - `version_label`: from Step 0
       - `dry_run`: from caller input
     - After creation, update `issue-map.json` with the new mapping:
       ```json
       {
         "issues": {
           "s_001": {
             "issue_url": "https://gitcode.com/.../issues/45",
             "issue_number": 45,
             "question_ids": ["q_036", "q_037"],
             "citation_types": ["C"],
             "created_at": "2026-03-28",
             "created_in_run": "2026-03-28",
             "last_updated_run": "2026-03-28"
           }
         }
       }
       ```
4. Write updated `issue-map.json` back to `{community_dir}/`.
5. Record issue activity in `run-meta.json`: issues created count, comments added count.

### Step 5: Update Tracking Log

1. Read `{community_dir}/tracking-log.md` (create with header if not exists).
2. Read `{community_dir}/runs/{date}/scoring-results.json` for this run's data.
3. If a previous run exists (latest `runs/` directory before today), read its `scoring-results.json` for comparison.
4. Generate a new section and **prepend** it (newest first) to `tracking-log.md`:

   ```markdown
   ## {date} ({version_label})

   ### Overview
   - Questions: {n}, Platforms: {n}, Avg Score: {avg}/10
   - P0: {n}, P1: {n}, P2: {n}, OK: {n}
   - Platforms sampled: {platform_list}

   ### Changes from Previous Run ({prev_date})
   | Suggestion | Previous | Current | Change |
   |------------|----------|---------|--------|
   | s_001: ... | P0 (3.2) | P1 (5.8) | Improved |
   | s_012: ... | — | P0 (2.1) | New |

   ### Issues Activity
   - Created: {n} new issues
   - Updated: {n} existing issues with comments
   - Potentially resolved: {n} (score improved to OK)

   ### Issue Details
   | Issue | Action | Title |
   |-------|--------|-------|
   | #45 | New | [MindSpore][V4]: ... |
   | #12 | Comment | Score improved P0→P1 |

   ---
   ```

5. If no previous run exists, omit the "Changes from Previous Run" section.

### Step 6: Finalize

1. Update `run-meta.json` with completion data:
   ```json
   {
     "completed_at": "2026-03-28T10:15:00Z",
     "status": "success",
     "summary": {
       "questions": 47,
       "platforms": 4,
       "avg_score": 6.2,
       "p0": 20, "p1": 8, "p2": 3, "ok": 16,
       "issues_created": 3,
       "issues_updated": 7
     }
   }
   ```
2. Print final summary to stdout:
   ```
   GEO Assessment Run Complete
   ===========================
   Community: {community}
   Version: {version_label}
   Date: {date}
   Duration: {duration}

   Scoring: {scored}/{total} pairs
     P0: {p0} | P1: {p1} | P2: {p2} | OK: {ok}
     Avg score: {avg}/10

   Issues: {created} created, {updated} updated

   Outputs:
     {community_dir}/runs/{date}/scoring-results.json
     {community_dir}/runs/{date}/suggestions.md
     {community_dir}/assessment-tracker.md
     {community_dir}/tracking-log.md
     {community_dir}/issue-map.json
   ```

## Directory Structure

After multiple runs, the community directory looks like:

```
packages/assessments/MindSpore/
  approved-questions.json       <- frozen question set (manually maintained)
  content-labels.json           <- frozen labels (manually maintained)
  issue-map.json                <- cumulative issue mapping (auto-maintained)
  assessment-tracker.md         <- question-level priority & suggestion history (auto-maintained)
  tracking-log.md               <- cumulative run log (auto-maintained, newest first)
  questions.json                <- original question set (from get-question)
  questions.md                  <- human-readable questions
  runs/
    2026-03-28/
      questions.json            <- copy of approved-questions.json for this run
      content-labels.json       <- copy of content-labels.json for this run
      responses.json            <- platform sampling output
      responses.md              <- human-readable responses
      scoring-results.json      <- scoring output
      suggestions.md            <- improvement suggestions
      run-meta.json             <- run metadata and summary
    2026-04-04/
      ...
```

## Error Handling

- If `approved-questions.json` is missing, abort: `"approved-questions.json not found in {community_dir}/. Create it manually or run /get-question first."`
- If `content-labels.json` is missing, abort: `"content-labels.json not found in {community_dir}/. Human labeling required."`
- If `.env` is missing or has fewer than 2 platform tokens, abort with token check details.
- If platform-sampler produces zero responses, abort before scoring.
- If scoring-engine fails (>50% pairs failed), abort before issue creation.
- If issue creation API fails, log errors but do not abort — tracking log is still updated.
- Each step validates the previous step's output before proceeding.

## OpenClaw Compatibility

This workflow is designed to be triggered by OpenClaw as a single agent invocation:

```
openclaw trigger \
  --agent "AGENT.md" \
  --inputs '{"community_dir": "packages/assessments/MindSpore/", "repo_url": "https://gitcode.com/mindspore/mindspore-portal/"}' \
  --schedule "0 9 * * 1"  # Every Monday at 9:00 AM
```

Requirements for automated execution:
- All inputs (`approved-questions.json`, `content-labels.json`, `.env`) must be pre-provisioned
- `dry_run` defaults to `false` in automated mode
- `version_label` auto-increments
- `issue-map.json` and `tracking-log.md` are persistent across runs
- No human-in-the-loop steps — all checkpoints (question review, content labeling, spot-check) are handled offline between scheduled runs
