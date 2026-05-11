# GEO 搜索能力诊断系统技术设计文档

**状态:** 已发布
**作者:** ZhengZhenyu
**日期:** 2026-04-12
**版本:** 1.0

---

## 一、系统概述

本系统是一套 **GEO（Generative Engine Optimization）搜索能力诊断工具**，通过Agent触发：自动向主流 AI 平台（ChatGPT、DeepSeek、豆包、Qwen、Gemini）提问并收集回答，通过 URL 匹配评估官方内容引用情况，对开源社区的AI平台可搜索能力进行评估，输出评估结果，同时输出改进建议并自动在项目对应的 GitHub / GitCode 上创建和更新 Issue。

### 1.1 设计原则

- **Skill 链式流水线**: 5 个独立 Skill 串联，每步只读上游 JSON、只写自己的输出，无双向依赖
- **文件作为状态**: 所有中间状态以 JSON 文件持久化，无数据库，便于人工检查和修复
- **步骤可恢复**: 每个步骤均可独立重跑，支持从任意位置续跑
- **配置驱动**: 切换社区只需更新 `.env`，不修改任何代码
- **人工介入最小化**: 首次运行只有一个必要人工节点（填写 `official_urls`），后续复检全自动

### 1.2 关键约束

| 约束 | 说明 |
|------|------|
| 运行环境 | Claude Code CLI + Python 3.8+，无需 Web 服务器或数据库 |
| 最小平台数 | 至少 2 个 AI 平台有效 API Key 才允许运行采样 |
| 采样规模 | MVP 阶段支持 30-50 个问题，上限 100 个 |
| 评估频率 | 建议每周一次，AI 平台内容索引更新周期约为周级 |

---

## 二、整体架构

```mermaid
flowchart TD
    subgraph TRIGGER["触发层"]
        A1["Claude Code 对话\n（自然语言描述）"]
        A2["OpenClaw 定时调度\n openClaw trigger --agent AGENT.md"]
    end

    subgraph AGENT["编排层 AGENT.md"]
        B0["Step 0: init\n创建 runs/{date}/ 目录\n检测 questions.json 变更"]
        B1["Step 1: sample\n/platform-sampler"]
        B2["Step 2: score\n/scoring-engine"]
        B3["Step 3: issue\n/issue-creator"]
        B4["Step 4: report\n/assessment-report"]
        B5["Step 5: finalize\n写入 run-meta.json\n输出摘要"]
        B0 --> B1 --> B2 --> B3 --> B4 --> B5
    end

    subgraph SOURCES["问题来源（首次运行）"]
        S1["Discourse 论坛 API\n(Path 1: forum)"]
        S2["GitCode Issue API\n(Path 2: issue)"]
        S3["SIG 邮件列表 HyperKitty API\n(Path 3: maillist)"]
        S4["官网站内搜索热词 API\n(Path 4: website)"]
        S5["manual-questions.md\n(手动输入)"]
    end

    subgraph PLATFORMS["AI 平台采样"]
        P1["ChatGPT"]
        P2["DeepSeek"]
        P3["豆包"]
        P4["Qwen"]
        P5["Gemini"]
    end

    subgraph OUTPUT["输出层"]
        O1["GitHub / GitCode Issues\n（创建 / 评论 / 关闭建议）"]
        O2["assessment-report.md\n（人工可读评估报告）"]
        O3["run-meta.json\n（运行元数据）"]
    end

    A1 & A2 --> AGENT
    S1 & S2 & S3 & S4 & S5 -->|"/get-question\n生成 questions.json"| B0
    B1 -->|"并发采样"| P1 & P2 & P3 & P4 & P5
    P1 & P2 & P3 & P4 & P5 -->|"responses.json"| B2
    B2 -->|"scoring-results.json"| B3
    B3 --> O1
    B4 --> O2
    B5 --> O3
```

### 2.1 两种运行模式

| 模式 | 场景 | 人工介入点 | 触发方式 |
|------|------|-----------|---------|
| **首次运行** | 建立基线，生成问题集和标注 | 需要人工填写 `official_urls` | 手动逐步执行 |
| **定期复检** | 周期性重新评估，更新 Issue | 无需人工介入 | Claude Code 对话 / OpenClaw |

---

## 三、模块详解

### 3.1 编排层（AGENT.md）

AGENT.md 是唯一的流程控制入口，不含业务逻辑：

