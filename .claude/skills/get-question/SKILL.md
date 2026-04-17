---
name: get-question
description: Generates and incrementally appends to a structured question set for GEO search assessment. Supports 4 source paths (forum, issue, maillist, website) — select individually or all. Loads existing questions.json (if any) and appends only new, deduplicated questions. Preserves existing official_urls and notes. Outputs questions.json and questions.md. Use when starting or refreshing a GEO assessment. Do not use for platform sampling, scoring, or improvement suggestions.
---

# Get Question

## I/O

| Param | Required | Default | Notes |
|---|---|---|---|
| `community` | no | `GEO_COMMUNITY` from `.env` | e.g. "MindSpore" |
| `seed_keywords` | no | LLM-derived | comma-separated |
| `paths` | no | `GEO_PATHS` from `.env` → `all` | `forum` / `issue` / `maillist` / `website` / `all` |
| `forum_url` | no | `GEO_FORUM_URL` from `.env` | Discourse forum base URL (e.g. `https://discuss.mindspore.cn`) |
| `since` | no | none | Filter issue/mail records by `created_at >=` date, e.g. `2024-01-01` |
| `datastat_email` | no | `DATASTAT_EMAIL` from `.env` | Login email for issue path (datastat API) |
| `datastat_password` | no | `DATASTAT_PASSWORD` from `.env` | Login password for issue path (datastat API) |
| `limit` | no | `80` | Chinese format ok: "前10" → `10` |

**Outputs**: `questions.json`, `questions.md` in `assessments/{community}/` — appended in-place, never overwritten

**Constant**: `SD=.claude/skills/get-question`

---

## Step 1 — Init

1. Load `.env` from project root.
2. Resolve inputs with priority (explicit caller arg > `.env` var > default):
   - `community`: caller arg → `GEO_COMMUNITY` from `.env`. Abort if still unresolved: `"community not set. Provide as argument or set GEO_COMMUNITY in .env."`
   - `paths`: caller arg → `GEO_PATHS` from `.env` → `all`
   - `forum_url`: caller arg → `GEO_FORUM_URL` from `.env`
   - `since`: caller arg → none (optional)
   - `datastat_email`: caller arg → `DATASTAT_EMAIL` from `.env`
   - `datastat_password`: caller arg → `DATASTAT_PASSWORD` from `.env`
3. If `seed_keywords` missing → LLM: `"List 3-5 comma-separated technical keywords for '{community}'. Keywords only."`
4. **Load existing question set**: If `assessments/{community}/questions.json` exists, parse it:
   - `existing_questions`: the `questions` array (preserve `official_urls`, `notes`, `official_domains` as-is)
   - `last_id_num`: parse the numeric suffix of the highest `id` (e.g. `"q_031"` → `31`). New questions will be numbered from `last_id_num + 1`.
   - `existing_texts`: set of lowercased question strings for deduplication
   If the file does not exist, set `existing_questions=[]`, `last_id_num=0`, `existing_texts=set()`.
5. Log: `Community={community} existing={len(existing_questions)} keywords={seed_keywords} paths={paths} limit={limit}`

---

## Step 2 — Manual Questions

If `manual-questions.md` exists → run `python3 $SD/scripts/parse-manual-questions.py manual-questions.md`, capture stdout → `manual_questions`. Otherwise `manual_questions=[]`.

---

## Step 3 — Path 1: Forum [PRIMARY]

Skip if `paths` excludes `forum`.

1. Run `python3 $SD/scripts/fetch-forum-posts.py --community "{community}" [--api-url "{forum_url}"]`.
2. **exit=0** → Read `$SD/assets/prompt-templates.md` section `REWRITE_TO_QUESTIONS`, apply forum variant, send LLM call with fetched data. Capture → `path1_questions`.
3. **exit≠0** → Read `$SD/assets/prompt-templates.md` section `FORUM_FALLBACK`, send LLM call. Capture → `path1_questions`.

---

## Step 4 — Path 2: Issues

Skip if `paths` excludes `issue`.

1. Pre-validate: check that `datastat_email` and `datastat_password` are set.
   - If either is missing → log `SKIP: datastat_email/datastat_password not set`, set `path2_questions=[]`, go to Step 5.
2. Run:
   ```
   DATASTAT_EMAIL={datastat_email} DATASTAT_PASSWORD={datastat_password} \
   python3 $SD/scripts/fetch-dataset.py --community "{community}" --source issue [--since {since}]
   ```
