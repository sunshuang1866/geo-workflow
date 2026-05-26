# GEO Search Assessment

GEO（Generative Engine Optimization）搜索能力诊断系统 —— 自动评估开源社区在主流 AI 搜索平台中的表现，并生成可执行的改进建议。

当前已支持多个社区，本文示例统一使用 **openEuler**，可扩展至任意支持 Discourse 论坛或 GitCode/GitHub Issue 的开源社区。

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
│  get-question   │────▶│  platform-chat   │────▶│ scoring-engine │────▶│ issue-creator │────▶│ assessment-report │
│  生成问题集       │     │  采样 AI 平台     │     │  评分 + 诊断    │     │ 创建/更新Issue  │     │  生成评估报告       │
└─────────────────┘     └──────────────────┘     └───────┬────────┘     └───────────────┘     └───────────────────┘
       ↓                        ↓                        ↓                       ↓                       ↓
  questions.json          responses.json         scoring-results.json      created-issues.json   assessment-report.json
  questions.md                                   issue-map.json            assessment-report.md
                                                
                                                
```

运行模式有两种：

| 模式 | 场景 | 人工介入 | 触发方式 |
|------|------|----------|----------|
| **首次运行** | 建立基线，准备问题集和标注 | 需要多步人工操作 | 手动 |
| **定期复检** | 周期性检测分数变化，更新 Issue | 无需人工介入 | ClaudeCode / OpenClaw |

---

## 前置准备

### 1. 一键初始化环境

克隆仓库后，运行一次：

```bash
bash scripts/setup.sh
```

该脚本自动完成所有环境准备工作：

| 步骤 | 内容 |
|------|------|
| Python 依赖 | `pip3 install -r requirements.txt` |
| Playwright 浏览器 | 安装 Chromium（platform-chat 采样使用） |
| `.env` 文件 | 从 `.env.example` 自动生成（已存在则跳过） |
| git pre-commit hook | 安装提交前自动检查（格式 + lint） |

### 2. 填写凭证

编辑 `.env`（`setup.sh` 已自动创建），按下表填写必需凭证：

| 变量 | 用途 | 必需 |
|------|------|------|
| `DEEPSEEK_WEB_EMAIL` | DeepSeek Web 端自动登录账号 | 使用 deepseek-web 时必需 |
| `DEEPSEEK_WEB_PASSWORD` | DeepSeek Web 端自动登录密码 | 使用 deepseek-web 时必需 |
| `QWEN_WEB_EMAIL` | Qwen Web 端自动登录账号 | 使用 qwen-web 时必需 |
| `QWEN_WEB_PASSWORD` | Qwen Web 端自动登录密码 | 使用 qwen-web 时必需 |
| `GITCODE_TOKEN` | GitCode Issue 创建 | 在 GitCode 创建 Issue 时必需 |
| `GITHUB_TOKEN` | GitHub Issue 创建 | 在 GitHub 创建 Issue 时必需 |
| `MONGODB_HOST` | MongoDB 社区热点话题库主机地址 | get-question 必需（含论坛/Issue/邮件列表数据） |
| `MONGODB_PORT` | MongoDB 端口 | get-question 必需 |
| `MONGODB_USER` | MongoDB 用户名 | get-question 必需 |
| `MONGODB_PASSWORD` | MongoDB 密码 | get-question 必需 |
| `HOTOPIC_DB_CONFIG_JSON` | PostgreSQL 论坛帖子补充渠道多社区配置（JSON） | get-question forum 路径 Channel 2 可选 |

**工作流配置**（每次切换社区时更新）：

| 变量 | 用途 | 示例值 |
|------|------|--------|
| `GEO_COMMUNITY` | 社区名称，供所有 Skill 读取 | `openEuler` |
| `GEO_COMMUNITY_DIR` | 社区数据目录路径 | `output/openEuler/` |
| `GEO_FORUM_URL` | 社区 Discourse 论坛地址 | `https://forum.openeuler.org` |
| `GEO_PATHS` | get-question 默认来源路径 | `all` |
| `GEO_DRY_RUN` | 全局 dry-run 开关 | `false` |
| `GEO_REPO_URL` | Issue 创建目标仓库 URL | `https://github.com/opensourceways/geo-workflow/` |
| `GEO_QUESTION_TARGET_COUNT` | 目标新增问题数（`get-question` 使用） | `100` |

