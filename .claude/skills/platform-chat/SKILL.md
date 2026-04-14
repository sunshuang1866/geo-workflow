---
name: platform-chat
description: Samples AI platform responses via browser automation (Playwright + Chromium) for GEO search assessment. Reads questions.json, navigates to ChatGPT, DeepSeek, Gemini, or Qwen web UI, inputs each question, waits for response, extracts reply text and citation links, then outputs responses.json compatible with scoring-engine. Use when ChatGPT API is unavailable or when web-sourced citations are required. Requires a valid session token injected via --inject-token (ChatGPT) or DEEPSEEK_WEB_EMAIL/PASSWORD env vars (DeepSeek, auto-login). Gemini requires no auth — fully anonymous. Do not use for API-based sampling, question generation, scoring, or issue creation.
---

# Platform Chat

Collect AI platform web UI responses (ChatGPT, DeepSeek, Gemini, or Qwen) for each question and write them to `responses.json` in the same format as platform-sampler.

## Prerequisites

- `playwright` Python package installed: `pip3 install playwright`
- Chromium browser downloaded: `python3 -m playwright install chromium`
- **ChatGPT**: Valid session token stored in `assessments/{community}/.chatgpt-session.json`
- **DeepSeek**: Either a session cookie file `assessments/{community}/.deepseek-session.json`  
  OR env vars `DEEPSEEK_WEB_EMAIL` + `DEEPSEEK_WEB_PASSWORD` (auto-login, no manual token needed)
- **Gemini**: Anonymous usage (no citations) OR logged-in via `assessments/{community}/.gemini-session.json` (enables Search Grounding + citations)
- **Qwen**: Either a localStorage token file `assessments/{community}/.qwen-session.json`  
  OR env vars `QWEN_WEB_EMAIL` + `QWEN_WEB_PASSWORD` (auto-login, no CAPTCHA)
- `assessments/{community}/questions.json` (output from get-question skill)

## Inputs

| Param | Required | Default | Notes |
|-------|----------|---------|-------|
| `platform` | No | `chatgpt-web` | `chatgpt-web`, `deepseek-web`, `gemini-web`, or `qwen-web` |
| `community` | No | `GEO_COMMUNITY` from `.env` | e.g. `MindSpore` |
| `questions` | No | all | Comma-separated question IDs: `q_001,q_005` |
| `output_mode` | No | `new_run` | `append` — merge into latest date folder; `new_run` — create `{YYYY-MM-DD}/` |
| `timeout` | No | `90` | Seconds to wait for the platform to finish generating |
| `min_citations` | No | `8` | Minimum citation count per response; sends a follow-up message if not met |

## Step 1: Preflight Check

1. Read `.env` from the project root. Resolve `community`: caller arg → `GEO_COMMUNITY` env var. Abort if unresolved: `"community not set."`.
2. Resolve `platform`: caller arg → default `chatgpt-web`. Supported: `chatgpt-web`, `deepseek-web`, `gemini-web`, `qwen-web`.
3. Run:
   ```bash
   python3 .claude/skills/platform-chat/scripts/check-env.py
   ```
   The script verifies that `playwright` is importable, that the Chromium binary exists, and (for ChatGPT) that a session file is present.
4. **ChatGPT only**: Verify the session token is still valid:
   ```bash
   python3 .claude/skills/platform-chat/scripts/verify-session.py \
     --session assessments/{community}/.chatgpt-session.json
   ```
   On failure, print `SESSION_EXPIRED` and instruct the user to re-inject via `inject-token.py`.
5. **DeepSeek only**: Verify that either `assessments/{community}/.deepseek-session.json` exists  
   OR that `DEEPSEEK_WEB_EMAIL` + `DEEPSEEK_WEB_PASSWORD` are set in the environment.
   **Gemini**: Check if `assessments/{community}/.gemini-session.json` exists.  
   - If present → pass `--session` to `ask-gemini.py` (logged-in mode, citations enabled).  
   - If absent → run anonymous (no citations; note this to the user).
5b. **Qwen only**: Verify that either `assessments/{community}/.qwen-session.json` exists  
   OR that `QWEN_WEB_EMAIL` + `QWEN_WEB_PASSWORD` are set in the environment.
6. Resolve output path:
   - `append`: pick the latest `YYYY-MM-DD` subfolder under `assessments/{community}/`.
   - `new_run`: create `assessments/{community}/{YYYY-MM-DD}/`.
7. Print:
   ```
   Platform: {platform}
   Output: {resolved_output_path} (mode: {output_mode})
   ```

## Step 2: Load Question Set

