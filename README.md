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
| **定期复检** | 周期性检测分数变化，更新 Issue | 无需人工介入 | ClaudeCode / OpenClaw |

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
| `CHATGPT_API_KEY` | ChatGPT 采样 | 至少填 2 个平台 |
| `GEMINI_API_KEY` | Gemini 采样 | 至少填 2 个平台 |
| `DEEPSEEK_API_KEY` | DeepSeek 采样 | 至少填 2 个平台 |
| `DOUBAO_API_KEY` | 豆包采样 | 至少填 2 个平台 |
| `QWEN_API_KEY` | 千问采样 | 至少填 2 个平台 |
| `GITCODE_TOKEN` | GitCode Issue 创建 | Issue 创建时必需 |
| `GITHUB_TOKEN` | GitHub Issue 创建 | 用 GitHub 时必需 |

**工作流配置**（每次切换社区时更新）：

| 变量 | 用途 | 示例值 |
|------|------|--------|
| `GEO_COMMUNITY` | 社区名称，供所有 Skill 读取 | `MindSpore` |
| `GEO_COMMUNITY_DIR` | 社区数据目录路径 | `assessments/MindSpore/` |
| `GEO_REPO_URL` | Issue 创建目标仓库 URL | `https://gitcode.com/mindspore/mindspore-portal/` |
| `GEO_FORUM_URL` | 社区 Discourse 论坛地址 | `https://discuss.mindspore.cn` |
| `GEO_SOURCE_REPO_URL` | 问题来源仓库地址（get-question issue 路径） | `https://gitcode.com/mindspore/mindspore/` |
| `GEO_PATHS` | get-question 默认来源路径 | `all` |
| `GEO_DRY_RUN` | 全局 dry-run 开关 | `false` |

> 至少需要 **2 个平台** 的 API Key 才能运行采样。

### 3. 创建社区目录

社区数据统一存放在 `assessments/` 下：

```bash
mkdir -p assessments/MindSpore/
```

---

## 首次运行（初始化）

首次运行需要依次完成以下步骤。

### Step A: 生成问题集

在 Claude Code 中执行：

```
/get-question
```

> 社区名称、论坛 URL、问题来源路径等已从 `.env` 中的 `GEO_COMMUNITY`、`GEO_FORUM_URL`、`GEO_PATHS` 等变量自动读取，无需手动输入。

**输出**：
- `questions.json` — 结构化问题集
- `questions.md` — 人工审阅格式

### Step B: 首次采样

```
/platform-sampler
```

输入 `questions.json`，输出 `responses.json`。

### Step C: 填写 official_urls

`/get-question` 生成的 `questions.json` 中每个问题的 `official_urls` 默认为空数组。在运行评分前，需要人工为每个问题填写官方页面 URL：

```json
{
  "questions": [
    {
      "id": "q_001",
      "question": "MindSpore 支持哪些安装方式？",
      "official_urls": ["https://www.mindspore.cn/install"],
      "notes": "安装指南页面完整覆盖"
    },
    {
      "id": "q_002",
      "question": "MindSpore 和 PyTorch 相比有哪些优势？",
      "official_urls": [],
      "notes": "无官方对比文档"
    }
  ]
}
```

> 判定规则：`official_urls` 非空 → 官方有内容，检查 AI 回答是否引用；`official_urls` 为空 → 官方内容缺失，标 P1。

### Step D: 首次评分

```
/scoring-engine
```

输入 `responses.json` + `questions.json`（含 `official_urls`），输出 `scoring-results.json`。

### Step E: 首次创建 Issue

```
/issue-creator dry_run=true
```

> `repo_url` 自动从 `.env` 的 `GEO_REPO_URL` 读取。`dry_run=true` 覆盖 `.env` 中的 `GEO_DRY_RUN`。

**首次运行完成后**，`assessments/MindSpore/` 目录下应有：
- `questions.json` — 问题集（`/get-question` 生成，含人工填写的 `official_urls`）
- `issue-map.json` — Issue 映射（自动生成）

---

## 定期复检（自动化流水线）

首次运行完成后，后续复检由 `AGENT.md` 编排，**无需人工介入**。

### 手动触发

在 Claude Code 中直接描述意图即可，Claude 会按照 `AGENT.md` 执行：

```
请按照 AGENT.md 对 MindSpore 社区执行一次 GEO 复检
```

> `community_dir` 和 `repo_url` 自动从 `.env` 的 `GEO_COMMUNITY_DIR` 和 `GEO_REPO_URL` 读取，无需每次传入。

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

### get-question — 生成/追加问题集

4 个数据来源路径，可单独选择或全选：

| 路径 | 参数值 | 数据来源 | 场景 |
|------|--------|----------|------|
| Path 1 | `forum` | MindSpore Discourse 论坛热帖 | 使用阶段 |
| Path 2 | `issue` | GitCode 仓库 Issue | 使用阶段 |
| Path 3 | `maillist` | SIG 邮件列表归档 | 使用阶段 |
| Path 4 | `website` | 官网站内搜索热词 | 使用阶段 |

