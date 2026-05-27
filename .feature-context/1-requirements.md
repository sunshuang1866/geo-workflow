# Feature Requirements
> Status: **Awaiting Review** — reply `/req-approve` to proceed to architecture design.

---

## 业务背景与目标

**问题陈述**: GEO 评估报告无法按应用场景维度对覆盖率进行细分，使运营者无法识别哪些场景的文档引用率不足，内容改进优先级只能粗粒度排序。

**背景**: GEO 系统通过对各 AI 平台进行问题采样和评分，诊断开源社区官方内容的可见性。当前 `get-question` 生成的每个问题仅携带 `doc_form` 字段（T/H/R/E/F 五种文档形态），这是纯文本推断，与社区文档体系本身的应用场景结构完全解耦。不同社区的文档体系差异巨大（openEuler 侧重系统运维，MindSpore 侧重 AI 开发），现有单维度分类方案无法感知这种差异，导致报告缺乏场景层面的聚合分析能力。

**目标**:
- 自动从社区文档目录（`DOCS_INDEX_URL`）提取应用场景分类体系（如安装与升级、内核与驱动、虚拟化等）
- 将问题集中 100% 的问题归入对应场景（`scenario` 字段非空），"通用"场景占比 < 20%
- 在评估报告中新增场景维度聚合分析，按场景展示引用率分布
- 支持社区切换时自动重新识别场景体系，无需修改代码
- 为后续"按场景优先级排序 Issue"提供前置数据基础

**成功指标**:
- 评估报告（`assessment-report.md`）新增场景分组表格，运营者可按场景查看各场景引用率分布
- `questions.json` 所有问题携带非空 `scenario` 字段，"通用"场景占比 < 20%
- 切换社区（如 openEuler → MindSpore）时，仅更新 `DOCS_INDEX_URL` 即可自动识别新的场景体系，无需人工干预
- 运营者能从报告中直接识别高优先级场景缺口（如"容器场景 0% 引用率"）

---

## 用户与使用场景

**用户角色**:

| 角色 | 描述 | 主要场景 |
|------|------|---------|
| 社区运营负责人 | 负责社区内容建设与 GEO 优化工作，向管理层汇报引用覆盖率指标 | 每周查看 assessment-report.md，按应用场景引用率排序，识别"容器场景 0%"为优先方向，指派内容团队改进 |
| 技术文档团队 | 接收并执行 GEO 改进 Issue 的技术写作者和开发者 | 从 Issue 标题快速定位属于"虚拟化"场景，找到相关文档目录，针对性优化内容 |
| 跨社区运维工程师 | 部署和维护 GEO 评估流水线，需在多个社区间切换 | 设置 `DOCS_INDEX_URL` 后系统自动识别 MindSpore 的"模型训练/推理部署/分布式"场景，无需手动指定场景列表 |
| Claude Code Agent | 执行 GEO 评估流水线的自动化工作流引擎 | 在 get-question 完成后自动抓取文档目录、LLM 推导场景列表、为每个问题标注 `scenario` 字段 |

**使用场景**:

1. 运营者查看 assessment-report.md 中按应用场景分组的表格，发现"容器"场景 P0 占比最高（60%），在对应 Issue 中添加场景标签，推动内容团队集中改进该场景文档。
2. 内容贡献者收到 Issue "[GEO P0] 虚拟化引用率 25%"，直接从 questions.md 的"场景"列看出属于"虚拟化"场景，打开对应文档目录进行改进。
3. 部署人员将 `DOCS_INDEX_URL` 从 openEuler 切换至 MindSpore，系统自动识别"模型训练/推理部署/分布式/工具链"等新场景，无需修改代码或场景配置。
4. 运营负责人在周报中按场景汇报：某场景引用率从 25% 升至 40%，网络场景下降至 30% 需重点关注。
5. issue-creator 创建新 Issue 时，自动在标题中包含场景标签（如"[Scenario: 容器]"），便于内容团队快速筛选认领。
6. 运营者使用 `scope=scenario:容器` 参数仅重采样和重评分容器相关问题，加速该场景的迭代验证。

---

## 功能需求

