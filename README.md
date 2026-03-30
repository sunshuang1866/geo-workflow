# GEO Search Assessment

GEO（Generative Engine Optimization）搜索能力诊断系统 —— 自动评估开源社区在主流 AI 搜索平台中的表现，并生成可执行的改进建议。

初始目标社区：**MindSpore**（AI 计算框架，竞品：TensorFlow / PyTorch / PaddlePaddle）。

## 目录

- [系统架构](#系统架构)
- [前置准备](#前置准备)
- [首次运行（初始化）](#首次运行初始化)
- [定期复检（自动化流水线）](#定期复检自动化流水线)
- [各步骤详解](#各步骤详解)
- [目录结构](#目录结构)
- [文件说明](#文件说明)
- [OpenClaw 集成](#openclaw-集成)
- [常见问题](#常见问题)
- [使用 Claude Code 开发](#使用-claude-code-开发)

## 系统架构

本系统是一个由 Claude Code 驱动的 **Skill 链式流水线**，纯 CLI 运行，无 Web 界面。

核心是一条 **5 步 Skill 流水线**，由 `AGENT.md` 编排：

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐     ┌───────────────┐     ┌───────────────────┐
│  get-question   │────▶│ platform-sampler │────▶│ scoring-engine │────▶│ issue-creator │────▶│ assessment-report │
│  生成问题集      │     │  采样 AI 平台     │     │  评分 + 诊断   │     │ 创建/更新Issue │     │  生成评估报告      │
└─────────────────┘     └──────────────────┘     └───────┬────────┘     └───────────────┘     └───────────────────┘
       ↓                        ↓                        │                      ↓                       ↓
  questions.json          responses.json                 │               created-issues.json   assessment-report.json
  questions.md                                            │               issue-map.json        assessment-report.md
                                                         ↓
                                                 scoring-results.json
```

运行模式有两种：

| 模式 | 场景 | 人工介入 | 触发方式 |
|------|------|----------|----------|
| **首次运行** | 建立基线，准备问题集和标注 | 需要多步人工操作 | 手动 |
| **定期复检** | 周期性检测分数变化，更新 Issue | 无需人工介入 | 手动 / OpenClaw |

---

## 前置准备

### 1. 环境要求

- [Claude Code](https://claude.ai/code) CLI
- Python 3.8+
- Git

### 2. API Keys

复制 `.env.example` 为 `.env`，填入 API 密钥：

```bash
cp .env.example .env
```

| 变量 | 用途 | 必需 |
|------|------|------|
| `OPENAI_API_KEY` | ChatGPT 采样 | 至少填 2 个平台 |
| `DEEPSEEK_API_KEY` | DeepSeek 采样 | 至少填 2 个平台 |
| `DOUBAO_API_KEY` | 豆包采样 | 至少填 2 个平台 |
| `QWEN_API_KEY` | 千问采样 | 至少填 2 个平台 |
| `GITCODE_TOKEN` | GitCode Issue 创建 | Issue 创建时必需 |
| `GITHUB_TOKEN` | GitHub Issue 创建 | 用 GitHub 时必需 |

> 至少需要 **2 个平台** 的 API Key 才能运行采样。

### 3. 创建社区目录

社区数据统一存放在 `packages/assessments/` 下：

```bash
mkdir -p packages/assessments/MindSpore/
```

---

## 首次运行（初始化）

首次运行需要依次完成以下步骤，包含多处人工审核环节。

### Step A: 生成问题集

在 Claude Code 中执行：

```
/get-question community=MindSpore paths=all
```

**输出**：
- `questions.json` — 结构化问题集
- `questions.md` — 人工审阅格式

### Step B: 首次采样

```
/platform-sampler
```

输入 `questions.json`，输出 `responses.json`。

### Step C: 人工标注 content-labels

根据 `questions.json` 中的每个问题，人工判断 **官方是否已有对应内容**。

创建 `packages/assessments/MindSpore/content-labels.json`：

```json
{
  "labels": [
    {
      "question_id": "q_001",
      "question": "MindSpore 支持哪些安装方式？",
      "official_urls": ["https://www.mindspore.cn/install"],
      "notes": "安装指南页面完整覆盖"
    },
    {
      "question_id": "q_002",
      "question": "MindSpore 和 PyTorch 相比有哪些优势？",
      "official_urls": [],
      "notes": "无官方对比文档"
    }
  ]
}
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `question_id` | string | 问题 ID |
| `question` | string | 问题文本 |
| `official_urls` | array | 对应的官方页面 URL（空数组 = 官方无内容） |
| `notes` | string | 备注（可选） |

> 判定规则：`official_urls` 非空 → 官方有内容，检查 AI 回答是否引用；`official_urls` 为空 → 官方内容缺失，标 P1。

### Step D: 首次评分

```
/scoring-engine
```

输入 `responses.json` + `content-labels.json`，输出 `scoring-results.json`。

### Step E: 首次创建 Issue

```
/issue-creator repo_url=https://github.com/opensourceways/geo-workflow/ dry_run=true
```

> 建议先用 `dry_run=true` 预览 Issue 内容，确认无误后去掉 `dry_run` 正式创建。

**首次运行完成后**，`packages/assessments/MindSpore/` 目录下应有：
- `questions.json` — 问题集（`/get-question` 生成）
- `content-labels.json` — 人工标注
- `issue-map.json` — Issue 映射（自动生成）

---

## 定期复检（自动化流水线）

首次运行完成后，后续复检由 `AGENT.md` 编排，**无需人工介入**。

### 手动触发

在 Claude Code 中直接描述意图即可，Claude 会按照 `AGENT.md` 执行：

```
请按照 AGENT.md 对 MindSpore 社区执行一次 GEO 复检，
repo_url=https://github.com/opensourceways/geo-workflow/
```

### 自动化执行流程

AGENT.md 定义的 6 个步骤，支持通过 `steps` 和 `scope` 参数选择性执行：

```
Step 0 (init):      初始化 runs/{date}/ 目录，检测 questions.json 变更
         ↓
Step 1 (sample):    /platform-sampler → responses.json（scope 控制问题范围）
         ↓
Step 2 (score):     /scoring-engine → scoring-results.json
         ↓
Step 3 (issue):     新问题 → 新建 Issue；已有 Issue → 追加评论
         ↓
Step 4 (report):    /assessment-report → assessment-report.json + assessment-report.md
         ↓
Step 5 (finalize):  更新 run-meta.json，输出摘要
```

**常用组合**：

| 场景 | 参数 |
|------|------|
| 全量复检（默认） | 无需额外参数 |
| 已有采样，重新评分 | `steps=2,3,4,5` |
| 只重检 P0 问题 | `steps=1,2, scope=p0` |
| 采样指定问题 | `steps=1, scope=q_048,q_049` |
| 仅重新生成报告 | `steps=4` |
| 接受问题集变更并继续 | `accept_question_update=true` |
| 查看问题集变更详情 | `steps=update_questions` |

### 每次运行的输出

| 输出文件 | 位置 | 说明 |
|----------|------|------|
| `responses.json` | `runs/{date}/` | 本次平台采样原始数据 |
| `scoring-results.json` | `runs/{date}/` | 本次评分结果 |
| `assessment-report.json` | `runs/{date}/` | 问题集评估报告（机器可读） |
| `assessment-report.md` | `runs/{date}/` | 问题集评估报告（人工可读） |
| `run-meta.json` | `runs/{date}/` | 运行元数据（耗时、平台、统计） |
| `created-issues.json` | `runs/{date}/` | 本次 Issue 创建/更新记录 |
| `issue-map.json` | 社区目录根 | 累积 Issue 映射（跨运行持久化） |

---

## 各步骤详解

### get-question — 生成问题集

5 个数据来源路径，可单独选择或全选：

| 路径 | 参数值 | 数据来源 | 场景 |
|------|--------|----------|------|
| Path 1 | `forum` | MindSpore Discourse 论坛热帖 | 使用阶段 |
| Path 2 | `issue` | GitCode 仓库 Issue | 使用阶段 |
| Path 3 | `maillist` | SIG 邮件列表归档 | 使用阶段 |
| Path 4 | `website` | 官网站内搜索热词 | 使用阶段 |
| Path 5 | `industry` | LLM 生成行业问题 | 了解阶段 |

```
/get-question community=MindSpore paths=forum,issue,industry
/get-question community=MindSpore paths=all
```

### platform-sampler — 采样 AI 平台

- 自动检测 `.env` 中哪些平台有 API Key
- 对每个问题 x 每个平台发起一次查询
- 速率限制：同平台间隔 1 秒
- 单个平台失败不中断整体采样

### scoring-engine — 评分诊断

纯 URL 字符串匹配（精确 URL + 域名级），无 LLM 评估：

| 状态 | 描述 | 严重级别 | 说明 |
|------|------|----------|------|
| `satisfied` | 引用了官方内容 | OK | 回答中包含官方 URL 或域名 |
| `not_cited` | 有内容未被引用 | P0 | 官方已有内容但 AI 平台未引用 |
| `no_official_content` | 官方内容缺失 | P1 | 官方本身无对应内容 |

### issue-creator — 创建/更新 Issue

两种模式，通过 `issue-map.json` 自动判断：

| 场景 | 动作 | API 操作 |
|------|------|----------|
| 新发现的问题 | 创建新 Issue | POST /issues |
| 已有 Issue 的问题 | 追加评论 | POST /issues/{number}/comments |

追加评论包含：
- 评分变化（上次 vs 本次）
- 严重级别变化
- 本次发现描述
- 改善建议（如分数改善，建议关闭 Issue）

### assessment-report — 生成评估报告

综合 `scoring-results.json`、`content-labels.json`、`issue-map.json`，生成每次运行的问题集全量报告。

| 输出 | 格式 | 说明 |
|------|------|------|
| `assessment-report.json` | JSON | 机器可读，含完整 per-question 记录 |
| `assessment-report.md` | Markdown | 人工可读，按现象类别分组展示 |

报告按三类现象分组，每个问题显示：
- 各平台引用情况（✅ 已引用 / ❌ 未引用 / — 无官方内容）
- 引用率 + 严重级别
- 关联 Issue 链接和迭代次数

---

## 目录结构

```
geo-workflow/
├── AGENT.md                        # 工作流编排（定期复检入口）
├── CLAUDE.md                       # Claude Code 开发规则
├── CLAUDE-RESUME.md                # 会话恢复上下文
├── README.md                       # 本文档
├── .env.example                    # API Key 模板
├── .env                            # API Keys（不入库）
├── .gitignore
├── docs/
│   └── GEO搜索能力检测和优化改进-初步设计方案.md  # 完整设计文档
├── packages/
│   └── assessments/                # 社区评估数据
│       ├── MindSpore/              # MindSpore 社区
│       │   ├── questions.json           # 问题集（/get-question 生成，source of truth）
│       │   ├── questions.md             # 问题集（人工可读）
│       │   ├── content-labels.json      # 人工标注（手动维护）
│       │   ├── issue-map.json           # Issue 映射（自动维护）
│       │   └── runs/                    # 每次运行的数据
│       │       ├── 2026-03-28/
│       │       │   ├── questions.json
│       │       │   ├── content-labels.json
│       │       │   ├── responses.json
│       │       │   ├── scoring-results.json
│       │       │   ├── assessment-report.json
│       │       │   ├── assessment-report.md
│       │       │   ├── created-issues.json
│       │       │   └── run-meta.json
│       │       └── ...
│       └── openUBMC/               # openUBMC 社区
│           ├── questions.json
│           ├── questions.md
│           └── version1/           # 历史数据
└── .claude/
    └── skills/                     # Skill 定义
        ├── get-question/
        ├── platform-sampler/
        ├── scoring-engine/
        ├── issue-creator/
        ├── assessment-report/
        └── response-parser/
```

---

## 文件说明

### 手动维护的文件

这些文件需要人工创建和更新：

| 文件 | 更新时机 | 说明 |
|------|----------|------|
| `questions.json` | 运行 `/get-question` 后审核 | 问题集唯一来源；变更时 AGENT.md 会要求确认 |
| `content-labels.json` | 官方内容有变更时 | 人工判断每个问题的官方覆盖情况 |
| `manual-questions.md` | 有新的手动问题时 | 补充自动生成未覆盖的问题 |
| `.env` | API Key 变更时 | 平台 API 密钥 |

### 自动维护的文件

这些文件由系统自动创建和更新，**不要手动编辑**：

| 文件 | 生成时机 | 说明 |
|------|----------|------|
| `issue-map.json` | 每次 issue-creator 运行后 | 累积的 suggestion → issue 映射 |
| `runs/{date}/*` | 每次复检运行时 | 本次运行的所有中间和最终数据 |
| `run-meta.json` | 每次复检运行时 | 运行元数据和统计摘要 |
| `created-issues.json` | 每次 issue-creator 运行后 | 本次创建/更新的 Issue 记录 |
| `assessment-report.json` | 每次 assessment-report 运行后 | 问题集评估报告（机器可读） |
| `assessment-report.md` | 每次 assessment-report 运行后 | 问题集评估报告（人工可读） |

---

## OpenClaw 集成

系统架构已为 OpenClaw 定期触发做好准备。当接入时：

```bash
openclaw trigger \
  --agent "AGENT.md" \
  --inputs '{"community_dir": "packages/assessments/MindSpore/", "repo_url": "https://gitcode.com/mindspore/mindspore-portal/"}' \
  --schedule "0 9 * * 1"   # 每周一 9:00
```

**前提条件**：
- `questions.json` 和 `content-labels.json` 已就位
- `.env` 中 API Keys 配置完整
- 仓库可访问（有 push 权限更新 issue-map）

**建议调度频率**：每周一次。AI 平台回答变化较慢，更高频率只增加成本。

---

## 常见问题

### Q: 如何更新问题集？

重新运行 `/get-question` 或直接编辑 `packages/assessments/MindSpore/questions.json`。下次执行 AGENT.md 时，Step 0 会自动检测到变更并打印 diff，需要加 `accept_question_update=true` 才能继续。同时检查 `content-labels.json` 是否需要同步更新（新增问题需要新标注）。

### Q: 某个平台 API Key 过期了怎么办？

更新 `.env` 中对应的 Key。只要还有 2 个以上平台可用，采样不会中断。采样完成时 stdout 会输出覆盖率摘要，显示哪些平台缺失。

### Q: Issue 被手动关闭后，下次复检还会操作它吗？

会。系统通过 `issue-map.json` 追踪，如果该 suggestion 仍然存在，会向已关闭的 Issue 追加评论。如果 API 返回错误（如不允许评论已关闭 Issue），系统会记录错误并跳过，不会中断流程。

### Q: 如何查看某个问题的优化历史？

打开该问题在 GitCode/GitHub 上对应的 Issue，每次复检都会追加评论，包含引用率变化和平台覆盖情况，纵向看即为完整优化时间线。

### Q: 如何新增一个社区（如 openEuler）？

1. 创建目录 `packages/assessments/openEuler/`
2. 运行 `/get-question community=openEuler paths=all` 生成 `questions.json`
3. 审核 `questions.md`，直接编辑 `questions.json` 做必要调整
4. 人工标注 `packages/assessments/openEuler/content-labels.json`
5. 在 `.env` 中配置该社区的 `OFFICIAL_DOMAINS`
6. 按正常流程运行

### Q: dry-run 模式有什么用？

`dry_run=true` 时，所有 API 调用（采样、Issue 创建、评论）只打印 payload 到 stdout，不实际执行。适用于：
- 首次运行前验证 Issue 内容
- 调试 workflow 流程
- 培训新操作人员

### Q: 评分结果不准怎么办？

打开 `scoring-results.json`，找到对应的 `question_id` + `platform` 条目，确认 `official_urls` 标注是否准确。若标注有误，直接修改 `content-labels.json` 后重新运行 scoring-engine。

---

## 使用 Claude Code 开发

本仓库使用 [Claude Code](https://claude.ai/code) 作为主要开发工具，配置了自动化工作流和会话恢复机制。

### CLAUDE-RESUME.md —— 会话恢复

每次开启新的 Claude Code 会话时，Claude 会自动读取 `CLAUDE-RESUME.md` 来恢复项目上下文，无需重复说明背景。

该文件包含以下段落，**每次任务完成后自动更新**：

- **Project Overview** — 项目概述和架构
- **Current Status** — 当前开发阶段
- **TODO** — 待办事项清单
- **Recent Changes** — 近期变更记录
- **Key Decisions** — 已确定的关键决策

**约束**：
- 不要手动编辑此文件，由 Claude Code 自动维护
- 如需修正内容，在会话中告知 Claude 更新即可

### /release-skills —— 发布与变更日志

在 Claude Code 中执行 `/release-skills`，自动完成版本管理和 CHANGELOG.md 更新。

```
/release-skills              # 自动检测版本变更
/release-skills --dry-run    # 仅预览，不执行
/release-skills --major      # 强制主版本号升级
/release-skills --minor      # 强制次版本号升级
/release-skills --patch      # 强制补丁版本号升级
```

**约束**：
- 每次 git commit 前**必须**先执行 `/release-skills` 更新 CHANGELOG.md

### /skill-creator —— 创建新 Skill

在 Claude Code 中执行 `/skill-creator`，按照规范模版创建新的 skill。

**约束**：
- 创建新 skill 时**必须**使用 `/skill-creator`，不允许手动创建
- `SKILL.md` 主体逻辑不超过 500 行，超出部分拆分到 `references/`
- `name` 仅允许小写字母、数字和单连字符，1-64 字符
- `description` 不超过 1024 字符，使用第三人称，包含反向触发条件

## License

MIT
