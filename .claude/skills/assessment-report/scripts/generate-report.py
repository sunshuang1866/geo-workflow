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


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def issue_cell(record: dict) -> str:
    url = record.get("issue_url")
    num = record.get("issue_number")
    iters = record.get("issue_iterations") or 1
    if url and num:
        return f"[#{num}]({url}) ×{iters}"
    return "—"


def platform_cells(record: dict, platforms_present: list[str]) -> list[str]:
    cells = []
    for p in platforms_present:
        pdata = record["platforms"].get(p)
        if pdata is None:
            cells.append("—")
        else:
            cells.append(pdata.get("indicator", "—"))
    return cells


def build_table_row(record: dict, platforms_present: list[str], show_citation: bool = False) -> str:
    qid = record["question_id"]
    question = record["question"]
    pcells = platform_cells(record, platforms_present)
    issue = issue_cell(record)
    severity = record["severity"]
    rate = f"{record['citation_rate']*100:.0f}%" if record.get("citation_rate") is not None else "—"

    cells = [qid, question] + pcells
    if show_citation:
        cells += [rate, severity, issue]
    else:
        cells += [severity, issue]
    return "| " + " | ".join(cells) + " |"


def build_footnotes(records: list[dict], label: str) -> str:
    lines = []
    for r in records:
        urls = r.get("official_urls", [])
        if urls:
            url_strs = ", ".join(f"[{u}]({u})" for u in urls)
            lines.append(f"- **{r['question_id']}**: {url_strs}")
    if not lines:
        return ""
    return f"**官方链接参考：**\n" + "\n".join(lines)


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

    scoring_data = load_json(scoring_file)
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
    # Add any unlisted platforms at the end
    for p in sorted(all_platforms):
        if p not in platforms_present:
            platforms_present.append(p)

    platform_headers = [PLATFORM_DISPLAY.get(p, p) for p in platforms_present]

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
                "questions": not_cited,
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
    header_cols = ["ID", "问题"] + platform_headers

    def table_header(extra_cols: list[str]) -> str:
        cols = header_cols + extra_cols
        sep = ["-" * max(3, len(c)) for c in cols]
        return "| " + " | ".join(cols) + " |\n" + "|-" + "-|-".join(sep) + "-|"

    # no_official_content section
    rows_no = "\n".join(build_table_row(r, platforms_present) for r in no_official)
    footnotes_no = build_footnotes(no_official, "no_official")

    # not_cited section (flat table with citation rate)
    rows_nc = "\n".join(build_table_row(r, platforms_present, show_citation=True) for r in not_cited)
    footnotes_nc = build_footnotes(not_cited, "not_cited")

    # satisfied section
    rows_ok = "\n".join(build_table_row(r, platforms_present, show_citation=True) for r in satisfied)
    footnotes_ok = build_footnotes(satisfied, "satisfied")

    md_lines = [
        f"# GEO 问题集评估报告 — {community}",
        "",
        f"> 生成时间：{generated_at}",
        f"> 引用阈值：≥{pct}% 平台引用视为「满足」",
        f"> 数据来源：`{scoring_file}` · `{questions_file}` · `{issue_map_file}`",
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
        f"平台顺序：{'· '.join(platform_headers)}",
        "",
        "---",
        "",
        f"## 官方内容缺失（P1）— {len(no_official)} 个问题",
        "",
        "> 官方站点尚无覆盖此问题的内容，建议补充文档。",
        "",
        table_header(["严重级别", "Issue"]),
    ]
    if rows_no:
        md_lines.append(rows_no)
    else:
        md_lines.append("*(无)*")
    if footnotes_no:
        md_lines += ["", footnotes_no]
    md_lines += [
        "",
        "---",
        "",
        f"## 有内容未被引用（P0）— {len(not_cited)} 个问题",
        "",
        f"> 官方内容已存在，但未达到 {pct}% 平台引用阈值。",
        "",
        table_header(["引用率", "严重级别", "Issue"]),
    ]
    if rows_nc:
        md_lines.append(rows_nc)
    else:
        md_lines.append("*(无)*")
    if footnotes_nc:
        md_lines += ["", footnotes_nc]
    md_lines += [
        "",
        "---",
        "",
        f"## 引用了官方内容（OK）— {len(satisfied)} 个问题",
        "",
        f"> ≥{pct}% 平台已引用官方链接，状态健康，持续监控即可。",
        "",
        table_header(["引用率", "严重级别", "Issue"]),
    ]
    if rows_ok:
        md_lines.append(rows_ok)
    else:
        md_lines.append("*(无)*")
    if footnotes_ok:
        md_lines += ["", footnotes_ok]
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