1. The system shall accept a `DOCS_INDEX_URL` environment variable pointing to a community documentation directory (sitemap/index page) and fetch+parse its structure to identify application scenarios.
2. The system shall analyze the fetched documentation directory via LLM to extract an application scenario taxonomy (e.g., "安装与升级"、"内核与驱动"、"虚拟化"、"容器"), including per-scenario documentation coverage description.
3. The system shall classify each question in `questions.json` into exactly one scenario by LLM analysis, using the extracted docs taxonomy as classification context.
4. The system shall write a non-empty `scenario` field to every question in `questions.json`; questions not matching any identified scenario shall default to "通用" (general).
5. The system shall ensure the "通用" scenario represents < 20% of classified questions, logging a warning when this threshold is exceeded.
6. The system shall regenerate `questions.md` to display the `scenario` field and show questions grouped by scenario with a citation rate summary per scenario.
7. The system shall modify `assessment-report` generation to include a scenario-grouped summary table showing per-scenario citation rates as a new top-level section.
8. The system shall support community switching (changing only `DOCS_INDEX_URL`) such that the scenario taxonomy is re-derived automatically without code changes.
9. The system shall support incremental re-classification: new questions appended in a subsequent get-question run shall be classified using the existing scenario taxonomy without re-classifying already-classified questions.
10. The system shall provide `dry_run` mode: when `dry_run=true`, classification logic runs but no `questions.json` writes are performed.

---

## 验收标准

- [ ] Given a `questions.json` from `get-question` with 40+ questions and no `scenario` field, When scenario classification runs with a valid `DOCS_INDEX_URL`, Then all questions have a non-empty `scenario` field and < 20% are labeled "通用".
- [ ] Given a documentation directory with 5+ distinct application areas, When the docs analyzer extracts the taxonomy, Then at least 80% of questions are classified into non-generic scenarios whose labels correspond to the identified docs structure.
- [ ] Given an `assessment-report` with 50 questions across 2 platforms, When report generation reads `scenario` field from `questions.json`, Then the markdown report includes a new section showing a scenario-grouped summary table with per-scenario citation rates (e.g., "安装: 3/5 (60%)").
- [ ] Given two communities (openEuler and MindSpore) with different docs structures, When scenario classification runs on each with only `DOCS_INDEX_URL` changing, Then each community gets its own scenario taxonomy without code modification or manual label mapping.
- [ ] Given an unreachable `DOCS_INDEX_URL`, When classification runs, Then the system exits with `ERROR: ...` to stderr and exit code 1 (no partial writes).
- [ ] Given an existing `questions.json` with some questions already having `scenario` set, When classification re-runs with new questions appended, Then only the new questions (missing `scenario`) are classified; existing assignments remain unchanged.

---

## 范围外

- **文档内容修改**: 本特性仅对问题集进行场景分类，不修改或重构社区官方文档内容本身。
- **实时文档抓取（网络爬虫）**: 系统假定 `DOCS_INDEX_URL` 指向结构化目录页（HTML 目录树或 sitemap），不支持深度递归爬取整个文档站。
- **多场景归属**: 每个问题映射到唯一主场景，不支持跨多个场景的多标签分配。
- **`doc_form` 与 `scenario` 交叉分析**: 本期仅增加 `scenario` 维度分组，`doc_form` 与 `scenario` 的交叉分析（如"安装场景中的 Tutorial 文档引用率"）延迟到后续版本。
- **场景分类的人工大规模改写**: 系统提供 LLM 自动分类；允许单条手动覆盖，但不提供批量重分类 UI 或工具。
- **`responses.json` 和 `scoring-results.json` 的 schema 变更**: `scenario` 字段仅存在于 `questions.json`，评分结果通过 join 问题 ID 获取场景信息，不修改评分数据结构。

---

## 边界情况

- **文档目录结构扁平**: 若 `DOCS_INDEX_URL` 对应的目录只有 < 3 个明确场景，系统应仍提取现有场景，并允许高比例"通用"分类，在输出中明确记录。
- **DOCS_INDEX_URL 不可达或格式异常**: 返回 HTTP 错误或无法解析的 HTML/JSON 时，系统应以 `ERROR:` 前缀输出错误并 `sys.exit(1)`，不写入部分结果。
- **问题描述不匹配任何文档场景**: 来自论坛/Issue 的问题可能描述的用户行为在官方文档中没有对应场景——应归入"通用"，并单独记录供运营者审查。
- **场景名称歧义**: 若文档目录中存在语义重叠的场景（如"问题排查"和"调试"），LLM 分类可能在两者间不稳定——系统应在分类置信度 < 0.7 时记录 WARNING 并标记供人工复查。
- **增量追加问题后的场景一致性**: 后续 `get-question` 追加的新问题需用现有场景体系进行分类，而非重新推导场景分类体系（避免场景名称不一致）。
- **超大问题集（1000+ 条）**: LLM 批量分类可能因 token 超限而失败——系统应支持分批处理（`BATCH_SIZE` 参数，默认 80 条），并记录每批的处理状态。