```
AGENT.md
├── Step 0 (init)      解析参数 + .env → 合并配置；检测 questions.json 变更；创建 {date}/ 目录
├── Step 1 (sample)    根据 scope 参数过滤问题 → 调用 /platform-sampler
├── Step 2 (score)     调用 /scoring-engine
├── Step 3 (issue)     调用 /issue-creator
├── Step 4 (report)    调用 /assessment-report
└── Step 5 (finalize)  写 run-meta.json；校验 issue activity 一致性；打印摘要 + 行动提示
```

**支持的调用参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `steps` | 选择执行哪些步骤 | `steps=2,3,4,5`（跳过采样，直接重新评分） |
| `scope` | 问题范围（`all` / `p0` / 指定 ID） | `scope=p0`（只重检 P0 问题） |
| `accept_question_update` | 问题集有变更时才需要 | `accept_question_update=true` |
| `dry_run` | 不执行实际 API 写操作 | `dry_run=true` |

---

### 3.2 问题采集（get-question）

```
.claude/skills/get-question/
├── SKILL.md                        # 8 步过程定义
├── scripts/
│   ├── parse-manual-questions.py   # 解析 manual-questions.md → JSON
│   ├── fetch-forum-posts.py        # Discourse API → 热帖标题 → LLM 改写
│   ├── fetch-repo-issues.py        # GitCode Issue API → LLM 改写（需 GITCODE_TOKEN）
│   ├── fetch-sig-info.py           # SIG MagicAPI → HyperKitty → LLM 过滤
│   └── validate-questions.py       # 输出校验
├── references/
│   ├── forum-api-spec.md           # Discourse API 端点规范
│   ├── gitcode-api-spec.md         # GitCode API 端点规范
│   └── sig-api-spec.md             # SIG / HyperKitty API 规范
└── assets/
    ├── questions-template.md       # questions.md 输出模板
    └── prompt-templates.md         # LLM 改写提示词
```

**关键行为：**
- 每次执行**追加**新问题到已有 `questions.json` 末尾，不覆盖
- 语义去重：新问题与已有问题语义相似时自动跳过
- `official_urls` 和 `notes` 字段在追加操作中**保持不变**
- 输出：`questions.json`（机器可读）+ `questions.md`（人工可读）

---

### 3.3 AI 平台采样（platform-sampler）

```
.claude/skills/platform-sampler/
├── SKILL.md                        # 5 步过程定义
├── scripts/
│   ├── sample-platform.py          # 单问题单平台采样（LLM 后处理提取元数据）
│   ├── run-sampler.py              # 批量入口（5 问题/批，平台间 1s 间隔）
│   ├── validate-input.py           # 输入校验
│   └── validate-responses.py       # 输出校验（覆盖率报告）
├── references/
│   └── platform-rate-limits.md     # 各平台速率限制
└── assets/
    └── responses-template.md       # responses.json 输出模板
```

**采样策略：**
```
questions.json → 按 scope 过滤 → 分批（5 题/批）
  └── 对每个问题：
        └── 顺序调用各平台（同平台间隔 1s）
              └── 成功 → 提取 citations / mentions_community / recommendation_position
                  失败 → 标注 status=error，继续下一平台
              └── 即时 flush 写入 responses.json（防止中断丢失）
→ 最终合并（append 模式）去重（question_id + platform 为唯一键）
```

---

### 3.4 评分与诊断（scoring-engine）

```
.claude/skills/scoring-engine/
├── SKILL.md                        # 6 步过程定义
├── scripts/
│   ├── validate-inputs.py          # 校验 responses.json + questions.json
│   └── compile-report.py           # URL 匹配 → 聚合 → 建议匹配 → 写 scoring-results.json
├── references/
│   ├── geo-suggestions-catalog.md  # 72 条 GEO 建议目录（13 类别）
│   ├── suggestion-rules.md         # status → 建议映射规则
│   └── scoring-prompt-template.md  # 预留（当前评分无 LLM）
└── assets/
    └── suggestions-template.md     # 建议输出模板
```

**评分流程：**
```
对每个 (question_id, platform) 对：
    1. 归一化 responses.json 中的 citation URL（去 scheme/trailing-slash/query）
    2. 与 questions.json 中的 official_urls 逐一比对（精确字符串匹配）
    3. 命中任意一个 → cited=true

对每个 question_id 聚合：
    citation_rate = cited 平台数 / 总平台数

    if official_urls == []:     → no_official_content (P1)
    elif citation_rate >= 0.75: → satisfied (OK)
    else:                       → not_cited (P0)

→ 按 status + citation_rate 区间从 geo-suggestions-catalog 中匹配建议
→ 写入 scoring-results.json
→ 同步 official_urls 回 questions.md（新增「官方链接」列）
```

---

### 3.5 Issue 创建与追踪（issue-creator）

