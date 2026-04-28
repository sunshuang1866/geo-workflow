---
name: get-question
description: Generates and incrementally appends to a structured question set for GEO search assessment. Supports 2 source paths (forum, website) — select individually or all. The forum path uses a dual-channel strategy: MongoDB (community-hot-topic database) provides all consult-filtered aggregated topics covering forum posts, issues, and maillists; PostgreSQL/Discourse provides top 30 individual forum posts with views > 50. MongoDB consult-filter: exclude topics whose sources are all Req/Task/RFC/Doc; keep mixed topics if consult-type sources ≥ 50%. Each topic carries consult_count/exclude_count/total_count for sorting and display. Within each intent category, MongoDB topics sorted by consult_count desc; PG/Discourse topics by views desc. Both channels are combined before question rewriting. Loads existing questions.json (if any) and appends only new, deduplicated questions. Preserves existing official_urls and notes. Outputs questions.json and questions.md. Use when starting or refreshing a GEO assessment. Do not use for platform sampling, scoring, or improvement suggestions.
---

# Get Question

## I/O

| Param | Required | Default | Notes |
|---|---|---|---|
| `community` | no | `GEO_COMMUNITY` from `.env` | e.g. "MindSpore" |
| `target_count` | no | `GEO_QUESTION_TARGET_COUNT` from `.env` → `100` | Target number of newly generated questions in this run |
| `seed_keywords` | no | LLM-derived | comma-separated |
| `paths` | no | `GEO_PATHS` from `.env` → `all` | `forum` / `website` / `all` |
| `forum_url` | no | `GEO_FORUM_URL` from `.env` | Discourse forum base URL (e.g. `https://discuss.mindspore.cn`) |

**Outputs**: `questions.json`, `questions.md` in `assessments/{community}/` — appended in-place, never overwritten

**Constant**: `SD=.claude/skills/get-question`

---

## Step 1 — Init

1. Load `.env` from project root.
2. Resolve inputs with priority (explicit caller arg > `.env` var > default):
   - `community`: caller arg → `GEO_COMMUNITY` from `.env`. Abort if still unresolved: `"community not set. Provide as argument or set GEO_COMMUNITY in .env."`
   - `target_count`: caller arg → `GEO_QUESTION_TARGET_COUNT` from `.env` → `100`
   - `paths`: caller arg → `GEO_PATHS` from `.env` → `all`
   - `forum_url`: caller arg → `GEO_FORUM_URL` from `.env`
3. If `seed_keywords` missing → LLM: `"List 3-5 comma-separated technical keywords for '{community}'. Keywords only."`
4. **Load existing question set**: If `assessments/{community}/questions.json` exists, parse it:
   - `existing_questions`: the `questions` array (preserve `official_urls`, `notes`, `official_domains` as-is)
   - `last_id_num`: parse the numeric suffix of the highest `id` (e.g. `"q_031"` → `31`). New questions will be numbered from `last_id_num + 1`.
   - `existing_texts`: set of lowercased question strings for deduplication
   If the file does not exist, set `existing_questions=[]`, `last_id_num=0`, `existing_texts=set()`.
5. Log: `Community={community} target_count={target_count} existing={len(existing_questions)} keywords={seed_keywords} paths={paths}`

---

## Step 2 — Manual Questions

If `manual-questions.md` exists → run `python3 $SD/scripts/parse-manual-questions.py manual-questions.md`, capture stdout → `manual_questions`. Otherwise `manual_questions=[]`.

---

## Step 3 — Path 1: Forum [PRIMARY]

Skip if `paths` excludes `forum`.

The forum path runs **two channels** simultaneously and combines the results.

**Channel 1 — MongoDB aggregated topics** (primary; covers forum posts + repository issues + maillists):

MongoDB `community-hot-topic` is an aggregated database where each topic clusters multiple source posts from the community's forum, issue tracker, and maillist. It is the **primary data source for the forum path** and the reason MongoDB credentials are required for get-question. The **consult-filter** retains only user-question-type topics:
- `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USER`, `MONGODB_PASSWORD` — DB name is hardcoded to `community-hot-topic`; TLS is always enabled (hardcoded)
- Collections: `{community}_hot_topic` (one doc per topic) + `{community}_not_hot_topic` (single doc with `topics[]` array)
- **Include**: topics whose sources are `type=forum`, `[Question]`, `[Bug]`, or have no bracket prefix
- **Exclude**: topics where **all** sources are `[Req]`, `[Task]`, `[RFC]`, `[Doc]` (purely non-consult)
- **Mixed topics**: keep if consult-type sources ≥ 50% of total; discard otherwise
- Each retained topic carries `consult_count`, `exclude_count`, `total_count` — used for sorting and display

