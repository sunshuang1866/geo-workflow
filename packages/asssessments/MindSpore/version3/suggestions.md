# GEO 评分报告 — MindSpore (version3)

> 生成时间: 2026-03-25T00:00:00Z
> 标准答案: 无（跳过 Layer 2+ 事实覆盖分析）
> 官方域名: mindspore.cn, gitcode.com/mindspore, github.com/mindspore-ai, gitee.com/mindspore
> 备注: **单平台评估（仅 Qwen）**，跨平台对比分析不可用。建议补充 ChatGPT/DeepSeek/豆包 后重新评分。

---

## 一、概览

| 指标 | 数值 |
|------|------|
| 评估问题数 | 47 |
| 评估平台数 | 1（qwen） |
| Layer 2 评估对数 | 40/47（7 题官网无内容，跳过 Layer 2） |
| 平均引用比例（Layer 2） | 65.0% |
| Qwen 平均得分 | 5.8/10 |
| 内容源问题 | 3 类（单平台推断，需多平台验证） |

---

## 二、核心发现

1. **Qwen 存在严重幻觉模式**：17 个 C 类问题（占 Layer 2 的 42.5%），集中在三类触发词——模型转换 API（`export_from_torch`/`export_from_onnx` 不存在）、SIG 例会详情（滥用 issues/6789 捏造会议时间）、邮件列表平台（OpenI 与 mailweb.mindspore.cn 混淆）。

2. **官方文档结构空缺是幻觉的根本原因**：SIG 注册表、邮件列表订阅入口、模型转换工具边界说明均缺乏专项文档，迫使 AI 平台填补内容真空。

3. **安装/API 类问题表现最好**：12 个 D 类无需行动（含安装、数据集、TSC/SIG 治理文档），说明结构化官方文档覆盖好的问题 AI 能准确引用。

---

## 三、现象分布

| 现象 | 数量 | 占比 | 说明 |
|------|------|------|------|
| A — 官网无内容 | 7 | 14.9% | 内容缺口（竞品对比/选型类问题） |
| B — 有内容未引用 | 0 | 0% | — |
| C — 引用错误/幻觉 | 17 | 36.2% | 紧急纠错，API/事件/平台混淆 |
| D — 引用比例大 | 15 | 31.9% | 健康，其中 3 个有轻微问题（P2） |
| E — 引用比例小 | 8 | 17.0% | 内容深度优化 |

---

## 四、严重级别分布

| 级别 | 数量 | 百分比 | 说明 |
|------|------|--------|------|
| P0 | 24 | 51.1% | 立即行动（7×A + 17×C） |
| P1 | 8 | 17.0% | 计划改进（8×E） |
| P2 | 3 | 6.4% | 低优先级（3×D<8分） |
| 无需行动 | 12 | 25.5% | 持续监控 |

---

## 五、平台对比

| 平台 | 平均得分 | 平均引用比例 | 主要现象 | 备注 |
|------|---------|-------------|---------|------|
| Qwen | 5.8/10 | 65.0% | C（幻觉 42.5%）/ D（37.5%） | 单平台，待补充 ChatGPT/DeepSeek/豆包 |

---

## 六、模式分析

### 幻觉模式

| # | 触发词/场景 | 问题 | 典型表现 |
|---|-----------|------|---------|
| H1 | 模型转换 API | q_014, q_015, q_019 | 虚构 `export_from_torch()`/`export_from_onnx()` 函数，MindSpore 实际使用 converter_lite/MindConverter 工具 |
| H2 | SIG 例会安排 | q_036, q_038, q_040, q_041, q_047 | 将 `community/issues/6789` 作为所有 SIG 的例会信息来源，捏造具体例会时间（如"周四 19:00-20:00"） |
| H3 | 未来活动规划 | q_032 | 虚构 MindSpore Summit 2026 具体日期、"5000+ 开发者参与"等数字 |
| H4 | 国际会议历史 | q_048 | 虚构 KubeCon EU 2022 具体演讲主题 |
| H5 | vLLM 集成 | q_007 | 虚构 vLLM MindSpore 后端支持（官方不存在） |
| H6 | 性能基准 | q_034 | 虚构端侧推理延迟数据（ResNet50 约 2ms 等） |

### 消歧义问题

