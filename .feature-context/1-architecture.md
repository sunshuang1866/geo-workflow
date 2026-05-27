# Feature Architecture
> Status: **Awaiting Review** — reply `/arch-approve` to proceed to implementation.

---

## 实现方案

实现一个独立技能 `classify-scenarios`，定位于 AGENT.md 流水线中 `get-question` 之后、`prefill-urls` 之前。技能从 `DOCS_INDEX_URL` 抓取社区文档目录（支持 HTML/sitemap/JSON 多格式自适应），通过 LLM 推导应用场景分类体系（5–8 个场景标签），再按 BATCH_SIZE=80 批量为 `questions.json` 中尚未分类的问题写入 `scenario` 字段；同时将场景分类体系版本化存入 `questions.json` 根节点（`scenario_taxonomy` 字段），避免跨运行场景名称漂移。`assessment-report` 技能在现有状态分组之上新增独立的"按场景汇总"章节，不修改现有分组结构。全流程支持 `dry_run` 和增量重分类。

---

## 文件变更计划

### 修改

| 文件 | 变更内容 |
|------|---------|
| `.claude/skills/assessment-report/scripts/build-report.py` | 在每条 per-question 记录中透传 `scenario` 字段（从 questions.json join）；若问题缺少 scenario 字段则填入 `"通用"` |
| `.claude/skills/assessment-report/scripts/generate-report.py` | 新增 `_build_scenario_summary()` 函数（≤30行），从 records 列表聚合每个 scenario 的 question count / P0 count / avg citation_rate；在 Markdown 输出末尾追加 `## 按应用场景分组` 表格（列：场景、问题数、P0、平均引用率），不改动现有状态分组章节 |
| `.claude/skills/assessment-report/SKILL.md` | Step 5（Markdown 输出）新增子步骤说明：读取 scenario 字段，渲染场景汇总表格 |
| `.claude/skills/get-question/scripts/validate-questions.py` | 新增可选校验：当问题携带 `scenario` 字段时，校验其非空且为字符串；如 `通用` 占比 > 20% 则打印 `WARNING: 通用场景占比 X%，建议检查场景分类质量`（不 exit 1） |
| `tests/fixtures.py` | `GeoTestData.make_question()` 增加可选 `scenario` 参数，默认 `None`（不写入）；与现有 `doc_form` 参数同等处理方式 |
| `tests/test_validate_questions.py` | 新增测试：含 `scenario` 字段的问题通过校验；`scenario` 为空字符串时触发 WARNING |
| `AGENT.md` | 在 Step 1（get-question）之后、Step 2（prefill-urls）之前插入 classify-scenarios 调用说明；新增 `steps` 参数值 `classify` 支持单独运行 |
| `.env.example` | 新增 `DOCS_INDEX_URL=` 注释说明（社区文档目录 URL，HTML 目录树/sitemap.xml/JSON 均支持） |
| `.context/snapshot.md` | §3 数据 Schema 新增 questions.json 的 `scenario` 字段和根节点 `scenario_taxonomy` 字段描述（由 context-refresh 工作流自动重生成，此处标记为待刷新） |

### 新建

| 文件 | 用途 |
|------|------|
| `.claude/skills/classify-scenarios/SKILL.md` | 技能规格：6 步流程，I/O 参数表（community, docs_index_url, batch_size, dry_run），Prerequisites，示例调用 |
| `.claude/skills/classify-scenarios/scripts/fetch-docs-index.py` | 从 `DOCS_INDEX_URL` 下载并解析文档目录；自动检测格式（sitemap.xml → XML 解析，JSON → 直接解析，HTML → BeautifulSoup 提取 `<a>` 标签）；输出 JSON 数组 `[{url, title, category}]`；HTTP 错误 → `ERROR:` + exit 1 |
| `.claude/skills/classify-scenarios/scripts/extract-taxonomy.py` | 从文档目录列表（stdin JSON）调用 LLM 提取场景分类体系；prompt 从 `references/prompt-templates.md` 读取；验证结果包含 5–8 个场景标签；输出 `[{key, label}]`；按场景名去重 |
| `.claude/skills/classify-scenarios/scripts/classify-questions.py` | 主编排脚本：加载 questions.json → 筛选 `scenario` 缺失问题 → 按 BATCH_SIZE=80 分批 → 调用 LLM（携带场景分类体系上下文）→ 验证 `通用` 占比 → 若 `dry_run=false` 写回 questions.json（含 `scenario_taxonomy` 根字段） |
| `.claude/skills/classify-scenarios/references/prompt-templates.md` | 两段 Prompt 模板：(A) `TAXONOMY_EXTRACTION` — 从文档目录推导场景分类体系；(B) `QUESTION_CLASSIFICATION` — 给定分类体系对问题批量分类，返回 `{question_id: scenario_key}` JSON |
| `tests/test_classify_scenarios.py` | 单元测试：(1) DOCS_INDEX_URL 不可达 → exit 1；(2) sitemap/HTML/JSON 各格式解析；(3) 增量分类（已有 scenario 的问题跳过）；(4) 通用占比 >20% 触发 WARNING；(5) dry_run 不写文件；(6) 完整流程集成测试（含 fixture） |

