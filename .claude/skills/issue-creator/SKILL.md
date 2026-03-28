---
name: issue-creator
description: Creates or updates GitHub/GitCode Issues from GEO scoring results. Reads scoring-results.json and issue-map.json to decide whether to create new Issues or append comments to existing ones. Maps each improvement item to a structured Issue (title, labels, body with phenomenon code and affected platforms), creates via API or appends a review-update comment. Auto-detects platform from repo URL. Requires GITHUB_TOKEN or GITCODE_TOKEN. Use after scoring-engine completes. Do not use for question generation, platform sampling, or scoring.
---

# Issue Creator

Create or update GitHub/GitCode Issues from GEO improvement suggestions. New suggestions become new Issues; existing suggestions get a comment appended to their existing Issue with updated scoring data.

## Prerequisites

- `.env` file with:
  - `GITHUB_TOKEN` — GitHub Personal Access Token with `issues:write` scope (for GitHub repos)
  - `GITCODE_TOKEN` — GitCode personal access token with `read_projects` + `write_issues` scopes (for GitCode repos)
- `scoring-results.json` (output from scoring-engine skill)
- `content-labels.json` in the same directory (used to enrich root-cause analysis)
- Human review of scoring results completed

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root.
2. Accept required and optional inputs from the caller:
   - `repo_url` (required): Full repository URL, e.g. `https://github.com/opensourceways/portal-mcp-servers` or `https://gitcode.com/mindspore/mindspore-portal/`
   - `input_file` (optional): Path to scoring results. Default: `scoring-results.json`
   - `issue_map_file` (optional): Path to issue-map.json. Default: `{community_dir}/issue-map.json` (same parent as `input_file`'s grandparent, or project root)
   - `community` (optional): Community name for the Issue title prefix, e.g. `MindSpore`. Default: auto-read from `scoring-results.json` metadata field `community`, or inferred from the `input_file` path.
   - `version_label` (optional): Assessment round label for the title prefix, e.g. `V2`. Default: derived from the `input_file` directory name (e.g. `version3` → `V3`).
   - `run_date` (optional): Current run date for comment headers. Default: today's date `YYYY-MM-DD`.
   - `dry_run` (optional): If `true`, generate Issue payloads but do not POST to API. Default: `false`
3. **Auto-detect platform** from `repo_url`:
   - URL contains `github.com` → platform = `github`, load `GITHUB_TOKEN`
   - URL contains `gitcode.com` → platform = `gitcode`, load `GITCODE_TOKEN`
   - Extract `owner` and `repo` from the URL path.
4. If the required token is missing or empty, abort:
   - GitHub: `"GITHUB_TOKEN not set. Cannot create Issues."`
   - GitCode: `"GITCODE_TOKEN not set. Cannot create Issues."`
5. Read `references/gitcode-api-spec.md` for API endpoint details.
6. Read `issue_map_file`. If it does not exist, initialize as `{"issues": {}}`. This map tracks which suggestions already have Issues.

**Step 2: Parse Scoring Results**

1. Read the `input_file` (default: `scoring-results.json`).
2. Also read `content-labels.json` from the same directory if it exists — its `notes` and `official_urls` fields enrich root-cause analysis.
3. Run `python3 scripts/parse-suggestions.py {input_file}` to extract actionable items.
4. The script outputs a JSON array of suggestion objects to stdout:
   ```json
   [
     {
       "suggestion_id": "s_001",
       "question_id": "q_001",
       "question": "MindSpore 支持哪些安装方式？",
       "citation_type": "B",
       "severity": "P1",
       "affected_platforms": ["ChatGPT", "DeepSeek"],
       "suggestion_text": "...",
       "category": "seo"
     }
   ]
   ```
5. If the file is missing or the script fails, abort with a clear error.

**Step 3: Deduplicate, Group, and Enrich**

1. Prompt the LLM to deduplicate, group, and generate rich diagnostic content per group:

   ```
   You are a GEO (Generative Engine Optimization) analyst. The following are improvement
   suggestions extracted from AI platform scoring results for the {community} open-source community.

   Also provided: content-labels.json entries for context (official_urls and notes fields).

   Your tasks:
   A. Group semantically similar suggestions that target the same root cause.
      - Merge suggestions that recommend the same action across multiple platforms/questions.
      - Keep the highest severity when merging (P0 > P1 > P2).
      - Combine affected_platforms lists and preserve all question_ids.
      - Each group becomes one Issue.

   B. For each group, generate the following diagnostic content:

   phenomenon_type: A one-line label for the citation failure pattern. Use one of:
     - "内容空白 — 官方站点无相关页面"                          (type A)
     - "引用缺失 — 内容已存在但未被任何平台引用"                (type B)
     - "引用源错误 — 官方内容已存在但被错误来源替代"            (type C)
     - "引用比例低 — 第三方来源主导，官方引用不足"              (type E)

   content_judgment: A ⚠️ or ✅ prefixed one-line judgment. Use:
     - "✅ 内容源问题（建议创建官方页面）"                       (type A)
     - "⚠️ 非内容缺失问题，需修复 **SEO 可发现性** 或内链密度"  (type B)
     - "⚠️ 非内容缺失问题（内容已存在于官方页面，但被错误来源覆盖），需修复**可发现性/内链**"  (type C)
     - "✅ 内容源问题（建议深化官方文档，减少对第三方来源的依赖）"  (type E)

   phenomenon_detail: 2–4 sentences describing what was observed across platforms, naming
     the specific questions and the wrong sources that were cited. Reference official_urls
     from content-labels.json where relevant.

   causal_chain: A compact ASCII diagram of the root cause chain (3–5 steps), using the
     format:
       [正确信源/缺失根因]
           ↓ [原因]
           ↓ [传导]
           ↓ [最终表现]

   root_cause_bullets: 2–4 numbered technical reasons for the failure. Be specific —
     name actual URLs, file paths, or platform behaviors where known.

   cross_platform_section: If multiple platforms are involved with conflicting answers,
     generate a Markdown section:
       ### 跨平台不一致性\n\n| 平台 | [关键维度] | 引用来源 | 准确性 |\n|------|...
     with one row per platform+run. If only one platform is affected, return an empty string "".

   action_items: 2–4 concrete improvement measures in the format:
       **措施 N — [measure title]**\n\n[measure body with specific file paths, URLs, or code snippets]
     Order from highest to lowest impact.

   reference_urls: A short bullet list of the correct official sources, formatted as:
       - **正确官方来源**: `{url}`
       - **相关评分结果**: `{scoring-results-file-path}`

   Scoring results:
   {suggestions_json}

   Content labels (excerpt):
   {content_labels_json}

   Output as a JSON array. Each element:
   {
     "group_id": "g_001",
     "title_summary": "...",
     "severity": "P0",
     "citation_types": ["C"],
     "phenomenon_type": "...",
     "content_judgment": "...",
     "affected_platforms": ["qwen", "chatgpt"],
     "question_ids": ["q_036", "q_037"],
     "phenomenon_detail": "...",
     "causal_chain": "...",
     "root_cause_bullets": "1. ...\n2. ...",
     "cross_platform_section": "### 跨平台不一致性\n\n| ...",
     "action_items": "**措施 1 — ...**\n\n...",
     "reference_urls": "- **正确官方来源**: `url`\n- **相关评分结果**: `path`",
     "category": "seo"
   }
   ```
2. Collect the grouped and enriched suggestions.

**Step 4: Match Against Issue Map**

1. For each grouped suggestion from Step 3, determine if an existing Issue already covers it:
   - **Match key**: Look up each `suggestion_id` or the combination of `question_ids` + `citation_types` in `issue-map.json`.
   - A match is found when: (a) the `suggestion_id` exists as a key in `issue-map.json.issues`, OR (b) there is an entry whose `question_ids` overlap by ≥50% AND shares at least one `citation_type`.
2. Partition grouped suggestions into two lists:
   - `to_create`: No match in issue-map — these need new Issues.
   - `to_update`: Match found — these need a comment appended to the existing Issue.
3. Print partition summary:
   ```
   Issue map check:
     New suggestions (to create): {n}
     Existing suggestions (to update): {n}
   ```

**Step 5: Create New Issues**

For each suggestion in `to_create`:

1. Construct an Issue payload:
   - **Title**: `[{community}][{version_label}]: {title_summary}`
     - Example: `[MindSpore][V3]: 提升 SIG 专项页面可发现性：mindspore.cn/sig/* 未被AI平台引用`
   - **Labels**: `geo-improvement`, `{severity}`, `{category}`
   - **Body**: Read `assets/issue-template.md` and substitute:
     - `{phenomenon_type}` → group.phenomenon_type
     - `{affected_platforms}` → group.affected_platforms joined with "、"
     - `{content_judgment}` → group.content_judgment
     - `{question_list}` → each question_id as `- \`{id}\` {question_text}`
     - `{phenomenon_detail}` → group.phenomenon_detail
     - `{cross_platform_section}` → group.cross_platform_section (empty string removed)
     - `{causal_chain}` → group.causal_chain
     - `{root_cause_bullets}` → group.root_cause_bullets
     - `{action_items}` → group.action_items
     - `{reference_urls}` → group.reference_urls

2. Run `python3 scripts/create-issue.py --owner {owner} --repo {repo} --platform {github|gitcode} --payload '{json}' [--dry-run]` for each Issue.
3. The script behavior:
   - **GitHub**: POSTs to `api.github.com/repos/{owner}/{repo}/issues`; auth via `Authorization: Bearer {token}`; labels as JSON array.
   - **GitCode**: POSTs to `api.gitcode.com/api/v5/repos/{owner}/{repo}/issues`; auth via `access_token` body field; labels as comma-separated string.
   - **Label fallback**: If the API returns 403 or 422 due to non-existent labels, automatically retry the same request **without labels**. Log a warning: `"Labels not applied (insufficient permission or labels not found). Issue created without labels."`
   - **Dry-run**: Prints the payload to stdout without calling the API.
4. After successful creation, add the new Issue to `issue-map.json`:
   ```json
   {
     "suggestion_id": {
       "issue_url": "https://gitcode.com/.../issues/45",
       "issue_number": 45,
       "question_ids": ["q_036", "q_037"],
       "citation_types": ["C"],
       "severity": "P0",
       "title_summary": "...",
       "created_at": "2026-03-28",
       "created_in_run": "2026-03-28",
       "last_updated_run": "2026-03-28"
     }
   }
   ```

**Step 6: Update Existing Issues with Comments**

For each suggestion in `to_update`:

1. Look up the matched entry in `issue-map.json` to get `issue_number` and `issue_url`.
2. Compare this run's scoring data against the previous data stored in issue-map:
   - `old_severity` → from issue-map entry's `severity`
   - `new_severity` → from this run's grouped suggestion
3. Construct the comment body:
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
   | 引用类型 | {old_citation_types} | {new_citation_types} |
   | 影响平台 | {old_platforms} | {new_platforms} |

   {resolution_note}

   ---
   > 此评论由 GEO Search Assessment 系统自动生成（{version_label}）
   ```
   - `{resolution_note}`: If `old_severity` was P0/P1 and `new_severity` is now OK or P2, add: `> **建议关闭**: 该问题在本次复检中已明显改善，可考虑关闭此 Issue。`
4. Run `python3 scripts/comment-issue.py --owner {owner} --repo {repo} --platform {github|gitcode} --issue-number {number} --body '{comment_body}' [--dry-run]`.
5. After successful comment, update `issue-map.json`:
   - Set `last_updated_run` to `{run_date}`
   - Update `severity` to the new value
   - Update `citation_types` to current values

**Step 7: Save Issue Map and Output Summary**

1. Write the updated `issue-map.json` back to `issue_map_file`.
2. Write `created-issues.json` to the same directory as `input_file`:
   ```json
   {
     "created_at": "2026-03-28T...",
     "mode": "live",
     "repo": "gitcode.com/mindspore/mindspore",
     "community": "MindSpore",
     "version_label": "V4",
     "issues_created": [
       {
         "group_id": "g_001",
         "severity": "P0",
         "title": "[MindSpore][V4]: ...",
         "url": "https://gitcode.com/.../issues/45",
         "number": 45,
         "question_ids": ["q_036", "q_037"],
         "labels_applied": false
       }
     ],
     "issues_updated": [
       {
         "group_id": "g_003",
         "issue_url": "https://gitcode.com/.../issues/12",
         "issue_number": 12,
         "old_severity": "P0",
         "new_severity": "P1",
         "action": "comment_added"
       }
     ]
   }
   ```
3. Print a summary to stdout:
   ```
   Issue activity:
     Community: {community} [{version_label}]
     New Issues created: {created_count}
     Existing Issues updated: {updated_count}
       - P0: {p0_count} | P1: {p1_count} | P2: {p2_count}
     Potentially resolved: {resolved_count}
     Labels applied: {yes|no}
     Mode: {live|dry-run}
   Output: {output_path}/created-issues.json
   Updated: {issue_map_file}
   ```

## Error Handling

* If the required token is missing, abort immediately.
* If `input_file` is missing, abort with: `"File not found. Run scoring-engine skill first."`
* If `issue_map_file` is missing, initialize as `{"issues": {}}` and proceed (first run scenario).
* If `content-labels.json` is missing, continue without it — root-cause analysis will be less specific. Log: `"content-labels.json not found. Root-cause enrichment skipped."`
* If `parse-suggestions.py` returns zero actionable items, print `"No actionable suggestions found. All scores are healthy."` and exit cleanly.
* If `create-issue.py` fails for a specific Issue after label fallback (HTTP error other than label-related 403/422), log the error and continue with remaining Issues. Report failed Issues in the summary.
* If `comment-issue.py` fails for a specific comment (e.g. issue was closed/deleted), log the error and continue. Do NOT abort.
* If labels fail (HTTP 403/422 on label fields), retry **without labels** and log a warning. Do NOT abort.
* In dry-run mode, no API calls are made — all payloads are printed to stdout for review.
* Always write `issue-map.json` at the end, even if some operations failed — partial updates are better than losing all mappings.