1. Read `assessments/{community}/questions.json`.
2. If the `questions` param is provided, filter to only the specified IDs. Warn and skip unknown IDs.
3. Print: `Questions loaded: {n}`.

## Step 3: Sample Questions (Sequential)

For each question:

1. Print: `── q_{id}: {question_text[:60]}… ──`
2. Select the script based on `platform`:
   - `chatgpt-web`:
     ```bash
     python3 .claude/skills/platform-chat/scripts/ask-chatgpt.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --session assessments/{community}/.chatgpt-session.json \
       --timeout {timeout}
     ```
   - `deepseek-web` (cookie auth):
     ```bash
     python3 .claude/skills/platform-chat/scripts/ask-deepseek.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --session assessments/{community}/.deepseek-session.json \
       --timeout {timeout}
     ```
   - `deepseek-web` (password auth — no session file needed):
     ```bash
     DEEPSEEK_WEB_EMAIL=... DEEPSEEK_WEB_PASSWORD=... \
     python3 .claude/skills/platform-chat/scripts/ask-deepseek.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --timeout {timeout}
     ```
   - `gemini-web` (anonymous — no citations):
     ```bash
     python3 .claude/skills/platform-chat/scripts/ask-gemini.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --timeout {timeout}
     ```
   - `gemini-web` (logged-in — with Search Grounding citations):
     ```bash
     python3 .claude/skills/platform-chat/scripts/ask-gemini.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --session assessments/{community}/.gemini-session.json \
       --timeout {timeout}
     ```
   - `qwen-web` (token file):
     ```bash
     python3 .claude/skills/platform-chat/scripts/ask-qwen.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --session assessments/{community}/.qwen-session.json \
       --timeout {timeout}
     ```
   - `qwen-web` (password auth — no session file needed):
     ```bash
     QWEN_WEB_EMAIL=... QWEN_WEB_PASSWORD=... \
     python3 .claude/skills/platform-chat/scripts/ask-qwen.py \
       --question "{question_text}" \
       --question-id {question_id} \
       --timeout {timeout}
     ```
3. The script outputs a single JSON object to stdout:
   ```json
   {
     "question_id": "q_001",
     "platform": "chatgpt-web",
     "query": "...",
     "timestamp": "2026-04-02T08:00:00Z",
     "raw_response": "...",
     "citations": ["https://..."],
     "model": "ChatGPT (web)",
     "status": "success"
   }
   ```
   For DeepSeek: `"platform": "deepseek-web"`, `"model": "DeepSeek (web)"`.
   For Gemini: `"platform": "gemini-web"`, `"model": "Gemini (web)"`. Citations are unwrapped from Google search redirect URLs automatically.
   For Qwen: `"platform": "qwen-web"`, `"model": "Qwen (web)"`.
4. On `"status": "error"`, log the `error` field to stderr and continue to the next question.
5. After citation extraction, if `len(citations) < min_citations`, automatically send a follow-up
   message `"请继续补充更多相关参考来源链接，要求总共包含至少8个不同的来源。"`, wait for the response, and
   merge any new (deduplicated) citations into the result.
6. Immediately append the result to the output path after each question (do not batch).
7. Print: `✓ q_{id} {platform} — {len(citations)} citations` or `✗ q_{id} {platform} — {error}`.

## Step 4: Finalize

1. If `output_mode=append`, merge new results into the existing `responses.json`:
   - Key: `(question_id, platform)`. Replace existing entries with new ones; append the rest.
2. Run:
   ```bash
   python3 .claude/skills/platform-sampler/scripts/validate-responses.py \
     < {resolved_output_path}
   ```
3. Print summary:
   ```
   Sampling complete:
     Platform: {platform}
     Questions: {total}
     Successful: {success_count}
     With citations: {cited_count}
     Output: {resolved_output_path}
   ```

## ChatGPT: Obtain and Inject a Session Token

Read `references/get-session-token.md` for the full step-by-step guide.

Quick reference:
```bash
# Inject token once — writes assessments/{community}/.chatgpt-session.json
python3 .claude/skills/platform-chat/scripts/inject-token.py \
  --token "<__Secure-next-auth.session-token value>" \
  --community {community}
```

## Qwen: Auth Options

Qwen requires authentication but has **no CAPTCHA** — automated email/password login works directly.

```bash
# Option A: Password login (auto — no session file required)
export QWEN_WEB_EMAIL=you@example.com
export QWEN_WEB_PASSWORD=yourpassword

# Option B: Token injection (recommended for repeated use)
# 1. Log in at https://chat.qwen.ai/
# 2. DevTools → Application → Local Storage → chat.qwen.ai → copy "token" key value
# 3. Save:
echo '{"token":"<paste-here>"}' > assessments/{community}/.qwen-session.json
```