---

## ADR 决策记录

1. **ADR-F1-001: classify-scenarios 作为独立技能，而非 get-question Step 9**
   — 要求 #8（社区切换）和要求 #9（增量重分类）均需要能在不重新抓取问题的情况下单独触发场景分类。将其嵌入 get-question 会耦合数据获取与分类两个关注点，且无法独立重跑。`prefill-urls` 技能已证明该独立后处理模式有效：读 questions.json → LLM 批量处理 → 写回。classify-scenarios 完全复用此模式。

2. **ADR-F1-002: 场景分类体系版本化存入 questions.json 根节点（`scenario_taxonomy` 字段）**
   — LLM 非确定性风险：同一 DOCS_INDEX_URL 的两次场景提取可能产生语义相同但文本不同的标签（如"虚拟化"vs"KVM虚拟化"）。将分类体系作为结构化字段（含 `version`、`extracted_at`、`categories`）持久化到 questions.json，后续增量分类直接读取已有体系而非重新推导，确保场景名称一致性。若体系需更新，操作员显式传入 `force_reclassify=true` 全量重分类。

3. **ADR-F1-003: 执行顺序 — get-question → classify-scenarios → prefill-urls**
   — classify-scenarios 需要问题文本做分类，但不需要 `official_urls`（URL 信息对场景判断帮助有限）；prefill-urls 则需要问题文本和社区名称。先分类场景再填 URL，两步相互独立，失败可独立重跑。若颠倒顺序（先 prefill-urls），场景分类已可运行，但 official_urls 为空时分类结果无差异。确定先分类。

4. **ADR-F1-004: assessment-report 仅追加场景汇总表格，不修改现有分组结构**
   — 现有报告按状态（no_official_content / not_cited / satisfied）分组，内含按 action_type 的子分组。若将场景维度与状态维度交叉（3 status × 8 scenario = 24 子组），报告将急剧膨胀且难以阅读。选择"追加独立章节"而非"交叉分组"：在 Markdown 末尾新增 `## 按应用场景分组` 汇总表（场景 × 聚合指标），现有章节结构零变更，报告向后兼容。

5. **ADR-F1-005: DOCS_INDEX_URL 格式自适应（sitemap.xml / JSON / HTML），不引入额外配置**
   — 要求 #8 强调"仅更新 DOCS_INDEX_URL 即可"。若需额外 `DOCS_INDEX_TYPE` 变量，操作员需同步维护两个变量，增加切换成本。`fetch-docs-index.py` 通过 Content-Type header 和 URL 后缀自动判断格式：`.xml` → XML 解析，Content-Type `application/json` → JSON 解析，否则 → HTML/BeautifulSoup 解析。实现 ≤60 行，无额外配置。

6. **ADR-F1-006: `通用` 占比超阈值仅记 WARNING，不 exit 1**
   — 若文档目录结构扁平（<3 个明确场景），强制 exit 1 会完全阻断流水线，而非降级运行。设计为：当 `通用` > 20% 时打印 `WARNING: 通用场景占比 X%`，继续写入结果，并在报告中单独记录"建议运营者审查以下问题"列表。操作员可决定是否重新调整 DOCS_INDEX_URL 或接受较高通用占比。

---

## 风险处置

- **LLM 场景名称漂移**：通过 `scenario_taxonomy` 字段持久化已推导的分类体系，增量分类始终使用已有体系（不重新推导）。仅当 `force_reclassify=true` 时才重新推导分类体系并全量重分类，此时 `scenario_taxonomy.version` 递增，操作员可追溯变更历史。

- **下游 schema 兼容性（validate-inputs.py、score-urls.py、build-report.py）**：`scenario` 是可选字段（非必需），所有现有脚本均读取已知字段、忽略未知字段，无 JSON Schema 强验证，不会 break。build-report.py 变更仅新增一行 `record["scenario"] = q.get("scenario", "通用")`，无风险。validate-questions.py 的校验变更为 WARNING 而非 ERROR，不影响 exit code。

- **questions.md 渲染结构冲突**：现有 questions.md 按 intent 类别分组（认知/选型等）。新增 `scenario` 字段作为独立列（在已有列之后）渲染，不改变分组逻辑，保持向后兼容。不引入"按场景重组 questions.md"的全量重构。