---

## 开放问题

- [ ] `DOCS_INDEX_URL` 的预期格式是什么？是 JSON manifest、sitemap.xml、HTML 目录树还是自定义 API？不同社区文档站点的目录呈现差异较大，需要明确解析策略或是否引入多格式适配。
- [ ] 场景分类结果是否允许人工覆盖？若运营者认为某问题被错误分类，修改流程是什么——直接编辑 `questions.json` 还是提供专用命令？
- [ ] "通用"（general）场景在下游如何处理？在 assessment-report 的场景分组表中是否单独显示为一行，还是从场景维度的聚合中过滤掉？
- [ ] 场景体系是否需要跨运行周期持久化？若文档目录在两次运行之间结构发生变化，场景分类应如何处理——全量重分类还是保留旧分类体系？
- [ ] 新特性应作为 `get-question` 技能内的新步骤，还是独立的新技能（如 `classify-scenarios`）？考虑到后续可能需要单独重新分类（不重新抓取问题），独立技能可能更灵活。

---

## 技术背景（供架构设计参考）

**相关文件**:
- `.env.example` — 新增 `DOCS_INDEX_URL` 环境变量
- `.claude/skills/get-question/SKILL.md` — 新增场景分类步骤（Step 3a 或 Step 9）
- `.claude/skills/get-question/scripts/validate-questions.py` — 扩展 validator 支持可选 `scenario` 字段
- `.claude/skills/get-question/assets/prompt-templates.md` — 新增场景推导与分类的 LLM prompt 模板
- `.claude/skills/assessment-report/SKILL.md` — 新增场景分组维度的报告生成步骤
- `.claude/skills/assessment-report/scripts/build-report.py` — 在 per-question 记录中携带 `scenario` 字段并计算场景级指标
- `.claude/skills/assessment-report/scripts/generate-report.py` — 在 Markdown 报告中新增场景分组汇总表
- `tests/fixtures.py` — `GeoTestData.make_question()` 增加 `scenario` 参数
- `tests/test_validate_questions.py` — 新增 `scenario` 字段的可选验证测试
- `AGENT.md` — 文档新步骤的触发条件和执行位置
- `.context/snapshot.md` — 更新 §3 数据 Schema（`questions.json` 新增 `scenario` 字段）

**现有约束与规范**:
- 所有脚本 stdout 只输出 JSON，进度/警告/错误走 stderr（`ERROR:`/`WARNING:` 前缀）
- 可选字段遵循 `make_question()` 中 `doc_form` 参数的条件包含模式
- 环境变量用 `GEO_*` 前缀（如 `WEBSITE_SEARCH_URL`），新变量应为 `DOCS_INDEX_URL`
- 函数 ≤ 30 行，用 `pathlib.Path` 操作文件，`os.environ.get()` 读取环境变量
- 代码格式：Black（行宽 100）+ Flake8（max-line-length 100）
- 技能幂等性：重新运行不创建重复记录；支持 `dry_run=true`
- LLM 调用模式参考 `prefill-urls` 技能的 HTTP 验证和批处理方式

**测试文件**:
- `tests/test_validate_questions.py` — 扩展测试 `scenario` 字段的可选验证
- `tests/fixtures.py` — `make_question()` 增加 `scenario` 参数
- `tests/test_clean_code.py` — 已覆盖 stdout/stderr 协议，新脚本自动适用
- 新脚本（如 `classify-scenarios.py`）的单元测试：覆盖 HTTP 错误处理、场景推导、批量分类、增量重分类逻辑

**建议方向**: 将场景分类作为 `get-question` 技能内的新步骤（Step 9：场景分类）更简洁；但若预期后续需要"仅重新分类、不重新抓取问题"的独立操作，作为独立技能（`classify-scenarios`）更灵活。核心争议点在于场景分类的触发频率：若每次 get-question 后必然分类，合并到 get-question 即可；若需要独立重新分类（如社区切换场景体系时），独立技能更合适。
