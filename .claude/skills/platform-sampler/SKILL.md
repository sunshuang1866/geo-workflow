---
name: platform-sampler
description: Samples AI platform responses for GEO search assessment. Reads questions.json, sends each question to multiple AI platforms (ChatGPT, DeepSeek, Doubao, Qwen, Gemini) via API, collects raw responses with citations and metadata, then outputs responses.json. Supports platform and question filtering, batched output (5 questions per batch), and citation-required mode. Use when a question set is ready and platform responses need to be collected. Do not use for question generation, scoring, or improvement suggestion generation.
---

# Platform Sampler

Collect raw AI platform responses for each question in the question set, across configured platforms.

## Prerequisites

- `.env` file with API tokens (at least one platform required)
- `assessments/{community}/questions.json` (output from get-question skill)

## Inputs

| Param | Required | Default | Notes |
|-------|----------|---------|-------|
| `community` | No | `GEO_COMMUNITY` from `.env` | Community name, e.g. `MindSpore`. Determines the data path under `assessments/`. |
| `platforms` | No | all detected | Comma-separated list of platforms to sample: `chatgpt`, `deepseek`, `doubao`, `qwen`, `gemini` |
| `questions` | No | all | Comma-separated list of question IDs to sample: e.g. `q_001,q_005,q_012` |
| `output_mode` | No | `new_run` | `append` — write into the latest existing date folder; `new_run` — create a new `{YYYY-MM-DD}` date folder |

### Output Mode

| Mode | Behavior |
|------|----------|
| `append` | Find the latest date subfolder under `assessments/{community}/` (e.g. `2026-03-28/`). Load its `responses.json`, merge new results (replace entries with same `question_id` + `platform`, append the rest). If no date folder exists, fall back to `new_run`. |
| `new_run` | Create `assessments/{community}/{YYYY-MM-DD}/` and write a fresh `responses.json` there. If the folder already exists (same-day re-run), append to the existing file. |

## Procedures

### CLI Batch Entry (implemented)

Use the batch runner to execute multi-question x multi-platform sampling directly:

```bash
python3 .claude/skills/platform-sampler/scripts/run-sampler.py --community MindSpore
python3 .claude/skills/platform-sampler/scripts/run-sampler.py --community MindSpore --questions q_001,q_005 --platforms deepseek,qwen
python3 .claude/skills/platform-sampler/scripts/run-sampler.py --community MindSpore --output-mode append
```

Notes:
- Runs up to 5 questions in parallel per group (`--group-size`, default 5).
- Calls platforms sequentially within each question task, with same-platform rate-limit spacing.
- Writes to `{community}/{date}/responses.json` in object format: `{ metadata, responses }`.
- Merges by `(question_id, platform)` to support append and same-day reruns.

**Step 1: Load Configuration**

1. Read `.env` from the project root. Resolve `community`: caller arg → `GEO_COMMUNITY` from `.env`. Abort if still unresolved: `"community not set. Provide as argument or set GEO_COMMUNITY in .env."`
2. Each platform is configured by two vars:
   - `{PLATFORM}_API_KEY` — required for the platform to be active
   - `{PLATFORM}_BASE_URL` — optional; overrides the built-in default endpoint
2. Detect available platforms by checking which API keys are non-empty:
   - `CHATGPT_API_KEY` → `chatgpt`
   - `DEEPSEEK_API_KEY` → `deepseek`
   - `DOUBAO_API_KEY` → `doubao`
   - `QWEN_API_KEY` → `qwen`
   - `GEMINI_API_KEY` → `gemini`
3. If the `platforms` param is provided, filter detected platforms to only those listed. If a requested platform has no token, warn and skip it.
4. If no platforms remain after filtering, abort: `"No configured platforms available. Check .env tokens."`
5. Resolve output path based on `output_mode`:
   - `append`: scan `assessments/{community}/` for date-named subfolders (`YYYY-MM-DD`), pick the latest one. Target: `{latest_date_folder}/responses.json`. If no date folder exists, fall back to `new_run`.
   - `new_run`: target is `assessments/{community}/{YYYY-MM-DD}/responses.json`. Create the date folder if it does not exist. If it already exists (same-day re-run), load existing file as `existing_responses` for merging.
   - If `output_mode=append` and the target file exists, load its contents as `existing_responses` for later merging.
6. Print active platforms and output target to stdout:
   ```
   Platforms: chatgpt, deepseek, doubao, qwen, gemini
   Output: {resolved_output_path} (mode: {output_mode})
   ```

**Step 2: Load Question Set**