**Channel 2 — PostgreSQL/Discourse individual forum posts** (supplementary; non-fatal):
- Credential source: `HOTOPIC_DB_CONFIG_JSON`, or `HOTOPIC_DB_<COMMUNITY>_HOST/PORT/NAME/USER/PASSWORD`, or `HOTOPIC_DB_HOST/PORT/NAME/USER/PASSWORD`
- Queries `discussion` table (`source_type='forum'`), `views > 50`, sorted DESC, `LIMIT 30`
- Surfaces high-traffic individual posts not yet aggregated in MongoDB
- If PostgreSQL unavailable: falls back to Discourse API (`--api-url`); captures `pg_channel_status` for output

1. Run:
   ```
   python3 $SD/scripts/fetch-forum-posts.py \
     --community "{community}" \
     [--api-url "{forum_url}"]
   ```
2. **exit=0** → combined results contain both MongoDB topics and PG/API forum posts.
   - Read `$SD/assets/prompt-templates.md` section `REWRITE_TO_QUESTIONS`, apply forum variant, send LLM call with fetched data. Capture → `path1_questions`.
3. **exit≠0** → Read `$SD/assets/prompt-templates.md` section `FORUM_FALLBACK`, send LLM call. Capture → `path1_questions`.
4. Capture stderr for channel status:
   - Extract `pg_channel_status` from the `pg_channel_status=...` line if present (or `{}` if unavailable).
   - Extract `MONGO_SOURCE_TYPES` from the `MONGO_SOURCE_TYPES=...` line (JSON object with `forum`, `issue`, `maillist` counts; or `{}` if MongoDB was unavailable).
   - Record:
   ```
   forum_criteria = {
     "source": "combined",
     "channel1_mongodb": "{N} aggregated topics (consult-filter: exclude all-Req/Task/RFC/Doc; mixed ≥50% consult kept)",
     "channel2_forum": "{M} posts (views>50, top 30) from {pg|discourse|unavailable}",
     "mongo_source_types": {"forum": N, "issue": M, "maillist": K},
     "fetched_at": "{YYYY-MM-DD}"
   }
   ```

---

## Step 4 — Path 2: Website Search Keywords

Skip if `paths` excludes `website`.

1. Check: if `WEBSITE_SEARCH_URL` not set → log `SKIP: WEBSITE_SEARCH_URL not configured`, set `path2_questions=[]`, go to Step 5.
2. Fetch: `curl -s [-H "Authorization: Bearer {WEBSITE_SEARCH_TOKEN}"] "{WEBSITE_SEARCH_URL}"` → capture JSON response.
   - **HTTP ≠ 200** → log `SKIP: website search API returned HTTP {status}`, set `path2_questions=[]`, go to Step 5.
3. Extract keyword list from response (field name varies by API; try `data`, `keywords`, `hot_words`, `result`).
4. Read `$SD/assets/prompt-templates.md` section `WEBSITE_KEYWORDS_REWRITE`, send LLM call with raw keyword list.
   - LLM filters navigation terms (首页/登录/官网/下载) and pure brand terms.
   - LLM rewrites remaining keywords into full natural language search questions.
   - Capture → `path2_questions`.

---

## Step 5 — Merge & Deduplicate

1. Combine new candidates: `new_candidates = manual_questions + path1_questions + path2_questions`.
2. **Filter against existing**: Remove any candidate whose lowercased question text has cosine similarity ≥90% with any entry in `existing_texts`. Pass `new_candidates` and `existing_texts` to LLM for semantic dedup.
   - Result: `truly_new_questions` (candidates not already covered by existing questions).
3. **Tag source on each new question**: Set `"source"` field before merging:
   - From `manual_questions` → `"source": "manual"`
   - From `path1_questions` (MongoDB or PostgreSQL/API) → `"source": "forum"`
   - From `path2_questions` → `"source": "website"`
4. Read `$SD/assets/prompt-templates.md` section `MERGE_DEDUP`, then send LLM call with `truly_new_questions` only (no need to re-dedup existing ones). Do not enforce any total-question upper/lower bound.
5. Validate: `echo '{merged_json}' | python3 $SD/scripts/validate-questions.py`.
   - **errors** → show errors, LLM fixes JSON, re-validate once.
   - **still invalid** → abort.
6. Assign IDs to new questions starting from `last_id_num + 1`, zero-padded to 3 digits (e.g. `q_032`, `q_033`, ...).
7. **Sort** `truly_new_questions` before ID assignment:
   - Primary key: intent category (preserved for grouping in Step 6).
   - Within each category:
     - `source == "forum"` (from MongoDB) → sort by `source_breakdown.consult` descending (missing/0 last).
     - `source == "forum"` (from PostgreSQL/Discourse) → sort by `source_views` descending.
     - `source == "website"` or `source == "manual"` → no sort (preserve original order).
