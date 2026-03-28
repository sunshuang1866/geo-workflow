---
name: response-parser
description: Parses manually collected AI platform responses from a raw Markdown file into structured responses.json and responses.md. Reads a response.md where each question is prefixed with 'Q:' and platform responses are prefixed with platform names (Doubao, Qwen, 千问, ChatGPT, DeepSeek). Maps questions to IDs from questions.json, extracts citations, runs LLM metadata extraction, and produces the same output format as the platform-sampler skill. Do not use when responses are already in responses.json format; do not use for non-Markdown response files.
---

# Response Parser

Converts a manually collected `response.md` file into the standard `responses.json` + `responses.md` output used by the rest of the GEO pipeline.

## I/O

| Param | Required | Default | Notes |
|---|---|---|---|
| `input_file` | no | `response.md` | Path to the raw response file |
| `questions_file` | no | `questions.json` | Path to question set |
| `community` | no | auto-detected | Community name for metadata extraction |

**Outputs**: `responses.json`, `responses.md` in project root

**Constant**: `SD=.claude/skills/response-parser`

---

## Step 1 — Validate Inputs

1. Verify `input_file` exists. If not, abort: `"Input file not found: {input_file}"`.
2. Verify `questions.json` exists. If not, abort: `"questions.json not found. Run get-question skill first."`.
3. Read `questions.json` and build an `id → question_text` index.
4. Detect `community` name: if not provided, read `CLAUDE-RESUME.md` and extract from the "Project Overview" section, or infer from the first question in questions.json.

---

## Step 2 — Parse Raw Response File

1. Run:
   ```
   python3 $SD/scripts/parse-response-md.py --input "{input_file}" --questions "{questions_file}"
   ```
2. The script outputs a JSON array to stdout. Each element:
   ```json
   {
     "question_id": "q_001",
     "platform": "qwen",
     "query": "...",
     "raw_response": "...",
     "citations": ["https://..."],
     "model": "qwen-plus",
     "status": "success"
   }
   ```
3. **exit=0** → capture as `raw_responses`. Log count: `Parsed {n} responses across {q} questions`.
4. **exit≠0** → display stderr. If the error is `"Unmatched question"`, read `references/format-spec.md` and manually add the missing mapping, then retry.
5. Log any questions with `"platform": "unknown"` as warnings — these need manual Q-ID mapping.

---

## Step 3 — LLM Metadata Extraction

For each response in `raw_responses`, extract structured metadata using:

```
Given the following AI platform response to the question "{query}":

{raw_response}

For the community "{community}", extract:
- mentions_community (bool): Does the response mention {community} by name?
- community_description (string): How is {community} described? (empty string if not mentioned)
- competitors_mentioned (array): Competitor names mentioned in the response
- recommendation_position (string): one of "primary" / "alternative" / "mentioned" / "not_mentioned"
- citations_to_official (array): URLs that point to {community}'s official sites (from the citations list)

Output as JSON only, no prose.
```

Merge the returned fields into each response object. Add `"timestamp"` (current ISO 8601 UTC).

---

## Step 4 — Validate Output

1. Run:
   ```
   python3 .claude/skills/platform-sampler/scripts/validate-responses.py < responses_collection.json
   ```
2. If errors → fix missing fields and re-validate once.
3. Write validated collection to `responses.json`.

---

## Step 5 — Generate responses.md

1. Read `$SD/assets/responses-template.md`.
2. Render using:
   - Coverage matrix: questions × platforms (✅ / —)
   - Per-question blocks: platform name, model, metadata summary, raw_response truncated to 500 chars
3. Write to `responses.md`.
4. Print:
   ```
   Parse complete:
     Questions: {q_count}
     Platforms: {platform_list}
     Total responses: {total}
     Coverage: {pct}% ({total}/{q_count × platform_count})
     Missing: {missing} (see responses.md)
   Output: responses.json, responses.md
   ```

---

## Error Handling

- **Unmatched question text**: Run `python3 $SD/scripts/parse-response-md.py --list-unmatched` to see all unmatched question strings, then update `references/question-id-map.md` with the correct mappings and re-run.
- **Unknown platform name**: Read `references/format-spec.md` for the full alias table. Add the new alias to the script's `PLATFORM_NORM` dict.
- **Duplicate question block**: The parser picks the last occurrence. If multiple blocks exist for the same question+platform, check the raw file for copy-paste errors.
- **Missing questions.json**: Run `/get-question` first to generate the question set.
- **Malformed JSON from LLM metadata**: Retry the metadata extraction call once with stricter instructions (`"Output valid JSON only, starting with '{' — no markdown fences."`).