```
/get-question paths=forum,issue
/get-question paths=all
/get-question                           # 全部默认从 .env 读取
```

> 每次执行自动加载 `assessments/{community}/questions.json`，将新问题**追加**到现有问题集末尾，语义重复的问题自动过滤。已填写的 `official_urls` 和 `notes` 保将原样保留。`community`、`forum_url`、`source_repo_url` 均从 `.env` 对应变量读取，owner/repo 自动解析；`paths` 未传时取 `GEO_PATHS`。

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

评分完成后，自动将 `questions.json` 中已标注的 `official_urls` 同步回 `questions.md`，在每行问题后新增「官方链接」列。

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

综合 `scoring-results.json`、`questions.json`、`issue-map.json`，生成每次运行的问题集全量报告。

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
├── assessments/                    # 社区评估数据
│   └── MindSpore/                  # MindSpore 社区
│       ├── questions.json               # 问题集 + official_urls（人工填写，source of truth）
│       ├── questions.md                 # 问题集（人工可读）
│       ├── issue-map.json               # Issue 映射（自动维护）
│       └── 2026-03-30/                 # 运行数据（按日期命名）
│           ├── responses.json
│           ├── scoring-results.json
│           ├── assessment-report.json
│           ├── assessment-report.md
│           └── created-issues.json
└── .claude/
    └── skills/                     # Skill 定义
        ├── get-question/
        ├── platform-sampler/
        ├── scoring-engine/
        ├── issue-creator/
        ├── assessment-report/
        ├── release-skills/
        └── skill-creator/
```

---

## 文件说明

### 手动维护的文件

这些文件需要人工创建和更新：

| 文件 | 更新时机 | 说明 |
|------|----------|------|
| `questions.json` | 运行 `/get-question` 后填写 `official_urls` | 问题集唯一来源，含官方 URL 标注；变更时 AGENT.md 会要求确认 |
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
  --inputs '{}' \
  --schedule "0 9 * * 1"   # 每周一 9:00
```

> `community_dir`、`repo_url`、`dry_run` 均从 `.env` 读取，`.inputs` 只需在需要临时覆盖时传入。

**前提条件**：
- `questions.json` 已就位（含人工填写的 `official_urls`）
- `.env` 中 API Keys 配置完整
- 仓库可访问（有 push 权限更新 issue-map）

**建议调度频率**：每周一次。AI 平台回答变化较慢，更高频率只增加成本。

---

## 常见问题

### Q: 如何更新问题集？

重新运行 `/get-question` 或直接编辑 `assessments/MindSpore/questions.json`。下次执行 AGENT.md 时，Step 0 会自动检测到变更并打印 diff，需要加 `accept_question_update=true` 才能继续。新增问题记得在 `questions.json` 中补充 `official_urls`。

### Q: 某个平台 API Key 过期了怎么办？

更新 `.env` 中对应的 Key。只要还有 2 个以上平台可用，采样不会中断。采样完成时 stdout 会输出覆盖率摘要，显示哪些平台缺失。

### Q: Issue 被手动关闭后，下次复检还会操作它吗？

会。系统通过 `issue-map.json` 追踪，如果该 suggestion 仍然存在，会向已关闭的 Issue 追加评论。如果 API 返回错误（如不允许评论已关闭 Issue），系统会记录错误并跳过，不会中断流程。

### Q: 如何查看某个问题的优化历史？

打开该问题在 GitCode/GitHub 上对应的 Issue，每次复检都会追加评论，包含引用率变化和平台覆盖情况，纵向看即为完整优化时间线。

### Q: 如何新增一个社区（如 openEuler）？

1. 创建目录 `assessments/openEuler/`
2. 运行 `/get-question paths=all` 生成 `questions.json`（需先把 `.env` 中 `GEO_COMMUNITY=openEuler`、`GEO_COMMUNITY_DIR=assessments/openEuler/`、`GEO_FORUM_URL`、`GEO_SOURCE_REPO_URL`、`GEO_REPO_URL` 更新为 openEuler 对应值）
3. 审核 `questions.md`，直接编辑 `questions.json` 做必要调整
4. 在 `assessments/openEuler/questions.json` 中填写各问题的 `official_urls`（以及顶层 `official_domains`）
5. 在 `.env` 中配置该社区的平台 API Keys
6. 按正常流程运行

### Q: dry-run 模式有什么用？

`dry_run=true` 时，所有 API 调用（采样、Issue 创建、评论）只打印 payload 到 stdout，不实际执行。适用于：
- 首次运行前验证 Issue 内容
- 调试 workflow 流程
- 培训新操作人员

### Q: 评分结果不准怎么办？

打开 `scoring-results.json`，找到对应的 `question_id` + `platform` 条目，确认 `official_urls` 标注是否准确。若标注有误，直接修改 `assessments/{community}/questions.json` 中对应问题的 `official_urls`，然后重新运行 scoring-engine（`steps=2,3,4,5`）。

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
