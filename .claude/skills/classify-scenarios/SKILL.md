---
name: classify-scenarios
description: Classifies questions in questions.json into application scenario categories derived from the community's official documentation index. Fetches the docs directory from DOCS_INDEX_URL, uses LLM to extract a 5–8 scenario taxonomy, then batch-classifies all unclassified questions and writes the scenario field back to questions.json. Persists the taxonomy in questions.json root (scenario_taxonomy) to avoid label drift across runs. Supports dry_run and incremental re-classification. Run after get-question and before prefill-urls in the GEO assessment workflow.
---

# Classify Scenarios

Derive an application scenario taxonomy from the community documentation index, then classify all questions in `questions.json` into exactly one scenario per question.

## I/O

| Param | Required | Default | Notes |
|---|---|---|---|
| `community` | no | `GEO_COMMUNITY` from `.env` | e.g. "openEuler" |
| `docs_index_url` | no | `DOCS_INDEX_URL` from `.env` | Documentation directory URL (HTML/sitemap.xml/JSON) |
| `batch_size` | no | `80` | Questions per LLM classification call |
| `dry_run` | no | `false` | If true, run classification but do not write to questions.json |
| `force_reclassify` | no | `false` | If true, re-derive taxonomy and reclassify ALL questions (including already-classified); increments `scenario_taxonomy.version` |

**Input**: `output/{community}/questions.json` — must exist  
**Output**: same file, `scenario` field written to unclassified questions; `scenario_taxonomy` written to root  
**Constant**: `SD=.claude/skills/classify-scenarios`

---

## Step 1 — Init

1. Load `.env` from project root.
2. Resolve `community`: caller arg → `GEO_COMMUNITY` from `.env`. Abort if unresolved.
3. Resolve `docs_index_url`: caller arg → `DOCS_INDEX_URL` from `.env`. Abort if unresolved with:
   `ERROR: DOCS_INDEX_URL not set. Provide --docs-index-url or DOCS_INDEX_URL in .env`
4. Load `output/{community}/questions.json`. Abort if file does not exist.
5. Determine `target_questions`:
   - If `force_reclassify=true`: all questions.
   - Otherwise: only questions where `scenario` field is missing or empty string.
6. If `len(target_questions) == 0` → print "All questions already classified. Nothing to do." and exit 0.
7. Log: `Community={community} total={n} unclassified={len(target_questions)} skip={n-len(target_questions)}`

---

## Step 2 — Get Scenario Taxonomy

1. Check if `questions.json` root already contains `scenario_taxonomy.categories` AND `force_reclassify=false`:
   - If yes: use existing taxonomy (skip fetch + extract). Log: `Using existing taxonomy (version=X, N scenarios)`
2. Otherwise:
   a. Run `fetch-docs-index.py`:
      ```
      python3 $SD/scripts/fetch-docs-index.py --url "{docs_index_url}"
      ```
      - exit=0 → stdout is JSON array of pages. Pass to step (b).
      - exit=1 → abort (script already printed `ERROR:` to stderr).
   b. Run `extract-taxonomy.py` (piping pages from step a):
      ```
      python3 $SD/scripts/fetch-docs-index.py --url "{docs_index_url}" | \
        python3 $SD/scripts/extract-taxonomy.py
      ```
      - exit=0 → stdout is taxonomy JSON array `[{"key": ..., "label": ...}]`
      - exit=1 → abort.

---

## Step 3 — Batch Classify Questions

For each batch of `batch_size` questions from `target_questions`:

1. Build classification prompt from `references/prompt-templates.md` `QUESTION_CLASSIFICATION` template.
2. Call LLM with taxonomy context and batch of `{id, question}` pairs.
3. Parse response as `{question_id: scenario_key}` JSON.
4. Validate: unknown keys → default to `"general"` with WARNING.
5. If batch 通用 ratio > 50%: print `WARNING: Batch {i} 通用占比异常高 (X%)`.
6. Collect results into `all_classifications`.

---

## Step 4 — Validate Classification Quality

1. Compute overall 通用 ratio: `general_count / len(all_classifications)`.
2. If ratio > 20%:
   ```
   WARNING: 通用场景占比 X%，建议检查场景分类质量
   ```
   Continue — do not exit 1.
3. Log per-scenario distribution to stderr.

---

## Step 5 — Write Output

1. If `dry_run=true`:
   - Print proposed classifications per question to stderr.
   - Output `{"dry_run": true, "classified": N}` to stdout.
   - Exit 0 without writing.
2. For each question in `target_questions`, set `q["scenario"] = scenario_key` from `all_classifications`.
3. Update `questions.json` root field `scenario_taxonomy`:
   ```json
   {
     "version": 1,
     "extracted_at": "2026-05-28T...",
     "source_url": "https://docs.openeuler.org/",
     "categories": [{"key": "install_deploy", "label": "安装与部署"}, ...]
   }
   ```
   - If re-running without `force_reclassify`: preserve existing `scenario_taxonomy` as-is (already loaded in Step 2).
   - If `force_reclassify=true`: overwrite and increment `version`.
4. Write updated `questions.json` (preserving all other top-level fields).
5. Output summary JSON to stdout:
   ```json
   {"classified": N, "general_count": N, "total_with_scenario": N, "total_questions": N}
   ```
6. Print: `Classified {N} questions | 通用: {N} | Total with scenario: {N}/{total} | dry_run=false`

---

## Step 6 — Error Handling

- `DOCS_INDEX_URL` not reachable → `fetch-docs-index.py` exits 1 → abort; questions.json unchanged.
- LLM returns invalid JSON after retries → `WARNING: Batch {i} skipped`; other batches continue; write partial results.
- `questions.json` missing → `ERROR: questions.json not found: {path}` + exit 1.
- `ANTHROPIC_API_KEY` not set → `ERROR: ANTHROPIC_API_KEY not set` + exit 1.

---

## Prerequisites

| Env Var | Required | Notes |
|---------|----------|-------|
| `GEO_COMMUNITY` | yes (or arg) | Community name |
| `DOCS_INDEX_URL` | yes (or arg) | Community docs directory URL |
| `ANTHROPIC_API_KEY` | yes | For LLM taxonomy extraction and classification |

## Example Calls

```
# Standard run: classify unclassified questions using existing taxonomy if available
/classify-scenarios

# Explicit community and URL
/classify-scenarios community=MindSpore docs_index_url=https://www.mindspore.cn/docs

# Dry run: see what would be classified without writing
/classify-scenarios dry_run=true

# Force re-derive taxonomy and reclassify all questions (e.g. after community switch)
/classify-scenarios force_reclassify=true
```
