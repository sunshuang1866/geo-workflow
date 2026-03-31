#!/usr/bin/env python3
"""
generate-report.py — Generate assessment-report.json and assessment-report.md
from scoring-results.json, questions.json, and issue-map.json.

Usage:
  python3 generate-report.py <scoring_file> <questions_file> <issue_map_file> <output_dir>
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PLATFORM_ORDER = ["doubao", "qwen", "chatgpt", "deepseek"]
PLATFORM_DISPLAY = {"doubao": "豆包", "qwen": "Qwen", "chatgpt": "ChatGPT", "deepseek": "DeepSeek"}
CITATION_THRESHOLD = 0.9
SCRIPT_DIR = Path(__file__).parent

# Improvement action taxonomy
ACTION_TAXONOMY = [
    {
        "key": "create_dedicated_doc",
        "title": "补充专题文档页面",
        "description": "官方内容分散在新闻、Issue、邮件列表中，缺少独立的文档/教程/FAQ 页面，AI 平台难以引用。",
    },
    {
        "key": "optimize_structured_data",
        "title": "添加结构化数据标记",
        "description": "页面存在但缺少 Schema.org / JSON-LD 结构化标记，AI 平台无法解析内容语义，降低引用概率。",
    },
    {
        "key": "restructure_content",
        "title": "重构内容结构与关键词",
        "description": "页面存在但内容层级混乱、关键词不匹配用户搜索意图，AI 平台难以识别为权威来源。",
    },
    {
        "key": "improve_seo_metadata",
        "title": "优化 SEO 元数据",
        "description": "页面 title/description/canonical URL 不准确或缺失，影响搜索引擎和 AI 平台的索引质量。",
    },
    {
        "key": "submit_to_platforms",
        "title": "针对特定平台提交收录",
        "description": "多数平台已引用，但个别平台漏引，需向目标平台主动提交站点地图或内容收录申请。",
    },
    {
        "key": "add_multilingual",
        "title": "添加多语言页面",
        "description": "仅有中文页面，国际化 AI 平台（ChatGPT 等）倾向引用英文源，需补充英文内容。",
    },
]
ACTION_KEY_ORDER = [a["key"] for a in ACTION_TAXONOMY]
ACTION_META = {a["key"]: a for a in ACTION_TAXONOMY}


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def issue_cell(record: dict) -> str:
    url = record.get("issue_url")
    num = record.get("issue_number")
    if url and num:
        return f"[#{num}]({url})"
    return "—"


def issue_created_cell(record: dict) -> str:
    created = record.get("issue_created_at")
    if not created:
        return "—"
    # Keep only MM-DD (drop the year prefix "YYYY-")
    parts = created.split("-")
    return "-".join(parts[1:]) if len(parts) >= 3 else created


def issue_comments_cell(record: dict) -> str:
    iters = record.get("issue_iterations")
    if iters is None:
        return "—"
    # iterations: 1 = created only (0 comments), 2+ = has updates
    comments = max(0, iters - 1)
    return str(comments)


def platform_cells(record: dict, platforms_present: list) -> list:
    cells = []
    for p in platforms_present:
        pdata = record["platforms"].get(p)
        if pdata is None:
            cells.append("—")
        else:
            cells.append(pdata.get("indicator", "—"))
    return cells


def build_table_row(record: dict, platforms_present: list, show_citation: bool = False) -> str:
    qid = record["question_id"]
    question = record["question"]
    pcells = platform_cells(record, platforms_present)
    issue = issue_cell(record)
    created = issue_created_cell(record)
    comments = issue_comments_cell(record)
    severity = record["severity"]
    rate = f"{record['citation_rate']*100:.0f}%" if record.get("citation_rate") is not None else "—"

    cells = [qid, question] + pcells
    if show_citation:
        cells += [rate, severity, issue, created, comments]
    else:
        cells += [severity, issue, created, comments]
    return "| " + " | ".join(cells) + " |"


def build_question_index(records: list) -> str:
    """Full question index table shown before the summary section."""
    lines = [
        "## 问题清单",
        "",
        "| ID | 问题 | 官方链接 |",
        "|----|------|---------|",
    ]
    for r in records:
        qid = r["question_id"]
        question = r["question"]
        urls = r.get("official_urls", [])
        url_str = " ".join(f"[链接]({u})" for u in urls) if urls else "—"
        lines.append(f"| {qid} | {question} | {url_str} |")
    return "\n".join(lines)


def assign_action_keys(record: dict) -> list:
    """Assign improvement action keys to a not_cited P0 question (multi-label)."""
    citation_rate = record.get("citation_rate") or 0.0
    official_urls = record.get("official_urls", [])
    platforms = record.get("platforms", {})
    total = record.get("total_platforms") or len(platforms)
    cited_count = record.get("cited_count") or 0
    not_cited_platforms = [p for p, d in platforms.items() if not d.get("cited", False)]

    action_keys = []

    # Detect non-doc official URLs (news pages, issue search, gitee search)
    non_doc_url_signals = ["news/detail", "issues?q=", "activities", "version-updates",
                            "sig/meeting-guide", "mailweb", "/sig/", "/contribution"]
    is_non_doc = any(
        any(sig in url for sig in non_doc_url_signals)
        for url in official_urls
    )

    if citation_rate == 0.0:
        if is_non_doc:
            # Content is in news/issues/activities - needs dedicated doc
            action_keys.append("create_dedicated_doc")
            action_keys.append("optimize_structured_data")
        else:
            # Proper doc exists but not cited at all
            action_keys.append("restructure_content")
            action_keys.append("optimize_structured_data")
    elif citation_rate > 0.0:
        not_cited_count = total - cited_count
        # Check if mostly international platforms are missing
        intl_platforms = {"chatgpt", "gemini"}
        intl_missing = intl_platforms.intersection(set(not_cited_platforms))

        if not_cited_count == 1:
            action_keys.append("submit_to_platforms")
            if intl_missing:
                action_keys.append("add_multilingual")
        else:
            action_keys.append("improve_seo_metadata")
            if is_non_doc:
                action_keys.append("create_dedicated_doc")
            else:
                action_keys.append("restructure_content")

    return action_keys if action_keys else ["improve_seo_metadata"]


def build_action_groups(not_cited_records: list) -> list:
    """Build action groups for P0 not_cited questions."""
    # Assign action keys to each record
    enriched = []
    for r in not_cited_records:
        keys = assign_action_keys(r)
        enriched.append({**r, "action_keys": keys})

    # Group by action key
    groups_map = {}
    for r in enriched:
        for key in r["action_keys"]:
            if key not in groups_map:
                groups_map[key] = []
            groups_map[key].append(r)

    # Build group list in taxonomy order
    groups = []
    for key in ACTION_KEY_ORDER:
        if key not in groups_map:
            continue
        qs = groups_map[key]
        rates = [q["citation_rate"] or 0.0 for q in qs]
        avg_rate = sum(rates) / len(rates) if rates else 0.0

        # Collect deduplicated issue refs
        issue_refs = {}
        for q in qs:
            num = q.get("issue_number")
            url = q.get("issue_url")
            if num and url and num not in issue_refs:
                issue_refs[num] = url

        meta = ACTION_META[key]
        groups.append({
            "action_key": key,
            "action_title": meta["title"],
            "action_description": meta["description"],
            "questions": qs,
            "issue_refs": [{"number": n, "url": u} for n, u in sorted(issue_refs.items())],
            "avg_citation_rate": avg_rate,
            "unique_question_count": len(qs),
        })

    # Sort by avg_citation_rate ascending (worst first)
    groups.sort(key=lambda g: g["avg_citation_rate"])
    return groups


def render_grouped_not_cited(not_cited_records: list, platforms_present: list,
                              platform_headers: list) -> str:
    """Render the P0 not_cited section sub-grouped by action type."""
    groups = build_action_groups(not_cited_records)
    lines = []

    def table_header_nc() -> str:
        cols = ["ID", "问题"] + platform_headers + ["引用率", "Issue", "创建时间", "评论数"]
        sep = ["-" * max(3, len(c)) for c in cols]
        return "| " + " | ".join(cols) + " |\n" + "|-" + "-|-".join(sep) + "-|"

    for g in groups:
        lines.append(f"### {g['action_title']}")
        lines.append("")
        lines.append(f"> {g['action_description']}")
        lines.append("")
        lines.append(table_header_nc())
        for r in g["questions"]:
            rate = f"{r['citation_rate']*100:.0f}%" if r.get("citation_rate") is not None else "—"
            pcells = platform_cells(r, platforms_present)
            issue = issue_cell(r)
            created = issue_created_cell(r)
            comments = issue_comments_cell(r)
            cells = [r["question_id"], r["question"]] + pcells + [rate, issue, created, comments]
            lines.append("| " + " | ".join(cells) + " |")

        # Collect all official URLs for questions in this group
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 5:
        print("Usage: generate-report.py <scoring_file> <questions_file> <issue_map_file> <output_dir>",
              file=sys.stderr)
        sys.exit(1)

    scoring_file, questions_file, issue_map_file, output_dir = sys.argv[1:]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run build-report.py to get merged records
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "build-report.py"),
         scoring_file, questions_file, issue_map_file],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: build-report.py failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    records = json.loads(result.stdout)

    questions_data = load_json(questions_file)
    community = questions_data.get("community", "Unknown")
    generated_at = datetime.now(timezone.utc).isoformat()

    # Group
    no_official = [r for r in records if r["status"] == "no_official_content"]
    not_cited = [r for r in records if r["status"] == "not_cited"]
    satisfied = [r for r in records if r["status"] == "satisfied"]

    # Determine platforms present across all records
    all_platforms = set()
    for r in records:
        all_platforms.update(r["platforms"].keys())
    platforms_present = [p for p in PLATFORM_ORDER if p in all_platforms]
    for p in sorted(all_platforms):
        if p not in platforms_present:
            platforms_present.append(p)
    platform_headers = [PLATFORM_DISPLAY.get(p, p) for p in platforms_present]

    # Build action groups for JSON output
    action_groups = build_action_groups(not_cited)
    not_cited_with_actions = []
    for r in not_cited:
        keys = assign_action_keys(r)
        not_cited_with_actions.append({**r, "action_keys": keys})

    # ── JSON output ──────────────────────────────────────────────────────────
    json_output = {
        "metadata": {
            "community": community,
            "generated_at": generated_at,
            "total_questions": len(records),
            "total_platforms": len(platforms_present),
            "citation_threshold": CITATION_THRESHOLD,
            "source_files": {
                "scoring": scoring_file,
                "questions": questions_file,
                "issue_map": issue_map_file,
            },
        },
        "summary": {
            "by_category": {
                "no_official_content": len(no_official),
                "not_cited": len(not_cited),
                "satisfied": len(satisfied),
            },
            "by_severity": {
                "P0": len(not_cited),
                "P1": len(no_official),
                "OK": len(satisfied),
            },
        },
        "categories": {
            "no_official_content": {
                "title": "官方内容缺失",
                "description": "官方站点尚无覆盖此问题的内容",
                "questions": no_official,
            },
            "not_cited": {
                "title": "有内容未被引用",
                "description": "官方内容已存在，但未达到 90% 平台引用阈值",
                "questions": not_cited_with_actions,
                "action_groups": action_groups,
            },
            "satisfied": {
                "title": "引用了官方内容",
                "description": "≥90% 平台引用了官方链接，状态健康",
                "questions": satisfied,
            },
        },
    }

    json_path = output_dir / "assessment-report.json"
    json_path.write_text(json.dumps(json_output, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── Markdown output ──────────────────────────────────────────────────────
    pct = int(CITATION_THRESHOLD * 100)

    def table_header(extra_cols: list) -> str:
        cols = ["ID", "问题"] + platform_headers + extra_cols
        sep = ["-" * max(3, len(c)) for c in cols]
        return "| " + " | ".join(cols) + " |\n" + "|-" + "-|-".join(sep) + "-|"

    question_index = build_question_index(records)
    rows_no = "\n".join(build_table_row(r, platforms_present) for r in no_official)
    grouped_not_cited_md = render_grouped_not_cited(not_cited, platforms_present, platform_headers)
    rows_ok = "\n".join(build_table_row(r, platforms_present, show_citation=True) for r in satisfied)

    md_lines = [
        f"# GEO 问题集评估报告 — {community}",
        "",
        f"> 生成时间：{generated_at}",
        f"> 引用阈值：≥{pct}% 平台引用视为「满足」",
        f"> 数据来源：`{scoring_file}` · `{questions_file}` · `{issue_map_file}`",
        "",
        "---",
        "",
        question_index,
        "",
        "---",
        "",
        "## 概况",
        "",
        "| 类别 | 问题数 |",
        "|------|--------|",
        f"| 官方内容缺失（P1）| {len(no_official)} |",
        f"| 有内容未被引用（P0）| {len(not_cited)} |",
        f"| 引用了官方内容（OK）| {len(satisfied)} |",
        f"| **合计** | **{len(records)}** |",
        "",
        "### 严重级别分布",
        "",
        "| 级别 | 问题数 |",
        "|------|--------|",
        f"| P0 | {len(not_cited)} |",
        f"| P1 | {len(no_official)} |",
        f"| OK | {len(satisfied)} |",
        "",
        "### 平台图例",
        "",
        "| 指标 | 含义 |",
        "|------|------|",
        "| ✅ | 平台回答中引用了至少一条官方链接 |",
        "| ❌ | 官方内容存在，但平台未引用 |",
        "| — | 官方站点尚无相关内容，不适用 |",
        "",
        "平台顺序：" + "· ".join(platform_headers),
        "",
        "---",
        "",
        f"## 官方内容缺失（P1）— {len(no_official)} 个问题",
        "",
        "> 官方站点尚无覆盖此问题的内容，建议补充文档。",
        "",
        table_header(["严重级别", "Issue", "创建时间", "评论数"]),
    ]
    if rows_no:
        md_lines.append(rows_no)
    else:
        md_lines.append("*(无)*")
    md_lines += [
        "",
        "---",
        "",
        f"## 有内容未被引用（P0）— {len(not_cited)} 个问题",
        "",
        f"> 官方内容已存在，但未达到 {pct}% 平台引用阈值。按改进措施分组，同一 Issue 下的问题需要相同的改进行动。",
        "",
        grouped_not_cited_md,
        "---",
        "",
        f"## 引用了官方内容（OK）— {len(satisfied)} 个问题",
        "",
        f"> ≥{pct}% 平台已引用官方链接，状态健康，持续监控即可。",
        "",
        table_header(["引用率", "严重级别", "Issue", "创建时间", "评论数"]),
    ]
    if rows_ok:
        md_lines.append(rows_ok)
    else:
        md_lines.append("*(无)*")
    md_lines += ["", "---", "", "*由 GEO Search Assessment 系统自动生成*", ""]

    md_path = output_dir / "assessment-report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Assessment report generated:")
    print(f"  Community: {community}")
    print(f"  Total questions: {len(records)}")
    print(f"  官方内容缺失:    {len(no_official)} questions (P1)")
    print(f"  有内容未被引用:  {len(not_cited)} questions (P0)")
    print(f"  引用了官方内容:  {len(satisfied)} questions (OK)")
    print(f"  Output: {json_path}")
    print(f"          {md_path}")


if __name__ == "__main__":
    main()
