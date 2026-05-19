# Domain Discovery Procedure

Used by prefill-urls Step 1 when `official_domains` is empty in questions.json.

## Goal

Populate `official_domains` with verified official domains before URL inference begins.

## Discovery Steps

1. **Check questions.json source_criteria**: The `forum.channel2_forum` field may contain a Discourse URL. Extract the domain (e.g. `https://discuss.openubmc.cn` → `discuss.openubmc.cn`).

2. **LLM inference**: Ask the LLM:
   ```
   List the official domains for {community}. Include:
   - Official documentation/product website
   - Official source code repository (Gitee or GitHub)
   - Official community forum (if any)
   Return as JSON array of domain strings only, e.g. ["docs.openubmc.org", "gitcode.com/openubmc", "discuss.openubmc.cn"].
   Code hosting options: gitcode.com (preferred for domestic CN projects), gitee.com, github.com.
   Do not include third-party sites, CDNs, or mirrors.
   ```

3. **HTTP validation**: Run `python3 $SD/scripts/validate-urls.py` on each inferred domain (prepend `https://`). Keep only domains that return HTTP 2xx/3xx.

4. **Write back**: Update `official_domains` in `assessments/{community}/questions.json` with the verified list before proceeding to Step 2 of the main skill flow.

5. **If still empty after validation**: Abort with the error message specified in the Error Handling section of SKILL.md.