1. Read `assessments/{community}/questions.json`.
2. Run `python3 scripts/validate-input.py < questions.json` to verify the input format.
3. If validation fails, display the error and abort.
4. If the `questions` param is provided, filter the question list to only the specified IDs. If any requested ID is not found in the file, warn and skip it.
5. Print final question count to stdout:
   ```
   Questions loaded: {n} (filtered from {total} total)
   Platforms: {platform_list}
   ```

**Step 3: Sample Questions (5 parallel, per-question flush)**

Partition the filtered question list into groups of 5 for parallel execution.

For each group of 5 questions (or fewer for the last group):

1. Print group header:
   ```
   ── Group {n}/{total_groups} ({id_list}) ──
   ```

2. **Launch 5 questions in parallel.** For each question, sequentially call all active platforms:
   - Construct the query using the question text directly — do not modify or translate.
   - Execute:
     ```
     python3 scripts/sample-platform.py \
       --platform {name} \
       --query "{question}" \
       --question-id {id}
     ```
   - The script auto-loads `.env` from the project root and reads `{PLATFORM}_API_KEY` and `{PLATFORM}_BASE_URL`.
   - The script always instructs the model to include reference links in its response (via system prompt, minimum 7 links required).
   - The script returns a JSON object to stdout:
     ```json
     {
       "question_id": "q_001",
       "platform": "chatgpt",
       "query": "主流深度学习框架有哪些",
       "timestamp": "2026-03-10T08:00:00Z",
       "raw_response": "...",
       "citations": ["https://...", "https://..."],
       "model": "gpt-5.4",
       "status": "success"
     }
     ```
   - Rate limiting: wait 1 second between calls to the same platform. Read `references/platform-rate-limits.md` for platform-specific limits.

3. **Per-question flush**: As soon as one question finishes all its platform calls, immediately append its results to the resolved output path (do not wait for the other 4 questions in the group).

4. Print the question result inline upon completion:
   ```
   ✓ q_001 MindSpore 支持哪些安装方式？ — 豆包✓ Qwen✓ ChatGPT✓ DeepSeek✓
   ✗ q_002 MindSpore 和 PyTorch 相比… — 豆包✓ Qwen✗ ChatGPT✓ DeepSeek✓
   ```

5. After all 5 questions in the group complete, print group summary:
   ```
   Group {n} done: {success}/{total} questions, {response_count} responses written
   ```

**Step 4: Post-Process Responses**

1. For each response, prompt the LLM to extract structured metadata:
   ```
   Given the following AI platform response to the question "{query}":

   {raw_response}

   For the community "{community}", extract:
   - mentions_community (bool): Does the response mention {community} by name?
   - community_description (string): How is {community} described? (empty if not mentioned)
   - competitors_mentioned (array): List competitor names mentioned (e.g., TensorFlow, PyTorch)
   - recommendation_position (string): "primary" / "alternative" / "mentioned" / "not_mentioned"
   - citations_to_official (array): URLs pointing to {community}'s official sites (from citations list)

   Output as JSON.
   ```
2. Merge the extracted metadata into each response object.

**Step 5: Merge and Finalize**

1. If `existing_responses` was loaded in Step 1 (append mode or same-day new_run):
   - Build a lookup from existing responses keyed by `(question_id, platform)`.
   - For each new response, replace the existing entry with the same key, or append if no match.
   - Write the merged result to the resolved output path.
2. Otherwise: write only the new responses.
3. Run `python3 scripts/validate-responses.py < {resolved_output_path}` to verify completeness.
4. The script checks:
   - Every question has responses from all active platforms
   - No empty `raw_response` fields
   - All required metadata fields present
   - Reports missing combinations as warnings
5. Print final summary:
   ```
   Sampling complete:
     Mode: {output_mode}
     Questions: {total_questions}
     Platforms: {platform_list}
     Total responses: {total_responses} (new: {new_count}, existing: {kept_count})
     With citations: {cited_count} / {total_responses}
     Missing: {missing_count}
   Output: {resolved_output_path}
   ```

## Error Handling

* If a platform API call fails (timeout, auth error, rate limit), log the error to stderr, mark the response as `"status": "error"` with the error message, and continue with the next call. Do not abort the entire sampling run.
* If a platform returns an empty response, mark it as `"status": "empty"` and continue.
* If `assessments/{community}/questions.json` is missing, abort with a clear error: "questions.json not found for community '{community}'. Run get-question skill first."
* If rate-limited by a platform (HTTP 429), wait 30 seconds and retry once. If still rate-limited, mark as error and continue.
* After all sampling, if more than 50% of responses are errors, warn the user and suggest checking API tokens.
