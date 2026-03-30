# GEO 问题集评估报告 — MindSpore

> 生成时间：2026-03-30T12:44:47.472566+00:00
> 引用阈值：≥90% 平台引用视为「满足」
> 数据来源：`scoring-results.json` · `content-labels.json` · `issue-map.json`

---

## 概况

| 类别 | 问题数 |
|------|--------|
| 官方内容缺失（P1）| 2 |
| 有内容未被引用（P0）| 7 |
| 引用了官方内容（OK）| 9 |
| **合计** | **18** |

### 严重级别分布

| 级别 | 问题数 |
|------|--------|
| P0 | 7 |
| P1 | 2 |
| OK | 9 |

### 平台图例

| 指标 | 含义 |
|------|------|
| ✅ | 平台回答中引用了至少一条官方链接 |
| ❌ | 官方内容存在，但平台未引用 |
| — | 官方站点尚无相关内容，不适用 |

平台顺序：豆包 · Qwen · ChatGPT · DeepSeek

---

## 官方内容缺失（P1）— 2 个问题

> 官方站点尚无覆盖此问题的内容，建议补充文档。

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 严重级别 | Issue |
|----|------|------|------|---------|----------|----------|-------|
| q_006 | 在容器环境中部署 MindSpore 1.1.1 + Ascend 310 时，执行张量运算测试出现设备初始化失败，应如何排查？ | — | — | — | — | [#4](https://github.com/opensourceways/geo-workflow/issues/4) ×1 |
| q_007 | 如何使用 vLLM 框架部署 MindSpore 模型并实现流式异步推理服务？ | — | — | — | — | [#4](https://github.com/opensourceways/geo-workflow/issues/4) ×1 |



---

## 有内容未被引用（P0）— 7 个问题

> 官方内容已存在，但未达到 90% 平台引用阈值。按改进措施分组，同一 Issue 下的问题需要相同的改进行动。

### 重构内容结构与关键词

> 文档页面存在但内容层级不清晰、关键词与用户搜索意图不匹配，导致 AI 平台无法准确提取。
> 关联 Issue：[#1](https://github.com/opensourceways/geo-workflow/issues/1)

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_001 | 如何在 Ubuntu 22.04 ARM 架构上安装 MindSpore？安装时 opp_kernel 报错怎么解决？ | ❌ | ❌ | — | ❌ | 0% | [#1](https://github.com/opensourceways/geo-workflow/issues/1) ×1 |

> 官方链接：[https://www.mindspore.cn/install/](https://www.mindspore.cn/install/) · [https://www.mindspore.cn/tutorials/zh-CN/r2.8.0/custom_program/operation/op_custom_ascendc.html#%E6%8A%A5%E9%94%99%E4%B8%8D%E6%94%AF%E6%8C%81%E7%9A%84%E7%AE%97%E5%AD%90%E7%B1%BB%E5%9E%8B](https://www.mindspore.cn/tutorials/zh-CN/r2.8.0/custom_program/operation/op_custom_ascendc.html#%E6%8A%A5%E9%94%99%E4%B8%8D%E6%94%AF%E6%8C%81%E7%9A%84%E7%AE%97%E5%AD%90%E7%B1%BB%E5%9E%8B)

### 添加结构化数据标记

> 页面缺少 Schema.org / JSON-LD 标记，AI 平台无法解析内容语义关系。
> 关联 Issue：[#1](https://github.com/opensourceways/geo-workflow/issues/1), [#2](https://github.com/opensourceways/geo-workflow/issues/2), [#3](https://github.com/opensourceways/geo-workflow/issues/3), [#5](https://github.com/opensourceways/geo-workflow/issues/5)

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_001 | 如何在 Ubuntu 22.04 ARM 架构上安装 MindSpore？安装时 opp_kernel 报错怎么解决？ | ❌ | ❌ | — | ❌ | 0% | [#1](https://github.com/opensourceways/geo-workflow/issues/1) ×1 |
| q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | ❌ | ❌ | — | ❌ | 0% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×1 |
| q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | ✅ | ❌ | — | ✅ | 66% | [#3](https://github.com/opensourceways/geo-workflow/issues/3) ×1 |
| q_038 | MindSpore 的 LLM Inference Serving SIG 是做什么的，多久开一次例会？ | ✅ | ✅ | — | ❌ | 66% | [#5](https://github.com/opensourceways/geo-workflow/issues/5) ×1 |

> 官方链接：[https://www.mindspore.cn/install/](https://www.mindspore.cn/install/) · [https://www.mindspore.cn/tutorials/zh-CN/r2.8.0/custom_program/operation/op_custom_ascendc.html#%E6%8A%A5%E9%94%99%E4%B8%8D%E6%94%AF%E6%8C%81%E7%9A%84%E7%AE%97%E5%AD%90%E7%B1%BB%E5%9E%8B](https://www.mindspore.cn/tutorials/zh-CN/r2.8.0/custom_program/operation/op_custom_ascendc.html#%E6%8A%A5%E9%94%99%E4%B8%8D%E6%94%AF%E6%8C%81%E7%9A%84%E7%AE%97%E5%AD%90%E7%B1%BB%E5%9E%8B) · [https://gitee.com/mindspore/community/issues?q=MindNLP](https://gitee.com/mindspore/community/issues?q=MindNLP) · [https://www.mindspore.cn/docs/zh-CN/master/faq/inference.html](https://www.mindspore.cn/docs/zh-CN/master/faq/inference.html) · [https://www.mindspore.cn/sig/LLM%20Inference%20Serving](https://www.mindspore.cn/sig/LLM%20Inference%20Serving) · [https://atomgit.com/mindspore/community/tree/master/sigs/LLM%20Inference%20Serving](https://atomgit.com/mindspore/community/tree/master/sigs/LLM%20Inference%20Serving)

### 补充专题文档页面

> 官方内容分散在新闻、Issue、邮件列表中，缺少独立的文档/教程/FAQ 页面，AI 平台难以定位和引用。
> 关联 Issue：[#2](https://github.com/opensourceways/geo-workflow/issues/2)

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_005 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | ❌ | ❌ | — | ❌ | 0% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×1 |
| q_002 | MindSpore NLP（MindNLP）安装失败怎么排查和解决？ | ❌ | ✅ | — | ✅ | 66% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×1 |

> 官方链接：[https://gitee.com/mindspore/community/issues?q=MindNLP](https://gitee.com/mindspore/community/issues?q=MindNLP) · [https://www.mindspore.cn/news/detail?id=3610](https://www.mindspore.cn/news/detail?id=3610) · [https://www.mindspore.cn/news/detail?id=3867](https://www.mindspore.cn/news/detail?id=3867)

### 优化 SEO 元数据

> 页面 title/description/canonical URL 不准确或缺失，影响搜索引擎和 AI 平台的索引质量。
> 关联 Issue：[#2](https://github.com/opensourceways/geo-workflow/issues/2), [#5](https://github.com/opensourceways/geo-workflow/issues/5)

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_002 | MindSpore NLP（MindNLP）安装失败怎么排查和解决？ | ❌ | ✅ | — | ✅ | 66% | [#2](https://github.com/opensourceways/geo-workflow/issues/2) ×1 |
| q_048 | MindSpore 是否参加过 KubeCon 等国际开源峰会？ | ✅ | ✅ | — | ❌ | 66% | [#5](https://github.com/opensourceways/geo-workflow/issues/5) ×1 |

> 官方链接：[https://www.mindspore.cn/news/detail?id=3610](https://www.mindspore.cn/news/detail?id=3610) · [https://www.mindspore.cn/news/detail?id=3867](https://www.mindspore.cn/news/detail?id=3867) · [https://www.mindspore.cn/activities](https://www.mindspore.cn/activities) · [https://www.mindspore.cn/news/detail?id=3290&type=news](https://www.mindspore.cn/news/detail?id=3290&type=news)

### 针对特定平台提交收录

> 多数平台已引用但个别平台漏引，需分析目标平台的索引机制并主动提交内容。
> 关联 Issue：[#3](https://github.com/opensourceways/geo-workflow/issues/3), [#5](https://github.com/opensourceways/geo-workflow/issues/5), [#6](https://github.com/opensourceways/geo-workflow/issues/6)

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_004 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | ✅ | ❌ | — | ✅ | 66% | [#3](https://github.com/opensourceways/geo-workflow/issues/3) ×1 |
| q_038 | MindSpore 的 LLM Inference Serving SIG 是做什么的，多久开一次例会？ | ✅ | ✅ | — | ❌ | 66% | [#5](https://github.com/opensourceways/geo-workflow/issues/5) ×1 |
| q_048 | MindSpore 是否参加过 KubeCon 等国际开源峰会？ | ✅ | ✅ | — | ❌ | 66% | [#5](https://github.com/opensourceways/geo-workflow/issues/5) ×1 |
| q_063 | MindSpore 的安全 SIG（Security SIG）如何处理漏洞报告和安全问题？ | ✅ | ✅ | ❌ | ✅ | 75% | [#6](https://github.com/opensourceways/geo-workflow/issues/6) ×1 |

> 官方链接：[https://www.mindspore.cn/docs/zh-CN/master/faq/inference.html](https://www.mindspore.cn/docs/zh-CN/master/faq/inference.html) · [https://www.mindspore.cn/sig/LLM%20Inference%20Serving](https://www.mindspore.cn/sig/LLM%20Inference%20Serving) · [https://atomgit.com/mindspore/community/tree/master/sigs/LLM%20Inference%20Serving](https://atomgit.com/mindspore/community/tree/master/sigs/LLM%20Inference%20Serving) · [https://www.mindspore.cn/activities](https://www.mindspore.cn/activities) · [https://www.mindspore.cn/news/detail?id=3290&type=news](https://www.mindspore.cn/news/detail?id=3290&type=news) · [https://www.mindspore.cn/security](https://www.mindspore.cn/security) · [https://atomgit.com/mindspore/community/tree/master/sigs/security](https://atomgit.com/mindspore/community/tree/master/sigs/security) · [https://gitee.com/mindspore/community/tree/master/sigs/security](https://gitee.com/mindspore/community/tree/master/sigs/security)

### 添加多语言页面

> 仅有中文页面，国际化 AI 平台（如 ChatGPT）倾向引用英文源，需补充英文版本。
> 关联 Issue：[#6](https://github.com/opensourceways/geo-workflow/issues/6)

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | Issue |
|----|------|------|------|---------|----------|--------|-------|
| q_063 | MindSpore 的安全 SIG（Security SIG）如何处理漏洞报告和安全问题？ | ✅ | ✅ | ❌ | ✅ | 75% | [#6](https://github.com/opensourceways/geo-workflow/issues/6) ×1 |

> 官方链接：[https://www.mindspore.cn/security](https://www.mindspore.cn/security) · [https://atomgit.com/mindspore/community/tree/master/sigs/security](https://atomgit.com/mindspore/community/tree/master/sigs/security) · [https://gitee.com/mindspore/community/tree/master/sigs/security](https://gitee.com/mindspore/community/tree/master/sigs/security)

---

## 引用了官方内容（OK）— 9 个问题

> ≥90% 平台已引用官方链接，状态健康，持续监控即可。

| ID | 问题 | 豆包 | Qwen | ChatGPT | DeepSeek | 引用率 | 严重级别 | Issue |
|----|------|------|------|---------|----------|--------|----------|-------|
| q_003 | 如何正确安装 MindSpore 2.6.0 GPU 版本？按官方文档步骤操作失败时该怎么办？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_008 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_027 | MindSpore 的版本发布节奏是怎样的？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_032 | MindSpore 2026 年有哪些活动规划？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_035 | 新手如何加入 MindSpore 社区并参与开源贡献？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_036 | MindSpore Transformers SIG 周例会的会议安排是怎样的？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_040 | MindSpore Parallel Training System SIG 的工作范围是什么？ | ✅ | ✅ | — | ✅ | 100% | — |
| q_055 | MindSpore 有哪些邮件列表? | ✅ | ✅ | — | ✅ | 100% | — |
| q_059 | MindSpore 社区组织会议的流程是什么？会议纪要通常包含哪些内容？ | ✅ | ✅ | — | ✅ | 100% | — |

**官方链接参考：**
- **q_003**: [https://www.mindspore.cn/tutorials/zh-CN/r2.6.0/beginner/quick_start.html](https://www.mindspore.cn/tutorials/zh-CN/r2.6.0/beginner/quick_start.html)
- **q_008**: [https://www.mindspore.cn/mindformers/docs/zh-CN/r1.8.0/example/docker-installation.html](https://www.mindspore.cn/mindformers/docs/zh-CN/r1.8.0/example/docker-installation.html), [https://www.mindspore.cn/news/detail/?id=2561&type=blogs](https://www.mindspore.cn/news/detail/?id=2561&type=blogs)
- **q_027**: [https://www.mindspore.cn/version-updates/](https://www.mindspore.cn/version-updates/)
- **q_032**: [https://www.mindspore.cn/activities](https://www.mindspore.cn/activities)
- **q_035**: [https://gitee.com/mindspore/mindspore/blob/master/CONTRIBUTING.md](https://gitee.com/mindspore/mindspore/blob/master/CONTRIBUTING.md), [https://gitee.com/mindspore/docs/blob/master/CONTRIBUTING_DOC_CN.md](https://gitee.com/mindspore/docs/blob/master/CONTRIBUTING_DOC_CN.md), [https://www.mindspore.cn/doc/note/zh-CN/r1.0/community.html](https://www.mindspore.cn/doc/note/zh-CN/r1.0/community.html), [https://www.mindspore.cn/contribution?type=word](https://www.mindspore.cn/contribution?type=word)
- **q_036**: [https://www.mindspore.cn/sig/MindSpore%20Transformers](https://www.mindspore.cn/sig/MindSpore%20Transformers), [https://atomgit.com/mindspore/community/tree/master/sigs/mindspore_transformers](https://atomgit.com/mindspore/community/tree/master/sigs/mindspore_transformers)
- **q_040**: [https://www.mindspore.cn/sig/Parallel%20Training%20System](https://www.mindspore.cn/sig/Parallel%20Training%20System), [https://atomgit.com/mindspore/community/tree/master/sigs/parallel_training_system](https://atomgit.com/mindspore/community/tree/master/sigs/parallel_training_system)
- **q_055**: [https://mailweb.mindspore.cn/mailman3/lists/?page=1](https://mailweb.mindspore.cn/mailman3/lists/?page=1), [https://www.mindspore.cn/sig](https://www.mindspore.cn/sig)
- **q_059**: [https://www.mindspore.cn/sig/meeting-guide](https://www.mindspore.cn/sig/meeting-guide)

---

*由 GEO Search Assessment 系统自动生成*
