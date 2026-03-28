# MindSpore GEO 评分报告

> 评分时间: 2026-03-23T15:55:41Z
> 问题数: 3 | 平台数: 4 | 评分对数: 12
> 标准答案: 未提供（跳过 Layer 2+ 事实覆盖分析）
> 校准备注: q_032 content_exists 已由人工更正（官方活动页: mindspore.cn/activities）

---

## 执行摘要

### 现象分布

| 现象 | 说明 | 数量 | 占比 |
|------|------|------|------|
| A | 官网无内容 | 0 | 0% |
| B | 有内容未引用 | 1 | 8% |
| C | 引用错误信息 | 2 | 17% |
| D | 引用充分 | 5 | 42% |
| E | 引用比例低 | 4 | 33% |

### 严重等级分布

| 等级 | 数量 | 说明 |
|------|------|------|
| P0 🔴 | 2 | 需立即处理 |
| P1 🟠 | 1 | 2-4 周内处理 |
| P2 🟡 | 9 | 持续优化 |
| 无需行动 ✅ | 0 | 保持监控 |

---

## 平台对比矩阵

| 平台 | 平均评分 | 平均官方引用率 | 表现评价 |
|------|---------|-------------|--------|
| ChatGPT | 6.7 | 55% | 综合均衡，q_035 表现最佳（9分） |
| DeepSeek | 6.7 | 65% | 引用率最高，诚实承认不确定性 |
| Qwen | 5.3 | 72% | 官方引用率高但存在两处幻觉（C现象） |
| Doubao | 6.0 | 48% | 评分和引用率均最低，需重点关注 |

---

## 分问题详细结果

### q_027 — MindSpore 的版本发布节奏是怎样的？

> content_exists: ✅ true (partial) | 有 Release Notes 和 Gitee Releases，但无版本策略专页

| 平台 | 现象 | 评分 | 官方引用率 | 严重等级 | 主要问题 |
|------|------|------|-----------|--------|--------|
| ChatGPT | E | 6 | 50% | P2 | missing_scope, no_process_doc |
| DeepSeek | D | 7 | 100% | P2 | missing_scope, shallow_content（引用 Golden Stick 子组件而非主框架） |
| **Qwen** | **C** | **5** | 71% | **P0 🔴** | fabricated_claims（捏造 LTS 版本号 2.2.0/2.4.0）、version_confusion |
| Doubao | E | 5 | 43% | P2 | fabricated_claims（疑似虚构 /version-updates URL）、no_evidence |

**根本原因**: 官网缺少主框架版本节奏策略文档 → 所有平台只能推断，易产生幻觉。

---

### q_032 — MindSpore 2026 年有哪些活动规划？

> content_exists: ✅ true (partial) | 官方活动页: **mindspore.cn/activities**（人工校准更正）

| 平台 | 现象 | 评分 | 官方引用率 | 严重等级 | 主要问题 |
|------|------|------|-----------|--------|--------|
| ChatGPT | B | 5 | 14% | P1 🟠 | 未发现 /activities 页，声称无完整规划 |
| DeepSeek | E | 6 | 43% | P2 | 从论坛找到部分真实内容，但未引用 /activities |
| **Qwen** | **C** | **3** | 63% | **P0 🔴** | 捏造 mindspore.cn/activity/conference2026 等不存在的 URL |
| Doubao | D | 7 | 56% | P2 | 从论坛帖找到真实活动，官方引用率勉强过半 |

**关键发现**: /activities 页面存在但 SEO 不足 → ChatGPT 完全未找到；Qwen 在官方域名下捏造子路径（最危险）。

---

### q_035 — 新手如何加入 MindSpore 社区并参与开源贡献？

> content_exists: ✅ true (full) | mindspore.cn/developers 有完整贡献指南

| 平台 | 现象 | 评分 | 官方引用率 | 严重等级 | 主要问题 |
|------|------|------|-----------|--------|--------|
| ChatGPT | D | 9 | 100% | P2 | buried_answer（开头铺垫略长） |
| DeepSeek | D | 7 | 53% | P2 | missing_summary, no_direct_answer |
| Qwen | D | 8 | 83% | P2 | buried_answer, no_direct_answer |
| Doubao | E | 6 | 46% | P2 | missing_faq, missing_scope |

**关键发现**: 最佳表现问题。ChatGPT 9分/官方引用100%，证明优质文档直接带来高质量 AI 回答。

---

## 跨平台模式分析

### 幻觉模式（Hallucination Patterns）

| 触发词 | 受影响平台 | 典型示例 |
|--------|----------|--------|
| 版本节奏 / LTS版本 | Qwen | 声称 2.2.0、2.4.0 为 LTS 版本（官方无此声明） |
| 2026年具体活动URL | Qwen | 捏造 /activity/conference2026、/activity/mindspore-cup-2026 等不存在页面 |

