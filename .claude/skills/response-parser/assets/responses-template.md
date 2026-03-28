# Platform Responses Report

Generated: {timestamp}

## Coverage Matrix

| Question | {platform_headers} | Coverage |
|----------|{platform_separators}|----------|
{coverage_rows}

**Legend:** ✅ Success | ❌ Error | ⚠️ Empty | — Not sampled

## Summary

- **Questions:** {total_questions}
- **Platforms:** {platform_list}
- **Total Responses:** {total_responses}
- **Coverage:** {coverage_pct}%
- **Missing:** {missing_count} (see below for details)
- **Source:** {source_note}

---

## Responses by Question

{question_blocks}

<!-- Per-question block template:

### {question_id}: {query}

#### {platform_name} (`{model}`)

- **Status:** {status}
- **Mentions Community:** {mentions_community}
- **Recommendation Position:** {recommendation_position}
- **Competitors Mentioned:** {competitors_mentioned}
- **Citations to Official:** {citations_to_official}

> {raw_response_truncated_500}

---

-->
