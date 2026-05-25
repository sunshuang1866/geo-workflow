# GEO Search Assessment — 系统设计文档

> 版本：2026-05-25
> 目标：自动评估开源社区在主流 AI 搜索平台中的内容可见性，生成可追踪的改进 Issue。

---

## 一、系统概览

**核心流程**（5 步）：

```
问题集生成与分类       内容审计与链接预填         AI 平台采样
(get-question)   →   (prefill-urls)       →   (platform-chat)
                                                     ↓
                              Issue 生成         GEO 评估与打分
                           (issue-creator)  ←  (scoring-engine)
```

**数据流**：每步输出 JSON 文件，作为下一步输入。Markdown 文件供人工阅读。

**终点**：以 Issue 发布作为本 workflow 的输出终点。后续配套 workflow（内容改进 → PR）与本 workflow 形成对抗机制（见第八节）。

---

## 二、文档内容分类标准（doc_form 框架）

问题集分类的核心维度是"这个问题需要什么类型的答案"，而非问题所属的业务领域。这决定了官网应该在哪个路径下有什么内容。

### 2.0 框架选型依据

#### 2.0.1 候选标准综述

我们调研了以下 4 个主流文档分类标准或实践规范：

---

**① Diátaxis**（https://diataxis.fr/，Daniele Procida，2017–2021）

Diátaxis 是目前最具理论完备性的文档分类框架。其核心是一个二维坐标系：

- **横轴：习得（Acquisition）↔ 应用（Application）** — 用户是第一次接触正在学，还是已有基础正在用？
- **纵轴：实践（Practical）↔ 理论（Theoretical）** — 内容关注的是"做"还是"理解"？

两轴交叉产生 4 种内容类型：

| | 习得（Acquisition）| 应用（Application）|
|---|---|---|
| **实践（Practical）** | **Tutorial** — 带领学习者完成一件事，结果优先 | **How-to Guide** — 帮助有经验的用户解决特定问题 |
| **理论（Theoretical）** | **Explanation** — 提供背景知识，帮助理解"为什么" | **Reference** — 提供查阅性技术信息，不加解释 |

Diátaxis 的关键主张：**每种类型服务于不同的读者心理状态；将多种类型混入同一页面是文档质量差的根本原因**，而非内容量不足。

局限：Diátaxis 没有定义 Troubleshooting 类型，而这是社区问题中占比最高的内容形式之一。

---

**② DITA（Darwin Information Typing Architecture）**（OASIS 标准 DITA 1.3，2015）

DITA 是 IBM 于 1990 年代后期发明、2004 年开源的 XML 结构化文档标准，现为 OASIS 国际标准。它定义了以下 Topic 类型：

| 类型 | 官方定义摘要 |
|---|---|
| **Concept** | 提供用户在操作产品前必须了解的背景信息，回答"是什么" |
| **Task** | 回答"如何做"，采用严格的有序步骤结构，以完成目标为导向 |
| **Reference** | 提供支持用户执行任务的查阅性数据，如 API、参数、表格 |
| **Troubleshooting**（DITA 1.2 新增）| 描述用户可能遇到的条件（症状），并提供恢复建议（诊断+解法）|

DITA 的贡献是工业级的落地完备性，尤其是 Troubleshooting 类型的标准化定义（症状→原因→解法三段式）在 Diátaxis 中完全缺失。局限是 DITA 整体偏重 XML 结构实施，不提供"如何分类一个问题"的判断规则。

---

**③ Microsoft Learn 内容类型规范**（https://learn.microsoft.com/en-us/contribute/content/）

微软针对 Azure/M365 文档总结的工程化实践，非正式标准，但在大型技术文档中广泛参考。定义了 6 种内容类型：

| 类型 | 微软定义摘要 |
|---|---|
| **Quickstart** | 帮助用户第一次使用产品，10 分钟内可完成；最小可运行示例 |
| **Tutorial** | 引导用户综合使用多个功能完成真实场景任务 |
| **How-to Guide** | 帮助用户完成特定操作任务，假设用户有一定基础 |
| **Concept** | 解释背景信息、底层机制或功能工作原理 |
| **Reference** | 提供 API、命令、属性等技术细节 |
| **Resources** | FAQ、故障排查、示例代码（无统一结构要求）|