> 采样使用 `/platform-chat` 浏览器自动化，不依赖平台接口密钥；请至少准备 1 个可用平台的 Web 登录凭证或会话文件。

### 3. 验证环境

```bash
bash scripts/validate-env.sh
```

逐项检查 `.env` 变量、Python 依赖、Playwright 浏览器和系统库是否就绪，输出 ✓/✗ 和修复提示。**所有项目显示 ✓ 后再继续。**

### 4. 创建社区目录

社区数据统一存放在 `output/` 下：

```bash
mkdir -p output/openEuler/
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
/platform-chat
```

输入 `questions.json`，逐平台通过浏览器自动化采集 AI 回答，输出 `responses.json`。

> 支持 `chatgpt-web`、`deepseek-web`、`gemini-web`、`qwen-web`，通过 `platform` 参数指定；各平台所需凭证见前置准备。

### Step C: 填写 official_urls

`/get-question` 生成的 `questions.json` 中每个问题的 `official_urls` 默认为空数组。在运行评分前，需要人工为每个问题填写官方页面 URL：

```json
{
  "questions": [
    {
      "id": "q_001",
      "question": "openEuler 支持哪些安装方式？",
      "official_urls": ["https://www.openeuler.org/zh/download/"],
      "notes": "安装指南页面完整覆盖"
    },
    {
      "id": "q_002",
      "question": "openEuler 在服务器操作系统场景下有哪些优势？",
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

**首次运行完成后**，`output/openEuler/` 目录下应有：
- `questions.json` — 问题集（`/get-question` 生成，含人工填写的 `official_urls`）
- `issue-map.json` — Issue 映射（自动生成）

---

## 定期复检（自动化流水线）

首次运行完成后，后续复检由 `AGENT.md` 编排，**无需人工介入**。

### 手动触发

在 Claude Code 中直接描述意图即可，Claude 会按照 `AGENT.md` 执行：

```
请按照 AGENT.md 对 openEuler 社区执行一次 GEO 复检
```

> `community_dir` 和 `repo_url` 自动从 `.env` 的 `GEO_COMMUNITY_DIR` 和 `GEO_REPO_URL` 读取，无需每次传入。

### 自动化执行流程

AGENT.md 定义的 6 个步骤，支持通过 `steps` 和 `scope` 参数选择性执行：

```
Step 0 (init):      初始化 runs/{date}/ 目录，检测 questions.json 变更
         ↓
Step 1 (sample):    /platform-chat → responses.json（scope 控制问题范围）
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

---

## 各步骤详解

### get-question — 生成/追加问题集

#### 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `community` | 否 | `.env` 的 `GEO_COMMUNITY` | 社区名称，如 `openEuler`。未设置时中止并报错 |
| `target_count` | 否 | `.env` 的 `GEO_QUESTION_TARGET_COUNT` → `100` | 本次运行目标新增问题数（不限制问题集累积总数） |
| `seed_keywords` | 否 | LLM 自动推导 | 逗号分隔的技术关键词，用于辅助 LLM 改写问题 |
| `paths` | 否 | `.env` 的 `GEO_PATHS` → `all` | 数据来源路径：`forum` / `website` / `all` |
| `forum_url` | 否 | `.env` 的 `GEO_FORUM_URL` | Discourse 论坛 base URL（Channel 2 备用） |

> **参数优先级**：显式调用参数 > `.env` 变量 > 默认值

#### 数据来源渠道

本质上共 5 个数据渠道，由 `paths` 参数控制是否运行：

