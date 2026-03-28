#!/usr/bin/env python3
"""Generate Issue payloads from scoring-results.json suggestions (P0/P1 filter).
Dry-run: prints all payloads and writes created-issues.json without calling API.
"""
import json, datetime

BASE = "/root/workspace/GEO-Search-Assessment/MindSpore/version3"

with open(f"{BASE}/scoring-results.json", encoding="utf-8") as f:
    data = json.load(f)

suggestions = [s for s in data.get("suggestions", []) if s.get("severity") in ("P0", "P1")]

PHENOMENON_LABELS = {
    "A": "现象 A（官网无内容）",
    "C": "现象 C（引用错误/幻觉）",
    "E": "现象 E（官方引用比例低）",
}

CATEGORY_LABELS = {
    "content":      "content",
    "correction":   "correction",
    "optimization": "optimization",
    "seo":          "seo",
}

def make_body(s):
    sev = s["severity"]
    cat = s["category"]
    ct  = s["citation_type"]
    qids = s["question_ids"]
    platform = s.get("platform", "qwen")
    catalog_refs = ", ".join(s.get("catalog_refs", []))
    is_origin = s.get("is_content_origin", False)
    affected = s.get("affected_count", len(qids))
    suggestion_text = s["suggestion_text"]

    # Build question list
    with open(f"{BASE}/scoring-results.json", encoding="utf-8") as f:
        rd = json.load(f)
    qmap = {r["question_id"]: r["question"] for r in rd["results"]}
    q_lines = "\n".join(f"- `{qid}` {qmap.get(qid, '')}" for qid in qids)

    phenom_label = PHENOMENON_LABELS.get(ct, f"现象 {ct}")
    origin_note = "✅ 是内容源问题（建议修复官方内容本身）" if is_origin else "⚠️ 单平台检出（建议优先修复官方文档后观察多平台效果）"

    body = f"""## GEO 改进建议

**严重级别**: {sev}
**现象类型**: {phenom_label}
**影响平台**: {platform}
**影响问题数**: {affected}
**内容源判定**: {origin_note}

### 涉及问题

{q_lines}

### 问题描述

{suggestion_text}

### 影响范围

- **涉及平台**: {platform}
- **现象分类**: {phenom_label}
- **GEO 目录参考**: `{catalog_refs}`

### 建议改进措施

{suggestion_text}

### 参考信息

- **分析来源**: GEO Search Assessment 自动评分（MindSpore version3，单平台 Qwen）
- **评估日期**: 2026-03-25
- **关联问题 ID**: {', '.join(qids)}
- **评分结果文件**: `MindSpore/version3/scoring-results.json`

---
> 此 Issue 由 GEO Search Assessment 系统自动生成。建议在人工核实评分结果后再提交。
"""
    return body.strip()


TITLE_MAP = {
    "s_001": "补充竞品对比/选型/行业定位类问题的官方内容（7题内容空白）",
    "s_002": "修正模型转换API幻觉：澄清export_from_torch/export_from_onnx不存在",
    "s_003": "创建结构化SIG注册表页面，消除例会安排幻觉（5题受影响）",
    "s_004": "补充邮件列表平台说明，消除OpenI/mailweb.mindspore.cn混淆（3题受影响）",
    "s_005": "创建官方活动日历页面，防止AI平台生成虚假活动信息",
    "s_006": "在MindSpore Serving文档中声明vLLM兼容性状态",
    "s_007": "修正贡献指南中的OpenI治理模式错误引用",
    "s_008": "发布MindSpore Lite官方基准测试报告，终止性能数字幻觉",
    "s_009": "创建国际开源峰会参与记录页面，防止KubeCon等信息被捏造",
    "s_010": "提升安装/部署/选型类文档深度，降低AI平台对第三方博客的依赖（8题P1）",
}

issues = []
for s in suggestions:
    sid = s["suggestion_id"]
    sev = s["severity"]
    cat = s["category"]
    title = f"[GEO-{sev}] {TITLE_MAP.get(sid, s['suggestion_text'][:60])}"
    body = make_body(s)
    labels = f"geo-improvement,{sev},{CATEGORY_LABELS.get(cat, cat)}"
    payload = {
        "title": title,
        "body": body,
        "labels": labels,
    }
    issues.append({
        "suggestion_id": sid,
        "severity": sev,
        "category": cat,
        "question_ids": s["question_ids"],
        "title": title,
        "labels": labels,
        "body": body,
        "api_payload": payload,
    })

# Write created-issues.json (dry-run)
output = {
    "created_at": "2026-03-25T00:00:00Z",
    "mode": "dry-run",
    "repo": "(not submitted — confirm repo_url to submit)",
    "filter": "P0,P1",
    "issues": [
        {
            "suggestion_id": i["suggestion_id"],
            "severity": i["severity"],
            "category": i["category"],
            "title": i["title"],
            "labels": i["labels"],
            "question_ids": i["question_ids"],
            "body_preview": i["body"][:200] + "...",
            "api_payload": i["api_payload"],
        }
        for i in issues
    ]
}

with open(f"{BASE}/created-issues.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Print summary
print(f"Issues generated (dry-run): {len(issues)}")
print(f"  P0: {sum(1 for i in issues if i['severity']=='P0')}")
print(f"  P1: {sum(1 for i in issues if i['severity']=='P1')}")
print(f"  Labels applied: pending (dry-run)")
print(f"  Mode: dry-run")
print(f"  Output: MindSpore/version3/created-issues.json")
print()
for i in issues:
    print(f"  [{i['severity']}] {i['title']}")
    print(f"         labels={i['labels']}")
    print(f"         questions={i['question_ids']}")
    print()
