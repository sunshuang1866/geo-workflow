---
name: assessment-report
description: Generates a structured question assessment report after issue-creator completes. Reads scoring-results.json, questions.json, and issue-map.json to compile per-question records including question_id, question text, official URLs, per-platform citation status with emoji indicators, severity level, linked Issue URL, issue creation date, and iteration count. Groups questions by phenomenon category (官方内容缺失, 有内容未被引用, 引用了官方内容) and outputs both machine-readable JSON and human-readable Markdown. Use after issue-creator skill completes. Do not use for question generation, platform sampling, scoring, or issue creation.
---

# Assessment Report

Compile a structured question assessment report from scoring and issue data. Each question gets a full record: citation status per platform, severity, linked Issue, and history. Output is grouped by phenomenon category in both JSON and Markdown.

## Prerequisites

- `scoring-results.json` — output from scoring-engine
- `questions.json` — source of `official_urls` and `notes` per question (from `assessments/{community}/`)
- `issue-map.json` — Issue URL, creation date, and update history from issue-creator

## Inputs

| Param | Required | Default | Notes |
|-------|----------|---------|-------|
| `scoring_file` | no | `scoring-results.json` | Path to scoring results |
| `questions_file` | no | `assessments/{GEO_COMMUNITY}/questions.json` | Path to questions file; `{GEO_COMMUNITY}` resolved from `.env` |
| `issue_map_file` | no | `issue-map.json` | Path to issue map |
| `prev_report_file` | **yes** | — | Path to previous run's `assessment-report.json`. Pass `"none"` on first run — all questions will be marked as `new` and no trend delta is computed. |
| `output_dir` | no | same directory as `scoring_file` | Where to write output files |
| `community` | no | `GEO_COMMUNITY` from `.env`, then auto-detected from path | Community name for report header |

## Procedures

**Step 1: Load Inputs**

1. Read `scoring_file`. Extract `results` array (question-level records with `status`, `description`, `severity`, `citation_rate`, `platforms` array) and `metadata`.
2. Read `questions_file`. Build a lookup map `{id → {official_urls, notes}}`.
3. Read `issue_map_file`. Build a lookup map `{question_id → {issue_url, issue_number, created_at, last_updated_run, update_count}}`.
   - Derive `update_count` for each question: count how many entries in `issue-map.json` reference this `question_id`, or read the `last_updated_run` vs `created_at` diff as iteration count. Use the number of times `last_updated_run` has changed as the iteration count (if not tracked, default to 1 for entries that exist).
   - If `issue_map_file` does not exist, proceed with empty issue data.
4. Read `prev_report_file`. If `"none"` or the file does not exist, treat as first run: `prev_map = {}`. Otherwise parse the JSON and build `prev_map = {question_id → record}` by iterating all `categories.*.questions` arrays.
5. Run `python3 scripts/build-report.py {scoring_file} {questions_file} {issue_map_file}` to merge all three sources into a unified per-question record list. The script outputs JSON to stdout.
6. Print load summary:
   ```
   Inputs loaded:
     Questions: {n}
     Platforms: {platform_list}
     Questions with Issues: {n}
     Questions without Issues: {n}
     Previous report: {prev_report_file | "none (first run)"}
   ```

**Step 2: Build Per-Question Records**

For each question in `scoring-results.json`, construct a record. After building the base record, enrich it with trend fields by comparing against `prev_map`:

```json
{
  "question_id": "q_001",
  "question": "MindSpore 支持哪些安装方式？",
  "official_urls": ["https://www.mindspore.cn/install"],
  "severity": "P0",
  "status": "not_cited",
  "description": "有内容未被引用",
  "citation_rate": 0.25,
  "platforms": {
    "qwen":     {"cited": true,  "indicator": "✅"},
    "chatgpt":  {"cited": false, "indicator": "❌"},
    "deepseek": {"cited": false, "indicator": "❌"},
    "doubao":   {"cited": false, "indicator": "❌"}
  },
  "issue_url": "https://gitcode.com/.../issues/45",
  "issue_number": 45,
  "issue_created_at": "2026-03-30",
  "issue_iterations": 2,
  "trend": "improved",
  "prev_status": "not_cited",
  "prev_citation_rate": 0.0,
  "citation_rate_delta": 0.25
}
```

**Trend computation rules** (compare current record against `prev_map[question_id]`):