| 渠道 | `paths` | 数据来源 | 额外依赖 |
|------|---------|----------|----------|
| 邮件列表 | `forum` | MongoDB `community-hot-topic` — 聚合自社区邮件列表，经 consult-filter 过滤，按咨询数降序 | `MONGODB_*`（必需） |
| 仓库 Issue | `forum` | MongoDB `community-hot-topic` — 聚合自社区仓库 Issue，经 consult-filter 过滤，按咨询数降序 | `MONGODB_*`（必需） |
| 论坛帖子 | `forum` | MongoDB `community-hot-topic` — 聚合自社区论坛，经 consult-filter 过滤，按咨询数降序；**另**：PostgreSQL/Discourse 单帖补充（`views > 50`，top 30，按浏览量降序） | `MONGODB_*`（必需）；`HOTOPIC_DB_*` 或 `GEO_FORUM_URL`（可选） |
| 官网热词 | `website` | 官网站内搜索热词 API，LLM 改写为自然语言问题 | `WEBSITE_SEARCH_URL` |
| 人工 | 自动 | `manual-questions.md`（项目根目录）存在时自动加载，无需在 `paths` 中指定 | 文件存在即可 |

> **consult-filter 规则**：MongoDB 中仅保留含用户咨询类内容的话题。排除全为 `[Req]`/`[Task]`/`[RFC]`/`[Doc]` 的话题；混合话题当咨询类来源 ≥ 50% 时保留。每个话题携带 `咨询数c/排除数e/总数t` 用于排序展示。

#### 使用示例

```
/get-question                                    # 全部从 .env 读取
/get-question paths=forum                        # 只采集论坛（双渠道：MongoDB + PG）
/get-question paths=website                      # 只采集官网热词
/get-question community=openEuler target_count=50
```

> 每次执行自动加载 `output/{community}/questions.json`，将新问题**追加**到现有问题集末尾，语义重复的问题自动过滤。已填写的 `official_urls` 和 `notes` 将原样保留。

### platform-chat — 采样 AI 平台（浏览器自动化）

通过 Playwright + Chromium 驱动各平台 Web UI，无需平台接口密钥：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `platform` | 目标平台 | `chatgpt-web` |
| `questions` | 指定问题 ID（逗号分隔） | 全部 |
| `output_mode` | `new_run` / `append` | `new_run` |
| `timeout` | 等待平台回答的秒数 | `90` |
| `min_citations` | 最少引用数，不足时自动追问 | `8` |

各平台凭证要求：
- **ChatGPT**：`output/{community}/.chatgpt-session.json`
- **DeepSeek**：`DEEPSEEK_WEB_EMAIL` + `DEEPSEEK_WEB_PASSWORD`（自动登录）
- **Gemini**：匿名可用（无引用）；有 `.gemini-session.json` 时启用 Search Grounding
- **Qwen**：`QWEN_WEB_EMAIL` + `QWEN_WEB_PASSWORD`（自动登录）

### scoring-engine — 评分诊断

纯 URL 字符串匹配（精确 URL + 域名级），无 LLM 评估：

| 状态 | 描述 | 严重级别 | 说明 |
|------|------|----------|------|
| `satisfied` | 引用了官方内容 | OK | ≥75% 平台回答中包含官方 URL |
| `not_cited` | 有内容未被引用 | P0 | 官方已有内容但 <75% 平台引用 |
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
├── .env.example                    # 环境变量模板
├── .env                            # 凭证配置（不入库）
├── .gitignore
├── pyproject.toml                  # Python 项目配置（pytest、black、coverage）
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI 门禁（PR 合入前自动运行）
├── scripts/                        # 开发环境工具脚本
│   ├── setup.sh                    # 一键初始化（克隆后运行一次）
│   ├── validate-env.sh             # 环境健康检查（随时可运行）
│   └── pre-commit.sh               # git pre-commit hook（由 setup.sh 自动安装）
├── tests/                          # 自动化测试集（由 CI 门禁执行）
│   ├── conftest.py                 # 公共 fixture 与辅助函数
│   ├── test_score_urls.py          # scoring-engine URL 匹配逻辑测试
│   ├── test_shared_utils.py        # _shared/utils.py 工具函数测试
│   ├── test_validate_questions.py  # 问题集格式校验测试
│   └── test_clean_code.py          # stdout/stderr 协议与退出码合规测试
├── output/                    # 社区评估数据
│   └── openEuler/                  # openEuler 社区
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
        ├── platform-chat/
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
| `.env` | 凭证变更时 | Web 登录凭证、Issue Token、工作流变量 |

### 自动维护的文件

这些文件由系统自动创建和更新，**不要手动编辑**：

