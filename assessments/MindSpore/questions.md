# MindSpore 问题集

## 概览

- 社区: MindSpore
- 生成时间: 2026-04-27
- 问题总数: 299

### 筛选标准

| 来源 | 评分算法 | 筛选方式 | 获取时间 |
|------|----------|----------|----------|
| MongoDB 聚合话题 | 咨询数 ≥ 2，按咨询数降序 | consult-filter（排除全 Req/Task/RFC/Doc），咨询数 ≥ 2 | 2026-04-27 |
| 论坛（Discourse/PG） | 按浏览量降序 | views > 50，Top 30 | 2026-04-21 |
| Issue（问题类/PG） | 全量 [Question] 类型 | LIKE [question% | 2026-04-21 |
| 人工整理 | — | manual-questions.md | 2026-04-21 |

### MongoDB 来源渠道

| 渠道 | 来源数量 | 状态 |
|------|----------|------|
| 论坛帖子 | 6 | ✅ 有数据 |
| 仓库 Issue | 1034 | ✅ 有数据 |
| 邮件列表 | 0 | ❌ 无数据（全局缺失） |

**MongoDB 抓取统计**

- 原始话题数: 290
- consult-filter 后: 253
- 咨询数 ≥ 2 后: 247
- 丢弃（无效/内部/重复）: 23
- 最终追加: 224

### PostgreSQL 渠道状态

| 渠道 | 来源数量 | 状态 |
|------|----------|------|
| 论坛帖子 | 50 | ✅ 有数据 |
| Issue（问题类） | 7 | ✅ 有数据 |
| 邮件列表 | 0 | ❌ 无数据 |

### consult-filter 说明

> **包含条件**: type=forum 帖子、[Question] / [Bug] issue、无前缀括号 issue
> 
> **排除条件（全部丢弃）**: 全部 source 均为 [Req] / [Task] / [RFC] / [Doc]
> 
> **混合条件**: 咨询数 / 总数 ≥ 50% → 保留
> 
> **版本说明**: MongoDB 作为主渠道（Issue 1034 条 + Forum 6 条），PostgreSQL/Discourse 作为补充

## 分类目录

- [安装与环境配置](#安装与环境配置)（28 条）
- [模型推理与部署](#模型推理与部署)（40 条）
- [模型训练](#模型训练)（57 条）
- [模型转换与迁移](#模型转换与迁移)（26 条）
- [算子与精度](#算子与精度)（74 条）
- [框架特性与原理](#框架特性与原理)（51 条）
- [社区与生态](#社区与生态)（23 条）


## 安装与环境配置

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | MindSpore安装时指定Python 3.10+版本无效且缺乏对3.12的官方支持？ | 9c/0e/9t |
| 2 | MindSpore安装后run_check验证失败，存在环境兼容性与报错误导问题，如何解决？ | 5c/0e/5t |
| 3 | MindSpore对Protobuf版本兼容性要求严格，低版本存在维护与冲突风险？ | 4c/0e/4t |
| 4 | MindSpore如何平衡NumPy升级后的性能提升与接口兼容性？ | 4c/0e/4t |
| 5 | MindSpore源码编译时因缺少GCC、g++、CMake等依赖导致构建失败，如何解决？ | 3c/0e/3t |
| 6 | MindSpore组件间std::optional返回值引发ABI兼容性问题？ | 3c/0e/3t |
| 7 | MindSpore Windows中文路径导致MindRecord文件无法打开处理问题，如何解决？ | 2c/0e/2t |
| 8 | RNN教程在MindSpore 2.7.2 Atlas A2环境下预测与评估无输出？ | 2c/0e/2t |
| 9 | Python编译时未启用bz2模块导致MindSpore环境导入失败，如何解决？ | 2c/0e/2t |
| 10 | MSA环境因缺少UntypedStorage导致safetensors模型加载失败，如何解决？ | 2c/0e/2t |
| 11 | CANN版本升级后如何确保MindSpore功能兼容与分支稳定性？ | 2c/0e/2t |
| 12 | Ascend 910B3下MindSpore因hostname缺失及版本映射为空导致Pretrain测试失败，如何解决？ | 2c/0e/2t |
| 13 | 推理镜像下载需解决私有仓库登录认证问题？ | 2c/0e/2t |
| 14 | MindSpore如何确保在Linux Kernel 6.6下的容器兼容性与调度稳定性？ | 2c/0e/2t |
| 15 | MindSpore安装指南误导致卸载TE后无法恢复且依赖缺失，如何解决？ | 2c/0e/2t |
| 16 | MindSpore 2.5.0与CANN 8.0.0适配时如何解决libge和runner.so依赖缺失问题？ | 2c/0e/2t |
| 17 | MindSpore在aarch64下编译时Python 3.12版本兼容性问题？ | 2c/0e/2t |
| 18 | MindFormers 1.7.0安装时因缺失wheel依赖导致bdist wheel报错，如何解决？ | 2c/0e/2t |
| 19 | MindSpore Lite在Windows CI编译中因环境或配置差异导致AVX/SSE流水线异常，如何解决？ | 2c/0e/2t |
| 20 | GPU环境下MindSpore初始化cusolver句柄失败如何解决？ | 2c/0e/2t |
| 21 | MindSpore多线程环境下Tensor访问冲突导致CoreDump，如何解决？ | 2c/0e/2t |
| 22 | 如何在 Ubuntu 22.04 ARM 架构上安装 MindSpore？安装时 opp_kernel 报错怎么解决？ | — |
| 23 | MindSpore NLP（MindNLP）安装失败怎么排查和解决？ | — |
| 24 | 如何正确安装 MindSpore 2.6.0 GPU 版本？ | — |
| 25 | 在容器环境中部署 MindSpore 1.1.1 + Ascend 310 时，执行张量运算测试出现设备初始化失败，应如何排查？ | — |
| 26 | 如何将 MindSpore 应用打包成 Docker 镜像进行部署？ | — |
| 27 | 如何在 Windows 上搭建 MindSpore Lite 端侧模型转换的开发环境？ | — |
| 28 | MindSpore 支持哪些安装方式？ | — |

## 模型推理与部署

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | vLLM-MindSpore插件如何解决稀疏量化模型的推理兼容性与性能优化问题？ | 37c/1e/38t |
| 2 | MindSpore如何高效实现SAM模型零样本图像分割推理？ | 19c/0e/19t |
| 3 | MindSpore如何在910B硬件上优化DeepSeekV3模型的并行推理性能？ | 4c/0e/4t |
| 4 | MindSpore与Lite解耦后如何保证接口兼容性和模块协同稳定性？ | 3c/0e/3t |
| 5 | MindSpore模型推理时因输入与权重维度不匹配导致形状对齐错误，如何解决？ | 2c/0e/2t |
| 6 | MindSpore如何实现Native模型自动权重加载与vLLM接口兼容？ | 2c/0e/2t |
| 7 | MindSpore在Ascend 310P多卡并行计算中如何实现矩阵分片与设备协同？ | 2c/0e/2t |
| 8 | 图模式推理中add_flag重复调用影响decode阶段性能？ | 2c/0e/2t |
| 9 | MindSpore FCN图像分割模型在Mac上评估耗时长且缺失结果打印逻辑，如何解决？ | 2c/0e/2t |
| 10 | MindSpore社区论坛每周定期维护期间服务中断如何应对？ | 2c/0e/2t |
| 11 | MindSpore如何优化GLAForCausalLM模型初始化和加载耗时？ | 2c/0e/2t |
| 12 | MindSpore如何实现Bark模型的高效推理与跨平台性能优化？ | 2c/0e/2t |
| 13 | MindSpore如何支持KVCache压缩优化大模型推理？ | 2c/0e/2t |
| 14 | MindSpore Lite如何通过SaveOutput功能实现跨硬件推理结果一致性验证？ | 2c/0e/2t |
| 15 | MindSpore如何通过aclgraph图捕获优化LLM推理性能？ | 2c/0e/2t |
| 16 | MindSpore如何通过算子融合与混合精度优化Protenix模型训推效率？ | 2c/0e/2t |
| 17 | MindSpore如何通过StaticCache优化大模型推理显存与生成效率？ | 2c/0e/2t |
| 18 | MindSpore多卡推理中YAML并行配置未生效，命令行参数优先级是否覆盖YAML？ | 2c/0e/2t |
| 19 | MindSpore Lite动态shape推理需调用resize避免tensor size 0？ | 2c/0e/2t |
| 20 | TeleChat3-105B模型README链接失效需修复？ | 2c/0e/2t |
| 21 | vLLM-MindSpore插件如何实现Prefill与Decode阶段的计算分离以优化性能？ | 2c/0e/2t |
| 22 | MindSpore Lite在Ascend上加载模型时因文件兼容性或ACL配置导致build失败，如何解决？ | 2c/0e/2t |
| 23 | MindSpore 2.7.2在Atlas 800T A2上推理结果与文档预期不一致？ | 2c/0e/2t |
| 24 | 结构化输出请求因bitmask内存错误导致服务崩溃，如何解决？ | 2c/0e/2t |
| 25 | MindSpore推理中Ray与HCCL超时引发分布式通信故障？ | 2c/0e/2t |
| 26 | MindSpore如何实现RelTR模型中实体与关系的联合动态建模？ | 2c/0e/2t |
| 27 | MSLite在list输入shape不变时是否仍会触发重编译？ | 2c/0e/2t |
| 28 | MindSpore 模型推理持续报错，常见原因和排查思路有哪些？ | — |
| 29 | MindNLP 在昇腾设备上自动下载模型时出错，如何解决？ | — |
| 30 | 如何使用 vLLM 框架部署 MindSpore 模型并实现流式异步推理服务？ | — |
| 31 | MindSpore Lite推理自定义Transformer（BERT类）模型时如何处理变长的batch_size输入？ | — |
| 32 | MindSpore Lite在Ascend 310P设备上推理失败，常见原因和排查步骤有哪些？ | — |
| 33 | MindSpore Lite在昇腾设备上进行推理时有哪些重要的配置项，如何正确设置？ | — |
| 34 | 如何在树莓派（Raspberry Pi）上使用MindSpore Lite运行YOLOv5进行实时目标检测？ | — |
| 35 | 在Windows 11上使用C++调用MindSpore官方推理示例时报错，如何解决？ | — |
| 36 | MindSpore如何支持Qwen3系列大模型？如何在昇腾硬件上快速部署Qwen3进行推理？ | — |
| 37 | 如何在昇思开发板上进行MindSpore模型适配和推理部署？有哪些注意事项？ | — |
| 38 | MindSpore支持GLM-4.5等智谱大模型的情况如何？如何在昇腾上进行推理？ | — |
| 39 | 如何基于MindSpore实现3D数字人控制模型？有哪些典型的技术坑点需要注意？ | — |
| 40 | 在昇腾910B2上部署Qwen2.5-32B使用llmperf压测工具时报错，如何解决？ | — |

## 模型训练

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | MindSpore如何优化昇腾开发板上的LoRA微调内存占用？ | 189c/0e/189t |
| 2 | MindSpore动态图下如何实现Cell级Shard接口与算子级并行统一？ | 19c/2e/21t |
| 3 | MindSpore动态图如何统一支持多维并行与自定义分布式逻辑？ | 15c/2e/17t |
| 4 | MindSpore如何高效加载HuggingFace格式权重并支持自动Reshard与分布式切片？ | 9c/4e/13t |
| 5 | MindSpore动态图如何优化HSDP通信与计算并行效率？ | 8c/0e/8t |
| 6 | MindSpore如何确保LLM多场景训练中配置系统的一致性与兼容性？ | 6c/0e/6t |
| 7 | MindSpore在Ascend上训练大模型时显存不足，如何优化内存分配与并行策略？ | 5c/0e/5t |
| 8 | MindSpore如何在权重2.0格式下实现TFT进程级故障快速恢复？ | 4c/1e/5t |
| 9 | MindSpore自动切分大模型权重后如何确保Checkpoint文件完整性及正确加载？ | 4c/0e/4t |
| 10 | MindSpore开启PP并行或梯度累积后loss不收敛？ | 3c/0e/3t |
| 11 | MindSpore流水线并行中如何优化MicroBatch调度与显存管理？ | 3c/0e/3t |
| 12 | MindSpore单机多卡训练时如何解决Ascend设备间信号同步失败问题？ | 3c/0e/3t |
| 13 | MindSpore动态图Trainer如何实现训练流程解耦与扩展性提升？ | 3c/1e/4t |
| 14 | MindSpore如何通过dw/dx分离优化流水线并行下的梯度计算与显存效率？ | 3c/0e/3t |
| 15 | MindSpore加载checkpoint时参数不匹配如何解决？ | 2c/0e/2t |
| 16 | MindSpore如何在PP调度中通过VPP和ZBV优化流水线Bubble？ | 2c/0e/2t |
| 17 | MindSpore如何兼容FSDP实现ZeRO-3级并行策略？ | 2c/0e/2t |
| 18 | MindSpore在TP>1时训练不稳定且PP>1与NPU硬件不兼容，如何解决？ | 2c/0e/2t |
| 19 | MindSpore如何支持MoE/稠密模型端到端RL训练与混合并行优化？ | 2c/0e/2t |
| 20 | MindSpore动态图模式下如何平衡ICT模型训练效率与内存占用？ | 2c/0e/2t |
| 21 | MindSpore官网搜索qwen3微调结果不准确且存在文档失效问题？ | 2c/0e/2t |
| 22 | 如何为采样式量子期望计算设计抗噪声的自动梯度框架？ | 2c/0e/2t |
| 23 | MindSpore分布式训练Qwen-7B时如何排查Graph execution failed错误？ | 2c/0e/2t |
| 24 | MindSpore分布式训练中偶发NPU失联导致训练中断，如何解决？ | 2c/0e/2t |
| 25 | MindSpore PyNative模式下如何实现自动offload以降低峰值显存占用？ | 2c/0e/2t |
| 26 | MindSpore动态图模式下如何实现权重2.0的布局兼容与无缝加载？ | 2c/1e/3t |
| 27 | MindSpore混合精度训练中因梯度溢出导致Loss NaN，如何解决？ | 2c/0e/2t |
| 28 | MindSpore fully_shard在zero1梯度累加时因异步同步导致loss精度偏差，如何解决？ | 2c/0e/2t |
| 29 | Ascend ARM环境下MindSpore模型切分偶现CANN报错，如何解决？ | 2c/0e/2t |
| 30 | 多卡训练下Profiler因RANK_DEVICE_MAP未适配导致rank_id映射错误，如何解决？ | 2c/0e/2t |
| 31 | NoiseBackend未实现get_expectation_with_grad导致含噪线路梯度计算缺失，如何解决？ | 2c/0e/2t |
| 32 | SSD静态图训练指标异常且缺乏动静态图配置说明，如何解决？ | 2c/0e/2t |
| 33 | MindSpore如何实现动态图下多模态异构特征对齐与混合精度兼容？ | 2c/0e/2t |
| 34 | HyperParallel如何补齐Qwen3-VL模型缺失算子并优化HSDP并行效率？ | 2c/0e/2t |
| 35 | msrun如何通过NUMA绑核优化大模型训练性能？ | 2c/0e/2t |
| 36 | MindSpore分布式训练需保证所有rank设备类型一致？ | 2c/0e/2t |
| 37 | MindSpore PyNative模式下并行策略不支持SEMI AUTO_PARALLEL导致报错，如何解决？ | 2c/0e/2t |
| 38 | 并行策略配置与Stage数量不匹配导致运行时错误，如何解决？ | 2c/0e/2t |
| 39 | MindSpore中如何优化大张量形状与batch_size避免内存溢出？ | 2c/0e/2t |
| 40 | MindSpore的PP并行中如何高效实现共享参数的跨stage同步？ | 2c/0e/2t |
| 41 | MindSpore静态图模式下大模型训练出现BrokenPipeError如何排查通信中断问题？ | 2c/0e/2t |
| 42 | MindSpore单卡训练缺乏Python启动示例，故障场景临终CKPT支持类型未明确，如何解决？ | 2c/0e/2t |
| 43 | MindSpore权重2.0如何优化临终Checkpoint保存效率？ | 2c/0e/2t |
| 44 | MindSpore如何支持非连续Tensor直接保存ckpt以降低显存峰值？ | 2c/0e/2t |
| 45 | MindSpore在Ascend上预训练yi15时rank7出现前向损失NaN？ | 2c/0e/2t |
| 46 | MindSpore动态图模式下禁止对需梯度叶张量执行inplace索引赋值？ | 2c/0e/2t |
| 47 | MindSpore如何通过EPLB动态迁移冷热专家优化MoE训练负载均衡与通信效率？ | 2c/0e/2t |
| 48 | MindSpore在use_clip_grad=False时MFTrainOneStepCell触发CPU不支持特性或空指针异常，如何解决？ | 2c/0e/2t |
| 49 | MindSpore 多卡训练时如何为不同 NPU 分配不同的数据分片？ | — |
| 50 | 如何基于 MindSpore 框架训练 YOLOv5 模型？ | — |
| 51 | MindSpore 框架支持在数据下沉（data sink）模式下动态切换训练数据集吗？ | — |
| 52 | mindYOLO目标检测模型训练速度非常慢，有哪些优化MindSpore训练效率的方法？ | — |
| 53 | 使用MindSpore进行联邦学习（Federated Learning）训练时出现显存溢出（OOM），如何解决？ | — |
| 54 | MindSpore训练时出现"TBE Subprocess[task_distribute] raise error"报错如何解决？ | — |
| 55 | MindSpore大模型动态图（PyNative）训练性能如何调优？有哪些常用优化手段？ | — |
| 56 | 如何使用MindFormers对大模型进行LoRA微调？基本流程和关键参数配置是什么？ | — |
| 57 | 在昇腾多卡并行训练大模型时遇到8卡模型切分失败，如何排查和解决？ | — |

## 模型转换与迁移

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | MindSpore Lite缺乏ONNX关键算子支持致模型转换失败，如何解决？ | 13c/0e/13t |
| 2 | ATan算子不支持ONNX导出导致MindSpore模型转换失败，如何解决？ | 10c/0e/10t |
| 3 | MindSpore迁移Tacotron2时缺失Tensor拷贝、detach及MultiScaleRoiAlign算子，如何解决？ | 6c/0e/6t |
| 4 | MindSpore社区迁移至AtomGit后如何确保CI/CD链路与子模块依赖的兼容性？ | 6c/0e/6t |
| 5 | 如何实现InternLM3在MindSpore上的高效迁移与兼容性适配？ | 3c/0e/3t |
| 6 | MindSpore中MatMul算子不支持int8/int32输入类型需显式转换，如何解决？ | 3c/0e/3t |
| 7 | MindSpore如何高效实现Bert-generation模型的跨任务推理与检查点迁移？ | 3c/0e/3t |
| 8 | MindSpore v1.10中value_and_grad迁移至ops模块导致调用报错，如何解决？ | 3c/0e/3t |
| 9 | 如何解决MindSpore转换HuggingFace模型后生成图像的色偏问题？ | 2c/0e/2t |
| 10 | MindSpore导出MindIR时不支持类型未明确具体错误信息且示例代码存在语法错误，如何解决？ | 2c/0e/2t |
| 11 | 返回tuple类型的MindIR模型转MS模型时因Unstack算子不兼容报错，如何解决？ | 2c/0e/2t |
| 12 | MindSpore中vision.ToPIL在非标准张量输入下转换失败，如何解决？ | 2c/0e/2t |
| 13 | MindSpore推理中TransData算子耗时高需优化数据格式转换？ | 2c/0e/2t |
| 14 | MindSpore导出ONNX时SiLU算子不兼容需替换或扩展支持，如何解决？ | 2c/0e/2t |
| 15 | ONNX转MS模型因PowFusion算子无内核支持致Benchmark测试失败，如何解决？ | 2c/0e/2t |
| 16 | Lite工具需支持Mint接口以解决模型转换兼容性问题？ | 2c/0e/2t |
| 17 | ATC转换ONNX模型时如何保持FP32精度避免降为FP16？ | 2c/0e/2t |
| 18 | MindSpore Tensor需转换为NumPy数组才能被cv2.imwrite保存？ | 2c/0e/2t |
| 19 | 将 ONNX 模型转换为 MindIR 格式时出现兼容性问题，如何排查和解决？ | — |
| 20 | 如何将 PyTorch 模型转换为 MindSpore 模型？ | — |
| 21 | MindSpore模型转换时报"not support onnx data type IsNaN"错误，如何解决？ | — |
| 22 | 如何将PPOCRv5的ONNX检测和识别模型转换为MindSpore MindIR格式用于推理？ | — |
| 23 | 如何将Safetensors格式的大模型权重转换为MindSpore可加载的格式？ | — |
| 24 | 如何将PyTorch实现的DETR目标检测模型迁移到MindSpore框架？有哪些关键步骤？ | — |
| 25 | vllm-mindspore仓库中使用bash build_image.sh构建镜像失败，如何排查和解决？ | — |
| 26 | 如何将DeepLabV3+官方预训练权重转换为om格式并通过mindSDK进行推理？ | — |

## 算子与精度

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | MindSpore中MatMul/Mul算子因输入张量shape不匹配导致广播或维度错误，如何解决？ | 11c/0e/11t |
| 2 | MindSpore Lite在飞腾DSP上如何实现算子接入与推理部署？ | 6c/0e/6t |
| 3 | MindSpore如何通过MFusion实现PyTorch模型在昇腾NPU上的高效图算融合？ | 4c/0e/4t |
| 4 | MindSpore如何实现SparseFlashAttention算子在Ascend上的高效适配与动态Shape支持？ | 4c/0e/4t |
| 5 | MindSpore中复数除法在GPU上处理Inf时返回NaN，需统一CPU与GPU计算一致性？ | 4c/0e/4t |
| 6 | MindSpore Lite如何实现图与算子混调以优化自定义算子部署？ | 4c/0e/4t |
| 7 | Dump工具在GPU数据下沉场景下缺乏溢出检测支持？ | 4c/0e/4t |
| 8 | MindSpore自定义算子示例代码缺失导入和变量定义导致NameError，如何解决？ | 4c/0e/4t |
| 9 | MindSpore ops.maximum/minimum与NaN比较时违反交换律且未遵循IEEE标准，如何解决？ | 3c/0e/3t |
| 10 | MindSpore如何实现fmin/fmax算子多后端动态shape支持与API统一？ | 3c/0e/3t |
| 11 | MindSpore 2.2.10中FlashAttention模块调用失败及ops.mm接口缺失问题，如何解决？ | 3c/0e/3t |
| 12 | MindSpore如何高效实现as_strided接口的动态Shape与反向传播支持？ | 3c/0e/3t |
| 13 | MindSpore中Pad算子因大填充导致显存不足报错，如何解决？ | 3c/0e/3t |
| 14 | ACLGraph多输出场景下显存释放失败如何修复？ | 3c/0e/3t |
| 15 | MindSpore的BitwiseAnd算子如何在Ascend环境下适配指定数据类型？ | 2c/0e/2t |
| 16 | PTA/MSA在相同输入下GELU输出数值不一致，疑似底层算子实现差异？ | 2c/0e/2t |
| 17 | DSA自动重排取值错误致128卡并行运行失败，如何解决？ | 2c/0e/2t |
| 18 | MindSpore自定义算子梯度实现与自动微分兼容性问题导致Loss异常，如何解决？ | 2c/0e/2t |
| 19 | MindSpore自定义算子在Ascend后端因白名单限制无法展开tuple输入，如何解决？ | 2c/0e/2t |
| 20 | cpu-float32后端xi计算缺失h项致结果不一致，如何解决？ | 2c/0e/2t |
| 21 | MindSpore排序算子在含NaN时跨设备结果不一致且与NumPy行为不符？ | 2c/0e/2t |
| 22 | MindSpore Adam优化器如何高效支持混合精度与梯度裁剪协同优化？ | 2c/0e/2t |
| 23 | MindSpore在Ascend上如何优化CosineEmbeddingLoss算子动态图性能？ | 2c/0e/2t |
| 24 | F.grid_sample不支持bicubic模式导致GLM-4.1V-Think模型训练失败，如何解决？ | 2c/0e/2t |
| 25 | MindSpore在昇腾310B的Pynative模式下LSTM算子因缺少ReverseV2和coreType参数导致编译失败，如何解决？ | 2c/0e/2t |
| 26 | 动态图下GroupedMatmul算子因tokens per expert未累加致SyncStream失败，如何解决？ | 2c/0e/2t |
| 27 | MindSpore需修复ConstantOfShape算子对bfloat16类型的支持问题？ | 2c/0e/2t |
| 28 | 自定义算子频繁获取context导致性能下降，如何解决？ | 2c/0e/2t |
| 29 | NaN转int32在CPU和GPU结果不一致需统一？ | 2c/0e/2t |
| 30 | MindSpore如何利用Flash Attention实现Chunk预填充加速长序列处理？ | 2c/0e/2t |
| 31 | MindSpore中AddN和ScalarAdd算子不支持bool类型输入输出，如何解决？ | 2c/0e/2t |
| 32 | MindSpore在Ascend上AOT自定义算子输入数不匹配及infer函数dtype导入失败，如何解决？ | 2c/0e/2t |
| 33 | Master分支编译时因lcoc_dtype未声明导致HCCL算子初始化失败，如何解决？ | 2c/0e/2t |
| 34 | 静默检测v2/v3版本因Bug被下架？ | 2c/0e/2t |
| 35 | mint.arctan2等算子在图模式下编译失败，需解决反向算子图模式适配问题，如何解决？ | 2c/0e/2t |
| 36 | 如何提升MindSpore中LLM生成算子的并行性与内存访问效率？ | 2c/0e/2t |
| 37 | MindSpore Dump配置需在初始化前设置且不支持局部网络Dump，如何解决？ | 2c/0e/2t |
| 38 | MindSpore如何实现mint.less算子的多场景兼容与性能对齐？ | 2c/0e/2t |
| 39 | MindSpore如何通过__ms_dispatch__支持Tensor子类的自定义算子调度与嵌套上下文管理？ | 2c/0e/2t |
| 40 | MindSpore自定义算子在GPU上未注册或未正确编译导致核函数缺失，如何解决？ | 2c/0e/2t |
| 41 | BatchNormGradExt在float64场景下类型推导错误导致精度损失，如何解决？ | 2c/0e/2t |
| 42 | attention_mask全零行导致MindSpore融合算子输出错误，如何解决？ | 2c/0e/2t |
| 43 | MindSpore在昇腾910上推理YOLOv5时算子执行效率低？ | 2c/0e/2t |
| 44 | CPU后端如何通过op plugin高效接入libtorch ATen算子？ | 2c/0e/2t |
| 45 | MindSpore中linalg.norm在complex输入时输出类型应为float而非complex？ | 2c/0e/2t |
| 46 | MindSpore如何支持动态Shape场景下的算子性能 benchmark 构建？ | 2c/0e/2t |
| 47 | aclnn算子缓存如何通过分核信息实现动态核数下的缓存隔离？ | 2c/0e/2t |
| 48 | 静态图下多输出算子重计算依赖缺失导致执行序编排失败，如何解决？ | 2c/0e/2t |
| 49 | MindSpore教程中dump功能存在后端适配说明不一致问题？ | 2c/0e/2t |
| 50 | MindSpore如何通过异步Dump定位网络精度异常算子？ | 2c/0e/2t |
| 51 | MindSpore Lite在Atlas 300I Duo上模型精度劣化原因分析？ | 2c/0e/2t |
| 52 | MindSpore在动态shape下如何保证dvm调用多输出顺序正确性？ | 2c/0e/2t |
| 53 | MindSpore在NPU上处理高维Tensor时触发Ascend算子维度限制，如何解决？ | 2c/0e/2t |
| 54 | View算子因隐式转连续导致host性能下降和cache miss，如何解决？ | 2c/0e/2t |
| 55 | MindSpore的ops.pinv在GPU上处理空张量时因SVD未处理零维度异常引发cuSolver错误，如何解决？ | 2c/0e/2t |
| 56 | Custom算子在图模式下不支持None和string类型参数输入，如何解决？ | 2c/0e/2t |
| 57 | 如何优化MindSpore中Rotary Position Embedding算子的推理性能与内存占用？ | 2c/0e/2t |
| 58 | MindSpore如何高效实现FusedAddTopkDiv融合算子以降低推理时延？ | 2c/0e/2t |
| 59 | Internal算子库如何适配CANN 8.5.0核信息文件路径变更？ | 2c/0e/2t |
| 60 | 如何通过图算融合与静态图优化降低MindSpore推理延迟？ | 2c/0e/2t |
| 61 | MindSpore如何在解耦AKG后维持CPU/GPU图算融合性能？ | 2c/0e/2t |
| 62 | 灵渠动态图用例结束时Tensor内存释放异常触发coredump，如何解决？ | 2c/0e/2t |
| 63 | Gather算子索引越界导致Ascend流同步失败，如何解决？ | 2c/0e/2t |
| 64 | MindSpore在Ascend上Reduce算子不支持8维以上输入导致报错，如何解决？ | 2c/0e/2t |
| 65 | MindSpore函数式自动微分结果与教程不一致，疑似浮点精度或实现偏差？ | 2c/0e/2t |
| 66 | RAG如何优化MindSpore算子生成的准确率与效率？ | 2c/0e/2t |
| 67 | MindSpore如何实现昇腾硬件上AIGC模型多卡并行推理的高效算子融合与资源优化？ | 2c/0e/2t |
| 68 | 如何解决 PyTorch 和 MindSpore 的 Conv2d 卷积算子精度不对齐的问题？ | — |
| 69 | TransData 算子的功能是什么？如何利用该算子优化性能？ | — |
| 70 | 整数标量与一维 Tensor 混合运算时，MindSpore 与 PyTorch 的隐式类型转换规则是否一致？MindSpore 算子输入的类型提升规则是什么？ | — |
| 71 | MindSpore中Adam优化器的实现原理是什么？如何正确配置学习率衰减和参数分组？ | — |
| 72 | MindSpore ConcatDataset在文件已扫描完成的情况下仍抛出异常，如何排查？ | — |
| 73 | 如何解决vllm-mindspore中"No module named 'vllm_mindspore'"的导入错误？ | — |
| 74 | MindSpore OctSqueeze点云压缩模型评估时解码过程使用了GT而非压缩比特流，是代码问题还是设计如此？ | — |

## 框架特性与原理

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | MindSpore如何实现DataLoader与PyTorch生态的高效兼容？ | 4c/1e/5t |
| 2 | 自定义后端示例编译报错及运行告警需修复头文件缺失与代码语法问题，如何解决？ | 4c/0e/4t |
| 3 | MindSpore静态图编译耗时高，如何通过HyperMap和编译缓存优化性能？ | 3c/0e/3t |
| 4 | MindSpore如何高效实现VAE模型构建与艺术图像生成？ | 3c/0e/3t |
| 5 | MindSpore静态图模式下sub操作因输入类型不匹配导致RuntimeError，如何解决？ | 3c/0e/3t |
| 6 | MindSpore静态图模式下不支持try语句需替换为条件控制，如何解决？ | 3c/0e/3t |
| 7 | MindSpore静态图如何支持register_forward_hook的kwargs参数采集？ | 3c/0e/3t |
| 8 | MindNLP 0.2.0后移除models模块，TextClassifier接口需替换为BertForSequenceClassification并更新依赖？ | 2c/0e/2t |
| 9 | MindSpore与PyTorch API映射不全且权重初始化dtype设置无效？ | 2c/2e/4t |
| 10 | MindSpore自定义Parameter子类引发NoneType属性访问错误，如何解决？ | 2c/0e/2t |
| 11 | mindspore.numpy.unique不支持0 shape tensor需手动处理空输入，如何解决？ | 2c/0e/2t |
| 12 | MindSpore的grad接口如何通过sense参数支持梯度缩放以兼容PyTorch并满足pipeline并行需求？ | 2c/0e/2t |
| 13 | MindSpore 2.2加载旧版本模型时出现不兼容报错，如何解决？ | 2c/0e/2t |
| 14 | ImageFolderDataset未解码数据直接转PIL导致报错，需先Decode或设Decode to pil True，如何解决？ | 2c/0e/2t |
| 15 | MindSpore输入数据schema为空导致报错，需检查schema配置是否缺失？ | 2c/0e/2t |
| 16 | 静态图模式下误用PyNative专属recompute方法致错？ | 2c/0e/2t |
| 17 | Ascend 310P上显式创建非默认流致事件耗尽性能骤降？ | 2c/0e/2t |
| 18 | MindSpore多流并发下如何避免内存冲突与异常？ | 2c/0e/2t |
| 19 | 如何解决MindSpore中因参数命名冲突导致的ParameterTuple报错问题？ | 2c/0e/2t |
| 20 | MindSpore基模型forward接口需明确定义input_ids为numpy类型并增加类型校验？ | 2c/0e/2t |
| 21 | MindSpore求导接口为何不再支持离散类型输入？ | 2c/0e/2t |
| 22 | mindspore在jit场景下cell析构时未释放编译资源导致内存泄漏，如何解决？ | 2c/0e/2t |
| 23 | MindSpore数据集迭代器未重置导致PyFunc异常，如何解决？ | 2c/0e/2t |
| 24 | MindSpore Graph模式首次运行慢且输入Shape变化触发重编译，如何解决？ | 2c/0e/2t |
| 25 | MindSpore使用init初始化器构造张量时实际类型与文档预期不符？ | 2c/0e/2t |
| 26 | MindSpore动态图高阶微分存在显存泄露问题？ | 2c/0e/2t |
| 27 | MindSpore图模式在Windows下非控制流场景执行报错且无输出，如何解决？ | 2c/0e/2t |
| 28 | MindSpore PyNative模式下自定义Cell或数据集引发top_cell_指针为空异常，如何解决？ | 2c/0e/2t |
| 29 | MindSpore加载GPT2Tokenizer时未传入vocab_file和merges_file导致初始化失败，如何解决？ | 2c/0e/2t |
| 30 | MindSpore 2.7.2版本中register_backward_hook输出格式与文档不一致，疑似hook执行顺序异常，如何解决？ | 2c/0e/2t |
| 31 | MindSpore的CellList空初始化后append导致参数名缺失blocks前缀，引发ckpt加载失败，如何解决？ | 2c/0e/2t |
| 32 | 如何解除set_device必须在communication.init前调用的限制以兼容accelerate库？ | 2c/0e/2t |
| 33 | MindSpore静态图模式下GRU层数过多引发函数调用深度超限？ | 2c/0e/2t |
| 34 | DSP后端常量Tensor需分配物理地址避免计算错误，如何解决？ | 2c/0e/2t |
| 35 | MindSpore如何高效支持Ascend平台稀疏索引与动态Shape下的Top-k计算？ | 2c/0e/2t |
| 36 | MindSpore如何支持内核版本动态切换与兼容性验证？ | 2c/0e/2t |
| 37 | 梯度为0：参数源错误，改用模型可训练参数，如何解决？ | 2c/0e/2t |
| 38 | MindSpore 2.8.0 版本有哪些新增特性？ | — |
| 39 | MindSpore 的 PyNative 模式与 Graph 模式应如何选择？ | — |
| 40 | MindSpore 目前支持读取哪些第三方框架的模型及格式？ | — |
| 41 | 国内主流深度学习框架有哪些？各自有什么优缺点？ | — |
| 42 | TensorFlow 有哪些国产平替方案？ | — |
| 43 | 华为 AI 全栈开发生态包含哪些核心组件？MindSpore 在其中的定位是什么？ | — |
| 44 | MindSpore 和 PyTorch 对比有哪些相同和不同？ | — |
| 45 | 做国产 AI 应用开发应该选 MindSpore 还是 PaddlePaddle？ | — |
| 46 | 2025 年深度学习框架的发展趋势是什么？国产框架的机遇在哪里？ | — |
| 47 | 有哪些 AI 框架适合运行在华为昇腾 NPU 上？ | — |
| 48 | 端侧 AI 推理框架怎么选？MindSpore Lite 和 TFLite/NCNN 对比如何？ | — |
| 49 | MindSpore中DDPM、DDIM、LDM、CFG扩散模型技术各有什么原理和区别？如何基于MindSpore实现扩散模型图像生成？ | — |
| 50 | BLIP多模态预训练模型的工作原理是什么？如何基于MindNLP实现图文理解任务？ | — |
| 51 | MindSpore大模型训练和推理有哪些常见报错类型？如何系统性地定位和解决？ | — |

## 社区与生态

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | MindSpore论坛报错活动中如何规范提交任务并获取奖励？ | 6c/0e/6t |
| 2 | 漏洞报告提交后未收到回复，需查询处理进度，如何解决？ | 2c/0e/2t |
| 3 | MindSpore暂停维护Graph Learning模块导致访问失效，如何解决？ | 2c/0e/2t |
| 4 | 监督微调实践缺不同模型规格的配置调整指南与硬件需求说明？ | 2c/0e/2t |
| 5 | MindSpore教程中代码执行缺乏结果说明，影响用户验证正确性？ | 2c/0e/2t |
| 6 | MindSpore r1.5.0分支OBS链接安全风险影响from_pretrained功能稳定性？ | 2c/0e/2t |
| 7 | MindSpore 的版本发布节奏是怎样的？ | — |
| 8 | MindSpore 2026 年有哪些活动规划？ | — |
| 9 | 新手如何加入 MindSpore 社区并参与开源贡献？ | — |
| 10 | MindSpore Transformers SIG 周例会的会议安排是怎样的？ | — |
| 11 | MindSpore 的 LLM Inference Serving SIG 是做什么的，多久开一次例会？ | — |
| 12 | MindSpore Parallel Training System SIG 的工作范围是什么？ | — |
| 13 | MindSpore MindQuantum SIG 的职责和活动是什么？ | — |
| 14 | 如何向 MindSpore TSC 申请成立新的 SIG？ | — |
| 15 | MindSpore TSC 是什么，它的职责和会议频率是怎样的？ | — |
| 16 | MindSpore 有哪些 SIG（Special Interest Groups）？各个 SIG 负责什么方向？ | — |
| 17 | MindSpore 是否参加过 KubeCon 等国际开源峰会？ | — |
| 18 | 如何向 MindSpore 邮件列表发送邮件或订阅邮件列表？ | — |
| 19 | MindSpore 的邮件列表系统使用什么平台？如何查看历史邮件存档？ | — |
| 20 | MindSpore 有哪些邮件列表，它们分别面向什么受众？ | — |
| 21 | MindSpore 社区组织会议的流程是什么？会议纪要通常包含哪些内容？ | — |
| 22 | MindSpore 的安全 SIG（Security SIG）如何处理漏洞报告和安全问题？ | — |
| 23 | MindSpore 的 TSC 会议是否对外公开？社区成员如何参与治理讨论？ | — |
