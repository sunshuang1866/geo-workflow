---
name: issue-creator
description: Creates or updates GitHub/GitCode Issues from GEO scoring results. Reads scoring-results.json and issue-map.json to decide whether to create new Issues or append comments to existing ones. Maps each improvement item to a structured Issue using LLM-enriched diagnostic content (phenomenon detail, causal chain, action items). Displays citation_rate as additional context. Auto-detects platform from repo URL. Requires GITHUB_TOKEN or GITCODE_TOKEN. Use after scoring-engine completes. Do not use for question generation, platform sampling, or scoring.
---

# Issue Creator

Create or update GitHub/GitCode Issues from GEO improvement suggestions. New suggestions become new Issues; existing suggestions get a comment appended to their existing Issue with updated scoring data and citation rate.

## Prerequisites

- `.env` file with:
  - `GITHUB_TOKEN` — GitHub Personal Access Token with `issues:write` scope (for GitHub repos)
  - `GITCODE_TOKEN` — GitCode personal access token with `read_projects` + `write_issues` scopes (for GitCode repos)
- `scoring-results.json` (output from scoring-engine skill)
- `questions.json` in `output/{community}/` (used to enrich root-cause analysis with `official_urls` and `notes`)
- Human review of scoring results completed

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root.
2. Accept required and optional inputs from the caller:
   - `repo_url` (optional): Full repository URL. Default: `GEO_REPO_URL` from `.env`. Abort if still unresolved: `"repo_url not set. Provide as argument or set GEO_REPO_URL in .env."`
   - `input_file` (optional): Path to scoring results. Default: `scoring-results.json`
   - `issue_map_file` (optional): Path to issue-map.json. Default: `{community_dir}/issue-map.json`
   - `community` (optional): Community name for the Issue title prefix, e.g. `MindSpore`. Default: auto-read from `scoring-results.json` metadata field `community`, or inferred from the `input_file` path.
   - `version_label` (optional): Assessment round label, e.g. `V2`. Default: derived from the `input_file` directory name.
   - `run_date` (optional): Current run date for comment headers. Default: today's date `YYYY-MM-DD`.
   - `dry_run` (optional): If `true`, generate Issue payloads but do not POST to API. Default: `GEO_DRY_RUN` from `.env` → `false`
3. **Auto-detect platform** from `repo_url`:
   - URL contains `github.com` → platform = `github`, load `GITHUB_TOKEN`
   - URL contains `gitcode.com` → platform = `gitcode`, load `GITCODE_TOKEN`
   - Extract `owner` and `repo` from the URL path.
4. If the required token is missing or empty, abort:
   - GitHub: `"GITHUB_TOKEN not set. Cannot create Issues."`
   - GitCode: `"GITCODE_TOKEN not set. Cannot create Issues."`
5. Read `references/gitcode-api-spec.md` for API endpoint details.
6. Read `issue_map_file`. If it does not exist, initialize as `{"issues": {}}`.

**Step 2: Parse Scoring Results**

1. Read the `input_file` (default: `scoring-results.json`).
2. Also read `questions.json` from `output/{community}/` if it exists — its `notes` and `official_urls` fields enrich root-cause analysis.
3. Run `python3 scripts/parse-suggestions.py {input_file}` to extract actionable items.
4. The script outputs a JSON array of suggestion objects to stdout — one per question with `not_cited` or `no_official_content` status:
   ```json
   [
     {
       "suggestion_id": "s_001",
       "question_id": "q_001",
       "question": "MindSpore 支持哪些安装方式？",
       "status": "not_cited",
       "description": "有内容未被引用",
       "severity": "P0",
       "citation_rate": 0.25,
       "cited_count": 1,
       "total_platforms": 4,
       "cited_platforms": ["qwen"],
       "not_cited_platforms": ["chatgpt", "deepseek", "doubao"],
       "official_urls": ["https://www.mindspore.cn/install"],
       "suggestion_text": "..."
     }
   ]
   ```