| 文件 | 生成时机 | 说明 |
|------|----------|------|
| `issue-map.json` | 每次 issue-creator 运行后 | 累积的 suggestion → issue 映射 |
| `{community_dir}/{date}/*` | 每次复检运行时 | 本次运行的所有中间和最终数据 |
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
- `.env` 中平台 Web 凭证、Issue Token 与工作流变量配置完整
- 仓库可访问（有 push 权限更新 issue-map）

**建议调度频率**：每周一次。AI 平台回答变化较慢，更高频率只增加成本。

---

## 常见问题

### Q: 如何更新问题集？

重新运行 `/get-question` 或直接编辑 `output/openEuler/questions.json`。下次执行 AGENT.md 时，Step 0 会自动检测到变更并打印 diff，需要加 `accept_question_update=true` 才能继续。新增问题记得在 `questions.json` 中补充 `official_urls`。

### Q: 某个平台 Web 凭证或会话失效了怎么办？

更新对应平台凭证即可：
- DeepSeek/Qwen：更新 `.env` 中 `*_WEB_EMAIL` 与 `*_WEB_PASSWORD`
- ChatGPT/Gemini：更新 `output/{community}/.*-session.json` 会话文件
只要至少 1 个平台可用，采样即可继续；失败平台会记录在 `skipped_platforms`。

### Q: Issue 被手动关闭后，下次复检还会操作它吗？

会。系统通过 `issue-map.json` 追踪，如果该 suggestion 仍然存在，会向已关闭的 Issue 追加评论。如果 API 返回错误（如不允许评论已关闭 Issue），系统会记录错误并跳过，不会中断流程。

### Q: 如何查看某个问题的优化历史？

打开该问题在 GitCode/GitHub 上对应的 Issue，每次复检都会追加评论，包含引用率变化和平台覆盖情况，纵向看即为完整优化时间线。

### Q: 如何新增一个社区（以 openEuler 为例）？

1. 创建目录 `output/openEuler/`
2. 运行 `/get-question paths=all` 生成 `questions.json`（需先把 `.env` 中 `GEO_COMMUNITY=openEuler`、`GEO_COMMUNITY_DIR=output/openEuler/`、`GEO_FORUM_URL`、`GEO_REPO_URL` 更新为 openEuler 对应值）
3. 审核 `questions.md`，直接编辑 `questions.json` 做必要调整
4. 在 `output/openEuler/questions.json` 中填写各问题的 `official_urls`（以及顶层 `official_domains`）
5. 在 `.env` 中配置该社区的平台 Web 凭证与 Issue Token
6. 按正常流程运行

### Q: dry-run 模式有什么用？

`dry_run=true` 时，不会执行 Issue 创建与评论等写操作（仅输出预览 payload）。适用于：
- 首次运行前验证 Issue 内容
- 调试 workflow 流程
- 培训新操作人员

### Q: 评分结果不准怎么办？

打开 `scoring-results.json`，找到对应的 `question_id` + `platform` 条目，确认 `official_urls` 标注是否准确。若标注有误，直接修改 `output/{community}/questions.json` 中对应问题的 `official_urls`，然后重新运行 scoring-engine（`steps=2,3,4,5`）。

---

## 使用 Claude Code 开发

本仓库使用 [Claude Code](https://claude.ai/code) 作为主要开发工具，配置了自动化工作流和会话恢复机制。

### CI 门禁 —— 代码合入保障

质量检查分两层，分工明确：

| 层级 | 触发时机 | 检查内容 | 目的 |
|------|----------|----------|------|
| **本地 pre-commit** | `git commit` | black 格式检查 + flake8 lint | 本地即时拦截低级错误，秒级反馈 |
| **GitHub Actions CI** | PR 创建/更新 | black + flake8 + 全套测试 + 覆盖率（≥70%） | 合入主分支前的强制门禁 |

CI 配置文件：`.github/workflows/ci.yml`，PR 所有检查通过后方可合入 `main`。

测试集位于 `tests/`，涵盖：
- URL 匹配算法（`test_score_urls.py`）
- 共享工具函数（`test_shared_utils.py`）
- 问题集格式校验（`test_validate_questions.py`）
- stdout/stderr 协议合规（`test_clean_code.py`）

本地手动运行全套测试：

```bash
python3 -m pytest
```

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