3. **exit=0** → Read `$SD/assets/prompt-templates.md` section `REWRITE_TO_QUESTIONS`, apply issue variant, send LLM call with fetched data. Capture → `path2_questions`.
4. **exit=2** (auth failed) → log `SKIP: datastat login failed`, set `path2_questions=[]`, go to Step 5.
5. **other failure** → log warning, set `path2_questions=[]`. No LLM fallback.

---

## Step 5 — Path 3: Maillist

Skip if `paths` excludes `maillist`.

1. Run:
   ```
   python3 $SD/scripts/fetch-dataset.py --community "{community}" --source mail [--since {since}]
   ```
2. **exit=0** → Read `$SD/assets/prompt-templates.md` section `MAILLIST_REWRITE`, send LLM call with fetched data. Capture → `path3_questions`.
3. **exit≠0** → Read `$SD/assets/prompt-templates.md` section `MAILLIST_FALLBACK`, send LLM call. Capture → `path3_questions`.

---

## Step 6 — Path 4: Website Search Keywords

Skip if `paths` excludes `website`.

1. Check: if `WEBSITE_SEARCH_URL` not set → log `SKIP: WEBSITE_SEARCH_URL not configured`, set `path4_questions=[]`, go to Step 7.
2. Fetch: `curl -s [-H "Authorization: Bearer {WEBSITE_SEARCH_TOKEN}"] "{WEBSITE_SEARCH_URL}"` → capture JSON response.
   - **HTTP ≠ 200** → log `SKIP: website search API returned HTTP {status}`, set `path4_questions=[]`, go to Step 7.
3. Extract keyword list from response (field name varies by API; try `data`, `keywords`, `hot_words`, `result`).
4. Read `$SD/assets/prompt-templates.md` section `WEBSITE_KEYWORDS_REWRITE`, send LLM call with raw keyword list.
   - LLM filters navigation terms (首页/登录/官网/下载) and pure brand terms.
   - LLM rewrites remaining keywords into full natural language search questions.
   - Capture → `path4_questions`.

---

## Step 7 — Merge & Deduplicate

1. Combine new candidates: `new_candidates = manual_questions + path1_questions + path2_questions + path3_questions + path4_questions`.
2. **Filter against existing**: Remove any candidate whose lowercased question text has cosine similarity ≥90% with any entry in `existing_texts`. Pass `new_candidates` and `existing_texts` to LLM for semantic dedup.
   - Result: `truly_new_questions` (candidates not already covered by existing questions).
3. Read `$SD/assets/prompt-templates.md` section `MERGE_DEDUP`, substitute `{question_target_min}` and `{question_target_max}` from `.env` (`GEO_QUESTION_TARGET_MIN` / `GEO_QUESTION_TARGET_MAX`, defaults 30/40), then send LLM call with `truly_new_questions` only (no need to re-dedup existing ones).
4. Validate: `echo '{merged_json}' | python3 $SD/scripts/validate-questions.py`.
   - **errors** → show errors, LLM fixes JSON, re-validate once.
   - **still invalid** → abort.
5. Assign IDs to new questions starting from `last_id_num + 1`, zero-padded to 3 digits (e.g. `q_032`, `q_033`, ...).
6. If `len(truly_new_questions) == 0` → print `No new questions found. Existing set unchanged.` and exit cleanly.

---

## Step 8 — Output

1. Build final question list: `final_questions = existing_questions + truly_new_questions`.
2. Write `questions.json` to `assessments/{community}/` with the following structure:
   ```json
   {
     "community": "{community}",
     "generated_at": "{YYYY-MM-DD}",
     "official_domains": [],
     "questions": [
       {
         "id": "q_001",
         "question": "...",
         "official_urls": [],
         "notes": ""
       }
     ]
   }
   ```
   - **Preserve** `official_domains` from the existing file if it was non-empty; only reset to `[]` on first run.
   - **Preserve** each existing question's `official_urls` and `notes` exactly as-is.
   - New questions get `official_urls: []` and `notes: ""`.

3. **Human action required for new questions**: After each run, populate `official_urls` for newly appended questions (those with empty `official_urls`). Existing annotated questions are unaffected.

4. Render `questions.md` using `$SD/assets/questions-template.md` — regenerate from `final_questions`, group by intent, include summary table, mark source per question. `questions.md` does not include `official_urls` or `notes`.

5. Print: `Added {n_new} questions (total {len(final_questions)}) | New sources: manual={n} forum={n} issue={n} maillist={n} website={n} | Paths: {paths_run}`.
