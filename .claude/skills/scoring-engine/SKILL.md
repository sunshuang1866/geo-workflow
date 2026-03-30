---
name: scoring-engine
description: Evaluates AI platform responses by checking whether they cite official URLs from questions.json. Pure URL string matching (exact + domain-level), no LLM. Scores at question level: if ≥90% of platforms cite official URLs the question is "引用了官方内容" (OK), otherwise "有内容未被引用" (P0), or "官方内容缺失" (P1) when no official URLs exist. Matches GEO catalog suggestions and outputs scoring-results.json. Use after platform-sampler completes sampling. Do not use for question generation, platform sampling, or issue creation.
---

# Scoring Engine

Evaluate AI platform responses against official content availability. Pure URL string matching — checks whether each platform's response cites any official URL listed in `questions.json`. Final status is determined per question by aggregating across platforms using a 90% citation threshold.

## Prerequisites

- `responses.json` in the run directory (output from platform-sampler skill)
- `questions.json` in `packages/assessments/{community}/` (output from get-question skill, with `official_urls` and `official_domains` fields populated by human)

## Procedures

**Step 1: Load and Validate Inputs**

1. Read `responses.json` from the run directory.
2. Read `questions.json` from `packages/assessments/{community}/`. Build a lookup map `{id → {official_urls, notes}}`.
3. Run `python3 scripts/validate-inputs.py responses.json {questions_json_path}` to verify both files exist and are structurally valid.
4. The script checks:
   - `responses.json` contains a `responses` array with `question_id`, `platform`, `response_text` fields.
   - `questions.json` contains a `questions` array with `id`, `official_urls` fields.
   - Every `question_id` in responses has a matching entry in `questions.json`.
5. If validation fails, abort with the specific error from stderr.
6. If a question in `responses.json` has no matching entry in `questions.json`:
   - Log a warning: `"question {question_id} has no entry in questions.json, skipping"`.
   - Exclude from scoring.
6. Print input summary to stdout:
   ```
   Inputs loaded:
     Questions: {n}
     Platforms: {platforms list}
     Response pairs: {n}
     Questions with official URLs: {n}
     Questions without official URLs: {n}
   ```

**Step 2: Per-Platform URL Matching**

For each (question, platform) pair, run a binary URL match check:

1. Look up the question's `official_urls` from `questions.json`.

2. **If `official_urls` is empty (`[]`)**: mark the pair as `no_official_content`. Skip URL matching.

3. **If `official_urls` is non-empty**, check the platform's `response_text`:

   a. **Exact URL match**: For each URL in `official_urls`, check if it appears in `response_text` (case-insensitive).
      - Normalize before matching: strip trailing slashes, treat `http://` and `https://` as equivalent, strip `www.` prefix.
      - Example: `"https://www.mindspore.cn/install"` matches `mindspore.cn/install` in response text.

   b. **Domain-level match**: Extract domain from each `official_url` (strip `www.`, ignore path), check if domain appears in `response_text`.
      - Example: `"https://www.mindspore.cn/install"` → domain `mindspore.cn` → matches if `mindspore.cn` appears anywhere in response text.

   c. **Result**: If any match found (exact or domain), mark pair as `cited`. Record `match_type` (`exact_url` or `domain`) and which URLs matched. If no match, mark as `not_cited`.

4. Build a per-platform record for each pair:
   ```json
   {
     "platform": "qwen",
     "cited": true,
     "match_type": "exact_url",
     "matched_urls": ["https://www.mindspore.cn/install"]
   }
   ```

**Step 3: Question-Level Aggregation and Status Assignment**

For each question, aggregate the per-platform results from Step 2 to determine the final question-level status:

1. **If `official_urls` is empty**: The question has no official content regardless of platform responses.
   - Status: `no_official_content`
   - Description: `官方内容缺失`
   - Severity: `P1`

2. **If `official_urls` is non-empty**: Compute the citation rate across platforms.
   - `cited_count` = number of platforms where `cited = true`
   - `total_platforms` = total number of platforms with a response for this question
   - `citation_rate` = `cited_count / total_platforms`

   - **If `citation_rate >= 0.9`** (90% or more platforms cited official URLs):
     - Status: `satisfied`
     - Description: `引用了官方内容`
     - Severity: `OK`

   - **If `citation_rate < 0.9`**:
     - Status: `not_cited`
     - Description: `有内容未被引用`
     - Severity: `P0`

3. Build the question-level result object:
   ```json
   {
     "question_id": "q_001",
     "question": "MindSpore 支持哪些安装方式？",
     "official_urls": ["https://www.mindspore.cn/install"],
     "status": "satisfied",
     "description": "引用了官方内容",
     "severity": "OK",
     "citation_rate": 1.0,
     "cited_count": 4,
     "total_platforms": 4,
     "platforms": [
       {"platform": "qwen",     "cited": true,  "match_type": "exact_url", "matched_urls": ["https://www.mindspore.cn/install"]},
       {"platform": "chatgpt",  "cited": true,  "match_type": "domain",    "matched_urls": []},
       {"platform": "deepseek", "cited": true,  "match_type": "exact_url", "matched_urls": ["https://www.mindspore.cn/install"]},
       {"platform": "doubao",   "cited": true,  "match_type": "domain",    "matched_urls": []}
     ]
   }
   ```

