---
name: platform-sampler
description: Samples AI platform responses for GEO search assessment. Reads questions.json, sends each question to multiple AI platforms (Perplexity, ChatGPT, DeepSeek, Doubao, Qwen) via API, collects raw responses with citations and metadata, then outputs responses.json and responses.md. Supports parallel and sequential sampling modes with rate limiting. Use when a question set is ready and platform responses need to be collected. Do not use for question generation, scoring, or improvement suggestion generation.
---

# Platform Sampler

Collect raw AI platform responses for each question in the question set, across all configured platforms.

## Prerequisites

- `.env` file with API tokens (at least 2 platforms required)
- `questions.json` in the project root (output from get-question skill)

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root to load API tokens.
2. Detect available platforms by checking which tokens are non-empty:
   - `PERPLEXITY_API_KEY` → Perplexity
   - `OPENAI_API_KEY` → ChatGPT
   - `DEEPSEEK_API_KEY` → DeepSeek
   - `DOUBAO_API_KEY` → 豆包
   - `QWEN_API_KEY` → Qwen
3. If fewer than 2 platforms are available, abort with an error message listing which tokens are missing.
4. Print detected platforms to stdout.

**Step 2: Load Question Set**

1. Read `questions.json` from the project root.
2. Run `python3 scripts/validate-input.py < questions.json` to verify the input format.
3. If validation fails, display the error and abort.
4. Print question count to stdout.

**Step 3: Sample Each Platform**

For each question in `questions.json`, for each available platform:

1. Construct the query. Use the question text directly — do not modify or translate.
2. Execute `python3 scripts/sample-platform.py --platform {name} --api-key {key} --query "{question}" --question-id {id}`.
3. The script returns a JSON object to stdout with fields:
   ```json
   {
     "question_id": "q_001",
     "platform": "perplexity",
     "query": "主流深度学习框架有哪些",
     "timestamp": "2026-03-10T08:00:00Z",
     "raw_response": "...",
     "citations": [],
     "model": "sonar"
   }
   ```
4. Append each result to the responses collection.
5. Rate limiting: wait 1 second between calls to the same platform. Read `references/platform-rate-limits.md` for platform-specific limits.

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

**Step 5: Validate and Output**

1. Run `python3 scripts/validate-responses.py < responses_collection.json` to verify completeness.
2. The script checks:
   - Every question has responses from all available platforms
   - No empty raw_response fields
   - All required metadata fields present
   - Reports missing combinations as warnings
3. Write the validated collection to `responses.json` in the project root.
4. Generate `responses.md` using the template in `assets/responses-template.md`:
   - Group by question, then by platform
   - Show raw response (truncated to 500 chars) + metadata summary
   - Include a coverage matrix at the top
5. Print a summary to stdout:
   ```
   Sampling complete:
     Questions: {total_questions}
     Platforms: {platform_list}
     Total responses: {total_responses}
     Coverage: {coverage_pct}%
     Missing: {missing_count} (see responses.md for details)
   Output: responses.json, responses.md
   ```

## Error Handling

* If a platform API call fails (timeout, auth error, rate limit), log the error to stderr, mark the response as `"status": "error"` with the error message, and continue with the next call. Do not abort the entire sampling run.
* If a platform returns an empty response, mark it as `"status": "empty"` and continue.
* If `questions.json` is missing, abort with a clear error: "questions.json not found. Run get-question skill first."
* If rate-limited by a platform (HTTP 429), wait 30 seconds and retry once. If still rate-limited, mark as error and continue.
* After all sampling, if more than 50% of responses are errors, warn the user and suggest checking API tokens.