| Condition | `trend` value |
|-----------|--------------|
| `question_id` not in `prev_map` | `new` |
| current `satisfied`, prev was not | `resolved` |
| prev was `no_official_content`, current is `not_cited` | `improved` (content added) |
| `citation_rate_delta > 0` | `improved` |
| `citation_rate_delta < 0` | `regressed` |
| everything else | `stable` |

**Trend indicators** used in Markdown tables (prefix the ID cell):

| `trend` | Indicator |
|---------|-----------|
| `improved` | `↑` |
| `regressed` | `↓` |
| `stable` | `→` |
| `new` | `★` |
| `resolved` | `✓` |

Platform indicator rules (read from `references/indicator-rules.md`):
- `cited: true` → `✅`
- `cited: false`, question has official URLs → `❌`
- question has no official URLs → `—`

**Step 3: Group by Phenomenon Category**

Partition questions into three groups based on `status`:

| Group | Status | 中文分类标题 |
|-------|--------|-------------|
| `no_official_content` | `no_official_content` | 官方内容缺失 |
| `not_cited` | `not_cited` | 有内容未被引用 |
| `satisfied` | `satisfied` | 引用了官方内容 |

Within each group, sort by:
1. `severity` descending (P0 → P1 → OK)
2. `citation_rate` ascending (lowest coverage first)

**Step 3b: Sub-group P0 questions by improvement action type (multi-label)**

For the `not_cited` group, classify each question into **one or more** improvement action categories. A single question may appear in multiple action groups simultaneously.

**Improvement Action Taxonomy:**

| Action Key | 中文标题 | 适用场景 |
|------------|---------|---------|
| `optimize_structured_data` | 添加结构化数据标记 | 页面存在但缺少 Schema.org / JSON-LD 标记，AI 平台无法解析内容语义 |
| `create_dedicated_doc` | 补充专题文档页面 | 官方内容分散在新闻、Issue、邮件列表中，缺少独立的文档/教程/FAQ 页面 |
| `improve_seo_metadata` | 优化 SEO 元数据 | 页面 title/description/canonical URL 不准确或缺失，影响索引质量 |
| `submit_to_platforms` | 针对特定平台提交收录 | 多数平台已引用但个别平台漏引，需向目标平台主动提交 |
| `add_multilingual` | 添加多语言页面 | 仅有中文页面，国际化 AI 平台（ChatGPT 等）倾向引用英文源 |
| `restructure_content` | 重构内容结构与关键词 | 页面存在但内容层级混乱、关键词不匹配用户搜索意图 |

**Classification logic (multi-label):**

For each P0 question, analyze the following信号 to assign **所有适用的** action keys（不限一个）:

1. **citation_rate = 0 且 official_urls 指向非文档页面**（如 Gitee Issues 搜索页、新闻页）→ `create_dedicated_doc`；同时可加 `optimize_structured_data`
2. **citation_rate = 0 且 official_urls 指向正规文档页面** → `restructure_content`；若页面也缺少结构化标记 → 同时加 `optimize_structured_data`
3. **citation_rate > 0 且仅 1 个平台未命中** → `submit_to_platforms`；若未命中平台为 ChatGPT 等国际平台 → 同时加 `add_multilingual`
4. **citation_rate > 0 且多个平台未命中** → `improve_seo_metadata`；若页面结构也有问题 → 同时加 `restructure_content` 或 `optimize_structured_data`

当信号不足时，结合 LLM 分析问题文本、official_urls 页面类型和未引用平台特征做出判断。每题至少分配 1 个 action，可分配多个。

**Sub-group construction:**

1. Assign each P0 question an `action_keys: [...]` array (one or more keys from the taxonomy).
2. Group questions by `action_key` — 同一问题可出现在多个分组中。
3. Each action group gets:
   - `action_key`, `action_title`, `action_description`
   - `questions` array (the question records belonging to this group)
   - `issue_refs` array (linked Issues from issue-map, deduplicated)
   - `avg_citation_rate` (average of questions in this group)
4. Sort action groups by `avg_citation_rate` ascending (worst first).
5. Store in `not_cited.action_groups` array in the JSON output.
6. In the report summary, `unique_question_count` records the deduplicated P0 question count (since questions may repeat across groups).

**Step 4: Write JSON Output**

Write `assessment-report.json` to `output_dir`:

