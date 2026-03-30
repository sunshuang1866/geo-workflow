---
name: assessment-report
description: Generates a structured question assessment report after issue-creator completes. Reads scoring-results.json, content-labels.json, and issue-map.json to compile per-question records including question_id, question text, official URLs, per-platform citation status with emoji indicators, severity level, linked Issue URL, issue creation date, and iteration count. Groups questions by phenomenon category (官方内容缺失, 有内容未被引用, 引用了官方内容) and outputs both machine-readable JSON and human-readable Markdown. Use after issue-creator skill completes. Do not use for question generation, platform sampling, scoring, or issue creation.
---

# Assessment Report

Compile a structured question assessment report from scoring and issue data. Each question gets a full record: citation status per platform, severity, linked Issue, and history. Output is grouped by phenomenon category in both JSON and Markdown.

## Prerequisites

- `scoring-results.json` — output from scoring-engine
- `content-labels.json` — human-labeled official URLs per question
- `issue-map.json` — Issue URL, creation date, and update history from issue-creator

## Inputs

| Param | Required | Default | Notes |
|-------|----------|---------|-------|
| `scoring_file` | no | `scoring-results.json` | Path to scoring results |
| `labels_file` | no | `content-labels.json` | Path to content labels |
| `issue_map_file` | no | `issue-map.json` | Path to issue map |
| `output_dir` | no | same directory as `scoring_file` | Where to write output files |
| `community` | no | auto-detected from path | Community name for report header |

## Procedures

**Step 1: Load Inputs**

1. Read `scoring_file`. Extract `results` array (question-level records with `status`, `description`, `severity`, `citation_rate`, `platforms` array) and `metadata`.
2. Read `labels_file`. Build a lookup map `{question_id → {official_urls, notes}}`.
3. Read `issue_map_file`. Build a lookup map `{question_id → {issue_url, issue_number, created_at, last_updated_run, update_count}}`.
   - Derive `update_count` for each question: count how many entries in `issue-map.json` reference this `question_id`, or read the `last_updated_run` vs `created_at` diff as iteration count. Use the number of times `last_updated_run` has changed as the iteration count (if not tracked, default to 1 for entries that exist).
   - If `issue_map_file` does not exist, proceed with empty issue data.
4. Run `python3 scripts/build-report.py {scoring_file} {labels_file} {issue_map_file}` to merge all three sources into a unified per-question record list. The script outputs JSON to stdout.
5. Print load summary:
   ```
   Inputs loaded:
     Questions: {n}
     Platforms: {platform_list}
     Questions with Issues: {n}
     Questions without Issues: {n}
   ```

**Step 2: Build Per-Question Records**

For each question in `scoring-results.json`, construct a record:

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
  "issue_iterations": 2
}
```

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
      "labels": "content-labels.json",
      "issue_map": "issue-map.json"
    }
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

1. **Report header**: community name, generation date, scoring threshold, source files.
2. **Summary table**: counts by category and severity.
3. **Platform legend**: list all platforms with their indicator meanings.
4. **Per-category sections**: one `##` section per category, with a table of questions:

```markdown
## 有内容未被引用（P0）— 20 个问题

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | 严重级别 | Issue |
|----|------|------|------|---------|----------|--------|----------|-------|
| q_001 | MindSpore 支持哪些安装方式？ | ❌ | ✅ | ❌ | ❌ | 25% | P0 | [#45](url) ×2 |
| q_002 | MindSpore 和 PyTorch 相比有哪些优势？ | ❌ | ❌ | ❌ | ❌ | 0% | P0 | [#46](url) ×1 |
```

   - Issue column format: `[#{number}](url) ×{iterations}` if issue exists; `—` if no issue.
   - Official URLs shown as footnotes below each category table.

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
- If `labels_file` is missing, continue with empty `official_urls` for all questions and log a warning.
- If `issue_map_file` is missing, continue with empty issue data — `issue_url` and `issue_iterations` will be `null`.
- If a question in `scoring-results.json` has no matching entry in `content-labels.json`, use `official_urls: []`.
- If `build-report.py` fails, abort with the stderr output.