```
.claude/skills/issue-creator/
├── SKILL.md                        # 7 步过程定义
├── scripts/
│   ├── parse-suggestions.py        # 解析 scoring-results.json → 候选 Issue 列表
│   ├── create-issue.py             # GitHub / GitCode Issue 创建 API
│   └── comment-issue.py            # Issue 追加评论 API
├── references/
│   └── gitcode-api-spec.md         # GitCode Issue / Comment API 规范
└── assets/
    └── issue-template.md           # Issue 正文模板（现象、根因、action items）
```

**去重与状态机制：**
```
scoring-results.json（本次评分）
    ↓
LLM 语义分组（将相关问题聚合为一组）
    ↓
与 issue-map.json 比对（match key: question_ids 重叠度 ≥ 50%）
    ├── 无匹配 → 创建新 Issue → 写入 issue-map.json
    ├── 有匹配 + status 变化 → 追加评论（含引用率变化）
    └── 有匹配 + status = satisfied → 追加关闭建议评论
→ 写 created-issues.json（本次活动日志）
```

---

### 3.6 评估报告（assessment-report）

```
.claude/skills/assessment-report/
├── SKILL.md                        # 6 步过程定义
├── references/
│   └── indicator-rules.md          # 平台指示符（✅/❌/—）判断规则和列序
└── assets/
    └── report-template.md          # assessment-report.md 输出模板
```

**输入 → 输出：**
```
scoring-results.json   ╮
questions.json         ├─→ 按三类现象分组（no_official_content / not_cited / satisfied）
issue-map.json         ╯       → 每题：平台指示符 + 引用率 + 严重级别 + Issue URL + 迭代次数
                               → 与上次报告对比：标注 new / improved / regressed / stable
                     ↓
assessment-report.json（机器可读）
assessment-report.md（人工可读 Markdown）
```

---

## 四、全流程数据流追踪

以"对 MindSpore 社区执行一次完整复检"为例：

```
用户在 Claude Code 输入："按照 AGENT.md 对 MindSpore 执行一次 GEO 复检"
    │
    ▼
AGENT.md Step 0 (init)
    ├── 读取 .env → GEO_COMMUNITY=MindSpore, GEO_COMMUNITY_DIR=assessments/MindSpore/
    ├── 比对 questions.json 与上次运行快照 → 无变更，继续
    └── 创建 assessments/MindSpore/2026-04-14/ 目录
    │
    ▼
AGENT.md Step 1 (sample) → /platform-sampler
    ├── 加载 assessments/MindSpore/questions.json（42 个问题）
    ├── 检测 .env 中有效 Key: deepseek ✅, qwen ✅, gemini ✅, chatgpt ✅, doubao ❌
    ├── 分 9 批（每批 5 题）× 4 平台 = 168 次 API 调用
    └── 输出 assessments/MindSpore/2026-04-14/responses.json（168 条，3 条 error）
    │
    ▼
AGENT.md Step 2 (score) → /scoring-engine
    ├── 读取 responses.json + questions.json（含 official_urls）
    ├── 对 168 个 (question_id, platform) 对执行 URL 匹配
    ├── 聚合：42 题中 8 题 satisfied, 30 题 not_cited, 4 题 no_official_content
    └── 输出 assessments/MindSpore/2026-04-14/scoring-results.json
    │
    ▼
AGENT.md Step 3 (issue) → /issue-creator
    ├── 读取 scoring-results.json + assessments/MindSpore/issue-map.json（已有 18 组）
    ├── LLM 对 30 个 not_cited 问题语义分组 → 14 组
    ├── 与 issue-map.json 比对 → 12 组匹配已有 Issue（追加评论），2 组新建
    ├── 调用 GitHub API: POST /issues × 2, POST /issues/*/comments × 12
    └── 更新 issue-map.json，写 assessments/MindSpore/2026-04-14/created-issues.json
    │
    ▼
AGENT.md Step 4 (report) → /assessment-report
    ├── 读取 scoring-results.json + questions.json + issue-map.json
    ├── 与上次报告（2026-04-07/assessment-report.json）对比
    └── 输出 assessments/MindSpore/2026-04-14/assessment-report.json + .md
    │
    ▼
AGENT.md Step 5 (finalize)
    ├── 验证 issue activity（created-issues.json 统计与 run-meta 一致）
    ├── 写入 assessments/MindSpore/2026-04-14/run-meta.json
    └── 打印摘要：satisfied=8, not_cited=30, no_official_content=4, issues_created=2, issues_updated=12
```

---

## 五、数据持久化

### 5.1 目录结构

