# Platform Indicator Rules

Rules for assigning emoji indicators to per-platform citation results in the assessment report.

## Indicator Mapping

| Condition | Indicator | Meaning |
|-----------|-----------|---------|
| `cited: true` | ✅ | Platform cited at least one official URL (exact or domain match) |
| `cited: false` AND `official_urls` non-empty | ❌ | Official content exists but platform did not cite it |
| Question has `no_official_content` status | — | No official URLs to cite; not applicable |

## Display Format

In Markdown tables, each platform column shows the indicator only.

In JSON output, each platform entry includes both the boolean `cited` field and the string `indicator` field:

```json
{
  "qwen": {"cited": true,  "indicator": "✅"},
  "chatgpt": {"cited": false, "indicator": "❌"},
  "doubao": {"cited": false, "indicator": "—"}
}
```

## Column Order

Platforms appear in a fixed canonical order in the Markdown table:
`豆包 | Qwen | ChatGPT | DeepSeek`

Use the platform names as they appear in `scoring-results.json`. Map known aliases:
- `doubao` → `豆包`
- `qwen` → `Qwen`
- `chatgpt` → `ChatGPT`
- `deepseek` → `DeepSeek`
