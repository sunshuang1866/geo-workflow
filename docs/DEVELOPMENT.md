# 软件开发规范

> **适用范围**: 本规范适用于 geo-workflow 的所有开发活动，包括人类开发者和 Claude Code Agent。
> **版本**: v1.0 (2026-05-26)
> **状态**: 强制执行

---

## 目录

1. [需求分析规范](#一需求分析规范)
2. [Skill 设计规范](#二skill-设计规范)
3. [开发流程规范](#三开发流程规范)
4. [代码规范](#四代码规范)
5. [测试标准](#五测试标准)
6. [环境搭建规范](#六环境搭建规范)
7. [版本管理规范](#七版本管理规范)
8. [文档规范](#八文档规范)
9. [AI Agent 开发规范](#九ai-agent-开发规范)
10. [代码审查规范](#十代码审查规范)

---

## 一、需求分析规范

### 1.1 需求文档要求

所有新 Skill 或流水线变更开发前，**必须**完成需求分析：

- **需求来源**: 明确需求来源（GEO 指标优化、社区扩展、平台支持、技术债务）
- **用户故事**: 使用标准格式 `As a [role], I want to [action], So that [benefit]`
- **验收标准**: 每个需求必须有可验证的验收标准（Given-When-Then 格式）
- **优先级**: 使用 MoSCoW 方法（Must/Should/Could/Won't）

### 1.2 需求评审清单

- [ ] 需求描述清晰、无歧义
- [ ] 明确影响哪些 Skill（get-question / platform-chat / scoring-engine / issue-creator / assessment-report）
- [ ] 明确影响哪些共享文件（questions.json 格式、scoring-results.json 格式、issue-map.json 格式）
- [ ] 格式变更是否向后兼容（已有 output/ 数据是否失效）
- [ ] 测试策略已定义
- [ ] 文档更新计划已明确（SKILL.md、README.md、AGENT.md）

### 1.3 需求变更

- 需求变更必须记录变更原因和对下游 Skill 的影响链
- 涉及跨 Skill 数据格式变更（如 scoring-results.json 新增字段）需要重新评审
- 变更必须同步更新所有受影响 Skill 的 `SKILL.md` 和 `AGENT.md`

---

## 二、Skill 设计规范

### 2.1 Skill 是什么

geo-workflow 的核心代码单元是 **Skill**，每个 Skill 是一个自包含的 Claude Code 可调用功能模块，位于 `.claude/skills/{skill-name}/`。

```
.claude/skills/{skill-name}/
├── SKILL.md            # 核心：过程性指令，供 Claude Code 执行
├── scripts/            # 小型 CLI 工具（Python），处理精确/脆弱逻辑
├── references/         # 参考资料（API 规范、规则文档、目录表）
└── assets/             # 输出模板、静态文件、JSON Schema
```

### 2.2 新 Skill 创建规范

**必须使用 `/skill-creator` 创建**，禁止手动创建 Skill 目录结构：

```
/skill-creator   # 在 Claude Code 中执行
```

`/skill-creator` 会自动校验 metadata 合规性并生成标准目录结构。

**SKILL.md 编写规范：**

| 要素 | 规范 |
|------|------|
| `name` | 1-64 字符，仅小写字母、数字、单连字符 |
| `description` | ≤ 1024 字符，第三人称，**必须包含反向触发条件**（"Do not use for..."） |
| 主体逻辑 | ≤ 500 行；超出部分拆分到 `references/` |
| 指令语气 | 第三人称祈使句（"Extract the text", "Run the build"） |
| 文件路径 | 使用相对路径，正斜杠（`/`） |

### 2.3 Skill 设计原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 每个 Skill 只做流水线中的一步，不跨步骤 |
| **接口明确** | 输入文件、输出文件、所需环境变量在 SKILL.md 顶部 Prerequisites 中列明 |
| **可跳过性** | Skill 必须支持 `dry_run` 参数，不写操作时仅输出预览 |
| **幂等性** | 重复运行同一 Skill 不应产生重复数据（`issue-map.json` 的 append-or-update 逻辑） |
| **降级策略** | 外部依赖（DB、平台会话）不可用时有明确降级路径，不直接 abort |
| **错误隔离** | 单个平台失败不应中断整个流水线 |

### 2.4 Script 设计规范

Skill 内部的 `scripts/` 用于处理精确逻辑（正则、JSON 解析、API 调用）：

- 每个 script 是**独立 CLI 工具**，通过 `argparse` 接收参数
- **stdout** 输出 JSON（机器可读），**stderr** 输出进度/警告/错误（人工可读）
- Exit code：`0` = 成功，`1` = 失败
- 共享工具函数提取到 `_shared/utils.py`，不在各 script 中重复实现

### 2.5 设计评审要点

- [ ] SKILL.md 主体逻辑 ≤ 500 行
- [ ] Prerequisites 列明了所有输入文件和必需环境变量
- [ ] Error Handling 章节覆盖了所有已知失败场景
- [ ] stdout/stderr 输出协议清晰
- [ ] `dry_run` 参数已实现
- [ ] 与 AGENT.md 流水线中的上下游接口已对齐

---

## 三、开发流程规范

### 3.1 开发工作流

```
需求分析 → Skill 设计（/skill-creator）→ 编码实现 → 手动验证 → 代码审查 → 合并 → /release-skills
```

### 3.2 分支策略

| 分支 | 用途 | 说明 |
|------|------|------|
| `main` | 稳定分支 | 仅接受经过审查的 PR |
| `feature/{skill-name}` | 新 Skill 开发 | 命名格式 `feature/skill-名称` |
| `fix/{brief-desc}` | 问题修复 | 命名格式 `fix/问题描述` |
| `refactor/{scope}` | 重构 | 命名格式 `refactor/范围` |

### 3.3 提交规范

使用 Conventional Commits 格式。**每次 commit 前必须先执行 `/release-skills` 更新 CHANGELOG.md**：

```
<type>(<scope>): <description>

[optional body]
```

**scope 约定**（对应 Skill 名称或项目级）：

| scope | 适用场景 |
|-------|---------|
| `get-question` | 问题生成 Skill |
| `platform-chat` | 平台采样 Skill |
| `scoring-engine` | 评分 Skill |
| `issue-creator` | Issue 创建 Skill |
| `assessment-report` | 评估报告 Skill |
| `prefill-urls` | URL 预填充 Skill |
| `shared` | `_shared/utils.py` 等共享代码 |
| `agent` | `AGENT.md` 流水线编排 |
| `project` | 根目录文件（CLAUDE.md、README.md、.env.example） |

**示例**:

```
feat(scoring-engine): support citations field for URL matching

Add Check 2 (citations field exact match) alongside existing
response_text substring match. Prevents false negatives when
AI platforms embed URLs in citation links but not in response text.

BREAKING CHANGE: None
```

### 3.4 提交前检查清单

- [ ] `black .claude/skills/` 格式化通过
- [ ] `flake8 .claude/skills/ --max-line-length=100` 无错误
- [ ] 无硬编码 token、密码、URL
- [ ] 已执行 `/release-skills` 更新 CHANGELOG.md
- [ ] 已更新受影响 Skill 的 SKILL.md
- [ ] 若涉及 AGENT.md 接口变更，已同步更新 AGENT.md
- [ ] 已更新 CLAUDE-RESUME.md 的 Current Status / Recent Changes 段落

---

## 四、代码规范

### 4.1 Python 编码规范

遵循 **PEP 8** 风格，使用工具自动检查：

```bash
# 代码格式化（项目根目录执行）
black .claude/skills/

# 代码风格检查
flake8 .claude/skills/ --max-line-length=100

# 类型检查（渐进式，优先对 _shared/ 启用）
mypy .claude/skills/_shared/
```

### 4.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 脚本文件名 | kebab-case 动词短语 | `fetch-forum-posts.py`, `score-urls.py` |
| 函数名 | snake_case，动词开头 | `fetch_from_db()`, `normalize_url()` |
| 私有函数 | 前缀 `_` | `_load_db_config()`, `_is_label_error()` |
| 常量 | UPPER_SNAKE_CASE | `MIN_VIEWS = 50`, `FORUM_TOP_N = 30` |
| 变量名 | snake_case，含义清晰 | `citation_rate`, `platform_records` |

### 4.3 stdout / stderr 通信协议

这是 Skill 脚本最核心的设计约束，**所有脚本必须严格遵守**：

| 流 | 用途 | 格式 |
|----|------|------|
| **stdout** | 机器可读输出（供下游脚本或 Claude 解析） | 纯 JSON |
| **stderr** | 人工可读进度、警告、错误 | 自由文本，见前缀约定 |

**stderr 前缀约定：**

```python
print(f"ERROR: questions.json not found: {path}", file=sys.stderr)   # 致命 → sys.exit(1)
print(f"WARNING: DB connection failed: {e}", file=sys.stderr)         # 非致命 → 继续运行
print(f"DB: fetched {n} posts for '{community}'", file=sys.stderr)   # 进度 → 无前缀
```

### 4.4 错误处理规范

```python
# ✅ 具体异常 + 上下文信息 + 合理降级
try:
    conn = psycopg2.connect(host=cfg["host"], ...)
except Exception as e:
    print(f"WARNING: DB connection failed: {e}", file=sys.stderr)
    return None   # 调用方切换到 Discourse API 回退路径

# ✅ 致命错误直接退出，信息含路径
try:
    return json.loads(p.read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
    sys.exit(1)

# ❌ 禁止：裸 except，吞掉异常
try:
    result = call_api(url)
except:
    result = {}
```

**异常类型优先级**（从具体到宽泛）：

1. `urllib.error.HTTPError` / `urllib.error.URLError`
2. `json.JSONDecodeError`
3. `psycopg2.Error`（数据库操作）
4. `playwright.async_api.Error`（浏览器自动化）
5. `Exception`（最后兜底，必须打印错误信息）

### 4.5 文档规范

```python
# ✅ 脚本级 docstring：说明用途、Usage、Exit codes
"""Fetch individual forum posts from PostgreSQL hotopic DB or Discourse API.

Usage:
    python3 fetch-forum-posts.py --community openeuler
    python3 fetch-forum-posts.py --community mindspore --api-url https://discuss.mindspore.cn

Exit codes:
  0 — success (at least one post returned)
  1 — no posts fetched from any source
"""

# ✅ 函数 docstring：Returns 标注 None 场景
def fetch_from_db(community: str, since: str | None, limit: int | None) -> list[dict] | None:
    """Fetch forum posts from PostgreSQL hotopic DB. Returns list or None on failure."""
```

### 4.6 环境变量读取规范

```python
# ✅ 推荐：明确处理缺失场景
community = os.environ.get("GEO_COMMUNITY", "")
if not community:
    print("ERROR: GEO_COMMUNITY not set in .env", file=sys.stderr)
    sys.exit(1)

# ✅ 可选变量给合理默认值
dry_run = os.environ.get("GEO_DRY_RUN", "false").lower() == "true"

# ❌ 禁止：直接 os.environ[key]（KeyError 无上下文）
community = os.environ["GEO_COMMUNITY"]
```

### 4.7 安全规范

- **禁止硬编码凭证**: token、密码、API Key 全部从环境变量读取
- **禁止提交 .env**: `.gitignore` 已排除，提供 `.env.example` 模板
- **输入验证**: 外部 API 响应和用户输入必须验证后使用
- **最小权限**: Issue Token 仅申请 `issues:write` 权限

---

## 五、测试标准

### 5.1 当前测试现状

geo-workflow 目前**无测试基础设施**（无 `tests/` 目录，无 pytest）。核心逻辑通过端到端手动运行验证。

**优先补充测试的模块：**

| 模块 | 原因 |
|------|------|
| `_shared/utils.py` | 被所有 Skill 脚本依赖 |
| `score-urls.py` | URL 匹配算法，边界情况多 |
| `parse-llm-score.py` | 验证逻辑，字段校验规则复杂 |
| `create-issue.py` | 标签错误降级逻辑需要 mock API |

### 5.2 脚本验证规范（当前替代测试的手段）

在无测试基础设施的情况下，每次修改脚本后**必须执行**以下验证：

```bash
# 1. 验证 stdout 输出为合法 JSON
python3 .claude/skills/scoring-engine/scripts/score-urls.py \
  output/openEuler/responses.json \
  output/openEuler/questions.json \
  /dev/stdout 2>/dev/null | python3 -m json.tool

# 2. 验证 dry-run 模式正常工作（无副作用）
python3 .claude/skills/issue-creator/scripts/create-issue.py \
  --owner opensourceways --repo geo-workflow \
  --payload '{"title":"test","body":"test","labels":[]}' \
  --dry-run

# 3. 验证 exit code 正确（错误参数应返回 1）
python3 .claude/skills/scoring-engine/scripts/validate-inputs.py; echo "Exit: $?"
```

### 5.3 添加单元测试（目标规范）

新增测试文件放在 `tests/` 目录（待创建），使用 pytest：

```bash
pip install pytest pytest-mock
pytest tests/ -v --tb=short
```

**测试编写规范：**

- 命名：`test_{脚本名无扩展名}_{场景}_{预期结果}`
- 结构：Arrange-Act-Assert
- 外部依赖（API、数据库）必须 Mock

```python
# tests/test_score_urls.py
def test_normalize_url_strips_protocol_and_www():
    from score_urls import normalize_url    # Arrange (implicit)
    result = normalize_url("https://www.mindspore.cn/install/")   # Act
    assert result == "mindspore.cn/install"                       # Assert

def test_is_cited_returns_false_when_no_match():
    from score_urls import is_cited
    cited, matched = is_cited("some response text", ["https://mindspore.cn/page"])
    assert cited is False
    assert matched == []
```

### 5.4 端到端验证流程

手动验证完整流水线（首次接入新社区或大版本改动后执行）：

```bash
# Step 1: 问题生成
/get-question community=openEuler paths=forum target_count=5

# Step 2: dry_run 模式运行全流水线（不实际创建 Issue）
# 在 Claude Code 中：
请按照 AGENT.md 对 openEuler 社区执行一次 GEO 复检 dry_run=true

# Step 3: 验证各输出文件格式
python3 -m json.tool output/openEuler/{date}/scoring-results.json > /dev/null
python3 -m json.tool output/openEuler/{date}/assessment-report.json > /dev/null
```

---

## 六、环境搭建规范

### 6.1 基础环境要求

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | >= 3.8 | 所有 Skill 脚本 |
| Claude Code CLI | 最新版 | Skill 调用入口 |
| Git | 任意版本 | 版本管理 |
| Chromium | 通过 Playwright 安装 | platform-chat 浏览器自动化 |

### 6.2 Python 依赖安装

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装 Playwright（浏览器自动化，platform-chat 必需）
pip install playwright
playwright install chromium

# 安装 PostgreSQL 客户端（get-question Channel 2 可选）
pip install psycopg2-binary

# 安装代码质量工具
pip install black flake8 mypy

# 安装测试工具（如已添加测试）
pip install pytest pytest-mock
```

### 6.3 环境变量配置

```bash
# 复制模板
cp .env.example .env

# 编辑 .env，按以下优先级填写
```

**最小可运行配置（首次评估）：**

| 变量 | 必填场景 | 说明 |
|------|---------|------|
| `GEO_COMMUNITY` | 始终 | 当前评估的社区名称，如 `openEuler` |
| `GEO_COMMUNITY_DIR` | 始终 | 社区数据目录，如 `output/openEuler/` |
| `GEO_FORUM_URL` | get-question forum 路径 | Discourse 论坛地址 |
| `GEO_REPO_URL` | issue-creator | Issue 创建目标仓库 |
| `MONGODB_HOST/PORT/USER/PASSWORD` | get-question | 热点话题数据库 |
| `GITHUB_TOKEN` 或 `GITCODE_TOKEN` | issue-creator | Issue 创建权限（`issues:write`） |

**平台采样凭证（platform-chat）：**

| 平台 | 凭证方式 |
|------|---------|
| ChatGPT | `output/{community}/.chatgpt-session.json` |
| DeepSeek | `DEEPSEEK_WEB_EMAIL` + `DEEPSEEK_WEB_PASSWORD` |
| Gemini | 匿名可用（无引用）；有 `.gemini-session.json` 启用 Search Grounding |
| Qwen | `QWEN_WEB_EMAIL` + `QWEN_WEB_PASSWORD` |

### 6.4 社区目录初始化

```bash
# 创建社区目录
mkdir -p output/openEuler/

# 生成初始问题集
# 在 Claude Code 中：
/get-question community=openEuler paths=all target_count=100

# 预填充 official_urls
/prefill-urls community=openEuler

# 人工审核并补充 official_urls
# 编辑 output/openEuler/questions.json，检查 official_urls 字段

# 验证配置
cat .env | grep GEO_
```

### 6.5 工具配置文件

**black 配置**（`pyproject.toml`，如项目根不存在则创建）：

```toml
[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi?$'
```

**flake8 配置**（`.flake8`）：

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv
extend-ignore = E203, W503
per-file-ignores =
    # sys.path.insert is intentional for _shared imports
    .claude/skills/*/scripts/*.py: E402
```

---

## 七、版本管理规范

### 7.1 版本号规则

使用语义化版本号 `MAJOR.MINOR.PATCH`（存储于项目根 `VERSION` 文件或 `marketplace.json`）：

| 变更类型 | 版本升级 | 示例 |
|---------|---------|------|
| 不兼容的数据格式变更（scoring-results.json 字段删除） | MAJOR | 1.x.x → 2.0.0 |
| 新增 Skill 或新增可选字段 | MINOR | 1.2.x → 1.3.0 |
| Bug 修复、文档更新 | PATCH | 1.2.3 → 1.2.4 |

### 7.2 发布流程

**必须使用 `/release-skills` 执行发布，禁止手动编辑 CHANGELOG.md：**

```
/release-skills              # 自动检测版本变更类型
/release-skills --dry-run    # 预览发布内容
/release-skills --minor      # 强制次版本升级（新 Skill）
/release-skills --patch      # 强制补丁升级（bug fix）
/release-skills --major      # 强制主版本升级（破坏性变更）
```

`/release-skills` 自动完成：
1. 分析 `git log` 按 Conventional Commits 分类
2. 按 Skill 分组生成 CHANGELOG.md 条目
3. 创建 git commit + tag
4. 可选 push 到 remote

### 7.3 Git 操作规范

- 禁止直接推送 `main` 分支
- PR 合并前必须通过代码审查
- 提交信息必须遵循 Conventional Commits 格式
- **每次 commit 前必须先执行 `/release-skills`**（CLAUDE.md 规则 #7）

---

## 八、文档规范

### 8.1 文档体系

| 文档 | 位置 | 维护者 | 说明 |
|------|------|--------|------|
| `README.md` | 根目录 | 人工 | 用户快速开始、目录结构、使用示例 |
| `CLAUDE.md` | 根目录 | 人工 | Claude Code 开发规则（11 条强制规则） |
| `AGENT.md` | 根目录 | 人工 | 流水线编排规范（6 步骤详细定义） |
| `CLAUDE-RESUME.md` | 根目录 | **Claude 自动维护** | 会话恢复上下文，禁止人工编辑 |
| `SKILL.md` | 各 Skill 目录 | 人工/Claude | Skill 过程性指令 |
| `docs/PRD.md` | docs/ | 人工 | 产品需求文档 |
| `docs/architecture.md` | docs/ | 人工 | 架构设计 |
| `docs/DEVELOPMENT.md` | docs/ | 人工 | 本文档 |
| `docs/CLEAN_CODE.md` | docs/ | 人工 | 代码规范与评估 |
| `CHANGELOG.md` | 根目录 | **`/release-skills` 自动维护** | 版本变更记录，禁止手工编辑 |

### 8.2 文档更新要求

| 变更类型 | 必须更新的文档 |
|---------|--------------|
| 新增 Skill | 对应 SKILL.md、README.md（目录结构）、AGENT.md（如接入流水线） |
| 修改 Skill 输入/输出格式 | SKILL.md、AGENT.md（上下游接口）、README.md（示例） |
| 新增环境变量 | `.env.example`、README.md（前置准备表）、AGENT.md（Prerequisites） |
| 新增支持的社区 | README.md（常见问题：如何新增社区） |
| 修复 Bug | CHANGELOG.md（通过 `/release-skills`） |

### 8.3 CLAUDE-RESUME.md 维护规则

每次完成任何改变项目状态的任务后，**Claude Code 必须更新** `CLAUDE-RESUME.md`：

```markdown
## Current Status
[当前开发阶段和完成情况]

## TODO
- [ ] 待办事项（优先级从高到低）

## Recent Changes
- YYYY-MM-DD: [变更描述]

## Key Decisions
- [已确定的关键技术决策]
```

> 禁止人工编辑此文件；如需修正内容，在 Claude Code 会话中告知 Claude 更新。

### 8.4 文档格式

- 使用 Markdown 格式，代码块必须指定语言
- 表格必须对齐，链接必须有效
- 中英文混排时，中英文之间加空格

---

## 九、AI Agent 开发规范

> geo-workflow 以 **Claude Code** 作为主要开发工具，本节规定 Claude Code Agent 的开发行为准则。

### 9.1 会话开始时的强制行为

每次开启新 Claude Code 会话，**必须立即**执行：

```
# 读取项目上下文（CLAUDE.md 规则 #9）
Read CLAUDE-RESUME.md
```

不得在恢复上下文前开始任何代码修改。

### 9.2 开发前置要求

| 规则 | 说明 |
|------|------|
| 描述方案后等待确认 | 编写任何代码前，先描述实现方案，等待人工确认（CLAUDE.md 规则 #1） |
| 澄清歧义需求 | 需求不清晰时，先提问再动手（CLAUDE.md 规则 #2） |
| 限制单次变更范围 | 涉及超过 3 个文件的任务，先拆分后执行（CLAUDE.md 规则 #4） |
| 创建新 Skill 必须用 `/skill-creator` | 禁止手动创建 Skill 目录（CLAUDE.md 规则 #8） |

### 9.3 开发流程

```
1. 读取 CLAUDE-RESUME.md 恢复上下文
2. 理解需求和现有代码（读取相关 SKILL.md / AGENT.md）
3. 描述实现方案，等待确认
4. 若需新 Skill：执行 /skill-creator
5. 实现功能代码（脚本 / SKILL.md 指令）
6. 手动验证（dry_run 或脚本级验证）
7. 检查代码规范（black / flake8）
8. 更新相关文档（SKILL.md / AGENT.md / README.md）
9. 更新 CLAUDE-RESUME.md
10. 执行 /release-skills 更新 CHANGELOG.md
11. 提交代码
```

### 9.4 代码生成要求

- 生成的脚本必须有完整的模块级 docstring（用途、Usage、Exit codes）
- 必须实现 stdout/stderr 分离协议
- 必须包含适当的错误处理（具体异常类型 + 上下文信息）
- 禁止硬编码配置（token、URL、密码）
- 修改共享 `_shared/utils.py` 时，列出所有调用方并确认无破坏性影响

### 9.5 自检清单

Agent 完成代码后必须自检：

- [ ] `black .claude/skills/` 格式化通过
- [ ] `flake8 .claude/skills/ --max-line-length=100` 无错误
- [ ] stdout/stderr 分离正确（stdout 输出纯 JSON）
- [ ] exit code 规范（失败时 `sys.exit(1)`）
- [ ] 无硬编码凭证
- [ ] 脚本级 docstring 完整
- [ ] CLAUDE-RESUME.md 已更新

### 9.6 常见错误防范

| 禁止行为 | 原因 |
|---------|------|
| 在 stdout 混入进度文本 | 破坏 JSON 解析，导致下游 Skill 失败 |
| 裸 `except:` 吞掉异常 | 隐藏问题，调试困难 |
| 直接编辑 CLAUDE-RESUME.md | 应由 Claude 在任务完成后自动更新 |
| 直接编辑 CHANGELOG.md | 必须通过 `/release-skills` 维护 |
| 在未 dry_run 确认前执行 Issue 创建 | 会在 GitCode/GitHub 产生真实 Issue |
| 创建 Skill 时不用 `/skill-creator` | SKILL.md metadata 可能不合规 |
| 在新会话中不读 CLAUDE-RESUME.md | 会重复已完成的工作或遗漏上下文 |

---

## 十、代码审查规范

### 10.1 审查要点

| 检查项 | 说明 |
|-------|------|
| **接口正确性** | stdout 输出格式是否与 AGENT.md / 下游 Skill 预期一致 |
| **错误处理** | 是否覆盖了 SKILL.md Error Handling 中列出的所有失败场景 |
| **stdout/stderr 分离** | 是否严格遵守通信协议 |
| **环境变量** | 新增变量是否同步更新 `.env.example` |
| **向后兼容** | 数据格式变更是否影响已有 output/ 文件 |
| **安全性** | 无硬编码凭证，无敏感信息泄漏 |
| **文档** | SKILL.md / AGENT.md / README.md 是否同步更新 |
| **Dry-run** | `dry_run=true` 是否正常工作（无副作用） |

### 10.2 审查流程

1. 拉取 PR 分支，检查变更文件列表
2. 重点审查 `SKILL.md`（是否 ≤ 500 行，接口是否清晰）
3. 审查脚本 stdout/stderr 实现
4. 执行 `black --check` 和 `flake8` 验证格式
5. 若涉及 Issue 创建相关脚本，验证 `dry_run` 路径
6. 提出审查意见后，作者修复并请求重新审查

### 10.3 审查意见格式

```
✅ 通过：URL 规范化逻辑正确，覆盖 http/https/www 三种情况
⚠️ 建议：fetch_from_db 函数过长（~90 行），建议拆分 SQL 构建和结果解析
❌ 必须修复：fetch_discourse() 的进度信息输出到了 stdout，会破坏 JSON 解析
```

---

## 附录

### A. 工具配置速查

**black**（`pyproject.toml`）:
```toml
[tool.black]
line-length = 100
target-version = ['py38']
```

**flake8**（`.flake8`）:
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv
extend-ignore = E203, W503
per-file-ignores =
    .claude/skills/*/scripts/*.py: E402
```

### B. 常用命令速查

```bash
# 代码格式化
black .claude/skills/

# 代码检查
flake8 .claude/skills/ --max-line-length=100

# 验证 JSON 输出
python3 .claude/skills/scoring-engine/scripts/score-urls.py \
  responses.json questions.json /dev/stdout 2>/dev/null | python3 -m json.tool

# 手动验证完整流水线（dry_run）
# 在 Claude Code 中：
# 请按照 AGENT.md 对 openEuler 社区执行一次 GEO 复检 dry_run=true

# 发布（每次 commit 前）
# /release-skills

# 创建新 Skill
# /skill-creator
```

### C. 参考资源

- [PEP 8 - Python 风格指南](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [agentskills.io Spec](https://agentskills.io/) — Skill SKILL.md 规范
- [Playwright Python](https://playwright.dev/python/) — 浏览器自动化
- [black 文档](https://black.readthedocs.io/)

---

*本文档版本: v1.0 | 更新日期: 2026-05-26*
*下次审查日期: 2026-08-26*
