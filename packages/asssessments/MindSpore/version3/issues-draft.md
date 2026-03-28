# GEO 改进 Issue 清单 — MindSpore version3

> 生成时间: 2026-03-25  
> 来源: `MindSpore/version3/scoring-results.json`  
> 筛选: P0 + P1  
> 状态: 待提交（dry-run）  
> 提交目标: 待确认（建议 `https://gitcode.com/mindspore/mindspore` 或文档仓库）

---

## 目录

**P0 — 立即行动（11 条）**

- [[GEO-P0] 补充竞品对比/选型/行业定位类问题的官方内容（7题内容空白）](#s_001)
- [[GEO-P0] 修正模型转换API幻觉：澄清export_from_torch/export_from_onnx不存在](#s_002)
- [[GEO-P0] 创建结构化SIG注册表页面，消除例会安排幻觉（5题受影响）](#s_003)
- [[GEO-P0] 补充邮件列表平台说明，消除OpenI/mailweb.mindspore.cn混淆（3题受影响）](#s_004)
- [[GEO-P0] 创建官方活动日历页面，防止AI平台生成虚假活动信息](#s_005)
- [[GEO-P0] 在MindSpore Serving文档中声明vLLM兼容性状态](#s_006)
- [[GEO-P0] 修正贡献指南中的OpenI治理模式错误引用](#s_007)
- [[GEO-P0] 发布MindSpore Lite官方基准测试报告，终止性能数字幻觉](#s_008)
- [[GEO-P0] 创建国际开源峰会参与记录页面，防止KubeCon等信息被捏造](#s_009)
- [[GEO-P0] 提升 SIG 专项页面可发现性：mindspore.cn/sig/* 未被AI平台引用，跨平台例会信息严重不一致](#s_011)
- [[GEO-P0] 修复 mindspore.cn/activities 可发现性：4 平台仅 1 个正确引用官方活动页面，3 个捏造或偏移](#s_012)

**P1 — 计划改进（1 条）**

- [[GEO-P1] 提升安装/部署/选型类文档深度，降低AI平台对第三方博客的依赖（8题P1）](#s_010)

---

## [GEO-P0] 补充竞品对比/选型/行业定位类问题的官方内容（7题内容空白） {#s_001}

**标签**: `geo-improvement,P0,content`  
**涉及问题**: `q_005`, `q_022`, `q_024`, `q_028`, `q_030`, `q_031`, `q_033`

## GEO 改进建议

**严重级别**: P0
**现象类型**: 现象 A（官网无内容）
**影响平台**: qwen
**影响问题数**: 7
**内容源判定**: ✅ 是内容源问题（建议修复官方内容本身）

### 涉及问题

- `q_005` MindNLP 在昇腾设备上自动下载模型时出错，如何解决？
- `q_022` 国内主流深度学习框架有哪些？各自有什么优缺点？
- `q_024` TensorFlow 有哪些国产平替方案？
- `q_028` MindSpore 和 PyTorch 相比有哪些优势和不足，应该如何选择？
- `q_030` 做国产 AI 应用开发应该选 MindSpore 还是 PaddlePaddle？
- `q_031` 2025 年深度学习框架的发展趋势是什么？国产框架的机遇在哪里？
- `q_033` 有哪些 AI 框架适合运行在华为昇腾 NPU 上？

### 问题描述

针对7个无官方内容问题，按类型分批创建专项文档：(1) 竞品对比页面（MindSpore vs PyTorch/PaddlePaddle/TensorFlow）：在官网创建选型指南，以客观对比表呈现，重点突出昇腾NPU适配优势；(2) 行业定位页面：明确MindSpore在华为AI全栈中的角色；(3) MindNLP昇腾设备故障排查页面：补充官方文档

### 影响范围

- **涉及平台**: qwen
- **现象分类**: 现象 A（官网无内容）
- **GEO 目录参考**: `CTX-01, CTX-02, CTX-03, CTX-06, CTX-08`

### 建议改进措施

针对7个无官方内容问题，按类型分批创建专项文档：(1) 竞品对比页面（MindSpore vs PyTorch/PaddlePaddle/TensorFlow）：在官网创建选型指南，以客观对比表呈现，重点突出昇腾NPU适配优势；(2) 行业定位页面：明确MindSpore在华为AI全栈中的角色；(3) MindNLP昇腾设备故障排查页面：补充官方文档

### 参考信息

- **分析来源**: GEO Search Assessment 自动评分（MindSpore version3，单平台 Qwen）
- **评估日期**: 2026-03-25
- **关联问题 ID**: q_005, q_022, q_024, q_028, q_030, q_031, q_033
- **评分结果文件**: `MindSpore/version3/scoring-results.json`

---
> 此 Issue 由 GEO Search Assessment 系统自动生成。建议在人工核实评分结果后再提交。

---

## [GEO-P0] 修正模型转换API幻觉：澄清export_from_torch/export_from_onnx不存在 {#s_002}

**标签**: `geo-improvement,P0,correction`  
**涉及问题**: `q_014`, `q_015`, `q_019`

## GEO 改进建议

**严重级别**: P0
**现象类型**: 现象 C（引用错误/幻觉）
**影响平台**: qwen
**影响问题数**: 3
**内容源判定**: ✅ 是内容源问题（建议修复官方内容本身）

### 涉及问题

- `q_014` 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？
- `q_015` 如何将 PyTorch 模型转换为 MindSpore 模型？
- `q_019` MindSpore 目前支持读取哪些第三方框架的模型及格式？

### 问题描述

在官方模型转换文档中明确声明：MindSpore不提供export_from_torch()或export_from_onnx()公开API。创建专项的'模型迁移指南'页面，清晰区分：(1) 使用converter_lite工具转换ONNX→MindIR；(2) 使用MindConverter工具从PyTorch迁移；(3) 添加显著的否定声明框：'MindSpore暂不支持直接加载PyTorch/TensorFlow原生格式'，防止AI平台误解

### 影响范围

- **涉及平台**: qwen
- **现象分类**: 现象 C（引用错误/幻觉）
- **GEO 目录参考**: `REF-04, NEG-03, DIS-03, CTX-04, NEG-01`

### 建议改进措施

在官方模型转换文档中明确声明：MindSpore不提供export_from_torch()或export_from_onnx()公开API。创建专项的'模型迁移指南'页面，清晰区分：(1) 使用converter_lite工具转换ONNX→MindIR；(2) 使用MindConverter工具从PyTorch迁移；(3) 添加显著的否定声明框：'MindSpore暂不支持直接加载PyTorch/TensorFlow原生格式'，防止AI平台误解

### 参考信息

- **分析来源**: GEO Search Assessment 自动评分（MindSpore version3，单平台 Qwen）
- **评估日期**: 2026-03-25
- **关联问题 ID**: q_014, q_015, q_019
- **评分结果文件**: `MindSpore/version3/scoring-results.json`

---
> 此 Issue 由 GEO Search Assessment 系统自动生成。建议在人工核实评分结果后再提交。

---



## [GEO-P0] 补充邮件列表平台说明，消除OpenI/mailweb.mindspore.cn混淆（3题受影响） {#s_004}

**标签**: `geo-improvement,P0,correction`  
**涉及问题**: `q_052`, `q_054`, `q_055`

## GEO 改进建议

**严重级别**: P0
**现象类型**: 现象 C（引用错误/幻觉）
**影响平台**: qwen
**影响问题数**: 3
**内容源判定**: ✅ 是内容源问题（建议修复官方内容本身）

### 涉及问题

- `q_052` 如何向 MindSpore 邮件列表发送邮件或订阅邮件列表？
- `q_054` MindSpore 的邮件列表系统使用什么平台？如何查看历史邮件存档？
- `q_055` MindSpore 有哪些邮件列表，它们分别面向什么受众？

### 问题描述

在mindspore.cn/community下创建'邮件列表'专项说明页面，明确：(1) 邮件服务托管地址（mailweb.mindspore.cn）；(2) 与OpenI平台的关系（如有）；(3) 各邮件列表订阅入口和用途；(4) 在gitee.com/mindspore/community的README中添加邮件列表入口链接。消除AI平台对OpenI/OpenAtom/mindspore.cn之间关系的混淆

### 影响范围

- **涉及平台**: qwen
- **现象分类**: 现象 C（引用错误/幻觉）
- **GEO 目录参考**: `DIS-01, DIS-02, REF-07, CTX-04, DIS-03`

### 建议改进措施

在mindspore.cn/community下创建'邮件列表'专项说明页面，明确：(1) 邮件服务托管地址（mailweb.mindspore.cn）；(2) 与OpenI平台的关系（如有）；(3) 各邮件列表订阅入口和用途；(4) 在gitee.com/mindspore/community的README中添加邮件列表入口链接。消除AI平台对OpenI/OpenAtom/mindspore.cn之间关系的混淆

### 参考信息

- **分析来源**: GEO Search Assessment 自动评分（MindSpore version3，单平台 Qwen）
- **评估日期**: 2026-03-25
- **关联问题 ID**: q_052, q_054, q_055
- **评分结果文件**: `MindSpore/version3/scoring-results.json`

---
> 此 Issue 由 GEO Search Assessment 系统自动生成。建议在人工核实评分结果后再提交。

---


## [GEO-P0] 修正贡献指南中的OpenI治理模式错误引用 {#s_007}

**标签**: `geo-improvement,P0,correction`  
**涉及问题**: `q_035`

## GEO 改进建议

**严重级别**: P0
**现象类型**: 现象 C（引用错误/幻觉）
**影响平台**: qwen
**影响问题数**: 1
**内容源判定**: ⚠️ 单平台检出（建议优先修复官方文档后观察多平台效果）

### 涉及问题

- `q_035` 新手如何加入 MindSpore 社区并参与开源贡献？

### 问题描述

在贡献指南和governance.md首段明确MindSpore的治理归属：'MindSpore社区遵循自有治理章程，由TSC负责技术决策。'消除与OpenI平台的混淆。在community首页添加'治理架构'简介卡片

### 影响范围

- **涉及平台**: qwen
- **现象分类**: 现象 C（引用错误/幻觉）
- **GEO 目录参考**: `REF-07, DIS-01, CTX-04`

### 建议改进措施

在贡献指南和governance.md首段明确MindSpore的治理归属：'MindSpore社区遵循自有治理章程，由TSC负责技术决策。'消除与OpenI平台的混淆。在community首页添加'治理架构'简介卡片

### 参考信息

- **分析来源**: GEO Search Assessment 自动评分（MindSpore version3，单平台 Qwen）
- **评估日期**: 2026-03-25
- **关联问题 ID**: q_035
- **评分结果文件**: `MindSpore/version3/scoring-results.json`

---
> 此 Issue 由 GEO Search Assessment 系统自动生成。建议在人工核实评分结果后再提交。

---

## [GEO-P1] 提升安装/部署/选型类文档深度，降低AI平台对第三方博客的依赖（8题P1） {#s_010}

**标签**: `geo-improvement,P1,optimization`  
**涉及问题**: `q_002`, `q_003`, `q_006`, `q_008`, `q_016`, `q_020`, `q_025`, `q_029`

## GEO 改进建议

**严重级别**: P1
**现象类型**: 现象 E（官方引用比例低）
**影响平台**: qwen
**影响问题数**: 8
**内容源判定**: ✅ 是内容源问题（建议修复官方内容本身）

### 涉及问题

- `q_002` MindSpore NLP（MindNLP）安装失败怎么排查和解决？
- `q_003` 如何正确安装 MindSpore 2.6.0 GPU 版本？按官方文档步骤操作失败时该怎么办？
- `q_006` 在容器环境中部署 MindSpore 1.1.1 + Ascend 310 时，执行张量运算测试出现设备初始化失败，应如何排查？
- `q_008` 如何将 MindSpore 应用打包成 Docker 镜像进行部署？
- `q_016` MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集吗？
- `q_020` TransData 算子的功能是什么？如何利用该算子优化性能？
- `q_025` 华为 AI 全栈开发生态包含哪些核心组件？MindSpore 在其中的定位是什么？
- `q_029` How does MindSpore compare to PyTorch for deep learning development?

### 问题描述

8个E类问题共同特征：内容准确但官方文档深度不足，导致AI平台引用第三方博客补充。优化方向：(1) 为MindNLP/Docker/data sink等常见问题创建专项FAQ页面，以结论先行格式组织；(2) 提升文档的完整性（参数说明、版本适配表、常见错误代码），减少AI平台对华为云博客/知乎的依赖；(3) 为选型问题（q_025/q_029）创建官方定位说明，提供可引用的对比框架

### 影响范围

- **涉及平台**: qwen
- **现象分类**: 现象 E（官方引用比例低）
- **GEO 目录参考**: `CTX-02, CTX-03, EXC-06, EXC-08, REF-02, REF-03`

### 建议改进措施

8个E类问题共同特征：内容准确但官方文档深度不足，导致AI平台引用第三方博客补充。优化方向：(1) 为MindNLP/Docker/data sink等常见问题创建专项FAQ页面，以结论先行格式组织；(2) 提升文档的完整性（参数说明、版本适配表、常见错误代码），减少AI平台对华为云博客/知乎的依赖；(3) 为选型问题（q_025/q_029）创建官方定位说明，提供可引用的对比框架

### 参考信息

- **分析来源**: GEO Search Assessment 自动评分（MindSpore version3，单平台 Qwen）
- **评估日期**: 2026-03-25
- **关联问题 ID**: q_002, q_003, q_006, q_008, q_016, q_020, q_025, q_029
- **评分结果文件**: `MindSpore/version3/scoring-results.json`

---
> 此 Issue 由 GEO Search Assessment 系统自动生成。建议在人工核实评分结果后再提交。

---