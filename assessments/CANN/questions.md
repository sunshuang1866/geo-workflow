# CANN 问题集

## 概览

- 社区: CANN
- 生成时间: 2026-04-23
- 问题总数: 119

### 来源渠道

| 渠道 | 来源数量 | 状态 |
|------|----------|------|
| 论坛帖子 | 186 | ✅ 有数据 |
| 仓库 Issue | 1241 | ✅ 有数据 |
| 邮件列表 | 0 | ❌ 无数据 |

> **说明**：CANN 社区的 PostgreSQL 论坛数据目前也不支持 `views` 字段排序，因此暂未启用"按浏览量筛选 Top 单帖"功能。本次问题集仅基于 MongoDB 聚合数据生成。

### 筛选标准

每个 topic 包含一组 source（来源链接），根据 source 类型判定是否为咨询类：

| 分类 | source 类型关键词 | 判定规则 |
|------|-------------------|----------|
| **纯咨询类** | Question、Bug、Forum（论坛帖子） | ✅ 全部保留 |
| **纯排除类** | Requirement、Req、Task、RFC、Roadmap、Documentation、Doc | ❌ 全部丢弃 |
| **混合类** | 同时含咨询和排除 source | 咨询占比 **≥ 30%** → ✅ 保留；< 30% → ❌ 丢弃 |

> **识别方式**：论坛 source 通过 `type=forum` 字段判断；issue source 通过 title 方括号前缀识别，
> 例如 `[Question|问题咨询]`、`[Bug-Report|缺陷反馈]`、`[Requirement|需求建议]`。
> 无方括号的 issue（用户自发报错帖）统一视为咨询类。


## 分类目录