```
assessments/{community}/
│
├── questions.json          ← 符号链接（指向 question.json 或 questions-new.json）
├── questions-new.json      ← 新问题集（待人工标注 official_urls）
├── questions-new.md        ← 新问题集 Markdown 视图
├── issue-map.json          ← 累积 Issue 映射（跨运行不覆盖）
│
├── summary/                ← 【新增】汇总目录（跨运行历史数据汇总）
│   ├── response.json           汇总响应数据
│   ├── scoring-results.json    汇总评分结果
│   └── scoring-report.md       汇总评估报告
│
├── previous-question/      ← 【新增】历史问题目录（历史问题评分）
│   ├── scoring-results.json    历史问题评分结果
│   └── scoring-report.md       历史问题报告
│
└── {YYYY-MM-DD}/           ← 每次 AGENT.md 运行创建一个日期目录
    ├── questions.json          questions.json 快照（防止后续修改影响评分）
    ├── responses.json          platform-sampler 输出
    ├── scoring-results.json    scoring-engine 输出
    ├── created-issues.json     issue-creator 活动日志（本次）
    ├── assessment-report.json  assessment-report 输出（机器可读）
    ├── assessment-report.md    assessment-report 输出（人工可读）
    └── run-meta.json           AGENT.md 运行元数据
```

**注意**：
- `questions.json` 现在是符号链接，通过修改链接目标切换问题集版本
- `summary/` 目录汇总多次运行的历史数据，便于趋势分析
- `previous-question/` 目录存储历史问题评分，用于对比分析
- `responses.json` 在部分运行中命名为 `response.json`（单数形式），两者格式相同

### 5.2 跨运行持久状态

只有少数文件跨运行保持状态，其余均按日期隔离：

| 文件 | 跨运行作用 | 维护方式 |
|------|-----------|---------|
| `questions.json`（符号链接） | 问题集版本切换 | 符号链接指向当前版本 |
| `questions-new.json` | 问题集 + `official_urls` 标注 | 半自动（脚本追加，人工标注 official_urls） |
| `issue-map.json` | suggestion → GitHub Issue 去重映射 | 全自动（累积追加） |
| `summary/*` | 历史数据汇总 | 全自动（跨运行汇总） |
| `previous-question/*` | 历史问题评分 | 全自动（历史对比分析） |

**新增数据流**：

```
历史运行数据（{date}/*）
    ↓ 汇总
summary/scoring-results.json（跨运行汇总）
    ↓ 报告生成
summary/scoring-report.md（趋势分析）

历史问题评分
    ↓ 对比
current_question.json（当前问题集）
    ↓ 评分差异分析
previous-question/scoring-report.md
```

---

## 六、技术选型

### 6.1 核心依赖

| 技术 | 用途 | 说明 |
|------|------|------|
| Python 3.8+ | Skill 脚本语言 | 各 Skill 下的 `scripts/*.py` |
| Claude Code Skill | 流程编排和 LLM 调用 | AGENT.md + SKILL.md 机制 |
| OpenAI-compatible API | 各 AI 平台采样 | ChatGPT / DeepSeek / Qwen / Gemini 均支持 |
| GitHub REST API v3 | Issue 创建和评论 | `POST /repos/{owner}/{repo}/issues` |
| GitCode REST API v5 | Issue 创建和评论（国内社区） | `api.gitcode.com/api/v5` |
| Discourse API | 论坛热帖抓取（Path 1） | `discuss.mindspore.cn` 公开 API，无需 Auth |
| HyperKitty API | SIG 邮件列表归档（Path 3） | `mailweb.mindspore.cn` |

### 6.2 外部依赖

| 依赖类型 | 要求 |
|---------|------|
| API Keys | 至少 2 个 AI 平台 Key（CHATGPT / DEEPSEEK / QWEN / DOUBAO / GEMINI） |
| `GITHUB_TOKEN` 或 `GITCODE_TOKEN` | Issue 创建时必须提供 |
| `GITCODE_TOKEN` | get-question Path 2（GitCode Issue 抓取）时必须提供 |
| `WEBSITE_SEARCH_URL` | get-question Path 4（官网搜索热词）时可选提供 |

---

## 七、目录结构

