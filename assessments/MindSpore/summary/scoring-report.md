# MindSpore GEO 引用评估报告

> 匹配规则：URL 精确匹配（response_text 子串 + citations 前缀匹配），归一化去除 http/https、www.、尾部斜杠，不区分大小写

**图例**

| 符号 | 含义 |
|------|------|
| ✅✅ | DeepSeek 和 Qwen 均引用了官方链接 |
| ✅❌ | 仅 DeepSeek 引用 |
| ❌✅ | 仅 Qwen 引用 |
| ❌❌ | 两平台均未引用 |
| —— | 该轮未采样 |

| 采样轮次 | 日期 | 平台 | 采样方式 |
|----------|------|------|----------|
| Run A | 2026-03-30 | DeepSeek-web · Qwen-web | 浏览器（联网搜索，含 citations 字段） |
| Run B | 2026-04-17 | DeepSeek-web · Qwen-web | 浏览器（联网搜索，含 citations 字段） |
| Run C | 2026-05-10 | DeepSeek-web · Qwen-web | 浏览器（联网搜索，含 citations 字段） |

---

## 对比总表

> 每格为 `DS · Qwen` 两平台的引用结果；**引用计** = 已引用平台数 / 已采样平台数，按引用率降序排列。

| ID | 问题 | Run A<br>03-30 | Run B<br>04-17 | Run C<br>05-10 | 引用计 | 官方链接 |
|----|------|----------------|----------------|----------------|--------|----------|
| q_043 | 如何向 MindSpore TSC 申请成立新的 SIG？ | —— | ✅✅ | ✅✅ | 4/4 | [sig](https://www.mindspore.cn/sig) |
| q_052 | 如何向 MindSpore 邮件列表发送邮件或订阅邮件列表？ | —— | ✅✅ | ✅✅ | 4/4 | [mailman3/lists](https://mailweb.mindspore.cn/mailman3/lists) |
| q_054 | MindSpore 如何查看历史邮件存档？ | —— | ✅✅ | ✅✅ | 4/4 | [archives](https://mailweb.mindspore.cn/archives/) |
| q_001 | 如何在 Ubuntu 22.04 ARM 架构上安装 MindSpore？ | ❌❌ | ❌✅ | ✅✅ | 3/6 | [install](https://www.mindspore.cn/install/) |
| q_010 | MindSpore 支持哪些安装方式？ | —— | ✅✅ | ❌✅ | 3/4 | [install](https://www.mindspore.cn/install) |
| q_048 | MindSpore 是否参加过 KubeCon 等国际开源峰会？ | ❌❌ | ✅✅ | ✅✅ | 4/6 | [activities](https://www.mindspore.cn/activities) |
| q_055 | MindSpore 有哪些邮件列表？ | ❌❌ | ✅✅ | ✅✅ | 4/6 | [mailman3/lists](https://mailweb.mindspore.cn/mailman3/lists/?page=1) |
| q_032 | MindSpore 2026 年有哪些活动规划？ | ❌❌ | ❌✅ | ✅✅ | 3/6 | [activities](https://www.mindspore.cn/activities) |
| q_035 | 新手如何加入 MindSpore 社区并参与开源贡献？ | ❌✅ | ✅❌ | ✅❌ | 3/6 | [contribution](https://www.mindspore.cn/contribution) |
| q_036 | MindSpore Transformers SIG 周例会的会议安排是怎样的？ | ❌❌ | ✅✅ | ❌✅ | 3/6 | [sig/MindSpore Transformers](https://www.mindspore.cn/sig/MindSpore%20Transformers) |
| q_040 | MindSpore Parallel Training System SIG 的工作范围是什么？ | ❌❌ | ✅✅ | ❌✅ | 3/6 | [sig](https://www.mindspore.cn/sig) |
| q_012 | 如何基于 MindSpore 框架训练 YOLOv5 模型？ | —— | ✅❌ | ✅❌ | 2/4 | [search?q=YOLOv5](https://www.mindspore.cn/search?q=YOLOv5) |
| q_014 | 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？ | —— | ✅❌ | ✅❌ | 2/4 | [topic/196](https://discuss.mindspore.cn/t/topic/196) |
| q_016 | MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集吗？ | —— | ✅❌ | ✅❌ | 2/4 | [mindspore.data_sink.html](https://www.mindspore.cn/docs/zh-CN/r2.8.0/api_python/mindspore/mindspore.data_sink.html) |
| q_018 | MindSpore 的 PyNative 模式与 Graph 模式应如何选择？ | —— | ✅❌ | ✅❌ | 2/4 | [context.html](https://www.mindspore.cn/doc/programming_guide/zh-CN/r1.0/context.html) |
| q_020 | TransData 算子的功能是什么？ | —— | ✅❌ | ✅❌ | 2/4 | [operators_api.html](https://www.mindspore.cn/docs/zh-CN/r2.8.0/faq/operators_api.html) |
| q_028 | MindSpore 和 PyTorch 对比有哪些相同和不同？ | —— | ✅❌ | ✅❌ | 2/4 | [typical_api_comparision.html](https://www.mindspore.cn/docs/zh-CN/r2.2/migration_guide/typical_api_comparision.html#) |
| q_041 | MindSpore MindQuantum SIG 的职责和活动是什么？ | —— | ❌✅ | ❌✅ | 2/4 | [sig](https://www.mindspore.cn/sig) |
| q_047 | MindSpore 有哪些 SIG（Special Interest Groups）？ | —— | ❌✅ | ❌✅ | 2/4 | [sig](https://www.mindspore.cn/sig/) |
| q_002 | MindSpore NLP（MindNLP）安装失败怎么排查和解决？ | ❌❌ | ✅❌ | ✅❌ | 2/6 | [topic/706](https://discuss.mindspore.cn/t/topic/706) |
| q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | ❌❌ | ✅❌ | ✅❌ | 2/6 | [inference.html](https://www.mindspore.cn/docs/zh-CN/master/faq/inference.html) |
| q_059 | MindSpore 社区组织会议的流程是什么？会议纪要通常包含哪些内容？ | ❌❌ | ❌✅ | ❌✅ | 2/6 | [meeting-guide](https://www.mindspore.cn/sig/meeting-guide) |
| q_063 | MindSpore 的安全 SIG（Security SIG）如何处理漏洞报告和安全问题？ | ❌❌ | ❌✅ | ❌✅ | 2/6 | [security](https://www.mindspore.cn/security) |
| q_017 | MindSpore 2.8.0 版本有哪些新增特性？ | —— | ❌❌ | ❌✅ | 1/4 | [RELEASE.html](https://www.mindspore.cn/docs/zh-CN/r2.8.0/RELEASE.html) |
| q_021 | MindSpore 的算子输入的类型转换规则是什么 | —— | ❌❌ | ❌✅ | 1/4 | [operators_api.html](https://www.mindspore.cn/docs/zh-CN/master/faq/operators_api.html) |
| q_008 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | ❌❌ | ✅❌ | ❌❌ | 1/6 | [docker-installation.html](https://www.mindspore.cn/mindformers/docs/zh-CN/r1.8.0/example/docker-installation.html) |
| q_038 | MindSpore 的 LLM Inference Serving SIG 是做什么的？ | ❌❌ | ❌✅ | ❌❌ | 1/6 | [sig/LLM Inference Serving](https://www.mindspore.cn/sig/LLM%20Inference%20Serving) |
| q_009 | 如何在 Windows 上搭建 MindSpore Lite 端侧模型转换的开发环境？ | —— | ❌❌ | ❌❌ | 0/4 | [downloads.html](https://www.mindspore.cn/lite/docs/zh-CN/stable/use/downloads.html) |
| q_011 | MindSpore 多卡训练时如何为不同 NPU 分配不同的数据分片？ | —— | ❌❌ | ❌❌ | 0/4 | [backend_running.html](https://www.mindspore.cn/doc/faq/zh-CN/r1.2/backend_running.html) |
| q_013 | 如何解决 PyTorch 和 MindSpore 的 Conv2d 卷积算子精度不对齐的问题？ | —— | ❌❌ | ❌❌ | 0/4 | [operators_api.html](https://www.mindspore.cn/docs/zh-CN/r2.8.0/faq/operators_api.html) |
| q_015 | 如何将 PyTorch 模型转换为 MindSpore 模型？ | —— | ❌❌ | ❌❌ | 0/4 | [migration_case_of_mindconverter.html](https://www.mindspore.cn/docs/migration_guide/zh-CN/r1.3/migration_case_of_mindconverter.html) |
| q_019 | MindSpore 目前支持读取哪些第三方框架的模型及格式？ | —— | ❌❌ | ❌❌ | 0/4 | [feature_advice.html](https://www.mindspore.cn/docs/zh-CN/master/faq/feature_advice.html) |

---

## 🔘 无官方链接（P1，5 题）

官方目前尚无对应内容，无法评估引用情况。

| ID | 问题 | 备注 |
|----|------|------|
| q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | Run A + Run B + Run C 均采样 |
| q_006 | 在容器环境中部署 MindSpore 1.1.1 + Ascend 310 时，执行张量运算测试出现设备初始化失败，应如何排查？ | Run A + Run B + Run C 均采样 |
| q_007 | 如何使用 vLLM 框架部署 MindSpore 模型并实现流式异步推理服务？ | Run A + Run B + Run C 均采样 |
| q_045 | MindSpore TSC 是什么，它的职责和会议频率是怎样的？ | Run B + Run C 均采样 |
| q_064 | MindSpore 的 TSC 会议是否对外公开？ | Run B + Run C 均采样 |

---

## 汇总统计

| | Run A（03-30） | Run B（04-17） | Run C（05-10） |
|--|:--------------:|:--------------:|:--------------:|
| 采样题数（含 P1） | 16 题 | 37 题 | 37 题 |
| 有官方链接题数 | 13 题 | 32 题 | 32 题 |
| DeepSeek 引用 ✅ | 0 / 13 | 14 / 32 | 16 / 32 |
| Qwen 引用 ✅ | 1 / 13 | 18 / 32 | 16 / 32 |
| 任一平台引用 | 1 题 | 24 题 | 25 题 |
| 无官方链接（P1） | 3 题 | 5 题 | 5 题 |