微软相比 Diátaxis 增加了 **Quickstart**（Tutorial 的简化子类，面向极短时间内的首次体验）和将 FAQ/故障排查纳入 **Resources** 大类。局限是把 Explanation 和 Concept 混用，且将 Troubleshooting 降格为无结构要求的 Resources 子项，削弱了其分类价值。

---

**④ Google Developer Documentation Style Guide**（https://developers.google.com/style）

谷歌为开发者文档制定的写作规范，未提供严格的分类框架，仅描述三类文档方向：
- **Conceptual documentation**：概念性内容，含 Overview、Background
- **Procedural documentation**：操作性内容，How-to 与 Tutorial 不作严格区分，统称 Guides
- **Reference documentation**：API/CLI 参考

谷歌的方案将 Explanation 和 How-to 合并为 Guides，**丢失了 Diátaxis 最重要的一个区分**（理解型 vs 操作型），分类粒度不足以指导 GEO 诊断。

---

#### 2.0.2 对比分析

| 维度 | Diátaxis | DITA | Microsoft Learn | Google |
|---|---|---|---|---|
| 类型数量 | 4 | 4（含 Troubleshooting）| 6 | 3（粗粒度）|
| 是否有判断规则 | ✅ 两轴坐标系，可推导 | ❌ 只给名称定义 | ❌ 只给名称定义 | ❌ |
| Troubleshooting 独立定义 | ❌ 缺失 | ✅ 标准化三段式 | △ 归入 Resources | ❌ |
| 区分 Tutorial vs How-to | ✅ 清晰 | △ Task 混合两者 | ✅ 额外增加 Quickstart | ❌ 合并为 Guides |
| 区分 Explanation vs How-to | ✅ 核心区分 | ✅（Concept vs Task）| ✅ | ❌ 混合 |
| 适用于问题分类推断 | ✅ | ❌ 需要对照文档逐条判断 | ❌ | ❌ |
| schema.org 对应关系 | 可推导 | 有 XML 类型但无 schema.org | 无 | 无 |

#### 2.0.3 选型结论

**我们采用 Diátaxis 4 象限 + DITA Troubleshooting 类型，共 5 种。**

- **选 Diátaxis 而非 DITA**：Diátaxis 提供两轴判断规则，面对模糊问题时有标准可推导；DITA 只给类型名称，无法指导 LLM 或人工做分类判断。
- **选 Diátaxis 而非 Microsoft Learn**：微软的 Quickstart 本质是 Tutorial 的简化子类，对 GEO 分类粒度意义有限；微软把 Troubleshooting 降级为无结构 Resources，削弱了其诊断价值。
- **选 Diátaxis 而非 Google**：谷歌合并了 Explanation 和 How-to，损失了 GEO 中最关键的区分——这两种内容对应完全不同的官网路径和失效诊断路径。
- **从 DITA 单独借用 Troubleshooting**：它是唯一在 Diátaxis 中缺失、但在社区问题中占比极高（故障类通常占 30–50%）的类型，且 DITA 给出了标准的三段式结构定义，直接对应 `FAQPage` schema.org 标注。

#### 2.0.4 核心洞察：不同类型的 AI 引用特征

不同 doc_form 被 AI 引用的难度和失效原因存在系统性差异：

| doc_form | AI 引用倾向 | 主要失效原因 |
|---|---|---|
| F（排障/FAQ）| 最高潜力：Q&A 结构天然匹配 AI 回答格式 | 中文开源项目**几乎普遍缺失**独立 FAQ 页；无 `FAQPage` schema |
| H（操作指引）| 较高：AI 偏好有步骤的操作性内容 | 步骤混在长文中、缺 `HowTo` schema、H1 无动词关键词 |
| R（参考文档）| 精准但依赖爬取：被引用时准确率高 | JS 动态渲染导致爬虫无法抓取；API 文档常见此问题 |
| T（教程）| 中等：整篇难以提取单一答案 | 页面过长，AI 无法定位关键段落；细拆为多个 H 页面后引用率提升 |
| E（概念解释）| 最低：AI 倾向于改写而非引用解释性内容 | 概念分散在博客/长文中，缺独立页面；H1 非问题句式 |

**关键推论**：开源社区 GEO 改进的最高性价比通常在 F 类——成本是新建一个 FAQ 页面，收益是覆盖所有与故障/疑问相关的问题查询。

#### 2.0.5 中文开源文档的典型缺陷分布