| 混淆项 | 影响问题 | 说明 |
|--------|---------|------|
| OpenI vs MindSpore 治理 | q_035 | 将 OpenI 平台误作 MindSpore 治理基金会 |
| OpenI vs 开放原子开源基金会 | q_054 | 两个不同组织被混为一谈 |
| OpenI 邮件列表 vs mailweb.mindspore.cn | q_052, q_054, q_055 | 邮件服务托管平台归属错误 |
| MeetingBot 下线历史 | q_059 | 捏造服务下线时间和原因 |

### 否定传递失败

| 未被传递的限制 | 影响问题 |
|--------------|---------|
| MindSpore 不直接支持读取 PyTorch/TF 模型 | q_019 |
| MindSpore 无 export_from_torch/export_from_onnx API | q_014, q_015 |
| vLLM 无官方 MindSpore 后端 | q_007 |

### 引用盲区

| 话题 | 缺失页面建议 |
|------|------------|
| SIG 注册表与例会安排 | `gitee.com/mindspore/community` 缺少结构化 SIG 目录页面 |
| MindSpore 邮件列表订阅 | `mailweb.mindspore.cn` 缺乏官方文档入口 |
| 模型转换工具边界（converter_lite/MindConverter） | converter_lite 工具独立文档页面 |
| 端侧框架性能基准 | `mindspore.cn/lite` 缺少官方 Benchmark 报告 |
| MindSpore 在华为 AI 全栈中的定位 | 缺少与昇腾/CANN 关系的定位说明页 |

---

## 七、改进建议（按优先级）

### P0 — 立即行动（1-2 周）

---

**s_001** | 类型: content | 影响 7 题 | 目录: CTX-01, CTX-02, CTX-03, CTX-06, CTX-08

**问题**: 7 个行业对比/选型/专项类问题无官方内容（q_005, q_022, q_024, q_028, q_030, q_031, q_033）

**建议**: 针对 7 个无官方内容问题，按类型分批创建专项文档：
1. **竞品对比页面**（q_022/q_024/q_028/q_030）：在官网创建框架选型指南，以客观对比表呈现 MindSpore vs PyTorch/PaddlePaddle/TensorFlow，重点突出昇腾 NPU 适配优势和国产化场景
2. **行业定位页面**（q_031/q_033）：明确 MindSpore 在华为 AI 全栈中的角色、国产 AI 框架生态位
3. **MindNLP 昇腾设备故障排查**（q_005）：在 MindNLP 文档中补充昇腾设备自动下载模型的配置说明

---

**s_002** | 类型: correction | 影响 3 题 (q_014, q_015, q_019) | 目录: REF-04, NEG-03, DIS-03, CTX-04, NEG-01

**问题**: 模型转换 API 幻觉——Qwen 生成虚构的 `export_from_torch()`/`export_from_onnx()` API 调用

**建议**: 在官方模型转换文档中：
1. 在页面显著位置添加**否定声明框**："MindSpore 暂不提供 `export_from_torch()` 或 `export_from_onnx()` 公开 API"
2. 创建独立的**模型迁移指南**页面，清晰区分：使用 `converter_lite` 工具转换 ONNX→MindIR；使用 MindConverter 工具从 PyTorch 迁移
3. 在 FAQ 中添加："我能直接加载 PyTorch 的 `.pth` 文件吗？" → "不能，需要先通过 MindConverter 转换"

---

**s_003** | 类型: correction | 影响 5 题 (q_036, q_038, q_040, q_041, q_047) | 目录: REF-04, REF-05, ORG-05, CTX-01, EXP-03

**问题**: SIG 例会信息幻觉——Qwen 滥用 `community/issues/6789` 捏造多个 SIG 的具体例会时间表

**建议**: 在 `gitee.com/mindspore/community` 创建**结构化 SIG 注册表**（`sigs/README.md` 或 `sig-list.md`），每个 SIG 条目包含：
- SIG 名称、负责人邮箱
- 例会频率和入会链接
- 邮件列表地址
- 相关仓库链接

将当前分散在 issue 评论中的 SIG 信息迁移至正式文档，确保搜索引擎可抓取。

---

**s_004** | 类型: correction | 影响 3 题 (q_052, q_054, q_055) | 目录: DIS-01, DIS-02, REF-07, CTX-04, DIS-03

**问题**: 邮件列表平台混淆——Qwen 将 MindSpore 邮件服务归属于 OpenI 平台

**建议**: 在 `mindspore.cn/community` 下创建**邮件列表专项说明页面**：
1. 明确声明：邮件服务托管于 `mailweb.mindspore.cn`（HyperKitty/Mailman 3）
2. 说明 OpenI 和 MindSpore 的关系（如有）
3. 提供各邮件列表订阅入口（dev、discuss、tsc）
4. 在 `gitee.com/mindspore/community` README 中添加邮件列表入口