> **How it works**: Qwen stores auth as a JWT in `localStorage["token"]`. All API requests use
> `Authorization: Bearer <token>`. Token injection sets this before the app loads, making it
> equivalent to a real browser session.

> **Password hashing note**: The login form hashes the password with SHA-256 client-side before
> sending to the API. Playwright handles this automatically since the browser JS runs normally.

## Gemini: Auth Options

Gemini supports two modes:

### Anonymous (no citations)

No setup needed. Gemini uses training data only — no web search, no citation links.

```bash
python3 .claude/skills/platform-chat/scripts/ask-gemini.py \
  --question "What is openEuler?" \
  --question-id q_001
```

### Logged-in (with Search Grounding citations)

With a valid Google session, Gemini performs real-time web search and returns citation links.

**Step 1 — Extract cookies from Chrome (after logging in at gemini.google.com):**

1. Open Chrome → log in at `https://gemini.google.com/`
2. Press `F12` → **Application** tab → **Cookies** → `https://gemini.google.com`
3. Copy the values for these cookies:

| Cookie name | Required |
|---|---|
| `__Secure-1PSID` | **Required** |
| `__Secure-3PSID` | Recommended |
| `__Secure-1PAPISID` | Recommended |
| `__Secure-3PAPISID` | Recommended |

**Step 2 — Inject and verify:**

```bash
python3 .claude/skills/platform-chat/scripts/inject-gemini-session.py \
  --community {community} \
  --1psid  "<__Secure-1PSID value>" \
  --3psid  "<__Secure-3PSID value>" \
  --1papisid "<__Secure-1PAPISID value>" \
  --3papisid "<__Secure-3PAPISID value>"
```

Writes `assessments/{community}/.gemini-session.json` and prints `SESSION_VALID` on success.

**Step 3 — Run with session:**

```bash
python3 .claude/skills/platform-chat/scripts/ask-gemini.py \
  --question "What is openEuler?" \
  --question-id q_001 \
  --session assessments/{community}/.gemini-session.json
```

> **Citation notes**: Gemini wraps source URLs inside Google search redirects
> (`https://www.google.com/search?q=<encoded_url>`). The script automatically extracts
> and decodes the actual target URLs into `citations[]`.
>
> **Session expiry**: Google sessions typically last several weeks. Re-run `inject-gemini-session.py`
> if you encounter `SESSION_EXPIRED`.

## DeepSeek: Auth Options

DeepSeek supports **automatic login** (no manual token extraction needed):

```bash
# Option A: Password login (auto — no session file required)
export DEEPSEEK_WEB_EMAIL=you@example.com
export DEEPSEEK_WEB_PASSWORD=yourpassword

# Option B: Cookie injection (if you prefer cookie-based auth)
# Get ds_session_id from browser DevTools → Application → Cookies → chat.deepseek.com
python3 -c "
import json, sys
cookie = input('Paste ds_session_id value: ')
out = {'cookies': [{'name': 'ds_session_id', 'value': cookie, 'domain': '.chat.deepseek.com', 'path': '/'}]}
open('assessments/{community}/.deepseek-session.json', 'w').write(json.dumps(out))
print('Saved.')
"
```

> **Key difference from ChatGPT**: DeepSeek does not trigger a CAPTCHA on email/password login,  
> so automated sign-in with credentials works directly. No manual browser session export needed.

## Error Handling

* If the script fails with `SESSION_EXPIRED`, stop and direct the user to re-inject the token.
* If the script fails with `INPUT_NOT_FOUND` (selector changed), save a screenshot to `assessments/{community}/debug-{timestamp}.png` and abort with: `"UI may have changed. Check the screenshot and update references/selectors.json."`.
* For DeepSeek: if `LOGIN_FAILED`, check that `DEEPSEEK_WEB_EMAIL` / `DEEPSEEK_WEB_PASSWORD` are correct, or that the account is not locked.
* For Gemini: if `INPUT_NOT_FOUND`, the Quill editor selector may have changed. Save a screenshot with `--screenshot-dir` and update `references/selectors.json`.
* For Qwen: if `SESSION_EXPIRED`, re-extract the token from LocalStorage or re-run with `QWEN_WEB_EMAIL`/`QWEN_WEB_PASSWORD`. If `LOGIN_FAILED`, verify credentials are correct — the login form has no CAPTCHA.
* If the script returns `"status": "timeout"`, log it and continue.
* If more than 50% of questions fail, warn and suggest re-running with `--questions` to retry only failed IDs.