5. Questions with `satisfied` status are excluded from this list — they require no new action (but may trigger issue updates if an existing issue exists; see Step 4).
6. If the file is missing or the script fails, abort with a clear error.

**Step 3: Deduplicate, Group, and Enrich via LLM**

1. Prompt the LLM to deduplicate, group, and generate rich diagnostic content per group:

   ```
   You are a GEO (Generative Engine Optimization) analyst. The following are improvement
   suggestions extracted from AI platform scoring results for the {community} open-source community.

   Also provided: questions.json entries for context (official_urls and notes fields).

   Your tasks:
   A. Group semantically similar suggestions that target the same root cause.
      - Merge suggestions that recommend the same action across multiple questions.
      - Keep the highest severity when merging (P0 > P1).
      - Combine cited_platforms and not_cited_platforms lists; preserve all question_ids.
      - Each group becomes one Issue.

   B. For each group, generate the following diagnostic content:

   phenomenon_type: A one-line label for the citation failure pattern. Use one of:
     - "内容空白 — 官方站点无相关页面"                          (status: no_official_content)
     - "引用缺失 — 官方内容已存在但未被平台引用"                (status: not_cited)

   content_judgment: A ⚠️ or ✅ prefixed one-line judgment. Use:
     - "✅ 内容源问题（建议创建官方页面）"                                        (no_official_content)
     - "⚠️ 非内容缺失问题，需修复 **SEO 可发现性** 或内链密度"                   (not_cited, citation_rate = 0)
     - "⚠️ 部分平台已引用，但覆盖率不足 90%，需扩大 **SEO 可发现性** 覆盖范围"  (not_cited, citation_rate > 0)

   phenomenon_detail: 2–4 sentences describing what was observed. Include:
     - Which platforms cited and which did not (use cited_platforms / not_cited_platforms).
     - The current citation rate (e.g. "当前引用率 25%，仅 qwen 引用了官方链接").
     - Reference official_urls from questions.json where relevant.

   causal_chain: A compact ASCII diagram of the root cause chain (3–5 steps):
       [正确信源/缺失根因]
           ↓ [原因]
           ↓ [传导]
           ↓ [最终表现]

   root_cause_bullets: 2–4 numbered technical reasons for the failure. Be specific —
     name actual URLs, file paths, or platform behaviors where known.

   cross_platform_section: If multiple platforms are involved with conflicting citation behavior,
     generate a Markdown section:
       ### 跨平台引用情况\n\n| 平台 | 是否引用 | 引用来源 |\n|------|---------|----------|\n...
     with one row per platform. If only one platform is affected, return an empty string "".

   action_items: 2–4 concrete improvement measures in the format:
       **措施 N — [measure title]**\n\n[measure body with specific file paths, URLs, or code snippets]
     Order from highest to lowest impact.

   reference_urls: A short bullet list of the correct official sources:
       - **正确官方来源**: `{url}`
       - **相关评分结果**: `{scoring-results-file-path}`

   Scoring results:
   {suggestions_json}

   Questions with official_urls (excerpt):
   {questions_json}

   Output as a JSON array. Each element:
   {
     "group_id": "g_001",
     "title_summary": "...",
     "severity": "P0",
     "status": "not_cited",
     "citation_rate": 0.25,
     "cited_count": 1,
     "total_platforms": 4,
     "cited_platforms": ["qwen"],
     "not_cited_platforms": ["chatgpt", "deepseek", "doubao"],
     "phenomenon_type": "...",
     "content_judgment": "...",
     "affected_platforms": ["qwen", "chatgpt", "deepseek", "doubao"],
     "question_ids": ["q_001"],
     "phenomenon_detail": "...",
     "causal_chain": "...",
     "root_cause_bullets": "1. ...\n2. ...",
     "cross_platform_section": "### 跨平台引用情况\n\n| ...",
     "action_items": "**措施 1 — ...**\n\n...",
     "reference_urls": "- **正确官方来源**: `url`\n- **相关评分结果**: `path`",
     "category": "seo"
   }
   ```
2. Collect the grouped and enriched suggestions.

