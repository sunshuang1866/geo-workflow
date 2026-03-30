# GEO 问题集评估报告 — {community}

> 生成时间：{generated_at}
> 引用阈值：≥{citation_threshold_pct}% 平台引用视为「满足」
> 数据来源：`{scoring_file}` · `{labels_file}` · `{issue_map_file}`

---

## 概况

| 类别 | 问题数 |
|------|--------|
| 官方内容缺失（P1）| {count_no_official_content} |
| 有内容未被引用（P0）| {count_not_cited} |
| 引用了官方内容（OK）| {count_satisfied} |
| **合计** | **{total_questions}** |

### 严重级别分布

| 级别 | 问题数 |
|------|--------|
| P0 | {count_p0} |
| P1 | {count_p1} |
| OK | {count_ok} |

### 平台图例

| 指标 | 含义 |
|------|------|
| ✅ | 平台回答中引用了至少一条官方链接 |
| ❌ | 官方内容存在，但平台未引用 |
| — | 官方站点尚无相关内容，不适用 |

平台顺序：豆包 · Qwen · ChatGPT · DeepSeek

---

## 官方内容缺失（P1）— {count_no_official_content} 个问题

> 官方站点尚无覆盖此问题的内容，建议补充文档。

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 严重级别 | Issue |
|----|------|------|------|---------|----------|----------|-------|
{rows_no_official_content}

{footnotes_no_official_content}

---

## 有内容未被引用（P0）— {count_not_cited} 个问题

> 官方内容已存在，但未达到 {citation_threshold_pct}% 平台引用阈值。按改进措施分组，同一 Issue 下的问题需要相同的改进行动。

{grouped_not_cited}

---

## 引用了官方内容（OK）— {count_satisfied} 个问题

> ≥{citation_threshold_pct}% 平台已引用官方链接，状态健康，持续监控即可。

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | 严重级别 | Issue |
|----|------|------|------|---------|----------|--------|----------|-------|
{rows_satisfied}

{footnotes_satisfied}

---

*由 GEO Search Assessment 系统自动生成*