基于对多个开源社区问题集的观察，中文开源项目文档缺陷呈现规律性分布：

- **T 类**：通常有但过于冗长（Getting Started 和完整教程混为一页），缺少 5 分钟可运行的最小示例
- **H 类**：覆盖率参差，进阶操作（高级配置、集成部署）最容易缺失
- **R 类**：存在但爬取不可达（JS 渲染、登录墙、无 sitemap）
- **E 类**：内容散落在博客和发布公告中，没有稳定 URL 的独立概念页
- **F 类**：**几乎全部缺失**，相关内容分散在 issue 评论、论坛帖子中，无结构化页面

这个分布直接指导了 `no_official_content` 状态下的内容创建优先级：**F > H（进阶）> E（独立页）> T（精简）**。

### 2.1 五种内容形式定义

| 代码 | 名称 | 回答什么问题 | 判断依据 | 期望 URL 路径模式 | schema.org 类型 |
|---|---|---|---|---|---|
| `T` | Tutorial（教程） | 如何从零完整地做一件事？ | 面向新手，结束后能独立交付成果 | `/tutorials/`、`/getting-started/` | `HowTo` |
| `H` | How-to（操作指引） | 如何完成某个具体任务？ | 读者有基础，针对特定问题，有步骤 | `/docs/how-to/`、`/guides/` | `HowTo` |
| `R` | Reference（参考文档） | 某个参数/API/配置项的具体值？ | 读者知道要查什么，只需查阅 | `/reference/`、`/api/` | `TechArticle` |
| `E` | Explanation（概念解释） | 原理/架构/设计决策是什么？ | 读者想理解，不要求立刻操作 | `/concepts/`、`/architecture/` | `Article` |
| `F` | Troubleshooting/FAQ（排障） | 遇到问题 X 怎么解决？ | 读者有症状，需要诊断路径或快速答案 | `/troubleshooting/`、`/faq/` | `FAQPage` |

### 2.2 分类判断规则（嵌入 LLM Prompt）

```
- T：以"如何开始/入门/从零"开头，面向新手，完成后有完整可交付产出
- H：以"如何/怎么/步骤是什么"开头，假设有一定基础，解决一个具体任务
- R：涉及具体参数/API/配置项的值、语法或用法
- E：以"是什么/为什么/原理/架构/区别"开头，理解型，不要求操作
- F：涉及错误/故障/失败/报错/"为什么不"/"解决方案"
```

### 2.3 doc_form 与 GEO 失效诊断的关系

当 scoring-engine 输出 `not_cited` 时，按 doc_form 走不同诊断路径：

| doc_form | 首先检查 | 然后检查 |
|---|---|---|
| T / H | H1/H2 标题是否含任务动词 + 关键词 | 是否用 `HowTo` schema 标注步骤 |
| R | 页面是否服务端渲染（非 JS 动态加载） | 是否在 sitemap.xml 中 |
| E | 页面是否过长（>5000 字）需要拆分 | H1 是否是问题句式 |
| F | 是否有 `FAQPage` schema.org 标注 | 问题文本是否涵盖中英文两个版本 |

> **注**：由于采用的 AI 平台均开启了网页搜索，训练数据截止日期对引用结果影响较小。`not_cited` 的失效原因主要集中在内容结构（schema.org）和爬取可见性（robots.txt / sitemap / SSR）两个方向。

---

## 三、Step 1：问题集生成（get-question）

### 3.1 热门问题抓取

数据来源为社区热词数据库（hotopic DB），双渠道策略：

| 渠道 | 数据来源 | 筛选标准 |
|---|---|---|
| MongoDB | 社区热门话题 DB（聚合 forum/issues/maillist） | consult-filter：至少 1 条咨询类来源（Req/Task/RFC/Doc 全为排除类时丢弃）|
| PostgreSQL / Discourse | 官方论坛帖子 | views > 50，取 top 30 |

热度评价指标：`consult_count`（咨询数量）为主排序字段，意图分类内降序排列。

### 3.2 问题改写与分类

LLM 将原始标题/帖子改写为自然语言问题后，**同步推断 `doc_form`**：

- 改写阶段：将社区讨论标题转化为用户视角的搜索问题（例："MindSpore 安装失败" → "如何在 Ubuntu 22.04 上安装 MindSpore？"）
- 分类阶段：按 2.2 节规则推断 `doc_form`，写入 questions.json

