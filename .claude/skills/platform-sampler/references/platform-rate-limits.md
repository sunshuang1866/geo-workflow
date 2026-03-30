# Platform Rate Limits

Default delay between calls to the same platform: **1 second**.

| Platform | Rate Limit | Recommended Delay | Retry on 429 |
|----------|-----------|-------------------|--------------|
| ChatGPT | Varies by tier (500-10000 RPM) | 1s | Wait 30s, retry once |
| DeepSeek | 60 RPM (free) | 1.5s | Wait 30s, retry once |
| 豆包 (Doubao) | Varies by endpoint | 1s | Wait 30s, retry once |
| Qwen | 60 RPM (free), higher for paid | 1.5s | Wait 30s, retry once |

## Notes

- Rate limits may change. Check platform documentation for latest values.
- For MVP (30-40 questions x 4 platforms = 120-160 calls), sequential sampling with 1s delay takes ~2-3 minutes total.
- If rate-limited (HTTP 429), wait 30 seconds and retry once. If still limited, mark as error and continue.