**Step 4: Match Against Issue Map**

1. For each grouped suggestion from Step 3, determine if an existing Issue already covers it:
   - **Match key**: Look up `question_ids` overlap in `issue-map.json`. A match is found when there is an entry whose `question_ids` overlap by ≥50%.
   - Note: `status` is intentionally excluded from the match key — a question moving from `no_official_content` to `not_cited` (official content was added) should still map to the same Issue.
2. Also check `satisfied` questions from `scoring-results.json` against `issue-map.json`. If a question is now `satisfied` and has an existing Issue entry, add it to `to_resolve` list.
3. Partition into three lists:
   - `to_create`: No match in issue-map — these need new Issues.
   - `to_update`: Match found, status is still `not_cited` or `no_official_content` — append a comment.
   - `to_resolve`: Match found, status is now `satisfied` — append a resolution comment suggesting close.
4. Print partition summary:
   ```
   Issue map check:
     New suggestions (to create):   {n}
     Existing suggestions (to update): {n}
     Resolved suggestions (to close):  {n}
   ```

**Step 5: Create New Issues**

For each suggestion in `to_create`:

1. Construct an Issue payload:
   - **Title**: `[{community}][{version_label}]: {title_summary}`
   - **Labels**: `geo-improvement`, `{severity}`, `{category}`
   - **Body**: Read `assets/issue-template.md` and substitute:
     - `{phenomenon_type}` → group.phenomenon_type
     - `{affected_platforms}` → group.affected_platforms joined with "、"
     - `{citation_rate_display}` → `{citation_rate*100:.0f}%（{cited_count}/{total_platforms} 平台引用）`
     - `{content_judgment}` → group.content_judgment
     - `{question_list}` → each question_id as `- \`{id}\` {question_text}`
     - `{phenomenon_detail}` → group.phenomenon_detail
     - `{cross_platform_section}` → group.cross_platform_section (omit section if empty string)
     - `{causal_chain}` → group.causal_chain
     - `{root_cause_bullets}` → group.root_cause_bullets
     - `{action_items}` → group.action_items
     - `{reference_urls}` → group.reference_urls

2. Run `python3 scripts/create-issue.py --owner {owner} --repo {repo} --platform {github|gitcode} --payload '{json}' [--dry-run]`.
3. The script behavior:
   - **GitHub**: POSTs to `api.github.com/repos/{owner}/{repo}/issues`.
   - **GitCode**: POSTs to `api.gitcode.com/api/v5/repos/{owner}/{repo}/issues`.
   - **Label fallback**: If API returns 403/422 due to non-existent labels, retry without labels and log a warning.
   - **Dry-run**: Prints the payload to stdout without calling the API.
4. After successful creation, add to `issue-map.json`:
   ```json
   {
     "s_001": {
       "issue_url": "https://gitcode.com/.../issues/45",
       "issue_number": 45,
       "question_ids": ["q_001"],
       "status": "not_cited",
       "severity": "P0",
       "citation_rate": 0.25,
       "title_summary": "...",
       "created_at": "2026-03-30",
       "created_in_run": "2026-03-30",
       "last_updated_run": "2026-03-30"
     }
   }
   ```

**Step 6: Update Existing Issues with Comments**

For each suggestion in `to_update`:

1. Look up the matched entry in `issue-map.json` to get `issue_number`, `old_severity`, `old_citation_rate`.
2. Construct the comment body:
   ```markdown
   ## GEO 复检更新 — {run_date}

   **版本**: {version_label}
   **严重级别**: {old_severity} → {new_severity}
   **影响平台**: {affected_platforms}

   ### 本次发现

   {phenomenon_detail}

   ### 评分变化

   | 维度 | 上次 | 本次 |
   |------|------|------|
   | 严重级别 | {old_severity} | {new_severity} |
   | 引用率 | {old_citation_rate*100:.0f}% | {new_citation_rate*100:.0f}%（{cited_count}/{total_platforms} 平台） |
   | 已引用平台 | {old_cited_platforms} | {new_cited_platforms} |
   | 未引用平台 | {old_not_cited_platforms} | {new_not_cited_platforms} |

   ---
   > 此评论由 GEO Search Assessment 系统自动生成（{version_label}）
   ```

