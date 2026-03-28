# response.md Format Specification

## Block Structure

Each file contains one or more **question blocks** followed by **platform response blocks**.

```
Q:<question_text>
<platform_name>：<optional_inline_response>
<response_body_continues_here>

<platform_name>：<optional_inline_response>
<response_body_continues_here>

Q：<next_question_text>
...
```

---

## Question Marker

| Pattern | Examples |
|---------|---------|
| `Q:text` | `Q:openUBMC的Redfish接口规范是什么？` |
| `Q：text` | `Q：openUBMC社区中可以通过PR评论触发哪些机器人自动化操作？` |
| `Q；text` | `Q；openUBMC如何适配MiniSAS接口及其下挂接的硬盘？` |

The question text runs to end of line. Blocks can be separated by divider lines (`---`, `====`, `---------`); these are ignored by the parser.

---

## Platform Marker

Must appear at the **start of a line** (no leading whitespace).

| Raw name | Normalized | Model |
|----------|-----------|-------|
| `Doubao` / `doubao` | `doubao` | `doubao-1.5-pro-32k` |
| `Qwen` / `qwen` / `千问` | `qwen` | `qwen-plus` |
| `ChatGPT` / `chatgpt` | `chatgpt` | `gpt-4o` |
| `DeepSeek` / `deepseek` | `deepseek` | `deepseek-chat` |
| `Perplexity` / `perplexity` | `perplexity` | `sonar` |

Delimiter after name is `：` (Chinese full-width colon) or `:` (ASCII colon). Text on the same line as the marker is included as the start of the response.

---

## Question ID Matching

The parser attempts to match question text to `questions.json` via:
1. Exact string match
2. Substring containment (either direction)

If no match is found, `question_id` is set to `"q_unknown"` and a warning is emitted.

To manually fix: add the mapping to `references/question-id-map.md` and update the `build_question_index` function, or rename the question in the source file to match exactly.

---

## Known Edge Cases

- **Q；** (Chinese semicolon): treated the same as `Q:`.
- **Inline response**: text after `Platform：` on the same line is prepended to the response body.
- **Duplicate platform block** for same question: last one wins.
- **No platform blocks** under a Q: emits a warning; question is skipped.
- **Divider lines** (`---`, `======`) between question blocks are included in block text but stripped from response content by the platform pattern split.