8. If `len(truly_new_questions) == 0` → print `No new questions found. Existing set unchanged.` and exit cleanly.

---

## Step 6 — Output

1. Build final question list: `final_questions = existing_questions + truly_new_questions`.
2. **Before writing, sort `final_questions` within each intent category**:
   - MongoDB topics (`source == "forum"`, `source_views == 0`) → sort by `source_breakdown.consult` descending (missing/0 last).
   - PG/Discourse topics (`source == "forum"`, `source_views > 0`) → sort by `source_views` descending.
   - `source == "website"` or `source == "manual"` → maintain original order within category.
   - Do NOT re-assign IDs after sorting; IDs stay fixed.
2. Write `questions.json` to `assessments/{community}/` with the following structure:
   ```json
   {
     "community": "{community}",
     "generated_at": "{YYYY-MM-DD}",
     "official_domains": [],
     "source_criteria": {
       "forum": {"source": "combined", "channel1_mongodb": "{N} aggregated topics (consult-filter)", "channel2_forum": "{M} posts (views>50, top 30)", "mongo_source_types": {"forum": N, "issue": M, "maillist": K}, "fetched_at": "{YYYY-MM-DD}"},
       "website": {"algorithm": "hot search keywords from API", "fetched_at": "{YYYY-MM-DD}"}
     },
     "pg_channel_status": {
       "forum":          {"count": 762, "available": true},
       "mail":           {"count": 29,  "available": true},
       "question_issue": {"count": 15,  "available": true}
     },
     "questions": [
       {
         "id": "q_001",
         "question": "...",
         "source": "forum",
         "source_views": 6847,
         "official_urls": [],
         "notes": ""
       }
     ]
   }
   ```
   - **Preserve** `official_domains` from the existing file if it was non-empty; only reset to `[]` on first run.
   - **Preserve** each existing question's `official_urls`, `notes`, `source`, and `source_views` exactly as-is.
   - New questions get `official_urls: []`, `notes: ""`, `source` set per Step 5 tagging, and `source_views` set to the integer views count of the originating forum/issue topic (omit field if not applicable, e.g., for manual or website questions).
   - `source_criteria`: merge/update only the keys for paths run in this session; preserve existing keys from prior runs.
   - `pg_channel_status`: write the `pg_channel_status` captured in Step 3 (or `{}` if PG was unavailable). Always overwrite — this reflects the latest DB check.

3. **Human action required for new questions**: After each run, populate `official_urls` for newly appended questions (those with empty `official_urls`). Existing annotated questions are unaffected.

4. Render `questions.md` using `$SD/assets/questions-template.md` — regenerate from `final_questions`. Requirements:
   - Group questions by intent category.
   - Within each group, render questions in the sorted order from step 2 above (forum/issue by `source_views` desc, others by original order).
   - Each row in a question table contains only `#` (sequential integer within the group) and `问题` columns. Do NOT include `来源` or `Views` columns.
   - The overview section must include a `筛选标准` table with columns: `来源`, `占比`, `评分算法`, `筛选方式`, `获取时间`.
     - List all channels that appear in `source_criteria` (forum, website) plus `手动` if any manual questions exist.
     - `占比`: count of questions from that source / total * 100, rounded to 1 decimal, formatted as `{n}%`.
     - `评分算法` / `筛选方式` / `获取时间`: pull from `source_criteria` in questions.json; use `-` if not available (e.g., manual source).
     - Include a total row at the bottom: `| **合计** | 100% | - | - | - |`.
   - The overview section must also include a `MongoDB 来源渠道` table from `source_criteria.forum.mongo_source_types`:
     - Columns: `渠道`, `来源数量`, `状态`.
     - Channel label mapping: `forum` → `论坛帖子`, `issue` → `仓库 Issue`, `maillist` → `邮件列表`.
     - `状态`: `✅ 有数据` if count > 0, `❌ 无数据` if count == 0.
     - If `mongo_source_types` is missing or empty, render a single row: `| - | - | MongoDB 未配置 |`.
   - The overview section must also include a `PostgreSQL 渠道状态` table from `pg_channel_status`:
     - Channel label mapping: `forum` → `论坛帖子`, `mail` → `邮件列表`, `question_issue` → `Issue (问题类)`.
     - `状态`: `✅ 有数据` if `available=true`, `❌ 无数据` if `available=false`.
     - If `pg_channel_status` is empty (`{}`), render a single row: `| - | - | PostgreSQL 未配置 |`.
   - `questions.md` does not include `official_urls` or `notes`.

5. Print: `Added {n_new} questions (total {len(final_questions)}) | New sources: manual={n} forum={n} issue={n} website={n} | Paths: {paths_run}`.