- [安装与环境配置](#安装与环境配置)（15 条）
- [模型转换与推理](#模型转换与推理)（9 条）
- [算子开发与编译](#算子开发与编译)（23 条）
- [算子精度与功能](#算子精度与功能)（20 条）
- [性能分析与优化](#性能分析与优化)（9 条）
- [运行时错误排查](#运行时错误排查)（15 条）
- [Triton 适配](#Triton-适配)（9 条）
- [框架集成](#框架集成)（6 条）
- [社区与协作](#社区与协作)（11 条）
- [安全漏洞](#安全漏洞)（2 条）

## 安装与环境配置

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_004 | 安装配置时遇到漏装必要软件包、版本匹配等问题导致运行失败如何解决？ | 18c/1e/19t |
| q_016 | 使用官方Docker镜像运行入门用例时遇到各种问题如何解决？ | 7c/0e/7t |
| q_072 | 运行昇腾CANN样例时因缺失库文件或头文件导致编译执行失败如何解决？ | 4c/0e/4t |
| q_063 | NPU设备被占用或DCMI模块初始化失败导致的容器启动报错如何解决？ | 3c/0e/3t |
| q_028 | 安装torch_npu时因ACL初始化失败及依赖缺失导致报错500001如何解决？ | 2c/0e/2t |
| q_055 | Docker构建中因shell环境或PATH问题导致sha256sum命令无法识别如何解决？ | 2c/0e/2t |
| q_058 | openEuler24.03上编译CATLASS示例算子因缺少NEON支持报错如何解决？ | 2c/0e/2t |
| q_075 | 因libascend_hal.so缺失导致ATC模型转换失败，需确认Atlas附加库安装及环境变量配置如何解决？ | 2c/0e/2t |
| q_090 | 无法配置Ascend NPU共享模式导致多Docker容器无法共享显卡如何解决？ | 2c/0e/2t |
| q_093 | 获取检测工具以验证昇腾环境是否满足构建要求？ | 2c/0e/2t |
| q_109 | 云开发环境下编译安装算子时目标目录缺失且依赖无法自动识别如何解决？ | 2c/0e/2t |
| q_116 | CANN 8.0.0 arm64环境下运行SampleYOLOV7时因缺少libmedia_minil.so库导致失败如何解决？ | 2c/0e/2t |
| q_119 | 使用SIP加速库时因环境配置或依赖缺失导致示例程序运行失败如何解决？ | 2c/0e/2t |
| q_121 | 编译算子时遇到npu supported ops json权限问题及日志缺失如何解决？ | 2c/0e/2t |
| q_123 | 升级CANN 8.5.0至8.5.1时因无详细日志提示失败如何解决？ | 2c/0e/2t |


## 模型转换与推理

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_012 | ATC转换模型时遇到报错如何解决？ | 139c/0e/139t |
| q_002 | 转换模型时在转换过程和推理过程中遇到报错如何解决？ | 32c/0e/32t |
| q_009 | 使用ATC转换模型时soc版本与设备不适配导致加载失败如何解决？ | 7c/0e/7t |
| q_003 | ATC工具转换warpPerspective算子时输入类型配置失败如何解决？ | 3c/0e/3t |
| q_088 | 如何将PTH模型转换为OM格式并配置DNN后端以支持CANN推理？ | 3c/0e/3t |
| q_011 | AMCT量化后BatchMatMulV2算子爆增导致推理耗时劣化问题如何解决？ | 2c/0e/2t |
| q_065 | 执行ais_bench加载resnet50.om模型时卡住无响应如何解决？ | 2c/0e/2t |
| q_114 | SlowFast模型动态batch下ATC转换后推理输出异常问题如何解决？ | 2c/0e/2t |
| q_122 | 排查ATC转换中精度模式配置导致的推理偏差如何解决？ | 2c/0e/2t |


## 算子开发与编译

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_107 | 昇腾CANN算子开发的快速入门与高效调试方法如何解决？ | 8c/0e/8t |
| q_112 | 如何将AscendC MicroAPI替换为AscendC Reg以适配最新CANN接口规范？ | 5c/0e/5t |
| q_010 | 如何排查Ascend310b上算子编译、部署和结果验证的错误？ | 4c/0e/4t |
| q_042 | 编译自定义算子时因头文件依赖不明确和交叉编译工具链配置错误导致编译失败如何解决？ | 4c/0e/4t |
| q_105 | 如何将VEC_SCOPE替换为带simd_vf标识的函数以符合AscendC接口规范？ | 4c/0e/4t |
| q_001 | cmake无法启用WITH_CANN选项的编译问题如何解决？ | 2c/0e/2t |
| q_007 | 遇到自定义算子入图用例失败的问题如何解决？ | 2c/0e/2t |
| q_008 | 编译ATB代码时出现对未开源代码仓的依赖导致编译失败如何解决？ | 2c/0e/2t |
| q_013 | 配置ASCEND_OPP_PATH同时支持系统算子和自定义算子路径如何解决？ | 2c/0e/2t |
| q_019 | op_host中CMakeLists.txt使用未定义变量OPTEST_NAME和函数add_modules_llt_sources导致UT构建失败如何解决？ | 2c/1e/3t |
| q_022 | CANN 8.5.T4.0以上版本以支持master分支experimental算子编译如何解决？ | 2c/0e/2t |
| q_024 | AvgPoolV2算子stride超过63时编译失败的问题如何解决？ | 2c/0e/2t |
| q_031 | MLA_Prolog op_graph目录UT覆盖率统计问题及用例缺失如何解决？ | 2c/0e/2t |
| q_043 | TBE算子开发中多核调度分片策略与混合精度适配规则？ | 2c/0e/2t |
| q_044 | 改进mla_prolog融合算子时遭遇编译错误和ooschedule错误如何解决？ | 2c/0e/2t |
| q_047 | 使用amct_onnx编译自定义算子时遭遇头文件缺失和版本兼容性问题如何解决？ | 2c/0e/2t |
| q_070 | 如何优化高频小批量场景下自定义算子的执行效率？ | 2c/0e/2t |
| q_083 | 如何适配CuPy算子如slicing与assignment至昇腾NPU并实现性能优化？ | 2c/0e/2t |
| q_085 | CANN 8.0 RC1中编译stft算子失败且无法找到实现文件如何解决？ | 2c/0e/2t |
| q_086 | 如何在AscendNPU IR中实现指令级性能监控算子以支持NPU操作检测？ | 2c/0e/2t |
| q_100 | cmake无法启用WITH_CANN选项的编译问题如何解决？ | 2c/0e/2t |
| q_111 | matmul_tutorials与matmul_recipes示例的行为差异及适用场景如何解决？ | 2c/0e/2t |
| q_126 | 编译FlashAttention算子时报错Tiling找不到如何解决？ | 2c/0e/2t |


## 算子精度与功能

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_068 | GDR算子中开启合轴优化或处理非整除场景时出现精度异常与报错如何解决？ | 12c/0e/12t |
| q_020 | 开启Mix合图后glm_attention等算子精度异常及执行报错问题如何解决？ | 11c/0e/11t |
| q_034 | reshape操作在动态shape、多算子组合场景下的精度问题及优化pass影响如何解决？ | 7c/0e/7t |
| q_124 | CANN 8.2 RC1环境下调用dlblas或Liger-Kernel的grouped_gemm、grpo_loss等算子时报错如何解决？ | 4c/0e/4t |
| q_046 | mla_prolog算子INT64转INT32_cast导致内存越界及pto_isa编译报错问题如何解决？ | 3c/0e/3t |
| q_089 | MOE算子二分查找中的未初始化变量、越界访问及int32溢出风险如何解决？ | 3c/0e/3t |
| q_102 | scatter_update多次刷新时依赖建立错误导致的精度问题如何解决？ | 3c/0e/3t |
| q_118 | pypto.full在loop外创建tensor导致的精度异常和构图错误如何解决？ | 3c/0e/3t |
| q_021 | Agent生成的mhc算子性能远低于AscendC且cube切分对齐约束过严如何解决？ | 2c/0e/2t |
| q_029 | A5上swiglu算子存在精度问题且bf16场景无法接入superkernel如何解决？ | 2c/0e/2t |
| q_030 | StatelessRandomChoiceWithMask算子空tensor场景下的功能失败问题如何解决？ | 2c/0e/2t |
| q_033 | 昇腾910B上带bias的matmul算子存在严重精度问题如何解决？ | 2c/0e/2t |
| q_041 | aclnnQuantBatchMatmul和WeightQuantBatchMatmulV2算子因输入校验缺失导致的aicore错误与GM越界问题如何解决？ | 2c/0e/2t |
| q_067 | PyTorch tensor直接assemble给outcast时machine层报错及OOO问题如何解决？ | 2c/0e/2t |
| q_073 | npu_ffn融合算子在SwiGLU激活下输出异常需排查数值稳定性问题如何解决？ | 2c/0e/2t |
| q_082 | prelugradupdate算子在0D/1D输入下报错且提示未定义接口prelugradreduce如何解决？ | 2c/0e/2t |
| q_087 | dynamic_quant_base.h中else块变量未初始化导致的未定义行为问题如何解决？ | 2c/0e/2t |
| q_092 | aclnn算子CubeMathType模式未生效及broadcast校验缺失问题如何解决？ | 2c/0e/2t |
| q_103 | Inductor生成融合kernel在特定tiling下偶现的精度问题如何解决？ | 2c/0e/2t |
| q_104 | aclnnIndexCopy多线程调用时的空指针校验和vector容器线程安全问题如何解决？ | 2c/0e/2t |


## 性能分析与优化

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_040 | 昇腾CANN调度延迟导致端到端耗时远高于泳道图算子时间的问题如何解决？ | 6c/0e/6t |
| q_052 | 动态shape场景下如何解决CANN中tiling offset out of range的警告与推理性能问题？ | 4c/0e/4t |
| q_025 | 泳道图任务依赖关系及开始时间显示异常问题如何解决？ | 3c/0e/3t |
| q_054 | 如何优化Qwen3-Next-80B-A3B-Instruct在910B上的vLLM并行策略以提升推理性能？ | 3c/0e/3t |
| q_080 | 执行msprof命令未采集到AI Core Metrics数据如何解决？ | 3c/0e/3t |
| q_048 | 开启Autotune时小shape场景下性能数据采集不准确如何解决？ | 2c/0e/2t |
| q_091 | 大shape下CANN算子因内存分配失败导致的执行卡死问题如何解决？ | 2c/0e/2t |
| q_096 | 遇aclmdlExecute接口偶发阻塞无返回，需排查原因及解决方案？ | 2c/0e/2t |
| q_110 | 如何提前构建所有profile以应对动态shape切换耗时与异常？ | 2c/0e/2t |


## 运行时错误排查

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_032 | 使用aclrtSynchronizeStream时频繁遇到错误码507015、507018等流同步失败问题，需定位与内存对齐、CANN版本兼容性及DVPP资源绑定相关的根本原因如何解决？ | 20c/0e/20t |
| q_101 | ERR00100 PTA调用ACL API失败问题，需排查驱动版本、C2控制接口支持及容器内ACL运行时初始化如何解决？ | 4c/0e/4t |
| q_005 | PyTorch与NPU适配中如何排查507018/507015硬件异常错误？ | 3c/0e/3t |
| q_006 | 如何排查SenseVoiceSmall模型执行错误码500002及ACL初始化失败问题？ | 3c/0e/3t |
| q_014 | 昇腾CANN多模型加载时ACL重复初始化错误解决如何解决？ | 2c/0e/2t |
| q_036 | 如何高效定位算子内存越界问题？ | 2c/0e/2t |
| q_050 | 排查sampleYOLOV7MultiInput在Atlas 300V Pro上ACL初始化后无输出的问题如何解决？ | 2c/0e/2t |
| q_060 | 编译执行昇腾自定义P2P算子时遇到Segmentation fault如何解决？ | 2c/0e/2t |
| q_062 | 昇腾910A环境下Python接口用例执行失败问题如何解决？ | 2c/0e/2t |
| q_064 | apply_rotary_pos_emb算子在arch38和arch35的兼容适配及信息库配置缺失问题如何解决？ | 2c/1e/3t |
| q_066 | 使用高阶封装VideoRead读取视频时因内存不足导致程序崩溃如何解决？ | 2c/0e/2t |
| q_076 | 多次linkdown时遭遇LLM_FAILED异常，无法构造CQE故障如何解决？ | 2c/0e/2t |
| q_084 | 多卡分布式场景下执行自定义算子stitch阶段时遭遇AICPU异常崩溃如何解决？ | 2c/0e/2t |
| q_097 | UB到UB的DataCopy所属的流水线类型如何解决？ | 2c/0e/2t |
| q_125 | 银河麒麟系统下执行PyTorch NPU算子时遇DDR地址越界错误如何解决？ | 2c/0e/2t |


## Triton 适配

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_117 | 统一Triton算子对bool、uint32等类型输入的错误拦截与提示如何解决？ | 7c/0e/7t |
| q_057 | VLLM MoE内核编译时类型转换与地址表达式支持问题如何解决？ | 4c/0e/4t |
| q_069 | CANN 8.2 RC1下dlBLAS算子在PyTorch 2.6.0rc1中的兼容性与编译报错问题如何解决？ | 3c/0e/3t |
| q_077 | Triton融合算子在NPU上对ARM架构的适配及精度性能保障如何解决？ | 3c/0e/3t |
| q_078 | Triton编译中缺失attribute及libdevice算子兼容性问题如何解决？ | 3c/0e/3t |
| q_106 | Triton fma和cast算子在非浮点输入或低精度类型下的精度达标与编译支持问题如何解决？ | 3c/0e/3t |
| q_049 | 关注Triton间接访存功能的编译、运行及性能达标情况如何解决？ | 2c/0e/2t |
| q_108 | TL.cumsum在CANN 8.2T3中因类型推导失败导致的编译错误如何解决？ | 2c/0e/2t |
| q_113 | CANN Triton算子在bf16输入下argmax/argmin报507035错误及max/min算子bool类型精度不达标问题如何解决？ | 2c/0e/2t |


## 框架集成

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_099 | 使用MindSpore Custom调用Ascend C算子时如何处理动态Shape和多输入多输出配置？ | 4c/0e/4t |
| q_045 | MindSpore与FastAPI集成实现多模型异步协同推理的部署方案？ | 2c/0e/2t |
| q_071 | 910A服务器上使用LlamaFactory以fp16微调Qwen3模型时遭遇梯度爆炸及BF16不支持的兼容性问题如何解决？ | 2c/0e/2t |
| q_079 | AMCT在2026年对低比特量化及主流模型量化支持的路线规划？ | 2c/0e/2t |
| q_098 | hunyuan-video关闭稀疏模式报错及补充block sparse attention功能文档如何解决？ | 2c/0e/2t |
| q_115 | Ascend310P和Ascend910A芯片对大模型推理部署的支持计划？ | 2c/0e/2t |


## 社区与协作

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_120 | 如何统一修改昇腾CANN多文件版权声明为附件E列标准格式？ | 18c/0e/18t |
| q_039 | 如何通过参与CANN直播答题和提交issue赢取定制奖品？ | 8c/0e/8t |
| q_037 | 申请成为成为昇腾CANN ops-nn仓committer需具备哪些贡献与能力？ | 3c/0e/3t |
| q_038 | 优化Issue模板以明确分类并提示标题填写如何解决？ | 3c/0e/3t |
| q_015 | 资料文档缺陷导致开发者开发、测试部署失败如何解决？ | 2c/0e/2t |
| q_018 | 按CONTRIBUTING.md模板B规范重构目录结构并补全基线与验证脚本？ | 2c/0e/2t |
| q_026 | 修复HcclGetAlgRes和HcclEngineCtxGet中的错误处理逻辑如何解决？ | 2c/0e/2t |
| q_027 | 昇腾CANN社区Committer晋升标准与贡献要求？ | 2c/0e/2t |
| q_059 | 数字化协作平台贡献统计缺失issue处理数据及SIG过滤功能异常如何解决？ | 2c/0e/2t |
| q_074 | 清理昇腾CANN代码告警及提示中的多余空行如何解决？ | 2c/0e/2t |
| q_081 | ISSUE模板中配置的Label未自动生效，需手动添加标签如何解决？ | 2c/0e/2t |


## 安全漏洞

> 表头说明：`consult/exclude` 列格式为 `咨询数c/排除数e/总数t`

| ID | 问题 | consult/exclude |
|----|------|-----------------|
| q_053 | CVE-2026-33210漏洞对CANN版本的安全影响如何解决？ | 3c/0e/3t |
| q_061 | 确认Ruby JSON组件CVE-2025-27788漏洞影响及修复方案？ | 2c/0e/2t |