For each suggestion in `to_resolve` (status now `satisfied`):

1. **Update the Issue title** by prepending `[已解决] ` to the existing title:
   - Fetch the current title via `GET /repos/{owner}/{repo}/issues/{number}`.
   - New title: `[已解决] {current_title}` (skip if title already starts with `[已解决]`).
   - PATCH the issue title via the API.
   - **Dry-run**: print the new title without calling the API.

2. Construct a resolution comment:
   ```markdown
   ## GEO 复检更新 — {run_date}

   **版本**: {version_label}
   **状态变化**: {old_description} → 引用了官方内容 ✅

   ### 本次发现

   当前引用率已达 {citation_rate*100:.0f}%（{cited_count}/{total_platforms} 平台引用官方链接），
   超过 90% 阈值，问题已解决。

   > **建议关闭**: 该问题在本次复检中已达标，可考虑关闭此 Issue。

   ---
   > 此评论由 GEO Search Assessment 系统自动生成（{version_label}）
   ```

3. Run `python3 scripts/comment-issue.py` for each comment.
4. After successful comment, update `issue-map.json`:
   - Set `last_updated_run` to `{run_date}`
   - Update `severity`, `status`, `citation_rate` to current values.

**Step 7: Save Issue Map and Output Summary**

1. Write the updated `issue-map.json` back to `issue_map_file`.
2. Write `created-issues.json` to the same directory as `input_file`:
   ```json
   {
     "created_at": "2026-03-30T...",
     "mode": "live",
     "repo": "gitcode.com/mindspore/mindspore",
     "community": "MindSpore",
     "version_label": "V4",
     "issues_created": [
       {
         "group_id": "g_001",
         "severity": "P0",
         "status": "not_cited",
         "citation_rate": 0.25,
         "title": "[MindSpore][V4]: ...",
         "url": "https://gitcode.com/.../issues/45",
         "number": 45,
         "question_ids": ["q_001"]
       }
     ],
     "issues_updated": [
       {
         "group_id": "g_003",
         "issue_url": "https://gitcode.com/.../issues/12",
         "issue_number": 12,
         "old_severity": "P0",
         "new_severity": "P0",
         "old_citation_rate": 0.0,
         "new_citation_rate": 0.25,
         "action": "comment_added"
       }
     ],
     "issues_resolved": [
       {
         "issue_url": "https://gitcode.com/.../issues/8",
         "issue_number": 8,
         "old_severity": "P0",
         "new_citation_rate": 1.0,
         "action": "resolution_comment_added"
       }
     ]
   }
   ```
3. Print a summary to stdout:
   ```
   Issue activity:
     Community: {community} [{version_label}]
     New Issues created:        {created_count}
     Existing Issues updated:   {updated_count}
     Resolved (suggest close):  {resolved_count}
     Mode: {live|dry-run}
   Output: {output_path}/created-issues.json
   Updated: {issue_map_file}
   ```

## Error Handling

* If the required token is missing, abort immediately.
* If `input_file` is missing, abort with: `"File not found. Run scoring-engine skill first."`
* If `issue_map_file` is missing, initialize as `{"issues": {}}` and proceed.
* If `questions.json` is missing, continue without it — root-cause analysis will be less specific. Log: `"questions.json not found. Root-cause enrichment skipped."`
* If `parse-suggestions.py` returns zero actionable items, print `"No actionable suggestions found. All scores are healthy."` and exit cleanly.
* If `create-issue.py` fails after label fallback, log the error and continue with remaining Issues.
* If `comment-issue.py` fails (e.g. issue was closed/deleted), log the error and continue.
* If labels fail (HTTP 403/422), retry without labels and log a warning.
* In dry-run mode, no API calls are made — all payloads are printed to stdout.
* Always write `issue-map.json` at the end, even if some operations failed.