### 内容缺口（Content-Origin Issues，≥3 平台）

| 问题 | 受影响平台 | 关联问题 |
|------|----------|--------|
| 版本策略文档缺失（missing_scope） | chatgpt, deepseek, qwen | q_027 |
| /activities 未被引用（buried/seo不足） | 全部 4 个 | q_032 |
| 贡献页 buried_answer（结构问题） | chatgpt, deepseek, qwen | q_035 |

---

## 优先改进建议

### P0 🔴 — 立即处理（1-2 周）

#### s_001 | 提升 mindspore.cn/activities 的 GEO 可发现性
- **问题**: q_032 | **现象**: B/C/E | **受影响**: 全部 4 个平台 | **类型**: seo
- **目录引用**: CTX-02, CTX-03, ORG-01, REF-04, DIS-03
- **建议**: 确保 /activities 页面标题含"2026年活动"关键词，首段给出活动日历摘要，添加 Event 结构化数据，使 AI 平台直接引用而非从论坛推断或捏造 URL。
- **预期效果**: ChatGPT B→D，Qwen 停止捏造，整体引用率提升。

#### s_001b | 用真实内容填充活动页，消除千问幻觉
- **问题**: q_032 | **现象**: C | **受影响**: Qwen | **类型**: correction
- **目录引用**: REF-04, REF-10, DIS-03, NEG-03
- **建议**: 在 /activities 页明确列出已确认活动（含时间/形式），让 AI 有权威内容可引用，从根本上消除在官方域名下捏造子路径的动机。

#### s_002 | 创建版本发布节奏与生命周期策略专页
- **问题**: q_027 | **现象**: C/E | **受影响**: 全部 4 个平台 | **类型**: content
- **目录引用**: CTX-05, REF-04, REF-05, EXP-03, EXC-01
- **建议**: 在官网创建版本节奏专题页，说明大版本周期、LTS 策略（或明确声明"目前无 LTS"）、补丁规则和 EOL 政策。
- **预期效果**: 消除 Qwen 的幻觉 LTS 版本号，将整体现象从 C/E 改善为 D。

#### s_003 | 在版本页面添加 LTS 否定声明
- **问题**: q_027 | **现象**: C | **受影响**: Qwen | **类型**: correction
- **目录引用**: REF-04, REF-10, DIS-03, NEG-03
- **建议**: 在 Release Notes 和版本历史页标注"目前无正式 LTS 版本声明"，防止 AI 错误推断。

---

### P1 🟠 — 2-4 周处理

#### （隐含于 s_001）ChatGPT q_032 B→D
确保 /activities 可被 AI 检索后，ChatGPT 的 B 现象将自然消除。

---

### P2 🟡 — 持续优化（4-8 周）

#### s_004 | 优化贡献页面内容前置结构
- **问题**: q_035 | **类型**: optimization | **目录引用**: CTX-02, ORG-02, CTX-09
- **建议**: 将贡献核心步骤提至正文前 150 字，结论先行，减少铺垫。

#### s_005 | 贡献指南增加锚点化 FAQ
- **问题**: q_035 | **类型**: optimization | **目录引用**: REF-01, REF-05, EXC-01, CTX-09
- **建议**: 增加 SIG 选择/PR 注意事项/CLA 步骤 FAQ，每项独立 anchor，提升 Doubao 引用率。

---

## 执行路线图

| 阶段 | 时间 | 行动 | 负责方 |
|------|------|------|--------|
| P0 — 立即 | 第 1-2 周 | /activities 页面 SEO 优化 + 活动内容完善 | 社区运营 |
| P0 — 立即 | 第 1-2 周 | 创建版本节奏策略页 + LTS 否定声明 | 文档团队 |
| P1 — 跟进 | 第 2-3 周 | 验证 ChatGPT 是否开始引用 /activities | GEO 负责人 |
| P2 — 优化 | 第 4-8 周 | 贡献页前置重构 + FAQ 锚点 | 文档团队 |
| 持续监控 | 每季度 | 重新运行评分引擎 | GEO 负责人 |

## KPI 追踪目标

| 问题 | 当前 | 目标 | 检验时间 |
|------|------|------|--------|
| q_032 整体 avg_score | 5.25 | ≥7.5 | /activities 优化后 1 个月 |
| q_032 Phenomenon C | Qwen | 0 平台 | 活动内容发布后 |
| q_032 ChatGPT B→D | B | D | /activities SEO 提升后 |
| q_027 平均评分 | 5.75 | ≥7.5 | 版本策略页发布后 |
| q_035 Doubao 引用率 | 46% | ≥60% | 贡献页重构后 |