---

**s_005** | 类型: correction | 影响 1 题 (q_032) | 目录: REF-04, REF-05, CTX-01, ORG-01

**问题**: 2026 年活动规划幻觉——Qwen 虚构具体活动日期和参与人数

**建议**: 在 `mindspore.cn/news` 或 `community/events` 创建**官方活动日历页面**，及时发布已确认的活动。当年度活动尚未规划时，页面保留框架并标注"活动计划将于 Q1 公布"，防止 AI 平台因内容空缺生成预测。

---

**s_006** | 类型: correction | 影响 1 题 (q_007) | 目录: NEG-01, NEG-03, REF-04, CTX-05, DIS-03

**问题**: vLLM + MindSpore 集成幻觉——虚构 vLLM MindSpore 后端支持

**建议**: 在 MindSpore Serving 文档首页添加集成状态声明："`MindSpore Serving` 是独立的推理服务框架，与 vLLM 当前版本不兼容（vLLM 无 MindSpore 后端）"。如有集成规划，在技术路线图中说明。同时创建 LLM 推理部署对比页面（MindSpore Serving vs vLLM 适用场景）。

---

**s_007** | 类型: correction | 影响 1 题 (q_035) | 目录: REF-07, DIS-01, CTX-04

**问题**: MindSpore 治理模式混淆——错误归属为 "OpenI 开源基金会治理模式"

**建议**: 在贡献指南和 `governance.md` 首段明确：「MindSpore 社区遵循自有治理章程，由 TSC 负责技术决策，不隶属于 OpenI 平台。」在 community 首页添加"治理架构"简介卡片，消除与第三方平台的混淆。

---

**s_008** | 类型: correction | 影响 1 题 (q_034) | 目录: REF-04, REF-01, EXC-01, CTX-08, EXP-08

**问题**: MindSpore Lite 性能基准幻觉——虚构与 TFLite/NCNN 对比的具体延迟数字

**建议**: 在 `mindspore.cn/lite` 发布**官方基准测试报告**，包含测试硬件（Ascend 310/310P）、测试模型（ResNet50/YOLOv5 等）、延迟数据。有了官方基准数据，AI 平台将引用真实数据而非生成虚假数字。

---

**s_009** | 类型: correction | 影响 1 题 (q_048) | 目录: REF-05, REF-04, ORG-01

**问题**: 国际峰会参与历史幻觉——虚构 KubeCon EU 2022 具体演讲信息

**建议**: 在 `mindspore.cn/community/events` 或 news 板块创建**国际交流专项页面**，列出 MindSpore 真实参与过的国际开源峰会（含演讲主题、链接）。若无此类活动，页面说明国际化战略；若有，提供可引用的官方记录。

---

### P1 — 计划改进（2-4 周）

---

**s_010** | 类型: optimization | 影响 8 题 | 目录: CTX-02, CTX-03, EXC-06, EXC-08, REF-02, REF-03

**问题**: E 类现象（官方引用比例低）— q_002, q_003, q_006, q_008, q_016, q_020, q_025, q_029

**共同特征**: 内容准确但官方文档深度不足，AI 平台依赖华为云博客/知乎补充信息。

**建议**:
1. **MindNLP 安装（q_002）**: 在 MindNLP 官方 Gitee 仓库添加详细故障排查节
2. **GPU/Docker 安装（q_003, q_006, q_008）**: 在安装文档末尾添加"常见错误代码速查表"，减少对博客的依赖
3. **data sink 动态切换（q_016）**: 为 `mindspore.Model` 的 data sink 模式创建专项教程，明确支持/不支持的场景
4. **TransData 算子（q_020）**: 在 API 文档中补充使用场景示例和性能对比
5. **华为 AI 生态定位（q_025）**: 创建"MindSpore 在华为 AI 全栈中的定位"专项说明页

---

### P2 — 持续优化

---

**s_011** | 类型: optimization | 影响 3 题 (q_013, q_017, q_027) | 目录: REF-06, VER-01, REF-01, EXC-08

**问题**: D 类轻微问题

**建议**:
- **q_013 Conv2d 精度**: 在精度对比文档中添加 Issues 搜索入口（避免虚构 URL `/issues/precision`）
- **q_017 v2.8.0 特性**: 将版本发布说明统一到 `version.html`，移除未核实的性能百分比；确认 `blog/mindspore-2-8-release` 是否存在
- **q_027 版本节奏**: 在 releases 页面添加版本周期说明（"约每半年一个主版本"），减少 AI 平台对历史日期的推断