```
geo-workflow/
├── AGENT.md                            # 工作流编排（6 步，复检入口）
├── CLAUDE.md                           # Claude Code 开发规则
├── CLAUDE-RESUME.md                    # 会话恢复上下文
├── README.md                           # 操作使用指南
├── .env.example                        # API Key 配置模板
├── .env                                # API Keys（不入库）
├── .gitignore
│
├── assessments/                        # 社区评估数据根目录
│   ├── MindSpore/
│   │   ├── questions.json              # 问题集（source of truth）
│   │   ├── questions.md
│   │   ├── issue-map.json              # 累积 Issue 映射
│   │   └── 2026-04-14/                 # 按日期隔离的运行数据
│   │       ├── responses.json
│   │       ├── scoring-results.json
│   │       ├── created-issues.json
│   │       ├── assessment-report.json
│   │       ├── assessment-report.md
│   │       └── run-meta.json
│   └── openEuler/                      # 其他社区（同结构）
│
├── docs/                               # 设计文档
│   ├── PRD.md
│   ├── architecture.md                 # 本文档
│   ├── data-model.md
│   └── geo-theory.md
│
└── .claude/
    └── skills/                         # Skill 定义（遵循 agentskills.io 规范）
        ├── get-question/
        ├── platform-sampler/
        ├── scoring-engine/
        ├── issue-creator/
        ├── assessment-report/
        ├── platform-chat/              # 浏览器自动化采样（Playwright 备用方案）
        ├── release-skills/             # 版本管理
        └── skill-creator/              # 创建新 Skill 的脚手架
```

---

## 八、部署与运行

### 8.1 环境要求

| 组件 | 要求 |
|------|------|
| Claude Code | 最新版，对话触发和 Skill 编排 |
| Python | >= 3.8 |
| 网络 | 可访问各 AI 平台 API Endpoint |

### 8.2 初始化

```bash
# 1. 克隆仓库
git clone https://github.com/opensourceways/geo-workflow.git
cd geo-workflow

# 2. 配置 API Keys
cp .env.example .env
# 编辑 .env，填入各平台 API Key 和社区配置

# 3. 创建社区目录
mkdir -p assessments/MindSpore/

# 4. 在 Claude Code 中生成初始问题集
# （需要先在项目根目录启动 claude）
/get-question paths=all
```

### 8.3 常用操作

```bash
# 首次完整运行（含人工审核 official_urls 步骤）
/get-question
# → 人工编辑 assessments/MindSpore/questions.json，填写 official_urls
/platform-sampler
/scoring-engine
/issue-creator dry_run=true   # 先预览 Issue 内容
/issue-creator                # 确认无误后正式创建

# 定期复检（全自动）
# 在 Claude Code 中输入：
"按照 AGENT.md 对 MindSpore 社区执行一次 GEO 复检"

# 只重新评分（已有采样数据）
# AGENT.md 参数：
steps=2,3,4,5

# 只重检 P0 问题
steps=1,2,3,4,5 scope=p0

# 针对特定问题追加采样
steps=1 scope=q_038,q_039
```

---

## 九、关键设计决策

### 9.1 评分采用纯 URL 字符串匹配，不使用 LLM

**决策背景：** 早期考虑用 LLM 评估 AI 平台回答是否"引用了官方内容的精神"。

**选择纯匹配的原因：**
- 确定性：相同输入始终产生相同结果，便于复现
- 成本可控：无额外 LLM 调用
- 可解释性："URL X 出现在回答中"比"LLM 认为引用充分"更容易被团队接受

**已知局限：** 无法检测 AI 隐式使用了官方内容但未给链接的情况。

---

### 9.2 issue-map.json 以 question_ids 重叠为去重依据

**决策背景：** 曾考虑将 status 变化也作为 match key，即同一问题组状态改变时创建新 Issue。

**当前方案原因：**
- 避免同一问题反复创建 Issue（Issue 爆炸）
- Issue 是长期追踪单元，status 变化通过追加评论体现完整历史

---

### 9.3 questions.json 是 official_urls 的唯一来源

**决策背景：** 早期有独立的 `content-labels.json` 存放人工标注。

**合并的原因：**
- 减少文件数量和同步负担
- 问题定义与标注在同一记录中，原子性更好

---

### 9.4 禁止将 AI 生成的问题作为问题来源

问题必须来自真实用户行为数据（论坛、Issue、邮件列表、搜索热词）。用 AI 生成问题再评估 AI 对这些问题的回答，存在循环论证风险，評估结果对实际用户行为没有代表性。

---

## 十、相关文档

- **产品需求文档:** [PRD.md](./PRD.md)
- **数据模型文档:** [data-model.md](./data-model.md)
- **GEO 理论基础:** [geo-theory.md](./geo-theory.md)
- **操作使用指南:** [../../README.md](../../README.md)
- **工作流编排规范:** [../../AGENT.md](../../AGENT.md)

---

*文档版本历史：v1.0 (2026-04-12) 初稿，参考 community-health 项目架构文档格式重写。*
