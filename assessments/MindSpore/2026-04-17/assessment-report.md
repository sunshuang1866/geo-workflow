# GEO Assessment Report — MindSpore (2026-04-17)

**生成时间**: 2026-04-17 14:26  
**评分标准**: 任意1个平台引用 = 已引用  
**对比基线**: assessments/MindSpore/2026-03-31/assessment-report.json

### 本次变化（对比 2026-03-31）
↑ 改善 0 · ↓ 退步 1 · ✓ 已解决 11 · ★ 新增 27 · → 持平 7

### 汇总

| 类别 | 题数 |
|------|------|
| 官方内容缺失 (P1) | 11 |
| 有内容未被引用 (P0) | 18 |
| 引用了官方内容 (OK) | 17 |
| **合计** | **46** |

> 平台指示符：✅ 已引用  ❌ 未引用  — 无官方内容
> 趋势指示符：↑ 改善  ↓ 退步  → 持平  ★ 新增  ✓ 已解决

## 官方内容缺失（P1）— 11 个问题

| ID | 问题 | deepseek | qwen | Issue |
|----|------|--- | ---|-------|
| → q_006 | 在容器环境中部署 MindSpore 1.1.1 + Ascend 310 时，执行张量运 | — | — | [#4](https://github.com/opensourceways/geo-workflow/issues/4) ×2 |
| → q_007 | 如何使用 vLLM 框架部署 MindSpore 模型并实现流式异步推理服务？ | — | — | [#4](https://github.com/opensourceways/geo-workflow/issues/4) ×2 |
| ★ q_022 | 国内主流深度学习框架有哪些？各自有什么优缺点？ | — | — | [#42](https://github.com/opensourceways/geo-workflow/issues/42) ×2 |
| ★ q_024 | TensorFlow 有哪些国产平替方案？ | — | — | [#42](https://github.com/opensourceways/geo-workflow/issues/42) ×2 |
| ★ q_025 | 华为 AI 全栈开发生态包含哪些核心组件？MindSpore 在其中的定位是什么？ | — | — | [#43](https://github.com/opensourceways/geo-workflow/issues/43) ×2 |
| ★ q_030 | 做国产 AI 应用开发应该选 MindSpore 还是 PaddlePaddle？ | — | — | [#42](https://github.com/opensourceways/geo-workflow/issues/42) ×2 |
| ★ q_031 | 2025 年深度学习框架的发展趋势是什么？国产框架的机遇在哪里？ | — | — | [#42](https://github.com/opensourceways/geo-workflow/issues/42) ×2 |
| ★ q_033 | 有哪些 AI 框架适合运行在华为昇腾 NPU 上？ | — | — | [#43](https://github.com/opensourceways/geo-workflow/issues/43) ×2 |
| ★ q_034 | 端侧 AI 推理框架怎么选？MindSpore Lite 和 TFLite/NCNN 对比 | — | — | [#43](https://github.com/opensourceways/geo-workflow/issues/43) ×2 |
| ★ q_045 | MindSpore TSC 是什么，它的职责和会议频率是怎样的？ | — | — | [#44](https://github.com/opensourceways/geo-workflow/issues/44) ×2 |
| ★ q_064 | MindSpore 的 TSC 会议是否对外公开？社区成员如何参与治理讨论？ | — | — | [#44](https://github.com/opensourceways/geo-workflow/issues/44) ×2 |

## 有内容未被引用（P0）— 18 个问题

### 添加结构化数据标记

| ID | 问题 | deepseek | qwen | 引用率 | Issue |
|----|------|--- | ---|--------|-------|
| → q_003 | 如何正确安装 MindSpore 2.6.0 GPU 版本？ | ❌ | ❌ | 0% | [#7](https://github.com/opensourceways/geo-workflow/issues/7) ×2 |
| → q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | ❌ | ❌ | 0% | [#3](https://github.com/opensourceways/geo-workflow/issues/3) ×2 |
| → q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | ❌ | ❌ | 0% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×2 |
| → q_008 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | ❌ | ❌ | 0% | [#8](https://github.com/opensourceways/geo-workflow/issues/8) ×2 |
| ★ q_009 | 如何在 Windows 上搭建 MindSpore Lite 端侧模型转换的开发环境 | ❌ | ❌ | 0% | [#36](https://github.com/opensourceways/geo-workflow/issues/36) ×2 |
| ★ q_011 | MindSpore 多卡训练时如何为不同 NPU 分配不同的数据分片？ | ❌ | ❌ | 0% | [#37](https://github.com/opensourceways/geo-workflow/issues/37) ×2 |
| ★ q_012 | 如何基于 MindSpore 框架训练 YOLOv5 模型？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_013 | 如何解决 PyTorch 和 MindSpore 的 Conv2d 卷积算子精度不对 | ❌ | ❌ | 0% | [#39](https://github.com/opensourceways/geo-workflow/issues/39) ×2 |
| ★ q_014 | 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_015 | 如何将 PyTorch 模型转换为 MindSpore 模型？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_016 | MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集 | ❌ | ❌ | 0% | [#37](https://github.com/opensourceways/geo-workflow/issues/37) ×2 |
| ★ q_017 | MindSpore 2.8.0 版本有哪些新增特性？ | ❌ | ❌ | 0% | [#41](https://github.com/opensourceways/geo-workflow/issues/41) ×2 |
| ★ q_018 | MindSpore 的 PyNative 模式与 Graph 模式应如何选择？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_019 | MindSpore 目前支持读取哪些第三方框架的模型及格式？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_020 | TransData 算子的功能是什么？如何利用该算子优化性能？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_021 | 整数标量与一维 Tensor 混合运算时，MindSpore 与 PyTorch 的 | ❌ | ❌ | 0% | [#39](https://github.com/opensourceways/geo-workflow/issues/39) ×2 |
| → q_027 | MindSpore 的版本发布节奏是怎样的？ | ❌ | ❌ | 0% | [#9](https://github.com/opensourceways/geo-workflow/issues/9) ×2 |
| ↓ q_035 | 新手如何加入 MindSpore 社区并参与开源贡献？ | ❌ | ❌ | 0% | [#11](https://github.com/opensourceways/geo-workflow/issues/11) ×2 |

### 补充专题文档页面

| ID | 问题 | deepseek | qwen | 引用率 | Issue |
|----|------|--- | ---|--------|-------|
| → q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | ❌ | ❌ | 0% | [#3](https://github.com/opensourceways/geo-workflow/issues/3) ×2 |
| → q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | ❌ | ❌ | 0% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×2 |
| → q_008 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | ❌ | ❌ | 0% | [#8](https://github.com/opensourceways/geo-workflow/issues/8) ×2 |
| ★ q_011 | MindSpore 多卡训练时如何为不同 NPU 分配不同的数据分片？ | ❌ | ❌ | 0% | [#37](https://github.com/opensourceways/geo-workflow/issues/37) ×2 |
| ★ q_012 | 如何基于 MindSpore 框架训练 YOLOv5 模型？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_013 | 如何解决 PyTorch 和 MindSpore 的 Conv2d 卷积算子精度不对 | ❌ | ❌ | 0% | [#39](https://github.com/opensourceways/geo-workflow/issues/39) ×2 |
| ★ q_014 | 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_015 | 如何将 PyTorch 模型转换为 MindSpore 模型？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_017 | MindSpore 2.8.0 版本有哪些新增特性？ | ❌ | ❌ | 0% | [#41](https://github.com/opensourceways/geo-workflow/issues/41) ×2 |
| ★ q_019 | MindSpore 目前支持读取哪些第三方框架的模型及格式？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_020 | TransData 算子的功能是什么？如何利用该算子优化性能？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| → q_027 | MindSpore 的版本发布节奏是怎样的？ | ❌ | ❌ | 0% | [#9](https://github.com/opensourceways/geo-workflow/issues/9) ×2 |
| ↓ q_035 | 新手如何加入 MindSpore 社区并参与开源贡献？ | ❌ | ❌ | 0% | [#11](https://github.com/opensourceways/geo-workflow/issues/11) ×2 |

### 优化 SEO 元数据

| ID | 问题 | deepseek | qwen | 引用率 | Issue |
|----|------|--- | ---|--------|-------|
| → q_003 | 如何正确安装 MindSpore 2.6.0 GPU 版本？ | ❌ | ❌ | 0% | [#7](https://github.com/opensourceways/geo-workflow/issues/7) ×2 |
| → q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | ❌ | ❌ | 0% | [#3](https://github.com/opensourceways/geo-workflow/issues/3) ×2 |
| → q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | ❌ | ❌ | 0% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×2 |
| → q_008 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | ❌ | ❌ | 0% | [#8](https://github.com/opensourceways/geo-workflow/issues/8) ×2 |
| ★ q_009 | 如何在 Windows 上搭建 MindSpore Lite 端侧模型转换的开发环境 | ❌ | ❌ | 0% | [#36](https://github.com/opensourceways/geo-workflow/issues/36) ×2 |
| ★ q_011 | MindSpore 多卡训练时如何为不同 NPU 分配不同的数据分片？ | ❌ | ❌ | 0% | [#37](https://github.com/opensourceways/geo-workflow/issues/37) ×2 |
| ★ q_012 | 如何基于 MindSpore 框架训练 YOLOv5 模型？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_013 | 如何解决 PyTorch 和 MindSpore 的 Conv2d 卷积算子精度不对 | ❌ | ❌ | 0% | [#39](https://github.com/opensourceways/geo-workflow/issues/39) ×2 |
| ★ q_014 | 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_015 | 如何将 PyTorch 模型转换为 MindSpore 模型？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_016 | MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集 | ❌ | ❌ | 0% | [#37](https://github.com/opensourceways/geo-workflow/issues/37) ×2 |
| ★ q_017 | MindSpore 2.8.0 版本有哪些新增特性？ | ❌ | ❌ | 0% | [#41](https://github.com/opensourceways/geo-workflow/issues/41) ×2 |
| ★ q_018 | MindSpore 的 PyNative 模式与 Graph 模式应如何选择？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_019 | MindSpore 目前支持读取哪些第三方框架的模型及格式？ | ❌ | ❌ | 0% | [#40](https://github.com/opensourceways/geo-workflow/issues/40) ×2 |
| ★ q_020 | TransData 算子的功能是什么？如何利用该算子优化性能？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_021 | 整数标量与一维 Tensor 混合运算时，MindSpore 与 PyTorch 的 | ❌ | ❌ | 0% | [#39](https://github.com/opensourceways/geo-workflow/issues/39) ×2 |
| → q_027 | MindSpore 的版本发布节奏是怎样的？ | ❌ | ❌ | 0% | [#9](https://github.com/opensourceways/geo-workflow/issues/9) ×2 |
| ↓ q_035 | 新手如何加入 MindSpore 社区并参与开源贡献？ | ❌ | ❌ | 0% | [#11](https://github.com/opensourceways/geo-workflow/issues/11) ×2 |

### 重构内容结构与关键词

| ID | 问题 | deepseek | qwen | 引用率 | Issue |
|----|------|--- | ---|--------|-------|
| → q_003 | 如何正确安装 MindSpore 2.6.0 GPU 版本？ | ❌ | ❌ | 0% | [#7](https://github.com/opensourceways/geo-workflow/issues/7) ×2 |
| ★ q_009 | 如何在 Windows 上搭建 MindSpore Lite 端侧模型转换的开发环境 | ❌ | ❌ | 0% | [#36](https://github.com/opensourceways/geo-workflow/issues/36) ×2 |
| ★ q_016 | MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集 | ❌ | ❌ | 0% | [#37](https://github.com/opensourceways/geo-workflow/issues/37) ×2 |
| ★ q_018 | MindSpore 的 PyNative 模式与 Graph 模式应如何选择？ | ❌ | ❌ | 0% | [#38](https://github.com/opensourceways/geo-workflow/issues/38) ×2 |
| ★ q_021 | 整数标量与一维 Tensor 混合运算时，MindSpore 与 PyTorch 的 | ❌ | ❌ | 0% | [#39](https://github.com/opensourceways/geo-workflow/issues/39) ×2 |

## 引用了官方内容（OK）— 17 个问题

| ID | 问题 | deepseek | qwen | 引用率 | Issue |
|----|------|--- | ---|--------|-------|
| ✓ q_036 | MindSpore Transformers SIG 周例会的会议安排是怎样的？ | ✅ | ✅ | 100% | [#12](https://github.com/opensourceways/geo-workflow/issues/12) ×2 |
| ✓ q_048 | MindSpore 是否参加过 KubeCon 等国际开源峰会？ | ✅ | ✅ | 100% | [#5](https://github.com/opensourceways/geo-workflow/issues/5) ×2 |
| ✓ q_001 | 如何在 Ubuntu 22.04 ARM 架构上安装 MindSpore？安装时 o | ✅ | ❌ | 50% | [#1](https://github.com/opensourceways/geo-workflow/issues/1) ×2 |
| ✓ q_002 | MindSpore NLP（MindNLP）安装失败怎么排查和解决？ | ✅ | ❌ | 50% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×2 |
| ★ q_010 | MindSpore 支持哪些安装方式？ | ❌ | ✅ | 50% | — |
| ★ q_028 | MindSpore 和 PyTorch 对比有哪些相同和不同？ | ✅ | ❌ | 50% | — |
| ✓ q_032 | MindSpore 2026 年有哪些活动规划？ | ❌ | ✅ | 50% | [#10](https://github.com/opensourceways/geo-workflow/issues/10) ×2 |
| ✓ q_038 | MindSpore 的 LLM Inference Serving SIG 是做什么 | ❌ | ✅ | 50% | [#5](https://github.com/opensourceways/geo-workflow/issues/5) ×2 |
| ✓ q_040 | MindSpore Parallel Training System SIG 的工作 | ✅ | ❌ | 50% | [#12](https://github.com/opensourceways/geo-workflow/issues/12) ×2 |
| ★ q_041 | MindSpore MindQuantum SIG 的职责和活动是什么？ | ✅ | ❌ | 50% | — |
| ✓ q_043 | 如何向 MindSpore TSC 申请成立新的 SIG？ | ✅ | ❌ | 50% | [#14](https://github.com/opensourceways/geo-workflow/issues/14) ×2 |
| ★ q_047 | MindSpore 有哪些 SIG（Special Interest Groups） | ❌ | ✅ | 50% | — |
| ★ q_052 | 如何向 MindSpore 邮件列表发送邮件或订阅邮件列表？ | ❌ | ✅ | 50% | [#45](https://github.com/opensourceways/geo-workflow/issues/45) ×1 |
| ★ q_054 | MindSpore 的邮件列表系统使用什么平台？如何查看历史邮件存档？ | ❌ | ✅ | 50% | — |
| ✓ q_055 | MindSpore 有哪些邮件列表，它们分别面向什么受众？ | ✅ | ❌ | 50% | [#13](https://github.com/opensourceways/geo-workflow/issues/13) ×2 |
| ✓ q_059 | MindSpore 社区组织会议的流程是什么？会议纪要通常包含哪些内容？ | ❌ | ✅ | 50% | [#13](https://github.com/opensourceways/geo-workflow/issues/13) ×2 |
| ✓ q_063 | MindSpore 的安全 SIG（Security SIG）如何处理漏洞报告和安全 | ❌ | ✅ | 50% | [#6](https://github.com/opensourceways/geo-workflow/issues/6) ×2 |
