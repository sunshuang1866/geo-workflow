# MindSpore GEO 问题集

> 社区: MindSpore
> 总数: 47
> 来源: forum, issue, maillist, industry, manual
> 更新日期: 2026-03-20

---

## 了解阶段

### 认知

| # | 问题 | 来源 |
|---|------|------|
| q_022 | 国内主流深度学习框架有哪些？各自有什么优缺点？ | industry |
| q_024 | TensorFlow 有哪些国产平替方案？ | industry |
| q_025 | 华为 AI 全栈开发生态包含哪些核心组件？MindSpore 在其中的定位是什么？ | industry |
| q_027 | MindSpore 的版本发布节奏是怎样的？ | manual |
| q_036 | MindSpore Transformers SIG 周例会的会议安排是怎样的？ | dev@mindspore.cn |
| q_038 | MindSpore 的 LLM Inference Serving SIG 是做什么的，多久开一次例会？ | dev@mindspore.cn |
| q_040 | MindSpore Parallel Training System SIG 的工作范围是什么？ | dev@mindspore.cn |
| q_041 | MindSpore Quantum SIG 的职责和活动是什么？ | dev@mindspore.cn |
| q_043 | 如何向 MindSpore TSC 申请成立新的 SIG？ | mindspore-tsc@mindspore.cn |
| q_045 | MindSpore TSC 是什么，它的职责和会议频率是怎样的？ | mindspore-tsc@mindspore.cn |
| q_047 | MindSpore 有哪些 SIG（Special Interest Groups）？各个 SIG 负责什么方向？ | mindspore-tsc@mindspore.cn |
| q_048 | MindSpore 是否参加过 KubeCon 等国际开源峰会？ | mindspore-tsc@mindspore.cn |
| q_059 | MindSpore 如何通过自动化工具管理社区例会通知？社区采用什么会议平台？ | mindspore-discuss@mindspore.cn |
| q_063 | MindSpore 的安全 SIG（Security SIG）如何处理漏洞报告和安全问题？ | mindspore-discuss@mindspore.cn |
| q_064 | MindSpore 的 TSC 会议是否对外公开？社区成员如何参与治理讨论？ | mindspore-tsc@mindspore.cn |

### 选型

| # | 问题 | 来源 |
|---|------|------|
| q_028 | MindSpore 和 PyTorch 相比有哪些优势和不足，应该如何选择？ | industry |
| q_029 | How does MindSpore compare to PyTorch for deep learning development? | industry |
| q_030 | 做国产 AI 应用开发应该选 MindSpore 还是 PaddlePaddle？ | industry |

### 趋势

| # | 问题 | 来源 |
|---|------|------|
| q_031 | 2025 年深度学习框架的发展趋势是什么？国产框架的机遇在哪里？ | industry |
| q_032 | MindSpore 2026 年有哪些活动规划？ | manual |

### 场景

| # | 问题 | 来源 |
|---|------|------|
| q_033 | 有哪些 AI 框架适合运行在华为昇腾 NPU 上？ | industry |
| q_034 | 端侧 AI 推理框架怎么选？MindSpore Lite 和 TFLite/NCNN 对比如何？ | industry |
| q_035 | 新手如何加入 MindSpore 社区并参与开源贡献？ | manual |

---

## 使用阶段

### 故障

| # | 问题 | 来源 | 热度 |
|---|------|------|------|
| q_001 | 如何在 Ubuntu 22.04 ARM 架构上安装 MindSpore？安装时 opp_kernel 报错怎么解决？ | forum | 168 views |
| q_002 | MindSpore NLP（MindNLP）安装失败怎么排查和解决？ | forum | 133 views |
| q_003 | 如何正确安装 MindSpore 2.6.0 GPU 版本？按官方文档步骤操作失败时该怎么办？ | forum | 94 views |
| q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | forum | 91 views |
| q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | forum | 77 views |
| q_006 | 在容器环境中部署 MindSpore 1.1.1 + Ascend 310 时，执行张量运算测试出现设备初始化失败，应如何排查？ | issue | — |

### 教程

| # | 问题 | 来源 | 热度 |
|---|------|------|------|
| q_007 | 如何使用 vLLM 框架部署 MindSpore 模型并实现流式异步推理服务？ | forum | 151 views |
| q_008 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | forum | 135 views |
| q_009 | 如何在 Windows 上搭建 MindSpore Lite 端侧模型转换的开发环境？ | forum | 45 views |
| q_010 | MindSpore 支持哪些安装方式？ | manual | — |
| q_011 | MindSpore 多卡训练时如何为不同 NPU 分配不同的数据分片？ | manual | — |
| q_012 | 如何基于 MindSpore 框架训练 YOLOv5 模型？ | forum | — |
| q_052 | 如何向 MindSpore 邮件列表发送邮件或订阅邮件列表？ | maillist | mindspore-discuss@mindspore.cn |
| q_054 | MindSpore 的邮件列表系统使用什么平台？如何查看历史邮件存档？ | maillist | mindspore-discuss@mindspore.cn |
| q_055 | MindSpore 有哪些邮件列表，它们分别面向什么受众？ | maillist | mindspore-discuss@mindspore.cn |

### 迁移

| # | 问题 | 来源 | 热度 |
|---|------|------|------|
| q_013 | 如何解决 PyTorch 和 MindSpore 的 Conv2d 卷积算子精度不对齐的问题？ | forum | 70 views |
| q_014 | 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？ | forum | 65 views |
| q_015 | 如何将 PyTorch 模型转换为 MindSpore 模型？ | manual | — |

### 特性

| # | 问题 | 来源 | 热度 |
|---|------|------|------|
| q_016 | MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集吗？ | forum | 69 views |
| q_017 | MindSpore 2.8.0 版本有哪些新增特性？ | manual | — |
| q_018 | MindSpore 的 PyNative 模式与 Graph 模式应如何选择？ | FAQ | — |
| q_019 | MindSpore 目前支持读取哪些第三方框架的模型及格式？ | FAQ | — |
| q_020 | TransData 算子的功能是什么？如何利用该算子优化性能？ | FAQ | — |
| q_021 | 整数标量与一维 Tensor 混合运算时，MindSpore 与 PyTorch 的隐式类型转换规则是否一致？MindSpore 算子输入的类型提升规则是什么？ | forum | — |

---

