# GEO 搜索能力诊断系统 — 数据模型文档

**版本**：v1.0
**日期**：2026-04-12
**状态**：已批准

---

## 目录

1. [概述](#1-概述)
2. [questions.json](#2-questionsjson)
3. [responses.json](#3-responsesjson)
4. [scoring-results.json](#4-scoring-resultsjson)
5. [issue-map.json](#5-issue-mapjson)
6. [created-issues.json](#6-created-issuesjson)
7. [run-meta.json](#7-run-metajson)
8. [文件依赖关系](#8-文件依赖关系)
9. [字段演变记录](#9-字段演变记录)

---

## 1. 概述

### 1.1 文件清单

| 文件 | 位置 | 生命周期 | 维护方式 |
|------|------|---------|---------|
| `questions.json` | `{community_dir}/` | 持久（跨运行） | **符号链接**（指向 `question.json` 或 `questions-new.json`） |
| `questions-new.json` | `{community_dir}/` | 持久（跨运行） | 半自动（脚本创建，人工维护 `official_urls`） |
| `responses.json` | `{community_dir}/{date}/` | 按运行日期隔离 | 全自动 |
| `scoring-results.json` | `{community_dir}/{date}/` | 按运行日期隔离 | 全自动 |
| `issue-map.json` | `{community_dir}/` | 持久（累积追加） | 全自动 |
| `created-issues.json` | `{community_dir}/{date}/` | 按运行日期隔离 | 全自动 |
| `run-meta.json` | `{community_dir}/{date}/` | 按运行日期隔离 | 全自动 |
| **新增汇总目录** ||||
| `summary/response.json` | `{community_dir}/summary/` | 持久（跨运行） | 全自动（汇总历史响应数据） |
| `summary/scoring-results.json` | `{community_dir}/summary/` | 持久（跨运行） | 全自动（汇总历史评分结果） |
| `summary/scoring-report.md` | `{community_dir}/summary/` | 持久（跨运行） | 全自动（汇总评估报告） |
| **新增历史问题目录** ||||
| `previous-question/scoring-results.json` | `{community_dir}/previous-question/` | 持久（跨运行） | 全自动（历史问题评分） |
| `previous-question/scoring-report.md` | `{community_dir}/previous-question/` | 持久（跨运行） | 全自动（历史问题报告） |

**注意**：`questions.json` 现在是一个符号链接，指向当前使用的问题集文件（通常是 `question.json` 或 `questions-new.json`）。新问题追加时先写入 `questions-new.json`，待人工标注 `official_urls` 后，符号链接指向该文件。

### 1.2 命名约定

| 规则 | 示例 |
|------|------|
| 问题 ID | `q_001`（三位数字，下划线分隔） |
| 数组字段命名 | 复数形式（`questions`, `responses`, `results`） |
| 时间戳格式 | ISO 8601（`2026-03-31T10:00:00Z`） |
| 日期目录 | `YYYY-MM-DD`（`2026-03-31`） |
| 平台标识符 | 小写（`chatgpt`, `deepseek`, `doubao`, `qwen`, `gemini`） |
| 严重级别 | 大写（`P0`, `P1`, `OK`） |
| **新增命名约定** ||
| 汇总目录 | `summary/`（固定名称，用于汇总历史数据） |
| 历史问题目录 | `previous-question/`（固定名称，用于历史问题评分） |
| 新问题集 | `questions-new.json` / `questions-new.md`（固定名称） |
| 问题集符号链接 | `questions.json -> question.json` 或 `questions-new.json` |
| 响应文件命名差异 | `response.json`（单数，部分运行）或 `responses.json`（复数，标准命名） |

---

## 2. questions.json 与 questions-new.json

**路径**：`output/{community}/questions.json`（符号链接） → `question.json` 或 `questions-new.json`

**用途**：问题集的唯一真实来源（source of truth），包含每个问题的定义、官方 URL 标注、以及自动生成的衍生数据。

### 2.0 符号链接机制

从 2026-05 起，`questions.json` 改为**符号链接**，指向当前使用的问题集文件：

```bash
questions.json -> question.json  # 或 questions-new.json
```

**设计目的**：
- **新旧问题分离**：新问题追加到 `questions-new.json`，待人工标注后启用
- **版本切换**：通过修改符号链接，快速切换使用的问题集版本
- **回滚便利**：问题集出错时，符号链接指向旧版本即可回滚

**生命周期**：
```
/questions-new.json (新追加，待标注)
    ↓ 人工标注 official_urls 完成
/questions.json -> questions-new.json (符号链接指向新版本)
    ↓ 下次追加新问题
/questions-new.json (新追加，待标注)
```

---

### 2.1 questions-new.json 结构

### 2.2 顶层结构

```json
{
  "community": "MindSpore",
  "generated_at": "2026-03-10T08:00:00Z",
  "last_updated": "2026-03-30T15:00:00Z",
  "official_domains": ["mindspore.cn", "mindspore.com.cn"],
  "total": 42,
  "questions": [ ... ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `community` | string | ✅ | 社区名称，与 `GEO_COMMUNITY` 对应 |
| `generated_at` | string (ISO 8601) | ✅ | 首次生成时间 |
| `last_updated` | string (ISO 8601) | ✅ | 最近更新时间 |
| `official_domains` | string[] | ✅ | 官方域名列表，供评分时域名级模糊匹配使用 |
| `total` | integer | ✅ | 问题总数 |
| `questions` | Question[] | ✅ | 问题列表 |

### 2.3 Question 对象

```json
{
  "id": "q_001",
  "question": "MindSpore 支持哪些安装方式？",
  "source": "forum",
  "source_url": "https://discuss.mindspore.cn/t/topic/12345",
  "category": "installation",
  "official_urls": [
    "https://www.mindspore.cn/install",
    "https://www.mindspore.cn/install#pip"
  ],
  "notes": "安装指南页面完整覆盖，含 pip/conda/Docker 三种方式"
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一问题 ID，格式为 `q_NNN` |
| `question` | string | ✅ | 自然语言问题文本（中文） |
| `source` | enum | ✅ | 来源：`forum` / `issue` / `maillist` / `website` / `manual` |
| `source_url` | string | ❌ | 原始来源 URL（论坛帖子、Issue 链接等） |
| `category` | string | ❌ | 问题分类标签（如 `installation`, `api-usage`, `performance`） |
| `official_urls` | string[] | ✅ | 官方权威 URL 列表（**人工填写**）；空数组表示官方无对应内容 |
| `notes` | string | ❌ | 人工备注（标注说明、已知问题等） |

**重要约束**：
- `official_urls` 为空数组（`[]`）时，该问题在评分中始终判为 `no_official_content`（P1）
- `id` 一旦分配不得修改；问题删除后该 ID 不可复用
- `official_urls` 中的 URL 必须为完整 URL（含 scheme），不允许使用相对路径

### 2.3 手动维护指南

运营者需要在 `/get-question` 生成后、运行 scoring-engine 前，为每个问题填写 `official_urls`：

```json
// 示例：有官方内容
"official_urls": ["https://www.mindspore.cn/install"]

// 示例：无官方内容（官方需要新建页面）
"official_urls": []

// 示例：多个相关 URL
"official_urls": [
  "https://www.mindspore.cn/docs/zh-CN/r2.4/api_python/nn/mindspore.nn.Adam.html",
  "https://www.mindspore.cn/tutorials/zh-CN/r2.4/training/optimizer.html"
]
```

---

## 3. responses.json

**路径**：`output/{community}/{date}/responses.json`

**用途**：记录各 AI 平台对每个问题的原始回答及后处理提取的结构化元数据。

### 3.1 顶层结构

```json
{
  "community": "MindSpore",
  "run_date": "2026-03-31",
  "platforms": ["chatgpt", "deepseek", "doubao", "qwen", "gemini"],
  "total_responses": 200,
  "responses": [ ... ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `community` | string | ✅ | 社区名称 |
| `run_date` | string (YYYY-MM-DD) | ✅ | 运行日期 |
| `platforms` | string[] | ✅ | 本次采样的平台列表 |
| `total_responses` | integer | ✅ | 响应总条数（含失败） |
| `responses` | Response[] | ✅ | 响应记录列表 |

### 3.2 Response 对象

```json
{
  "question_id": "q_001",
  "platform": "deepseek",
  "model": "deepseek-chat",
  "sampled_at": "2026-03-31T10:05:23Z",
  "status": "success",
  "response_text": "MindSpore 支持以下几种安装方式：\n1. pip 安装...",
  "citations": [
    "https://www.mindspore.cn/install",
    "https://github.com/mindspore-ai/mindspore"
  ],
  "mentions_community": true,
  "community_description": "华为开源的深度学习框架",
  "competitors_mentioned": ["PyTorch", "TensorFlow"],
  "recommendation_position": "primary",
  "citations_to_official": [
    "https://www.mindspore.cn/install"
  ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `question_id` | string | ✅ | 对应问题 ID |
| `platform` | string | ✅ | 平台标识符（小写） |
| `model` | string | ✅ | 实际使用的模型 ID |
| `sampled_at` | string (ISO 8601) | ✅ | 采样时间 |
| `status` | enum | ✅ | `success` / `error` / `empty` |
| `response_text` | string | ❌ | 平台返回的完整回答文本（`status=success` 时必须有） |
| `citations` | string[] | ✅ | 平台在回答中给出的所有 URL（AI 显式引用的链接） |
| `mentions_community` | boolean | ❌ | LLM 后处理：回答是否提及目标社区 |
| `community_description` | string | ❌ | LLM 后处理：回答中对社区的描述文字 |
| `competitors_mentioned` | string[] | ❌ | LLM 后处理：提及的竞品名称 |
| `recommendation_position` | enum | ❌ | LLM 后处理：`primary`（首选推荐）/ `secondary`（次选）/ `not_recommended` / `not_mentioned` |
| `citations_to_official` | string[] | ❌ | LLM 后处理：`citations` 中属于官方域名的子集 |

**约束**：
- 每个 `(question_id, platform)` 对在文件中唯一
- `status=error` 时 `response_text` 可为 `null`，`citations` 为空数组
- `citations` 只包含 AI 回答中显式出现的 URL，不包含推断的来源

---

## 4. scoring-results.json

**路径**：`output/{community}/{date}/scoring-results.json`

**用途**：每个问题的评分结果、平台覆盖详情、关联 GEO 改进建议。

### 4.1 顶层结构

```json
{
  "community": "MindSpore",
  "scored_at": "2026-03-31T10:12:00Z",
  "total_platforms": 4,
  "summary": {
    "total_questions": 40,
    "by_status": {
      "satisfied": 5,
      "not_cited": 30,
      "no_official_content": 5
    },
    "by_severity": {
      "OK": 5,
      "P0": 30,
      "P1": 5
    },
    "citation_rate_distribution": {
      "0.0": 28,
      "0.25": 8,
      "0.5": 4,
      "0.75": 3,
      "1.0": 2
    }
  },
  "results": [ ... ]
}
```

### 4.2 ScoringResult 对象

```json
{
  "question_id": "q_001",
  "question": "MindSpore 支持哪些安装方式？",
  "status": "not_cited",
  "severity": "P0",
  "citation_rate": 0.25,
  "official_urls": ["https://www.mindspore.cn/install"],
  "platform_results": [
    {
      "platform": "chatgpt",
      "cited": false,
      "matched_urls": [],
      "indicator": "❌"
    },
    {
      "platform": "deepseek",
      "cited": true,
      "matched_urls": ["https://www.mindspore.cn/install"],
      "indicator": "✅"
    },
    {
      "platform": "doubao",
      "cited": false,
      "matched_urls": [],
      "indicator": "❌"
    },
    {
      "platform": "qwen",
      "cited": false,
      "matched_urls": [],
      "indicator": "❌"
    }
  ],
  "suggestions": [
    {
      "id": "CTX-02",
      "title": "直接回答优先",
      "description": "...",
      "priority": "P0"
    }
  ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `question_id` | string | ✅ | 问题 ID |
| `question` | string | ✅ | 问题文本快照 |
| `status` | enum | ✅ | `satisfied` / `not_cited` / `no_official_content` |
| `severity` | enum | ✅ | `OK` / `P0` / `P1` |
| `citation_rate` | float | ✅ | 引用该问题的平台比例（0.0–1.0） |
| `official_urls` | string[] | ✅ | 来自 questions.json 的官方 URL |
| `platform_results` | PlatformResult[] | ✅ | 各平台的详细结果 |
| `suggestions` | Suggestion[] | ✅ | 匹配的 GEO 改进建议（来自 72 条目录） |

**status 判定规则（v1.1，2026-05 更新）**：

| 条件 | status | severity |
|------|--------|---------|
| `official_urls` 非空 且 `cited_count >= 1`（至少一个平台引用） | `satisfied` | `OK` |
| `official_urls` 非空 且 `cited_count == 0`（无平台引用） | `not_cited` | `P0` |
| `official_urls` 为空 | `no_official_content` | `P1` |

**历史判定规则（v1.0，2026-04）**：
- 旧阈值：`citation_rate >= 0.75`（75% 阈值）
- 已废弃，仅保留在历史评分报告中作为参考

### 4.3 PlatformResult 对象

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `platform` | string | ✅ | 平台标识符 |
| `cited` | boolean | ✅ | 是否引用了至少一个 official_url |
| `matched_urls` | string[] | ✅ | 命中的 official_url 列表 |
| `indicator` | string | ✅ | `✅` / `❌` / `—`（无官方内容时） |

---

## 5. issue-map.json

**路径**：`output/{community}/issue-map.json`

**用途**：记录 suggestion 组 → GitHub/GitCode Issue 的映射，用于跨运行去重（防止重复创建同一问题的 Issue）。

### 5.1 结构

```json
[
  {
    "group_id": "g_001",
    "question_ids": ["q_001", "q_002", "q_005"],
    "title": "安装文档在 AI 平台中引用率低",
    "issue_number": 15,
    "issue_url": "https://github.com/opensourceways/geo-workflow/issues/15",
    "platform": "github",
    "status": "open",
    "citation_rate": 0.2,
    "severity": "P0",
    "created_at": "2026-03-31",
    "last_updated_at": "2026-04-07",
    "iteration_count": 2
  }
]
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `group_id` | string | ✅ | Issue 组唯一 ID，格式 `g_NNN` |
| `question_ids` | string[] | ✅ | 该组包含的问题 ID 列表 |
| `title` | string | ✅ | Issue 标题 |
| `issue_number` | integer | ✅ | GitHub/GitCode Issue 编号 |
| `issue_url` | string | ✅ | Issue 完整 URL |
| `platform` | enum | ✅ | `github` / `gitcode` |
| `status` | enum | ✅ | `open` / `closed` |
| `citation_rate` | float | ✅ | 最近一次评分的组平均引用率 |
| `severity` | string | ✅ | 最近一次评分的严重级别 |
| `created_at` | string (YYYY-MM-DD) | ✅ | Issue 创建日期 |
| `last_updated_at` | string (YYYY-MM-DD) | ✅ | 最近评论/更新日期 |
| `iteration_count` | integer | ✅ | 评估迭代次数（含创建） |

**匹配规则**：新问题组与已有 issue-map 记录的 `question_ids` 重叠 ≥ 50% 时，视为同一组，追加评论而非创建新 Issue。

---

## 6. created-issues.json

**路径**：`output/{community}/{date}/created-issues.json`

**用途**：记录本次运行中 issue-creator 执行的所有 Issue 操作（创建/更新/关闭建议）的活动日志。

### 6.1 结构

```json
{
  "run_date": "2026-04-07",
  "community": "MindSpore",
  "dry_run": false,
  "summary": {
    "created": 3,
    "updated": 8,
    "resolved": 1
  },
  "activities": [
    {
      "action": "create",
      "group_id": "g_014",
      "question_ids": ["q_038", "q_039"],
      "issue_number": 28,
      "issue_url": "https://github.com/opensourceways/geo-workflow/issues/28",
      "title": "SIG 贡献流程文档 AI 覆盖率低"
    },
    {
      "action": "update",
      "group_id": "g_001",
      "question_ids": ["q_001", "q_002"],
      "issue_number": 15,
      "issue_url": "https://github.com/opensourceways/geo-workflow/issues/15",
      "comment_id": 98765432,
      "comment_summary": "引用率从 0.2 升至 0.4（DeepSeek 新增引用），建议继续优化"
    },
    {
      "action": "resolve",
      "group_id": "g_007",
      "question_ids": ["q_020"],
      "issue_number": 22,
      "issue_url": "https://github.com/opensourceways/geo-workflow/issues/22",
      "comment_summary": "引用率已达 0.8（≥ 75%），建议关闭 Issue"
    }
  ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `action` | enum | ✅ | `create` / `update` / `resolve` |
| `group_id` | string | ✅ | 对应的 issue-map 组 ID |
| `question_ids` | string[] | ✅ | 涉及的问题 ID |
| `issue_number` | integer | ✅ | Issue 编号 |
| `issue_url` | string | ✅ | Issue URL |
| `comment_id` | integer | ❌ | 追加评论的 ID（仅 update/resolve） |
| `comment_summary` | string | ❌ | 评论摘要（仅 update/resolve） |

---

## 7. run-meta.json

**路径**：`output/{community}/{date}/run-meta.json`

**用途**：记录单次运行的配置参数、执行状态和统计摘要。

### 7.1 结构

```json
{
  "run_date": "2026-04-07",
  "version_label": "V3",
  "community": "MindSpore",
  "community_dir": "output/MindSpore/",
  "repo_url": "https://github.com/opensourceways/geo-workflow",
  "dry_run": false,
  "started_at": "2026-04-07T09:00:00Z",
  "completed_at": "2026-04-07T09:18:32Z",
  "status": "success",
  "skipped_platforms": [
    {
      "platform": "doubao",
      "reason": "API error 429: rate limit exceeded"
    }
  ],
  "consistency_warnings": [],
  "summary": {
    "questions": 42,
    "platforms": 4,
    "satisfied": 6,
    "not_cited": 31,
    "no_official_content": 5,
    "issues_created": 2,
    "issues_updated": 9,
    "issues_resolved": 1
  }
}
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `run_date` | string (YYYY-MM-DD) | ✅ | 运行日期 |
| `version_label` | string | ✅ | 版本标签（自动递增，格式 `V{n}`） |
| `status` | enum | ✅ | `success` / `partial_success` / `failed` |
| `skipped_platforms` | object[] | ✅ | 跳过的平台及原因（空数组表示全平台成功） |
| `consistency_warnings` | string[] | ✅ | issue activity 一致性警告列表 |
| `summary` | object | ✅ | 核心统计数字 |

---

## 8. 文件依赖关系

```
questions.json (人工维护)
    │
    ├──▶ platform-sampler ──▶ responses.json
    │         │
    │         ▼
    └──▶ scoring-engine ◀── responses.json
              │
              ▼
        scoring-results.json
              │
    ┌─────────▼────────────┐
    │    issue-creator      │◀── issue-map.json (读)
    └─────────┬────────────┘
              │
    ┌─────────▼──────────────────────────────────┐
    │  issue-map.json (写) + created-issues.json  │
    └─────────┬──────────────────────────────────┘
              │
    ┌─────────▼────────────────────────────────────────────┐
    │          assessment-report                            │◀── questions.json
    │                                                       │◀── scoring-results.json
    └─────────┬─────────────────────────────────────────────┘◀── issue-map.json
              │
    assessment-report.json + assessment-report.md
```

---

## 9. 字段演变记录

| 日期 | 变更 | 影响文件 |
|------|------|---------|
| 2026-03-30 | `content-labels.json` 合并入 `questions.json`（`official_urls` 字段） | questions.json |
| 2026-03-30 | `approved-questions.json` 废弃，`questions.json` 直接作为 source of truth | questions.json |
| 2026-03-30 | scoring-results.json 从 A-E 现象码改为 `satisfied`/`not_cited`/`no_official_content` | scoring-results.json |
| 2026-03-30 | 移除 `suggestions.md` 输出，scoring-engine 只输出 JSON | scoring-results.json |
| 2026-03-28 | issue-map.json match key 从（question_ids + status）改为仅 question_ids | issue-map.json |
| 2026-03-28 | `created-issues.json` 新增 `action=resolve` 类型 | created-issues.json |
