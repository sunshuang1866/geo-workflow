---
name: prefill-urls
description: Pre-fills official_urls for questions in questions.json using the community's official website, official repositories, and official forum. For website URLs, both Chinese and English page variants are included. Reads official_domains from the existing questions.json and uses LLM inference to match each question to the most relevant official page. Validates candidate URLs with HTTP checks before writing. Runs after get-question in the GEO assessment workflow. Do not use for scoring, platform sampling, or generating new questions.
---

# Prefill URLs

## I/O

| Param | Required | Default | Notes |
|---|---|---|---|
| `community` | no | `GEO_COMMUNITY` from `.env` | e.g. "openUBMC" |
| `batch_size` | no | `50` | Questions processed per LLM call |
| `dry_run` | no | `false` | If true, print candidates without writing |

**Input**: `output/{community}/questions.json` — must exist  
**Output**: same file, `official_urls` populated for previously-empty questions  
**Constant**: `SD=.claude/skills/prefill-urls`

---

## Step 1 — Init

1. Load `.env` from project root.
2. Resolve `community`: caller arg → `GEO_COMMUNITY` from `.env`. Abort if unresolved.
3. Load `output/{community}/questions.json`. Abort if file does not exist.
4. Extract:
   - `official_domains`: the `official_domains` array from the JSON root.
   - `target_questions`: questions where `official_urls == []`.
5. If `len(target_questions) == 0` → print `All questions already have official_urls. Nothing to do.` and exit.
6. If `official_domains` is empty → read `references/domain-discovery.md` and follow the domain discovery procedure to populate `official_domains` before continuing.
7. Log: `Community={community} domains={official_domains} target={len(target_questions)} questions to fill`.

---

## Step 2 — Classify Domains by Type

For each domain in `official_domains`, classify into one of three types:

| Type | Description | i18n Rule |
|---|---|---|
| `website` | Official documentation/product site | Generate both `/zh/` and `/en/` variants |
| `repo` | Code hosting (gitee.com, github.com) | Single URL, no i18n expansion |
| `forum` | Community forum (Discourse, etc.) | Single URL, no i18n expansion |

Classification heuristic (apply in order):
- Contains `gitee.com`, `github.com`, or `gitcode.com` → `repo`
- Contains `discuss.` or `forum.` or `bbs.` → `forum`
- All others → `website`

Log the classification: `Domains classified: website=[...] repo=[...] forum=[...]`.

---

## Step 3 — Search-Based URL Discovery

For each question in `target_questions`, extract 3–5 search keywords via LLM:
```
Extract 3-5 search keywords from this question (Chinese or English, space-separated):
{question}
Return keywords only, no explanation.
```

Then query three channels in parallel per question. Collect results into `url_candidates` (dict: id → list of URLs). Leave the list empty if no channel returns a result — do NOT substitute domain roots as placeholders.

**Channel A — Discourse Search** (for all questions):
```
python3 $SD/scripts/search-discourse.py \
  --base-url "{forum_domain}" \
  --query "{keywords}" \
  --limit 2
```
- exit=0 → append returned topic URLs to candidates.
- exit=1 → no result; skip silently.

**Channel B — Docs Sitemap** (for all questions):
```
python3 $SD/scripts/discover-docs.py \
  --base-url "https://{website_domain}" \
  --query "{keywords}" \
  --limit 1
```
- exit=0 → append matched doc page URL to candidates.
- exit=1 → sitemap unavailable or no match; skip silently.

**Channel C — GitCode Repo Match** (for questions about code contribution, build, CI, components):
- Classify question as "dev-type" if it contains any of: 贡献/PR/构建/编译/CI/仓库/组件/Conan/bingo.
- If dev-type: append `https://{repo_domain}` directly (no sub-path; repo org page is the authoritative link).
- Non-dev-type: skip Channel C.

Log per question: `{id}: A={n_forum} B={n_docs} C={n_repo} candidates`.
Log summary: `Discovery complete: {n_with_urls}/{total} questions have ≥1 candidate`.

---

## Step 4 — i18n Expansion for Website URLs

For each candidate URL whose domain is classified as `website`:

Run:
```
python3 $SD/scripts/expand-i18n-urls.py "{url}"
```

- **exit=0** → stdout contains JSON array of expanded URLs (e.g. `["https://docs.openubmc.org/zh/install", "https://docs.openubmc.org/en/install"]`). Replace the original URL with the expanded list.
- **exit=1** → URL has no i18n structure detected; keep as-is.

`repo` and `forum` URLs are not expanded.

---

## Step 5 — HTTP Validation

Collect all unique candidate URLs across all questions. Run:

```
python3 $SD/scripts/validate-urls.py "{urls_json}"
```

- Script performs HEAD requests (timeout 8s) for each URL.
- **stdout**: JSON object `{"https://...": true/false, ...}` — true = HTTP 2xx/3xx, false = unreachable/4xx/5xx.
- **stderr**: progress and error details.

For each question, filter `candidates` to keep only URLs where result is `true`.  
If all candidates for a question fail validation → keep the domain root URL of the most relevant domain type (website > forum > repo) without validation, flagged with a `# unverified` suffix in the note.

Log: `Validated {n_pass}/{n_total} URLs reachable`.

---

## Step 6 — Write Output

1. If `dry_run=true` → print the proposed `official_urls` per question and exit without writing.
2. For each question in `target_questions`:
   - Set `official_urls` to the validated URL list for that question.
   - If a question's URL list is still empty after validation → leave `official_urls: []` and append `note: "prefill-urls: no reachable URL found"`.
3. Merge updated questions back into the full question list (existing questions with non-empty `official_urls` are unchanged).
4. Write the updated JSON back to `output/{community}/questions.json`, preserving all other top-level fields (`community`, `generated_at`, `official_domains`, `source_criteria`, `pg_channel_status`).
5. Print: `Filled {n_filled}/{len(target_questions)} questions | Skipped (no URL): {n_empty} | dry_run={dry_run}`.

---

## Error Handling

- **questions.json missing** → abort with `ERROR: output/{community}/questions.json not found. Run get-question first.`
- **official_domains empty after discovery** → abort with `ERROR: Cannot infer URLs without official_domains. Populate official_domains in questions.json first.`
- **validate-urls.py network timeout** → treat timed-out URLs as `false`; do not retry.
- **LLM returns malformed JSON** → re-prompt once with `Fix the JSON syntax. Return only the JSON array, no prose.` If still invalid → skip the batch and log `WARNING: Batch {i} LLM output invalid, skipped`.