4. Print a Step 3 summary:
   ```
   Question-Level Scoring (threshold: 90%):
     Total questions: {n}
     引用了官方内容 (OK):  {n}  — citation_rate ≥ 90%
     有内容未被引用 (P0):  {n}  — citation_rate < 90%
     官方内容缺失 (P1):    {n}  — no official URLs
   ```

**Step 4: Match Suggestions from GEO Catalog**

1. Read `references/geo-suggestions-catalog.md` — the 72-item GEO optimization suggestion catalog.
2. Read `references/suggestion-rules.md` for matching rules.
3. For each question with `not_cited` or `no_official_content` status:
   a. Use the status to look up candidate suggestions:
      - `not_cited` → SEO/discoverability suggestions (e.g., structured data, schema markup, content optimization)
      - `no_official_content` → Content creation suggestions (e.g., create FAQ, add documentation)
   b. Use `citation_rate` to refine priority:
      - `citation_rate = 0` (no platform cited) → highest priority, content-origin issue
      - `citation_rate > 0` (some platforms cited) → platform-specific issue
   c. Select the top 5 most relevant suggestions per question.
4. For each matched suggestion, generate:
   ```json
   {
     "suggestion_id": "s_001",
     "question_ids": ["q_001"],
     "status": "not_cited",
     "description": "有内容未被引用",
     "severity": "P0",
     "citation_rate": 0.25,
     "cited_platforms": ["qwen"],
     "not_cited_platforms": ["chatgpt", "deepseek", "doubao"],
     "catalog_refs": ["CTX-02", "ORG-05"],
     "suggestion_text": "..."
   }
   ```

**Step 5: Compile Output**

1. Run `python3 scripts/compile-report.py` with scoring results piped as JSON to stdin.
   The script:
   - Deduplicates suggestions with >80% text similarity
   - Sorts by severity (P0 → P1 → OK)
   - Assigns unique suggestion IDs
   - Outputs compiled JSON to stdout

2. Write `scoring-results.json` to the working directory:
   ```json
   {
     "metadata": {
       "scored_at": "2026-03-30T...",
       "total_questions": 47,
       "total_platforms": 4,
       "citation_threshold": 0.9,
       "match_mode": "url+domain"
     },
     "results": [
       {
         "question_id": "q_001",
         "question": "MindSpore 支持哪些安装方式？",
         "official_urls": ["https://www.mindspore.cn/install"],
         "status": "satisfied",
         "description": "引用了官方内容",
         "severity": "OK",
         "citation_rate": 1.0,
         "cited_count": 4,
         "total_platforms": 4,
         "platforms": [
           {"platform": "qwen",     "cited": true,  "match_type": "exact_url", "matched_urls": ["https://www.mindspore.cn/install"]},
           {"platform": "chatgpt",  "cited": false, "match_type": null,        "matched_urls": []},
           {"platform": "deepseek", "cited": true,  "match_type": "domain",    "matched_urls": []},
           {"platform": "doubao",   "cited": true,  "match_type": "exact_url", "matched_urls": ["https://www.mindspore.cn/install"]}
         ]
       }
     ],
     "summary": {
       "by_status": {
         "satisfied": 23,
         "not_cited": 20,
         "no_official_content": 4
       },
       "by_severity": {
         "P0": 20,
         "P1": 4,
         "OK": 23
       },
       "citation_rate_distribution": {
         "1.0": 10,
         "0.75": 8,
         "0.5": 5,
         "0.25": 4,
         "0.0": 3
       }
     },
     "suggestions": [...]
   }
   ```

3. Print a final summary to stdout:
   ```
   Scoring complete:
     Questions scored: {scored}/{total}
     引用了官方内容 (OK):  {n} ({pct}%)  — citation_rate ≥ 90%
     有内容未被引用 (P0):  {n} ({pct}%)  — citation_rate < 90%
     官方内容缺失 (P1):    {n} ({pct}%)

     Output: scoring-results.json
   ```

## Error Handling

* If `responses.json` is missing, abort with: `"responses.json not found. Run platform-sampler skill first."`
* If `questions.json` is missing, abort with: `"questions.json not found. Run get-question skill first."`
* If `questions.json` has an empty `questions` array, abort with: `"questions.json has no questions."`
* If all questions have empty `official_urls`, warn: `"No official_urls found in questions.json. Populate them before scoring for meaningful results."`
* If a question in `responses.json` has no matching entry in `questions.json`, log a warning and skip (do not abort).
* If `responses.json` contains zero valid pairs after filtering, abort with: `"No valid question-platform pairs to score."`
* If a question has only 1 platform response, the 90% threshold still applies (1/1 = 100% ≥ 90% → satisfied; 0/1 = 0% < 90% → not_cited).