```json
{
  "metadata": {
    "community": "MindSpore",
    "generated_at": "2026-03-30T...",
    "total_questions": 47,
    "total_platforms": 4,
    "citation_threshold": 0.9,
    "source_files": {
      "scoring": "runs/2026-03-30/scoring-results.json",
      "questions": "assessments/{community}/questions.json",
      "issue_map": "issue-map.json",
      "prev_report": "assessments/MindSpore/2026-03-23/assessment-report.json"
    }
  },
  "changes": {
    "prev_run_date": "2026-03-23",
    "improved": 3,
    "regressed": 1,
    "resolved": 2,
    "new": 0,
    "stable": 41
  },
  "summary": {
    "by_category": {
      "no_official_content": 4,
      "not_cited": 20,
      "satisfied": 23
    },
    "by_severity": {
      "P0": 20,
      "P1": 4,
      "OK": 23
    }
  },
  "categories": {
    "no_official_content": {
      "title": "官方内容缺失",
      "description": "官方站点尚无覆盖此问题的内容",
      "questions": [...]
    },
    "not_cited": {
      "title": "有内容未被引用",
      "description": "官方内容已存在，但未达到 90% 平台引用阈值",
      "questions": [...]
    },
    "satisfied": {
      "title": "引用了官方内容",
      "description": "≥90% 平台引用了官方链接，状态健康",
      "questions": [...]
    }
  }
}
```

**Step 5: Write Markdown Output**

Write `assessment-report.md` to `output_dir`. Read `assets/report-template.md` for the layout and fill in:

1. **Report header**: community name, generation date, scoring threshold, source files, and prev report reference.
2. **变化摘要 section** (immediately after header, before the summary table): show counts from `changes`. On first run, show "首次运行，无历史基线". Example:
   ```
   ### 本次变化（对比 2026-03-23）
   ↑ 改善 3 · ↓ 退步 1 · ✓ 已解决 2 · ★ 新增 0 · → 持平 41
   ```
3. **Summary table**: counts by category and severity.
4. **Platform legend**: list all platforms with their indicator meanings, plus trend indicator legend.
5. **Per-category sections**: one `##` section per category.

   **Trend indicator in all tables**: prefix the ID cell with the question's trend indicator. Example: `↑ q_001`, `★ q_048`, `→ q_003`.

   For `no_official_content` and `satisfied`, render a flat table as before.

   For `not_cited` (P0), render **sub-grouped by improvement action type**. For each action group:
   - A `### {action_title}` heading with action description
   - A table of questions in the group:

```markdown
## 有内容未被引用（P0）— 7 个问题

### 补充专题文档页面

> 官方内容分散在新闻、Issue 中，缺少独立文档页面，AI 平台难以引用。

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_002 | MindNLP 安装失败怎么排查？ | ❌ | ✅ | — | ✅ | 66% | [#2](url) ×1 |
| q_005 | MindNLP 在昇腾设备上出错 | ❌ | ❌ | — | ❌ | 0% | [#2](url) ×1 |

> 官方链接：url1, url2

### 针对特定平台提交收录

> 多数平台已引用，个别平台漏引，需向目标平台主动提交内容。

| ID | 问题 | ... | 引用率 | Issue |
...
```

   - Each action group heading is the action title (中文).
   - Action description rendered as blockquote below the heading.
   - Official URLs shown as a blockquote below each action group table.
   - Issue column format: `[#{number}](url) ×{iterations}` if issue exists; `—` if no issue.

5. **官方内容缺失 section**: additionally list official URL recommendations per question.

**Step 6: Print Summary**

```
Assessment report generated:
  Community: {community}
  Total questions: {n}
  官方内容缺失:    {n} questions
  有内容未被引用:  {n} questions (P0)
  引用了官方内容:  {n} questions (OK)

Output:
  {output_dir}/assessment-report.json
  {output_dir}/assessment-report.md
```

## Error Handling

- If `scoring_file` is missing, abort: `"scoring-results.json not found. Run scoring-engine first."`
- If `questions_file` is missing, continue with empty `official_urls` for all questions and log a warning.
- If `issue_map_file` is missing, continue with empty issue data — `issue_url` and `issue_iterations` will be `null`.
- If `prev_report_file` is `"none"` or the file does not exist, treat as first run: all questions get `trend: "new"`, `prev_status: null`, `prev_citation_rate: null`. The changes summary shows "首次运行，无历史基线".
- If a question in `scoring-results.json` has no matching entry in `questions.json`, use `official_urls: []`.
- If `build-report.py` fails, abort with the stderr output.