### 3.3 去重与输出

- 新生成问题与现有 questions.json 语义去重
- 输出：`questions.json`（机器读）+ `questions.md`（人工读）
- 本次新增问题追加至现有文件末尾，不覆盖已有问题

---

## 四、Step 2：内容审计与链接预填（prefill-urls 重设计）

这是对现有 prefill-urls skill 的重大扩展。原来只做"推断官方链接"，现在增加"判断内容是否存在"和"路径是否合适"两层判断。

### 4.1 三层判断逻辑

对 questions.json 中每条问题，AI 执行以下判断：

**第一层：官网是否有相关内容？**
- 有 → 进入第二层
- 没有 → `official_urls: []`，`note: "没有链接"`

**第二层：现有内容的 URL 路径是否符合 doc_form 对应的期望路径模式？**（见 2.1 节"期望 URL 路径模式"列）
- 符合 → 填入 `official_urls`，`note: ""`（无备注）
- 不符合 → 填入当前最佳可用 URL，`note: "有链接但位置不合适：[当前路径] → 建议路径 [期望路径]"`

**第三层：HTTP 验证**
- 对候选 URL 发起 HEAD 请求验证可访问性
- 不可访问的 URL 不写入 `official_urls`，改为写入 `note` 备注

### 4.2 判断示例

| 场景 | doc_form | official_urls | note |
|---|---|---|---|
| 官网无相关页面 | H | `[]` | `"没有链接"` |
| 内容在博客而非 How-to 区 | H | `["https://…/blog/install-docker"]` | `"有链接但位置不合适：当前在 /blog/，期望在 /docs/how-to/"` |
| 内容存在且路径正确 | H | `["https://…/docs/how-to/container/docker"]` | `""` |
| URL 存在但 HTTP 404 | E | `[]` | `"链接无法访问：https://…/concepts/arch（404），需新建或修复"` |

### 4.3 人工校核

AI 填写完成后，需人工对每条 `note` 非空的问题进行校核：
- 确认"没有链接"判断是否准确（官网可能有内容但 AI 未找到）
- 确认"位置不合适"的建议是否合理
- 人工补充或修正 `official_urls`

校核完成后，questions.json 成为 scoring-engine 的输入基准。

---

## 五、Step 3：AI 平台采样（platform-chat）

### 5.1 覆盖平台

本 workflow 覆盖 6 个主流 AI 平台：

| 平台 | 接入方式 | 网页搜索 |
|---|---|---|
| DeepSeek | Web UI（自动登录）| 开启 |
| Qwen（通义千问）| Web UI（自动登录）| 开启 |
| Kimi | Web UI（自动登录）| 开启 |
| ChatGPT | Web UI（session token 注入）| 开启 |
| Gemini | Web UI（匿名，无需登录）| 开启 |
| 豆包（Doubao）| Web UI（自动登录）| 开启 |

> 所有平台均需开启联网搜索功能，确保返回结果包含实时网页引用。

### 5.2 采样流程

1. 读取 questions.json，逐条将 `question` 文本输入 AI 平台
2. 等待响应完成，提取：回答正文（`response_text`）+ 引用链接列表（`citations`）
3. 输出 `responses.json`，格式：每条记录包含 `question_id`、`platform`、`response_text`、`citations`

---

## 六、Step 4：GEO 评估与打分（scoring-engine）

### 6.1 评分逻辑

以问题为单位，逐平台判断"是否引用了官方内容"：

```
对每个 (question_id, platform) 组合：
  citations 中是否有 URL 与 official_urls 匹配？
    - 精确匹配（URL 完全相同）→ cited = true
    - 域名匹配（URL 属于 official_domains）→ cited = true
    - 否则 → cited = false
```

### 6.2 问题级状态

| 状态 | 条件 |
|---|---|
| `satisfied` | 至少 1 个平台引用了官方内容（`cited_count ≥ 1`）|
| `not_cited` | 有 `official_urls` 但所有平台均未引用 |
| `no_official_content` | `official_urls` 为空（官网无内容）|

### 6.3 输出

`scoring-results.json`，每条记录包含：

