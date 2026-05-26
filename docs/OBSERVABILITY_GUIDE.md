# 可观测性指南

> **适用范围**: geo-workflow GEO 搜索能力诊断系统的运行监控、结果解读与故障排查。
> **版本**: v1.0 (2026-05-26)

---

## 目录

1. [运行时进度观测](#一运行时进度观测)
2. [运行结果文件体系](#二运行结果文件体系)
3. [GEO 指标解读](#三geo-指标解读)
4. [Issue 追踪状态](#四issue-追踪状态)
5. [故障排查](#五故障排查)
6. [健康检查命令速查](#六健康检查命令速查)

---

## 一、运行时进度观测

### 1.1 流水线执行输出

在 Claude Code 中触发 GEO 复检时，各步骤的 stderr 输出实时可见。典型的完整运行输出如下：

**Step 0 — 初始化**
```
[init] community_dir: output/openEuler/
[init] repo_url: https://github.com/opensourceways/geo-workflow
[init] dry_run: false
[init] questions.json: no previous run found, treating as first run
[init] Created: output/openEuler/2026-05-26/
[init] version_label: V3
```

**Step 1 — 平台采样（platform-chat）**
```
[platform-chat] Starting deepseek-web, 47 questions
  [q_001/47] Submitting to DeepSeek...
  [q_001/47] Response received (2847 chars, 3 citations)
  [q_002/47] Submitting to DeepSeek...
  ...
  [q_047/47] Response received (1923 chars, 5 citations)
[platform-chat] deepseek-web complete: 47/47 questions sampled
[platform-chat] Starting qwen-web, 47 questions
  ...
[platform-chat] qwen-web complete: 47/47 questions sampled
[platform-chat] Output: output/openEuler/2026-05-26/responses.json
```

**Step 2 — 评分（scoring-engine）**
```
Inputs loaded:
  Questions: 47
  Platforms: deepseek-web, qwen-web
  Response pairs: 94
  Questions with official URLs: 41
  Questions without official URLs: 6

Question-Level Scoring (threshold: 75%):
  Total questions: 47
  引用了官方内容 (OK):  18  — citation_rate ≥ 75%
  有内容未被引用 (P0):  23  — citation_rate < 75%
  官方内容缺失 (P1):    6   — no official URLs

Output: output/openEuler/2026-05-26/scoring-results.json
```

**Step 3 — Issue 创建/更新（issue-creator）**
```
[issue-creator] Processing 23 P0 + 6 P1 questions
[issue-creator] issue-map.json: 18 existing issues loaded
  q_001: matched existing issue #42 → appending comment
  q_002: matched existing issue #42 → appending comment
  q_015: no match → creating new issue
  [NEW] Issue created: #89 — https://github.com/.../issues/89
  ...
[issue-creator] Summary: 2 created, 16 updated, 3 resolved (score improved to OK)
Output: output/openEuler/2026-05-26/created-issues.json
```

**Step 5 — 完成摘要**
```
GEO Assessment Run Complete
===========================
Community: openEuler
Version: V3
Date: 2026-05-26

Scoring: 47/47 questions
  引用了官方内容 (OK): 18
  有内容未被引用 (P0): 23
  官方内容缺失 (P1):    6

Issues: 2 created, 16 updated, 3 resolved

Outputs:
  output/openEuler/2026-05-26/scoring-results.json
  output/openEuler/2026-05-26/assessment-report.json
  output/openEuler/2026-05-26/assessment-report.md
  output/openEuler/issue-map.json
```

### 1.2 运行日志捕获

将完整运行输出持久化到 `run.log`（推荐在长时间批量采样时使用）：

```bash
# 方式 1：在 Claude Code 中生成 run.sh 脚本后执行
bash output/{community}/{date}/run.sh 2>&1 | tee output/{community}/{date}/run.log

# 方式 2：使用 tee 实时同步并记录
python3 .claude/skills/platform-chat/scripts/run-platform-chat.py \
  --platform deepseek-web \
  --community openEuler \
  --date 2026-05-26 \
  2>&1 | tee -a output/openEuler/2026-05-26/run.log
```

> `run.log` 由 bash 脚本自动写入，用于事后分析 Playwright 浏览器输出、平台超时等底层错误。

### 1.3 部分步骤的进度观测

只跑流水线某几步时（如 `steps=2,3,4,5`），Claude Code 会跳过未执行步骤，直接输出已执行步骤的进度。可通过 `run-meta.json` 区分哪些步骤已完成（见 [§2.2](#22-run-metajson--运行状态快照)）。

---

## 二、运行结果文件体系

每次复检运行后，`output/{community}/{date}/` 目录下产生以下文件：

```
output/openEuler/
├── questions.json                  ← 问题集（source of truth，含 official_urls）
├── questions.md                    ← 问题集（人工可读，含官方链接列）
├── issue-map.json                  ← 累积 Issue 映射（跨轮次持久化）
├── question-update-log.md          ← 问题集变更历史（accept_question_update 时写入）
└── 2026-05-26/                     ← 本次运行目录
    ├── questions.json              ← 本次 questions.json 快照
    ├── responses.json              ← 各平台 AI 回答（Step 1 输出）
    ├── scoring-results.json        ← 评分结果（Step 2 输出）
    ├── created-issues.json         ← Issue 活动记录（Step 3 输出）
    ├── assessment-report.json      ← 完整评估报告（机器可读，Step 4 输出）
    ├── assessment-report.md        ← 完整评估报告（人工可读，Step 4 输出）
    ├── run-meta.json               ← 运行元数据和摘要（Step 0/5 写入）
    └── run.log                     ← 原始运行日志（bash tee 写入，可选）
```

### 2.1 文件用途速查

| 文件 | 一句话用途 | 典型查阅场景 |
|------|-----------|-------------|
| `run-meta.json` | 本次运行整体状态和 KPI | 快速判断运行是否成功、跳过了哪些平台 |
| `responses.json` | 各平台原始 AI 回答 | 调试引用判断时验证原始文本 |
| `scoring-results.json` | 每题评分结果 + 引用率 | 查看哪些题目 P0/P1、引用率排行 |
| `created-issues.json` | 本次 Issue 创建/更新活动 | 核查 Issue 是否实际写入 GitCode/GitHub |
| `assessment-report.json` | 完整评估报告（机器可读） | 自动化分析、与上轮对比 |
| `assessment-report.md` | 完整评估报告（人工可读） | 人工审阅、对外汇报 |
| `issue-map.json` | 跨轮次 Issue 映射 | 查询某问题对应哪个 Issue、是否已闭环 |

### 2.2 run-meta.json — 运行状态快照

```json
{
  "run_date": "2026-05-26",
  "version_label": "V3",
  "community_dir": "output/openEuler/",
  "repo_url": "https://github.com/opensourceways/geo-workflow",
  "dry_run": false,
  "started_at": "2026-05-26T09:00:00Z",
  "completed_at": "2026-05-26T10:15:00Z",
  "status": "success",           ← success | partial_success | failed
  "skipped_platforms": [],       ← 采样失败/跳过的平台列表
  "summary": {
    "questions": 47,
    "platforms": 2,
    "satisfied": 18,
    "not_cited": 23,
    "no_official_content": 6,
    "issues_created": 2,
    "issues_updated": 16,
    "issues_resolved": 3
  }
}
```

**status 含义：**

| status | 含义 | 处理建议 |
|--------|------|---------|
| `success` | 全部步骤正常完成 | 无需处理 |
| `partial_success` | Issue 活动记录与摘要不一致 | 检查 `consistency_warnings`，考虑重跑 `steps=3,4,5` |
| `failed` | 关键步骤未完成 | 查看 `run.log` 或 Claude Code 输出定位原因 |

### 2.3 scoring-results.json — 评分详情

关键字段：

```json
{
  "metadata": {
    "scored_at": "...",
    "total_questions": 47,
    "total_platforms": 2,
    "citation_threshold": 0.75,   ← 75% 为 satisfied 阈值
    "match_mode": "exact_url"
  },
  "results": [
    {
      "question_id": "q_001",
      "status": "not_cited",          ← satisfied | not_cited | no_official_content
      "severity": "P0",               ← OK | P0 | P1
      "citation_rate": 0.5,           ← 0.0 ~ 1.0
      "cited_count": 1,
      "total_platforms": 2,
      "platforms": [
        {"platform": "deepseek-web", "cited": false, "matched_urls": []},
        {"platform": "qwen-web",     "cited": true,  "matched_urls": ["https://..."]}
      ]
    }
  ],
  "summary": {
    "by_severity": {"P0": 23, "P1": 6, "OK": 18}
  }
}
```

---

## 三、GEO 指标解读

### 3.1 三级状态说明

| 状态 | severity | 含义 | 触发条件 |
|------|----------|------|---------|
| `satisfied` | OK | AI 平台已引用官方内容 | citation_rate ≥ 75% |
| `not_cited` | P0 | 官方有内容但 AI 未引用 | citation_rate < 75% 且 official_urls 非空 |
| `no_official_content` | P1 | 官方本身无对应内容 | official_urls 为空 |

**P0 是核心优化目标**：官方内容已存在，但 AI 平台没有索引或引用，可通过结构化标注、TDK 优化、SEO 改进来提升。

**P1 是内容建设目标**：需先创建官方文档/FAQ，才能进行 GEO 优化。

### 3.2 citation_rate 分层解读

| 引用率 | 典型含义 |
|--------|---------|
| 1.0 (100%) | 所有采样平台均引用了官方链接，内容 GEO 表现优异 |
| 0.5 (50%) | 部分平台引用（如 Qwen 引用而 DeepSeek 未引用），存在平台偏好分化 |
| 0.0 (0%) | 所有平台均未引用，内容可发现性问题较严重 |

> **注意**：citation_rate 基于"精确 URL 出现在回答文本或 citations 字段中"判断，不是语义相关性评分。官方 URL 不规范（如动态渲染、带 token 参数）可能导致低估。

### 3.3 跨轮次趋势对比

`assessment-report.md` 中的对比表展示了各题目在不同运行轮次的变化：

```markdown
| ID   | 问题 | Run 1 (04-02) DS | Run 1 (04-02) Qw | Run 2 (05-26) DS | Run 2 (05-26) Qw |
|------|------|:---:|:---:|:---:|:---:|
| q_001 | 如何安装 openEuler？ | ❌ | ❌ | ✅ | ✅ |
| q_002 | ...                | ❌ | ✅ | ❌ | ✅ |
```

**图例：**
- `✅` — 该平台引用了官方链接
- `❌` — 未引用
- `🔘` — 官方无内容（P1）
- `—` — 该轮次未采样此题

**趋势识别：**
- `❌❌ → ✅✅`：GEO 改进生效，两平台均开始引用
- `❌❌ → ✅❌`：单平台改善，存在平台偏好分化，仍需关注
- `✅❌ → ✅❌`：持平，DeepSeek 稳定引用，Qwen 持续未引用，可针对性优化

### 3.4 快速生成汇总统计

```bash
# 查看最新一次运行的评分摘要
COMMUNITY=openEuler
DATE=$(ls output/${COMMUNITY}/ | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort | tail -1)
python3 -c "
import json
data = json.load(open('output/${COMMUNITY}/${DATE}/scoring-results.json'))
s = data['summary']['by_severity']
total = sum(s.values())
print(f'Date: ${DATE}')
print(f'Total: {total}')
print(f'OK  (satisfied):          {s[\"OK\"]:3d} ({s[\"OK\"]/total*100:.0f}%)')
print(f'P0  (not_cited):          {s[\"P0\"]:3d} ({s[\"P0\"]/total*100:.0f}%)')
print(f'P1  (no_official_content):{s[\"P1\"]:3d} ({s[\"P1\"]/total*100:.0f}%)')
"
```

### 3.5 多轮次引用率变化

```bash
# 列出所有轮次的引用率汇总
COMMUNITY=openEuler
for DATE in $(ls output/${COMMUNITY}/ | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort); do
  FILE="output/${COMMUNITY}/${DATE}/scoring-results.json"
  [ -f "$FILE" ] || continue
  python3 -c "
import json
data = json.load(open('${FILE}'))
s = data['summary']['by_severity']
total = sum(s.values())
ok_pct = s['OK']/total*100 if total else 0
print(f'${DATE}: OK={s[\"OK\"]}/{total} ({ok_pct:.0f}%)  P0={s[\"P0\"]}  P1={s[\"P1\"]}')
"
done
```

示例输出：
```
2026-04-02: OK=12/47 (26%)  P0=29  P1=6
2026-04-07: OK=14/47 (30%)  P0=27  P1=6
2026-05-26: OK=18/47 (38%)  P0=23  P1=6
```

---

## 四、Issue 追踪状态

### 4.1 issue-map.json 结构

`issue-map.json` 是跨轮次持久化的 Issue 映射表，记录每个 GEO 问题组对应的 GitHub/GitCode Issue：

```json
{
  "issues": {
    "website_q_001+q_002+q_003": {
      "issue_number": "53",
      "issue_url": "https://gitcode.com/openUBMC/website/issues/53",
      "repo": "openUBMC/website",
      "question_ids": ["q_001", "q_002", "q_003"],
      "title": "[GEO] QEMU仿真开发环境相关内容 AI 可发现性不足",
      "created_at": "2026-05-20"
    }
  }
}
```

### 4.2 created-issues.json — 本次活动记录

每次 issue-creator 运行后写入，记录本次所有 Issue 操作：

```json
{
  "run_date": "2026-05-26",
  "community": "openEuler",
  "activities": [
    {
      "type": "created",              ← created | updated | resolved
      "question_ids": ["q_015"],
      "issue_url": "https://github.com/.../issues/89",
      "issue_number": 89,
      "title": "[GEO] ..."
    },
    {
      "type": "updated",
      "question_ids": ["q_001", "q_002"],
      "issue_url": "https://github.com/.../issues/42",
      "comment_url": "https://github.com/.../issues/42#issuecomment-..."
    }
  ],
  "summary": {
    "created": 2,
    "updated": 16,
    "resolved": 3,
    "errors": []
  }
}
```

### 4.3 查询指定问题的 Issue

```bash
# 查询 q_001 对应的 Issue URL
COMMUNITY=openEuler
python3 -c "
import json
imap = json.load(open('output/${COMMUNITY}/issue-map.json'))
for key, issue in imap['issues'].items():
    if 'q_001' in issue.get('question_ids', []):
        print(f'Issue: {issue[\"issue_url\"]}')
        print(f'Title: {issue[\"title\"]}')
        print(f'Created: {issue[\"created_at\"]}')
"
```

### 4.4 统计 Issue 闭环情况

```bash
# 查看 issue-map 中的总 Issue 数和各题目覆盖情况
COMMUNITY=openEuler
python3 -c "
import json
imap = json.load(open('output/${COMMUNITY}/issue-map.json'))
issues = imap.get('issues', {})
all_qids = set()
for v in issues.values():
    all_qids.update(v.get('question_ids', []))
print(f'Total issues tracked: {len(issues)}')
print(f'Questions with issues: {len(all_qids)}')
"
```

---

## 五、故障排查

### 问题 1：Playwright 启动失败 — 缺少共享库

**错误特征（run.log 中可见）：**
```
playwright._impl._errors.TargetClosedError: BrowserType.launch: Target page, context or browser has been closed
[pid=977298][err] chrome-headless-shell: error while loading shared libraries: libnspr4.so: cannot open shared object file
Script exited 1
```

**原因：** Playwright 的 Chromium 依赖系统共享库（`libnspr4`, `libnss3` 等），在非 Debian 系发行版（如 openEuler）上可能缺失。

**解决：**
```bash
# 方式 1：使用 Playwright 的依赖安装工具（推荐）
playwright install-deps chromium

# 方式 2：手动安装 NSS 相关库（openEuler/RHEL 系）
sudo dnf install -y nss nspr

# 方式 3：验证 Chromium 可用
python3 -c "from playwright.sync_api import sync_playwright; \
  with sync_playwright() as p: \
    b = p.chromium.launch(); b.close(); print('Chromium OK')"
```

---

### 问题 2：平台会话过期 — 登录失败

**错误特征（stderr）：**
```
WARNING: DeepSeek login failed: selector '#email-input' not found after 30s
WARNING: Skipping deepseek-web due to login failure
```

**原因：** Web 平台自动登录使用 Email/Password，平台更新 UI 后选择器失效；或 Cookie 过期。

**解决：**
```bash
# DeepSeek / Qwen：检查 .env 凭证是否正确
grep -E "DEEPSEEK|QWEN" .env

# ChatGPT / Gemini：刷新 session 文件
# 手动登录后重新执行：
/platform-chat community=openEuler platform=chatgpt-web   # 重新注入 session
```

> 至少一个平台可用时，流水线可继续运行；失败平台记录在 `run-meta.json` 的 `skipped_platforms` 字段。

---

### 问题 3：MongoDB 连接失败 — get-question 中止

**错误特征（stderr）：**
```
WARNING: DB connection failed: [Errno 111] Connection refused
WARNING: No DB credentials found, skipping DB path.
ERROR: No forum posts fetched.
```

**排查：**
```bash
# 检查 .env 中 MongoDB 配置
grep MONGODB .env

# 测试 MongoDB 连通性
python3 -c "
import os, pymongo
client = pymongo.MongoClient(
    host=os.environ['MONGODB_HOST'],
    port=int(os.environ['MONGODB_PORT']),
    username=os.environ['MONGODB_USER'],
    password=os.environ['MONGODB_PASSWORD'],
    tls=True, tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=5000
)
client.server_info()
print('MongoDB OK')
"
```

> MongoDB 不可用时，`get-question` 的 forum 路径仅保留 PostgreSQL/Discourse 渠道（Channel 2），若 Channel 2 也不可用则中止。可用 `paths=website` 仅运行官网热词路径。

---

### 问题 4：questions.json 变更被阻断

**错误特征（AGENT.md Step 0 输出）：**
```
ERROR: questions.json has changed since the last run.
Added:   q_048, q_049, q_050
Removed: q_012
To accept these changes and continue, re-run with accept_question_update=true.
```

**原因：** 系统检测到 `questions.json` 与上次运行时的快照不一致，防止无意识的问题集变更影响纵向对比。

**解决：**
```bash
# 确认变更无误后，带参数重新触发
# 在 Claude Code 中：
请按照 AGENT.md 对 openEuler 社区执行一次 GEO 复检 accept_question_update=true
```

---

### 问题 5：评分结果全为 P0，引用率为 0

**现象：** `scoring-results.json` 中所有题目 `citation_rate = 0.0`，即使该社区官方内容已存在。

**排查步骤：**

```bash
# 1. 检查 responses.json 是否有真实内容（非空响应）
python3 -c "
import json
responses = json.load(open('output/openEuler/2026-05-26/responses.json'))
sample = responses['responses'][0] if isinstance(responses, dict) else responses[0]
print('Response length:', len(sample.get('response_text', '')))
print('Citations:', sample.get('citations', []))
"

# 2. 检查 questions.json 中 official_urls 是否已填写
python3 -c "
import json
qs = json.load(open('output/openEuler/questions.json'))
empty = [q['id'] for q in qs['questions'] if not q.get('official_urls')]
print(f'Questions with empty official_urls: {len(empty)}')
if empty[:5]: print('e.g.:', empty[:5])
"

# 3. 手动验证 URL 规范化是否匹配
python3 -c "
import re
def normalize(url):
    url = url.strip().lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    return url.rstrip('/')
official = 'https://www.openeuler.org/zh/migration/'
in_response = 'For migration guides, see openeuler.org/zh/migration which covers...'
norm = normalize(official)
print('Normalized URL:', norm)
print('Found in response:', norm in in_response.lower())
"
```

**常见根因：**

| 根因 | 判断方法 | 解决 |
|------|---------|------|
| `official_urls` 未填写 | 检查 `questions.json` 的 `official_urls` 字段 | 运行 `/prefill-urls` 或手动填写 |
| URL 包含动态参数（如 `?token=...`） | 对比 URL 和回答文本 | 使用稳定的规范化 URL |
| 平台响应为空或超时 | 查看 `responses.json` 中 `response_text` 长度 | 检查平台会话，重新采样 |
| URL 指向已下线页面 | 用浏览器访问确认 | 更新 `official_urls` 为现有 URL |

---

### 问题 6：Issue Token 无权限

**错误特征（stderr）：**
```
ERROR: HTTP 403: {"message":"Resource not accessible by integration"}
HINT: Check that your token has 'issues:write' (GitHub) or 'write_issues' (GitCode) scope.
```

**解决：**
```bash
# GitHub：确认 token 有 issues 写权限
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/{owner}/{repo}/issues \
  -d '{"title":"test","body":"test"}' -s | python3 -m json.tool | grep -E "number|message"

# GitCode：确认 token 有效
curl "https://api.gitcode.com/api/v5/user?access_token=$GITCODE_TOKEN" -s | python3 -m json.tool | grep login
```

> 确认 token 权限后更新 `.env` 中 `GITHUB_TOKEN` 或 `GITCODE_TOKEN`，无需重跑采样和评分，仅重跑 `steps=3,4,5`。

---

### 问题 7：run-meta.json 显示 partial_success

**错误特征：**
```json
{
  "status": "partial_success",
  "consistency_warnings": [
    "run-meta.summary.issues_created=3 but created-issues.json shows 2"
  ]
}
```

**解决：**
```bash
# 重跑 Issue 创建 + 报告步骤
# 在 Claude Code 中：
请按照 AGENT.md 对 openEuler 社区重跑 steps=3,4,5
```

---

## 六、健康检查命令速查

### 6.1 检查最近一次运行状态

```bash
COMMUNITY=openEuler
DATE=$(ls output/${COMMUNITY}/ | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort | tail -1)
echo "Latest run: $DATE"
python3 -c "
import json
meta = json.load(open('output/${COMMUNITY}/${DATE}/run-meta.json'))
print('Status:', meta.get('status'))
print('Completed:', meta.get('completed_at', 'N/A'))
skipped = meta.get('skipped_platforms', [])
if skipped: print('Skipped platforms:', skipped)
s = meta.get('summary', {})
print(f'OK={s.get(\"satisfied\",\"?\")} P0={s.get(\"not_cited\",\"?\")} P1={s.get(\"no_official_content\",\"?\")}')
"
```

### 6.2 检查 questions.json 完整性

```bash
COMMUNITY=openEuler
python3 -c "
import json
qs = json.load(open('output/${COMMUNITY}/questions.json'))
questions = qs.get('questions', [])
total = len(questions)
with_urls = sum(1 for q in questions if q.get('official_urls'))
without_urls = total - with_urls
print(f'Total questions: {total}')
print(f'With official_urls: {with_urls} ({with_urls/total*100:.0f}%)')
print(f'Without official_urls: {without_urls} (P1 candidates)')
"
```

### 6.3 验证 responses.json 格式

```bash
COMMUNITY=openEuler; DATE=2026-05-26
python3 -c "
import json
data = json.load(open('output/${COMMUNITY}/${DATE}/responses.json'))
responses = data if isinstance(data, list) else data.get('responses', [])
platforms = set(r['platform'] for r in responses)
qids = set(r['question_id'] for r in responses)
print(f'Total responses: {len(responses)}')
print(f'Platforms: {sorted(platforms)}')
print(f'Questions covered: {len(qids)}')
empty = [r['question_id'] for r in responses if not r.get('response_text')]
if empty: print(f'WARNING: Empty responses: {empty[:5]}')
"
```

### 6.4 检查 issue-map.json 一致性

```bash
COMMUNITY=openEuler
python3 -c "
import json
imap = json.load(open('output/${COMMUNITY}/issue-map.json'))
issues = imap.get('issues', {})
print(f'Total tracked issues: {len(issues)}')
all_qids = set()
for v in issues.values():
    all_qids.update(v.get('question_ids', []))
print(f'Questions covered: {len(all_qids)}')
# Check for duplicate question_ids across issues
from collections import Counter
qid_counter = Counter()
for v in issues.values():
    for qid in v.get('question_ids', []):
        qid_counter[qid] += 1
dupes = {k: v for k, v in qid_counter.items() if v > 1}
if dupes:
    print(f'WARNING: question_ids in multiple issues: {dupes}')
else:
    print('No duplicate question_ids found')
"
```

### 6.5 批量检查所有社区的最新 OK 率

```bash
for COMMUNITY in $(ls output/); do
  DATE=$(ls output/${COMMUNITY}/ | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort | tail -1)
  FILE="output/${COMMUNITY}/${DATE}/scoring-results.json"
  [ -f "$FILE" ] || { echo "${COMMUNITY}: no scoring data"; continue; }
  python3 -c "
import json
data = json.load(open('${FILE}'))
s = data['summary']['by_severity']
total = sum(s.values())
print(f'${COMMUNITY} (${DATE}): OK={s[\"OK\"]}/{total} ({s[\"OK\"]/total*100:.0f}%)  P0={s[\"P0\"]}  P1={s[\"P1\"]}')
"
done
```

### 6.6 验证 Playwright + 环境健康

```bash
# 检查 Playwright 可用性
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('about:blank')
    browser.close()
print('Playwright OK')
"

# 检查必需环境变量
python3 -c "
import os
required = ['GEO_COMMUNITY', 'GEO_COMMUNITY_DIR', 'GEO_REPO_URL']
optional = ['GITHUB_TOKEN', 'GITCODE_TOKEN', 'DEEPSEEK_WEB_EMAIL', 'QWEN_WEB_EMAIL']
print('Required:')
for k in required:
    v = os.environ.get(k, '')
    print(f'  {k}: {\"OK\" if v else \"MISSING\"}')
print('Optional (for issue creation and sampling):')
for k in optional:
    v = os.environ.get(k, '')
    print(f'  {k}: {\"set\" if v else \"not set\"}')
" # (source .env first if needed: set -a; source .env; set +a)
```

---

## 附录：输出文件 JSON Schema 速查

### responses.json

```json
{
  "responses": [
    {
      "question_id": "q_001",
      "platform": "deepseek-web",
      "response_text": "...",
      "citations": ["https://..."],
      "sampled_at": "2026-05-26T09:10:00Z"
    }
  ]
}
```

### scoring-results.json（results 字段单条）

```json
{
  "question_id": "q_001",
  "question": "...",
  "official_urls": ["https://..."],
  "status": "not_cited",
  "severity": "P0",
  "citation_rate": 0.5,
  "cited_count": 1,
  "total_platforms": 2,
  "platforms": [
    {"platform": "deepseek-web", "cited": false, "matched_urls": [], "match_source": null},
    {"platform": "qwen-web",     "cited": true,  "matched_urls": ["https://..."], "match_source": "response_text"}
  ]
}
```

### issue-map.json（issues 字段单条）

```json
{
  "issue_number": "53",
  "issue_url": "https://gitcode.com/openUBMC/website/issues/53",
  "repo": "openUBMC/website",
  "question_ids": ["q_001", "q_002"],
  "title": "[GEO] ...",
  "created_at": "2026-05-20"
}
```

---

*本文档版本: v1.0 | 更新日期: 2026-05-26*