- **DOCS_INDEX_URL 不可达**：`fetch-docs-index.py` 在 HTTP 错误（非 200）或超时时打印 `ERROR: 无法访问 DOCS_INDEX_URL: <url>` 并 exit 1；`classify-questions.py` 捕获此 exit code，不写入 questions.json 的部分结果，确保原子性。

- **增量分类幂等性**：classify-questions.py 仅处理 `scenario is None` 或 `scenario == ""` 的问题；已有 scenario 值的问题跳过（不覆盖）。若批处理中途失败，已写入的记录保留；重跑时未分类问题重新处理，已分类问题跳过。满足幂等性要求。

- **测试覆盖率 70%**：新增约 250–350 LOC（3 个脚本 + 测试文件）；`test_classify_scenarios.py` 目标覆盖率 ≥80%（6 个测试用例覆盖主路径、错误路径、边界条件）；generate-report.py 新增函数 `_build_scenario_summary()` 单独可测，不影响现有测试。整体覆盖率维持 ≥70%。

- **场景分类置信度 <0.7 的标记**：LLM 输出结构化 JSON `{question_id: scenario_key}`，无内置置信度。替代方案：若 LLM 返回 `通用` 且该批次通用比例 >50%，classify-questions.py 打印 `WARNING: 本批次通用占比异常高 (X%)，建议检查分类体系或问题描述`，并在 questions.json 中对该批问题标注 `_scenario_review: true` 供操作员复查。

---

## 被排除的方案

- **方案 A — 将场景分类作为 get-question 的 Step 9**：违反关注点分离原则，将数据获取（论坛/数据库）与文档分类耦合到同一技能。要求 #8（社区切换时独立重分类）和要求 #9（增量追加后仅分类新问题）均需要在不重跑 get-question 的情况下触发分类。Step 9 方案无法满足这一操作需求，且使 get-question 测试更难隔离。排除。

- **方案 C — 惰性分类（仅在 assessment-report 生成时计算场景，不写回 questions.json）**：直接违反功能需求 #4（"所有问题携带非空 `scenario` 字段"）和要求 #6（"将 `scenario` 字段写入 questions.json"）。report 生成时的场景是临时计算结果，无法持久化、无法被 issue-creator 读取、无法供操作员手动纠错。该方案使 questions.json 不再是单一事实来源，引入数据一致性风险。排除。

- **方案 D — 在 scoring-engine 或 assessment-report 中扩展场景支持（不新建技能）**：会将场景信息放到评分之后，使早期步骤（platform-chat、issue-creator）无法按场景筛选（要求 #9 使用场景过滤重采样）。排除。

---

## 测试策略

1. **验收标准 AC1**：给定 40+ 条无 `scenario` 字段的 questions.json，运行 `classify-scenarios` 后，断言所有问题 scenario 非空且 `通用` 比例 < 20%。使用真实（或 stub）LLM 回调的 mock。

2. **验收标准 AC2**：给定包含 5+ 明确应用场景的文档目录（HTML fixture 或 JSON fixture），断言 `extract-taxonomy.py` 提取的场景列表 ≥ 5 个，且 ≥80% 的问题被分配到非通用场景。使用 `tests/fixtures/` 目录下的静态 HTML fixture。

3. **验收标准 AC3**：运行 `generate-report.py` 后，断言生成的 assessment-report.md 包含 `## 按应用场景分组` 章节，章节中至少包含 2 行场景数据（场景名 + 引用率）。

4. **验收标准 AC4**：用两个不同的文档目录 fixture（openEuler HTML + MindSpore JSON）分别运行 `extract-taxonomy.py`，断言两次提取的场景标签不同，且均不需要代码修改。

5. **验收标准 AC5**：mock `DOCS_INDEX_URL` 为返回 HTTP 404 的本地服务，断言 `fetch-docs-index.py` 输出 `ERROR:` 前缀到 stderr 并以 exit code 1 退出，questions.json 未被修改。

6. **验收标准 AC6**：构造含部分问题已有 `scenario` 字段的 questions.json fixture，运行 classify-questions.py，断言已有 scenario 的问题未被覆盖，仅新增问题被分类。验证幂等性（连续运行两次，结果相同）。

7. **dry_run 模式**：`dry_run=true` 时运行全流程，断言 questions.json 文件内容不变（使用 file hash 比较）。

8. **通用占比告警**：构造全部问题返回 `通用` 的 LLM mock，断言 stderr 包含 `WARNING: 通用场景占比`，exit code 仍为 0，questions.json 正常写入。

9. **`make_question(scenario=...)` fixture 测试**：在 test_validate_questions.py 中断言携带 `scenario` 字段的问题通过验证；`scenario=""` 触发 WARNING；其他现有测试不受影响（`scenario=None` 时不写入字段）。