```json
{
  "question_id": "q_001",
  "question": "如何在 openEuler 上安装 Docker？",
  "doc_form": "H",
  "official_urls": ["https://…"],
  "note": "",
  "status": "not_cited",
  "citation_rate": 0.0,
  "platform_results": {
    "deepseek": { "cited": false, "matched_urls": [] },
    "qwen":     { "cited": false, "matched_urls": [] },
    "kimi":     { "cited": false, "matched_urls": [] },
    "chatgpt":  { "cited": false, "matched_urls": [] },
    "gemini":   { "cited": true,  "matched_urls": ["https://…"] },
    "doubao":   { "cited": false, "matched_urls": [] }
  }
}
```

---

## 七、Step 5：Issue 生成（issue-creator）

### 7.1 核心原则：每问题一个 Issue

与旧设计（LLM 分组 → 每组一个 Issue）不同，新设计为**每个问题独立创建一个 Issue**，便于：
- 追踪单个问题的改进状态（不做跨 Issue 交叉引用）
- 精确关联 PR 与改进效果
- 触发新一轮 GEO 检测时以问题为粒度对比前后变化
- 支持后续看板可视化：每个 Issue 对应一张卡片，状态（open/closed/labeled）直接反映该问题的 GEO 改进进度

### 7.2 Issue 格式规范

**标题格式**：

```
【GEO】[{id}][{doc_form_label} · {status_label}] {question}
```

其中：

| 字段 | 取值映射 |
|---|---|
| `doc_form_label` | 教程(T) / 操作指引(H) / 参考文档(R) / 概念解释(E) / 排障FAQ(F) |
| `status_label` | 内容未被引用(not_cited) / 内容缺失(no_official_content) |

**示例**：

```
【GEO】[q_001][操作指引 · 内容未被引用] 如何在 openEuler 上安装 Docker？
【GEO】[q_002][概念解释 · 内容缺失] openEuler 的内存管理机制与 CentOS 有何不同？
```

> 标题在看板中直接呈现分类和问题现状，无需打开 Issue 正文即可判断优先处理方向。`satisfied` 状态的 Issue 标题补充 `[已解决]` 前缀，不含 status_label。

**正文结构**：

```markdown
## 问题信息

- **问题 ID**：q_001
- **问题**：如何在 openEuler 上安装 Docker？
- **文档类型**：How-to（H）— 期望位置：`/docs/how-to/container/docker/`
- **当前官方链接**：https://…（或"暂无官方链接"）
- **人工校核备注**：有链接但位置不合适：当前在 /blog/，建议移至 /docs/how-to/

## AI 平台引用现状

| 平台 | 是否引用官方内容 | 引用链接 |
|---|---|---|
| DeepSeek | ❌ 未引用 | — |
| Qwen | ❌ 未引用 | — |
| Kimi | ❌ 未引用 | — |
| ChatGPT | ❌ 未引用 | — |
| Gemini | ✅ 已引用 | https://… |
| 豆包 | ❌ 未引用 | — |

引用率：1/6（16.7%）

## 原因分析

**状态**：`not_cited` — 官网有内容，但 5 个平台未引用

**诊断**（基于文档类型 H）：
- 当前内容发布在 /blog/ 路径下，不符合 How-to 页面的期望路径 `/docs/how-to/`
- 页面可能缺少 `HowTo` schema.org 结构化数据标注
- 建议检查：H1/H2 标题是否含任务动词 + 关键词

## 改进建议

1. **内容搬迁**：将现有博客文章迁移至 `/docs/how-to/container/docker/`，并设置原路径 301 重定向
2. **结构化数据**：为页面添加 `HowTo` schema.org 标注（每个步骤用 `HowToStep` 标注）
3. **内容格式规范**：检查页面是否符合《GEO 内容设计规范》（规范制定中，待补充）
4. **Sitemap 更新**：确认新 URL 已加入 sitemap.xml

> 如该问题为"没有链接"（官网无内容），则改进建议为：按 How-to 模板新建页面，置于 `/docs/how-to/` 路径下。
```

### 7.3 Issue 状态流转

| scoring 状态 | Issue 动作 | 备注 |
|---|---|---|
| `not_cited` | 新建 / 更新评论 | 官网有内容，但 AI 未引用 |
| `no_official_content` | 新建 / 更新评论 | 官网无内容 |
| `satisfied` | 添加解决评论 + 标题加 `[已解决]` 前缀 | 所有平台均已引用 |

Issue 通过 `question_id` 唯一匹配（存储在 issue-map.json 中），避免重复创建。

### 7.4 内容格式规范（待补充）