---

## 八、逐题详情

| 问题 ID | 问题（摘要） | 现象 | 引用比例 | 得分 | 严重级 | 关键问题标签 |
|---------|------------|------|---------|------|--------|------------|
| q_001 | Ubuntu 22.04 ARM 安装 + opp_kernel | D | 71% | 8 | OK | missing_edge_cases |
| q_002 | MindNLP 安装失败排查 | E | 33% | 6 | P1 | missing_scope, no_query_variants |
| q_003 | MindSpore 2.6.0 GPU 安装 | E | 43% | 7 | P1 | missing_scope, outdated_info |
| q_004 | 模型推理报错排查 | D | 100% | 9 | OK | — |
| q_005 | MindNLP 昇腾设备下载出错 | **A** | — | — | **P0** | 官网无内容 |
| q_006 | Docker + Ascend 310 设备初始化失败 | E | 43% | 7 | P1 | missing_scope, outdated_info |
| q_007 | vLLM 部署 MindSpore 流式推理 | **C** | 50% | 3 | **P0** | fabricated_claims, negation_missed |
| q_008 | MindSpore 打包 Docker 镜像 | E | 50% | 7 | P1 | missing_scope |
| q_009 | Windows 搭建 MindSpore Lite 环境 | D | 83% | 9 | OK | — |
| q_010 | MindSpore 安装方式 | D | 80% | 9 | OK | — |
| q_011 | 多卡训练数据分片 | D | 67% | 8 | OK | — |
| q_012 | YOLOv5 训练 | D | 60% | 8 | OK | missing_scope |
| q_013 | Conv2d 精度对齐 | D | 67% | 7 | P2 | fabricated_claims (可疑URL) |
| q_014 | ONNX 转 MindIR 兼容性 | **C** | 50% | 3 | **P0** | fabricated_claims (export_from_onnx) |
| q_015 | PyTorch 模型转换 MindSpore | **C** | 40% | 3 | **P0** | fabricated_claims (export_from_torch) |
| q_016 | data sink 模式动态切换数据集 | E | 50% | 6 | P1 | missing_scope, negation_missed |
| q_017 | MindSpore 2.8.0 新特性 | D | 57% | 6 | P2 | vague_numbers, fabricated_claims |
| q_018 | PyNative vs Graph 模式选择 | D | 60% | 8 | OK | missing_use_cases |
| q_019 | 支持读取哪些第三方模型格式 | **C** | 50% | 3 | **P0** | fabricated_claims (虚构支持矩阵) |
| q_020 | TransData 算子功能与优化 | E | 40% | 7 | P1 | shallow_content |
| q_021 | 整数标量与 Tensor 类型提升规则 | D | 60% | 8 | OK | missing_edge_cases |
| q_022 | 国内主流深度学习框架对比 | **A** | — | — | **P0** | 官网无内容 |
| q_024 | TensorFlow 国产平替方案 | **A** | — | — | **P0** | 官网无内容 |
| q_025 | 华为 AI 全栈生态与 MindSpore 定位 | E | 29% | 7 | P1 | missing_scope, shallow_content |
| q_027 | MindSpore 版本发布节奏 | D | 80% | 7 | P2 | vague_numbers, outdated_info |
| q_028 | MindSpore vs PyTorch 选择 | **A** | — | — | **P0** | 官网无内容 |
| q_029 | MindSpore vs PyTorch（英文） | E | 29% | 6 | P1 | missing_scope, shallow_content |
| q_030 | MindSpore vs PaddlePaddle 选择 | **A** | — | — | **P0** | 官网无内容 |
| q_031 | 2025 年深度学习框架发展趋势 | **A** | — | — | **P0** | 官网无内容 |
| q_032 | MindSpore 2026 年活动规划 | **C** | 67% | 2 | **P0** | fabricated_claims (虚构活动) |
| q_033 | 华为昇腾 NPU 适合哪些框架 | **A** | — | — | **P0** | 官网无内容 |
| q_034 | MindSpore Lite vs TFLite/NCNN | **C** | 17% | 3 | **P0** | fabricated_claims (虚构基准) |
| q_035 | 新手加入 MindSpore 社区 | **C** | 71% | 5 | **P0** | entity_confusion (OpenI) |
| q_036 | Transformers SIG 例会安排 | **C** | 100% | 3 | **P0** | fabricated_claims (issues/6789) |
| q_038 | LLM Inference Serving SIG | **C** | 83% | 3 | **P0** | fabricated_claims (issues/6789) |
| q_040 | Parallel Training System SIG | **C** | 83% | 3 | **P0** | fabricated_claims (issues/6789) |
| q_041 | MindQuantum SIG | **C** | 83% | 5 | **P0** | fabricated_claims (issues/6789) |
| q_043 | 向 TSC 申请成立新 SIG | D | 86% | 8 | OK | — |
| q_045 | MindSpore TSC 职责 | D | 100% | 9 | OK | — |
| q_047 | MindSpore 各 SIG 列表 | **C** | 88% | 3 | **P0** | fabricated_claims (虚构SIG列表) |
| q_048 | MindSpore 参与国际开源峰会 | **C** | 67% | 3 | **P0** | fabricated_claims (虚构KubeCon演讲) |
| q_052 | 邮件列表订阅方式 | **C** | 83% | 5 | **P0** | entity_confusion (OpenI) |
| q_054 | 邮件列表系统平台和存档 | **C** | 50% | 3 | **P0** | entity_confusion (OpenI vs OpenAtom) |
| q_055 | MindSpore 各邮件列表受众 | **C** | 80% | 5 | **P0** | entity_confusion (OpenI) |
| q_059 | 社区例会自动化工具 | **C** | 83% | 4 | **P0** | fabricated_claims (MeetingBot历史) |
| q_063 | Security SIG 漏洞处理 | D | 86% | 8 | OK | — |
| q_064 | TSC 会议公开性与治理参与 | D | 83% | 8 | OK | — |

