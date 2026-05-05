# openFuyao 问题集

## 概览

- 社区: openFuyao
- 生成时间: 2026-05-05
- 问题总数: 61

### 筛选标准

| 来源 | 占比 | 评分算法 | 筛选方式 | 获取时间 |
|------|------|----------|----------|----------|
| 论坛 | 100.0% | consult-filter（MongoDB 聚合话题按咨询类型过滤） | 61 aggregated topics (consult-filter: exclude all-Req/Task/RFC/Doc; mixed ≥50% consult kept) + 0 posts from unavailable | 2026-05-05 |
| **合计** | 100% | - | - | - |

### MongoDB 来源渠道

| 渠道 | 来源数量 | 状态 |
|------|----------|------|
| 论坛帖子 | 0 | ❌ 无数据 |
| 仓库 Issue | 754 | ✅ 有数据 |
| 邮件列表 | 0 | ❌ 无数据 |

### PostgreSQL 渠道状态

| 渠道 | 数量 | 状态 |
|------|------|------|
| - | - | PostgreSQL 未配置 |

## 分类目录

- [安装与部署](#安装与部署)（10 条，#1–#10）
- [调度与混部](#调度与混部)（10 条，#11–#20）
- [集群运维](#集群运维)（14 条，#21–#34）
- [AI推理与适配](#AI推理与适配)（7 条，#35–#41）
- [社区与协作](#社区与协作)（17 条，#42–#58）
- [安全漏洞](#安全漏洞)（3 条，#59–#61）


## 安装与部署

| # | 问题 | 频率 |
|---|------|------|
| 1 | openFuyao 离线安装时镜像地址错误导致扩展组件部署失败如何解决？ | 24c/0e/24t |
| 2 | openFuyao 在多版本 openEuler 上安装时存在兼容性问题如何解决？ | 22c/0e/22t |
| 3 | openFuyao 安装部署如何配置多镜像仓库并规范目录结构？ | 16c/0e/16t |
| 4 | openFuyao 引导节点集群安装时长如何验证和优化？ | 6c/0e/6t |
| 5 | openFuyao SCA 问题整改后集群无法启动如何排查解决？ | 5c/0e/5t |
| 6 | openFuyao 镜像仓库地址变更后离线部署镜像拉取失败如何解决？ | 4c/0e/4t |
| 7 | openFuyao 扩展组件离线安装时如何优化全量与自定义部署流程？ | 3c/0e/3t |
| 8 | openFuyao 在线与离线安装各阶段耗时如何分析和优化？ | 2c/0e/2t |
| 9 | openFuyao 离线高可用集群安装时后置脚本未在多节点执行如何解决？ | 2c/0e/2t |
| 10 | openFuyao 安装包缺少木兰 PSL 2.0 许可证文件如何处理？ | 2c/0e/2t |

## 调度与混部

| # | 问题 | 频率 |
|---|------|------|
| 11 | openFuyao 混部策略配置中参数描述错误与开关逻辑混乱如何排查修复？ | 140c/0e/140t |
| 12 | openFuyao 众核调度如何验证多类型负载 Pod 分值独立计算与跨节点均衡？ | 66c/0e/66t |
| 13 | openFuyao NUMA 监控表格如何明确区分并标注仅展示绑核容器信息？ | 35c/0e/35t |
| 14 | openFuyao 中 Volcano 调度依赖关系异常与默认优先级配置问题如何解决？ | 14c/0e/14t |
| 15 | openFuyao 混部节点资源利用率低于阈值时如何避免误驱逐 Pod？ | 4c/0e/4t |
| 16 | openFuyao NUMA 亲和调度与众核调度策略冲突时如何配置解决？ | 4c/0e/4t |
| 17 | openFuyao 众核调度权限体系如何明确定义各角色的权限边界？ | 3c/0e/3t |
| 18 | openFuyao HLS 业务在 Kubernetes 独占策略下如何解决部署兼容性问题？ | 3c/0e/3t |
| 19 | openFuyao 多优先级业务间资源抢占问题如何配置和解决？ | 2c/0e/2t |
| 20 | openFuyao HLS 业务的 CPU 资源请求与限制配置规范是什么？ | 2c/0e/2t |

## 集群运维

| # | 问题 | 频率 |
|---|------|------|
| 21 | openFuyao 社区 Kubernetes 升级与版本发布流程如何协同管理？ | 95c/0e/95t |
| 22 | openFuyao v25.03 应用市场功能信息展示异常如何验证和修复？ | 43c/0e/43t |
| 23 | openFuyao 集群健康检查未能准确反映 Pod 异常状态如何解决？ | 39c/0e/39t |
| 24 | openFuyao 集群安装时节点名称与 IP 冲突校验不完善如何解决？ | 21c/0e/21t |
| 25 | openFuyao Ray 集群健康数据展示与 Grafana 集成出现问题如何排查？ | 15c/0e/15t |
| 26 | openFuyao 多版本适配与配置定义流程如何统一管理？ | 9c/0e/9t |
| 27 | openFuyao 核心组件如何完成 HTTPS 改造以提升通信安全性？ | 3c/0e/3t |
| 28 | openFuyao 准入控制器如何统一管理 Pod 节点亲和性标签？ | 3c/0e/3t |
| 29 | openFuyao 多集群管理前端报错与部署一致性问题如何修复？ | 2c/0e/2t |
| 30 | openFuyao 组件跨命名空间部署时创建失败如何解决？ | 2c/0e/2t |
| 31 | openFuyao 集群删除后 BKENode 资源残留如何清理？ | 2c/0e/2t |
| 32 | openFuyao 集群扩容时节点信息校验不完整如何解决？ | 2c/0e/2t |
| 33 | openFuyao 集群自定义证书配置未生效如何排查解决？ | 2c/0e/2t |
| 34 | openFuyao 开发者遇到 Docker 与 Helm 构建失败如何解决？ | 2c/0e/2t |

## AI推理与适配

| # | 问题 | 频率 |
|---|------|------|
| 35 | openFuyao InferNex 一键部署离线安装包缺乏 E2E 自动化测试如何解决？ | 7c/0e/7t |
| 36 | openFuyao AI 推理智能路由如何实现容灾能力与多策略支持？ | 4c/0e/4t |
| 37 | openFuyao InferNex 因残留 CR 未达阈值触发强制扩容如何解决？ | 3c/0e/3t |
| 38 | AI 推理软件套件退出后 GPU 适配如何迁移至 openFuyao InferNex？ | 2c/0e/2t |
| 39 | openFuyao 如何扩展硬件健康检测以关联业务负载并识别 NPU 过载？ | 2c/0e/2t |
| 40 | openFuyao 如何支持 Mooncake 共享内存池化与 KV Cache 分布式管理？ | 2c/0e/2t |
| 41 | openFuyao Proxy Server 与推理引擎如何分离部署以降低资源占用？ | 2c/0e/2t |

## 社区与协作

| # | 问题 | 频率 |
|---|------|------|
| 42 | openFuyao 社区特性转测流程如何统一文档规范与自动化标准？ | 30c/0e/30t |
| 43 | openFuyao 如何构建独立可复用的审计日志组件？ | 16c/0e/16t |
| 44 | openFuyao 社区多个 SIG 会议频繁取消影响协作如何改善？ | 12c/0e/12t |
| 45 | openFuyao 测试用例缺乏统一格式规范如何制定标准？ | 11c/0e/11t |
| 46 | openFuyao 社区如何推进 CleanCode 代码规范整改？ | 9c/0e/9t |
| 47 | openFuyao 社区文档缺失影响开发者贡献如何补充完善？ | 6c/0e/6t |
| 48 | openFuyao 社区文档不完善导致开发者困惑如何改进？ | 5c/0e/5t |
| 49 | openFuyao 社区奖项评选流程与评选标准如何制定和优化？ | 4c/0e/4t |
| 50 | openFuyao 离线混部脚本上传缺乏自动化测试如何补充支持？ | 4c/0e/4t |
| 51 | openFuyao 混部测试自动化框架与测试用例如何完善？ | 3c/0e/3t |
| 52 | openFuyao 如何构建系统级特性自动化测试用例？ | 2c/0e/2t |
| 53 | openFuyao 版本文档交付流程如何完善？ | 2c/0e/2t |
| 54 | openFuyao Chart 插件与 VictoriaMetrics 部署文档如何完善？ | 2c/0e/2t |
| 55 | openFuyao OAuth 组件单元测试覆盖率不足如何提升？ | 2c/0e/2t |
| 56 | openFuyao 社区测试流程缺乏明确文档支持如何建立？ | 2c/0e/2t |
| 57 | openFuyao 模块路径如何统一更新至 gopkg.openfuyao.cn？ | 2c/0e/2t |
| 58 | openFuyao ARM 镜像与 Chart 包描述信息如何评审和完善？ | 2c/0e/2t |

## 安全漏洞

| # | 问题 | 频率 |
|---|------|------|
| 59 | openFuyao 如何应对 CVE-2024-45338 漏洞导致的拒绝服务风险？ | 8c/0e/8t |
| 60 | openFuyao AI 安全扫描发现的多项安全漏洞如何紧急修复？ | 3c/0e/3t |
| 61 | openFuyao NPU-Operator 中如何增加 unzip 工具依赖检查机制？ | 2c/0e/2t |