改进建议中涉及"内容格式是否规范"的判断，依赖一套《GEO 内容设计规范》，该规范将在后续讨论中制定，内容将涵盖：

- 各 doc_form 类型的页面结构要求
- schema.org 标注规范
- 标题/关键词写法规范
- 中英文双版本要求

制定完成后，issue-creator 可以按规范逐项 checklist 生成具体改进建议，而非泛化描述。

---

## 八、双 Workflow 对抗机制

### 8.1 本 Workflow（GEO 检测）

```
输入：社区热门问题
流程：get-question → prefill-urls → platform-chat → scoring-engine → issue-creator
输出：GitHub Issues（含【GEO】标记）
终点：Issue 发布完成
```

### 8.2 配套 Workflow（内容改进，责任人：龚壮邦）

```
输入：【GEO】Issues
流程：分析改进建议 → 修改官网内容 → 提交 PR
输出：Merged PR（官网内容更新）
```

### 8.3 触发机制

```
PR 合入 → 触发新一轮 GEO 检测 → 对比前后 scoring-results.json → 量化改进效果
```

具体对比维度：
- 问题级：该问题的 `citation_rate` 变化（before/after）
- 平台级：哪些平台开始引用了官方内容
- 整体：`not_cited` / `no_official_content` / `satisfied` 数量变化

### 8.4 对抗价值

两个 workflow 形成闭环的内容质量改进体系：
- **GEO 检测 workflow** 持续发现问题，确保改进动作有依据
- **内容改进 workflow** 根据问题逐步修复，每次改动效果可量化
- PR 合入作为触发条件，确保"改了才测"，避免无效重复检测

---

## 九、数据格式规范

### 9.1 questions.json（核心数据文件）

```json
{
  "community": "openEuler",
  "official_domains": ["openeuler.org", "docs.openeuler.org"],
  "questions": [
    {
      "id": "q_001",
      "question": "如何在 openEuler 22.03 上安装并配置 Docker？",
      "doc_form": "H",
      "official_urls": [
        "https://docs.openeuler.org/zh/docs/22.03_LTS/docs/Container/container.html"
      ],
      "note": "有链接但位置不合适：当前在容器概览页 /Container/overview，期望在独立 How-to 页 /how-to/container/docker/"
    },
    {
      "id": "q_002",
      "question": "openEuler 的内存管理机制与 CentOS 有何不同？",
      "doc_form": "E",
      "official_urls": [],
      "note": "没有链接"
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 全局唯一，格式 `q_NNN`，社区内递增 |
| `question` | string | 中文自然语言问题，用户视角 |
| `doc_form` | string | `T`/`H`/`R`/`E`/`F`，由 get-question LLM 推断，人工可修正 |
| `official_urls` | array | prefill-urls 填入，HTTP 验证通过的官方页面链接 |
| `note` | string | prefill-urls AI 诊断备注，人工校核后可修改 |

### 9.2 文件流转关系

```
questions.json
    ↓ (get-question 生成 + doc_form 分类)
    ↓ (prefill-urls 填入 official_urls + note)
    ↓ (人工校核 official_urls / note)
    ↓ (scoring-engine 读取 official_urls 做 URL 匹配)
    ↓ (issue-creator 读取 doc_form + note 生成 Issue 内容)
scoring-results.json
    ↓ (assessment-report 读取，生成对比报告)
    ↓ (PR 合入后，作为下一轮对比基准)
```

---

## 十、待讨论 / 待建设项

| 项目 | 状态 | 说明 |
|---|---|---|
| GEO 内容设计规范 | 待讨论 | 各 doc_form 类型的页面结构标准，schema.org 标注规范 |
| 问题看板 | 待建设 | 可视化每个 question_id 对应 Issue 的改进状态，以 GitHub Projects 或外部看板实现 |
| 配套内容改进 Workflow | 待建设 | 读取【GEO】Issues，自动生成改进 PR |
| 6 平台 platform-chat 扩展 | 待实现 | 在现有 deepseek/qwen 基础上补充 kimi/chatgpt/gemini/doubao |
| doc_form 字段迁移 | 待实现 | 7 个社区共 522 条问题补充 doc_form；同步统一 note 字段命名（部分社区为 notes）|
| prefill-urls 重设计实现 | 待实现 | 三层判断逻辑 + 路径规范性校验 |