---

## 九、执行路线图

### 阶段一：紧急修复（1-2 周）— P0 项目

**内容创建（7 题 A 类）:**
- [ ] 创建框架选型指南页面（MindSpore vs PyTorch/PaddlePaddle/TensorFlow）
- [ ] 补充 MindNLP 昇腾设备自动下载故障排查文档

**幻觉纠错（17 题 C 类，按影响面排序）:**
- [ ] 在模型转换文档中添加否定声明（`export_from_torch` 不存在）+ 创建模型迁移指南
- [ ] 在 `gitee.com/mindspore/community` 创建结构化 SIG 注册表（解决 5 题 SIG 幻觉）
- [ ] 在 `mindspore.cn/community` 创建邮件列表说明页面（解决 3 题平台混淆）
- [ ] 在 MindSpore Serving 文档添加 vLLM 兼容性声明
- [ ] 在贡献指南消除 OpenI 治理模式混淆
- [ ] 创建官方活动日历页面，终止活动虚构
- [ ] 发布端侧基准测试报告，终止性能数字虚构
- [ ] 创建国际交流专项页面或说明

### 阶段二：短期改进（2-4 周）— P1 项目

- [ ] 为 MindNLP/GPU/Docker/data sink 安装类文档补充故障排查章节
- [ ] 为华为 AI 生态中 MindSpore 定位创建专项说明
- [ ] 提升 TransData 算子文档深度（使用场景 + 性能示例）
- [ ] 创建 MindSpore vs PyTorch 英文版对比页面

### 阶段三：持续优化（长期）— P2 项目

- [ ] 统一版本发布说明到 `version.html`，移除未核实性能数字
- [ ] 在精度对比文档添加 Issues 搜索正确入口
- [ ] 在 releases 页面添加版本发布周期说明

---

## 十、KPI 跟踪

| 指标 | 定义 | 当前（Qwen） | 目标 |
|------|------|-------------|------|
| 事实准确率（非幻觉率） | Layer 2 中非 C 类占比 | 57.5%（23/40） | ≥80% |
| 官方引用率 | 平均 official_source_ratio | 65.0% | ≥60% ✅ |
| 平均准确得分 | accuracy_score 均值 | 5.8/10 | ≥7.0 |
| P0 解决率 | P0 建议完成数/总数 | 0/9 | 100%（1 周内） |
| SIG 信息幻觉率 | SIG 相关问题 C 类占比 | 100%（5/5） | 0% |

---

> 此报告由 GEO Search Assessment scoring-engine 自动生成（2026-03-25）。
> **重要提醒**：本次仅有 Qwen 单平台数据。建议补充 ChatGPT/DeepSeek/豆包 响应后重新运行，以获得跨平台对比分析和更可靠的内容源问题识别（需 ≥3 平台共现）。
> 建议人工抽检 20% 的评分结果，校准记录保存到 `scoring-calibration.md`。
