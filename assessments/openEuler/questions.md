# openEuler GEO 问题集

社区：openEuler  
生成时间：2026-04-01  
问题总数：80  
来源分布：forum=32，maillist=48

---

## 汇总表

| ID | 问题 | 来源 | 类别 | 官方链接 |
| ---- | ---- | ---- | ---- | ---- |
| q_001 | 如何在个人电脑（PC）上安装 openEuler 操作系统？安装前需要做哪些准备？ | forum | installation | [https://forum.openeuler.org/t/topic/6872](https://forum.openeuler.org/t/topic/6872), [https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/server/installation_upgrade/installation/installation_modes.html](https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/server/installation_upgrade/installation/installation_modes.html) |
| q_002 | 在 VMware 中安装 openEuler 22.03 时无法识别网卡，应如何安装虚拟机网卡驱动？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/7378/2](https://forum.openeuler.org/t/topic/7378/2) |
| q_003 | openEuler 如何安装 WiFi 无线网卡驱动？ | forum | configuration | [https://forum.openeuler.org/t/topic/294](https://forum.openeuler.org/t/topic/294) |
| q_004 | 如何在飞腾 D2000 处理器平台上安装 openEuler？有哪些已知兼容性问题？ | forum | installation | [https://forum.openeuler.org/t/topic/19010](https://forum.openeuler.org/t/topic/19010), [https://forum.openeuler.org/t/topic/2713](https://forum.openeuler.org/t/topic/2713), [https://forum.openeuler.org/t/topic/1975/14](https://forum.openeuler.org/t/topic/1975/14) |
| q_005 | openEuler 的 A-Ops 智能运维工具 gala-ops 如何安装和部署？ | forum | deployment | [https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/server/aops/deploying_aops.html](https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/server/aops/deploying_aops.html) |
| q_006 | openEuler 是否支持飞腾 E2000Q 处理器平台？如何验证硬件兼容性？ | forum | feature | [https://forum.openeuler.org/t/topic/1975](https://forum.openeuler.org/t/topic/1975) |
| q_007 | 如何通过 Open Build Service（OBS）为 openEuler 社区构建和发布软件包？ | forum | tutorial | [https://forum.openeuler.org/t/topic/875](https://forum.openeuler.org/t/topic/875) |
| q_008 | 安装 openEuler 后系统中找不到 man 命令，是什么原因？如何安装 man 帮助手册？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/220](https://forum.openeuler.org/t/topic/220), [https://forum.openeuler.org/t/topic/1028](https://forum.openeuler.org/t/topic/1028) |
| q_009 | 如何使用 x2openEuler 工具将系统从 openEuler 20.03 原地升级到 22.03？ | forum | migration | [https://www.openeuler.openatom.cn/zh/migration/](https://www.openeuler.openatom.cn/zh/migration/), [https://forum.openeuler.org/t/topic/18990](https://forum.openeuler.org/t/topic/18990) |
| q_010 | CentOS 7.x 能否直接迁移到 openEuler 22.03 LTS？完整的迁移步骤和注意事项是什么？ | forum | migration | [https://www.openeuler.openatom.cn/zh/migration/](https://www.openeuler.openatom.cn/zh/migration/) |
| q_011 | 安装 openEuler 时 Anaconda 安装程序卡住无法继续，如何排查解决？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/3222](https://forum.openeuler.org/t/topic/3222) |
| q_012 | openEuler 22.03 LTS 上如何搭建 Mail 邮件服务器（Postfix/Dovecot）？ | forum | deployment | [https://forum.openeuler.org/t/topic/246](https://forum.openeuler.org/t/topic/246) |
| q_013 | openEuler 22.03 SP3 如何升级到 24.03 版本？有哪些官方推荐迁移方式？ | forum | migration | [https://forum.openeuler.org/t/topic/4572](https://forum.openeuler.org/t/topic/4572), [https://www.openeuler.openatom.cn/zh/migration/](https://www.openeuler.openatom.cn/zh/migration/) |
| q_014 | openEuler 22.03-lts 容器镜像启动后执行 yum update 报错，如何排查解决？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/2200](https://forum.openeuler.org/t/topic/2200) |
| q_015 | openEuler 上如何安装 VirtualBox 虚拟机软件？ | forum | configuration | [https://forum.openeuler.org/t/topic/4549](https://forum.openeuler.org/t/topic/4549) |
| q_016 | openEuler 22.03 LTS SP2 上如何修复 CVE-2024-1086 内核提权漏洞？ | forum | feature | [https://forum.openeuler.org/t/topic/4537](https://forum.openeuler.org/t/topic/4537) |
| q_017 | openEuler 22.03 SP3 如何安装 XFCE 桌面环境？ | forum | configuration | [https://forum.openeuler.org/t/topic/18345](https://forum.openeuler.org/t/topic/18345), [https://forum.openeuler.org/t/topic/18449](https://forum.openeuler.org/t/topic/18449), [https://forum.openeuler.org/t/topic/6270](https://forum.openeuler.org/t/topic/6270) |
| q_018 | 配置 openEuler 本地 DNF 仓库源时提示下载元数据失败，如何排查？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/2964](https://forum.openeuler.org/t/topic/2964) |
| q_019 | 鲲鹏 920 处理器的服务器应该安装哪个架构版本的 openEuler（X86 还是 AArch64）？ | forum | installation | [https://forum.openeuler.org/t/topic/2789](https://forum.openeuler.org/t/topic/2789) |
| q_020 | openEuler 22.03 ARM 架构上如何部署 Zabbix 监控系统？ | forum | deployment | [https://forum.openeuler.org/t/topic/4780](https://forum.openeuler.org/t/topic/4780) |
| q_021 | openEuler 22.03 SP1 是否支持将内核升级到 6.x 版本？如何操作？ | forum | feature | [https://forum.openeuler.org/t/topic/5035](https://forum.openeuler.org/t/topic/5035) |
| q_022 | openEuler 22.03 SP2 执行 dnf upgrade 失败，常见原因和解决方法有哪些？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/4897/2](https://forum.openeuler.org/t/topic/4897/2) |
| q_023 | 安装 x2openEuler 工具后找不到 service_start.sh 脚本，如何解决？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/3396](https://forum.openeuler.org/t/topic/3396) |
| q_024 | Red Hat 7.9 迁移到 openEuler 时出现 'can not clean repo info before upgrade' 错误，如何解决？ | forum | migration | [https://forum.openeuler.org/t/topic/3959](https://forum.openeuler.org/t/topic/3959), [https://forum.openeuler.org/t/topic/3745](https://forum.openeuler.org/t/topic/3745) |
| q_025 | openEuler 24.03 SP1 上安装英伟达显卡驱动时如何选择合适的 CUDA 版本？ | forum | configuration | [https://forum.openeuler.org/t/topic/6895](https://forum.openeuler.org/t/topic/6895) |
| q_026 | openEuler Embedded 是否支持通过 yum/dnf 在线安装软件包？ | forum | feature | [https://forum.openeuler.org/t/topic/4365](https://forum.openeuler.org/t/topic/4365) |
| q_027 | openEuler 系统强制关机后重启速度极慢（7-8 分钟），如何优化系统启动时间？ | forum | performance | [https://forum.openeuler.org/t/topic/3612](https://forum.openeuler.org/t/topic/3612) |
| q_028 | openEuler 升级过程中网络中断导致 SSH 无法连接，如何恢复升级并修复系统？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/3328](https://forum.openeuler.org/t/topic/3328) |
| q_029 | openEuler 如何禁用 /tmp 目录挂载为 tmpfs？有什么影响？ | forum | configuration | [https://forum.openeuler.org/t/topic/4266](https://forum.openeuler.org/t/topic/4266) |
| q_030 | 将系统 Python 版本升级到 3.11 后导致 dnf/yum 命令不可用，如何恢复？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/6230](https://forum.openeuler.org/t/topic/6230) |
| q_031 | openEuler 24.03 LTS SP1 无法安装 NVIDIA 显卡驱动，如何解决？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/6960](https://forum.openeuler.org/t/topic/6960) |
| q_032 | 误将 /usr 目录设置 chmod 777 导致无法切换 root 用户，如何修复 openEuler 系统权限？ | forum | troubleshooting | [https://forum.openeuler.org/t/topic/4337](https://forum.openeuler.org/t/topic/4337) |
| q_033 | openEuler 社区有哪些 SIG 组（特别兴趣小组），如何查看完整的 SIG 列表？ | maillist | governance | [https://www.openeuler.openatom.cn/zh/sig/sig-list/](https://www.openeuler.openatom.cn/zh/sig/sig-list/) |
| q_034 | 如何订阅 openEuler 社区邮件列表（如 dev@openeuler.org）参与技术讨论？ | maillist | subscription | [https://www.openeuler.openatom.cn/zh/sig/dev-utils](https://www.openeuler.openatom.cn/zh/sig/dev-utils) |
| q_035 | 如何加入 openEuler sig-Migration SIG，参与跨平台 OS 迁移相关开发贡献？ | maillist | governance | [https://www.openeuler.openatom.cn/zh/sig/sig-Migration](https://www.openeuler.openatom.cn/zh/sig/sig-Migration) |
| q_037 | openEuler AI SIG（ai-infra@openeuler.org）的目标是什么？支持哪些 AI 基础设施框架？ | maillist | technical | [https://www.openeuler.openatom.cn/zh/sig/ai](https://www.openeuler.openatom.cn/zh/sig/ai) |
| q_038 | openEuler sig-QA 如何进行版本质量测试？如何参与社区 QA 贡献？ | maillist | governance | [https://www.openeuler.openatom.cn/zh/sig/sig-QA](https://www.openeuler.openatom.cn/zh/sig/sig-QA) |
| q_039 | openEuler Embedded 操作系统有哪些应用场景？支持哪些嵌入式硬件平台？ | maillist | technical | [https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/embedded/index.html](https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/embedded/index.html) |
| q_040 | 如何向 openEuler TSC 提交 SIG 申请，新建特别兴趣小组的流程是什么？ | maillist | governance | [https://www.openeuler.openatom.cn/zh/sig/sig-list/](https://www.openeuler.openatom.cn/zh/sig/sig-list/) |
| q_041 | openEuler 社区版本的生命周期是如何规划的？LTS 版本与创新版本在支持周期和适用场景上有何区别？ | maillist | governance | — |
| q_042 | A-Tune 自调优工具在分布式场景下如何将客户端和服务端部署在不同机器上？ | maillist | deployment | — |
| q_043 | openEuler A-Tune 如何对 MySQL 数据库进行自动性能调优？ | maillist | performance | — |
| q_044 | 如何加入 openEuler A-Tune SIG 组参与系统性能自调优工具的开发？ | maillist | governance | — |
| q_045 | openEuler 上如何使用 UADK 进行用户态硬件加速开发？ | maillist | tutorial | — |
| q_046 | openEuler 鲲鹏 UADK 支持哪些加密算法（SM4、AES、RSA、SHA 等）？ | maillist | feature | — |
| q_047 | openEuler 如何查询鲲鹏加速器（hisilicon qm）的硬件故障状态？ | maillist | troubleshooting | — |
| q_048 | openEuler BigData SIG 支持哪些大数据组件（Hadoop、Spark、Flink 等）？ | maillist | feature | — |
| q_049 | 如何在 openEuler 上快速搭建大数据集群？BigData SIG 提供哪些工具支持？ | maillist | deployment | — |
| q_050 | 如何从头开始本地构建 openEuler ISO 镜像？EulerMaker 构建系统使用流程是什么？ | maillist | tutorial | — |
| q_051 | 如何申请成为 openEuler 官方镜像（mirror）站点？有哪些要求和申请流程？ | maillist | governance | — |
| q_052 | openEuler RPM 包的 spec 文件在哪个仓库管理？如何为 openEuler 贡献新的软件包？ | maillist | tutorial | — |
| q_053 | openEuler SDS SIG 中 Lustre 文件系统如何适配 openEuler 6.6 内核？ | maillist | technical | — |
| q_054 | openEuler 分布式存储（sig-SDS）SIG 支持哪些存储组件（Ceph、Lustre、DBS）？ | maillist | feature | — |
| q_055 | 如何参与 openEuler 版本 RC 测试阶段？issue 提交和修复流程是什么？ | maillist | governance | — |
| q_056 | openEuler 新版本分支初始化时，SIG maintainer 如何参与 PR 检视流程？ | maillist | governance | — |
| q_057 | openEuler 版本发布前如何处理降级的 issue？release 公告会包含哪些内容？ | maillist | governance | — |
| q_058 | openEuler CloudNative SIG 支持哪些云原生组件（containerd、iSula、kata-containers）？ | maillist | feature | — |
| q_059 | openEuler 上如何引入和使用 composefs 实现容器镜像只读挂载文件系统？ | maillist | technical | — |
| q_060 | 如何参与 openEuler CloudNative SIG 双周例会？议题如何提交？ | maillist | governance | [https://atomgit.com/openeuler/cloudnative](https://atomgit.com/openeuler/cloudnative), [https://www.openeuler.org/zh/sig/sig-CloudNative](https://www.openeuler.org/zh/sig/sig-CloudNative) |
| q_061 | openEuler 24.03-LTS-SP4 中 OpenSSL 升级到 3.5.x 对已有应用兼容性有哪些影响？ | maillist | feature | — |
| q_062 | 如何向 openEuler dev 邮件列表提交技术提案（RFC）或发起社区讨论？ | maillist | governance | — |
| q_063 | 如何申请在 openEuler 官方网站添加新的全球镜像节点？有哪些申请条件？ | maillist | governance | [https://www.openeuler.org/zh/mirror/list/](https://www.openeuler.org/zh/mirror/list/) |
| q_064 | openEuler 社区版本生命周期变更和发布节奏调整的公示流程是什么？ | maillist | governance | — |
| q_065 | openEuler OLK-6.6 内核 CPPC 调频驱动使用 ktime 替代 jiffies 的背景和原理是什么？ | maillist | technical | — |
| q_066 | openEuler xSched 调度器的 xcu cmdline 参数如何动态切换 cgroup 调度模式？ | maillist | technical | — |
| q_067 | 向 openEuler OLK 内核树提交补丁的格式要求是什么？如何通过邮件列表投递？ | maillist | tutorial | — |
| q_068 | openEuler 22.03 LTS-SP3 是否支持 DevStack 部署 OpenStack？有哪些兼容性问题？ | maillist | troubleshooting | — |
| q_070 | 如何在 openEuler 24.03 LTS 上部署 OpenStack Antelope 版本？ | maillist | deployment | [https://docs.openeuler.org/zh/docs/25.03/virtualization/virtualization_platform/openstack/install/antelope.html](https://docs.openeuler.org/zh/docs/25.03/virtualization/virtualization_platform/openstack/install/antelope.html) |
| q_071 | openEuler Virt SIG 支持哪些虚拟化技术（KVM、QEMU、libvirt）？工作范围是什么？ | maillist | feature | [https://docs.openeuler.org/zh/docs/25.03/virtualization/virtualization_platform/virtualization/introduction-to-virtulization.html](https://docs.openeuler.org/zh/docs/25.03/virtualization/virtualization_platform/virtualization/introduction-to-virtulization.html) |
| q_073 | openEuler 虚拟机如何支持 vNMI 热迁移？ | maillist | troubleshooting | [https://docs.openeuler.org/zh/docs/20.09/docs/Virtualization/%E7%83%AD%E8%BF%81%E7%A7%BB%E8%99%9A%E6%8B%9F%E6%9C%BA.html#:~:text=%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9%E5%92%8C%E7%BA%A6%E6%9D%9F%E9%99%90%E5%88%B6%20*%20%E7%83%AD%E8%BF%81%E7%A7%BB%E8%BF%87%E7%A8%8B%E4%B8%AD%EF%BC%8C%E9%9C%80%E8%A6%81%E4%BF%9D%E8%AF%81%E7%BD%91%E7%BB%9C%E7%8A%B6%E6%80%81%E8%89%AF%E5%A5%BD%E3%80%82%20%E5%A6%82%E6%9E%9C%E5%8F%91%E7%94%9F%E7%BD%91%E7%BB%9C%E4%B8%AD%E6%96%AD%EF%BC%8C%E7%83%AD%E8%BF%81%E7%A7%BB%E4%BC%9A%E6%9A%82%E5%81%9C%EF%BC%8C%E7%9B%B4%E5%88%B0%E7%BD%91%E7%BB%9C%E6%81%A2%E5%A4%8D%E5%90%8E%E6%89%8D%E4%BC%9A%E7%BB%A7%E7%BB%AD%EF%BC%8C%E5%BD%93%E5%8F%91%E7%94%9F%E8%B6%85%E6%97%B6%EF%BC%8C%E7%83%AD%E8%BF%81%E7%A7%BB%E4%BC%9A%E5%A4%B1%E8%B4%A5%E3%80%82%20*%20%E8%BF%81%E7%A7%BB%E8%BF%87%E7%A8%8B%E4%B8%AD%EF%BC%8C%E4%B8%8D%E5%85%81%E8%AE%B8%E5%AF%B9%E8%99%9A%E6%8B%9F%E6%9C%BA%E8%BF%9B%E8%A1%8C%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F%E5%92%8C%E7%AE%A1%E7%90%86%E8%99%9A%E6%8B%9F%E6%9C%BA%E7%A1%AC%E4%BB%B6%E8%AE%BE%E5%A4%87%E7%AD%89%E6%93%8D%E4%BD%9C%E3%80%82%20*,%E8%99%9A%E6%8B%9F%E6%9C%BA%E6%AD%A3%E5%9C%A8%E8%BF%81%E7%A7%BB%E7%9A%84%E8%BF%87%E7%A8%8B%E4%B8%AD%EF%BC%8C%E4%B8%8D%E5%85%81%E8%AE%B8%E5%AF%B9%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%81%9A%E5%85%B3%E6%9C%BA%E3%80%81%E9%87%8D%E5%90%AF%E6%88%96%E6%81%A2%E5%A4%8D%E6%93%8D%E4%BD%9C%EF%BC%8C%E5%90%A6%E5%88%99%E5%8F%AF%E8%83%BD%E4%BC%9A%E5%AF%BC%E8%87%B4%E7%83%AD%E8%BF%81%E7%A7%BB%E5%A4%B1%E8%B4%A5%EF%BC%8C%E5%BD%93%E6%89%A7%E8%A1%8CACPI%E6%96%B9%E5%BC%8F%E9%87%8D%E5%90%AF%E6%97%B6%EF%BC%8C%E5%86%8D%E6%89%A7%E8%A1%8C%E7%83%AD%E8%BF%81%E7%A7%BB%E4%BC%9A%E5%AF%BC%E8%87%B4%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%85%B3%E9%97%AD%E3%80%82%20*%20%E5%8F%AA%E6%94%AF%E6%8C%81%E5%90%8C%E6%9E%84%E7%83%AD%E8%BF%81%E7%A7%BB%EF%BC%8C%E5%8D%B3%E6%BA%90%E7%AB%AF%E5%92%8C%E7%9B%AE%E7%9A%84%E7%AB%AFCPU%E5%9E%8B%E5%8F%B7%E9%9C%80%E8%A6%81%E7%9B%B8%E5%90%8C%E3%80%82%20*%20%E8%B7%A8%E4%B8%9A%E5%8A%A1%E7%BD%91%E6%AE%B5%E8%99%9A%E6%8B%9F%E6%9C%BA%E8%BF%81%E7%A7%BB%E5%8F%AF%E4%BB%A5%E6%88%90%E5%8A%9F%EF%BC%8C%E4%BD%86%E6%98%AF%E5%88%B0%E7%9B%AE%E7%9A%84%E7%AB%AF%E5%90%8E%E4%BC%9A%E5%87%BA%E7%8E%B0%E7%BD%91%E7%BB%9C%E5%BC%82%E5%B8%B8%EF%BC%8C%E4%B8%BA%E4%BA%86%E9%98%B2%E6%AD%A2%E8%AF%A5%E6%83%85%E5%86%B5%E5%8F%91%E7%94%9F%EF%BC%8C%E9%9C%80%E8%A6%81%E7%94%A8%E6%88%B7%E4%BF%9D%E8%AF%81%E8%BF%81%E7%A7%BB%E4%B8%9A%E5%8A%A1%E7%BD%91%E6%AE%B5%E4%B8%80%E8%87%B4%E3%80%82%20*%20%E5%A6%82%E6%9E%9C%E6%BA%90%E7%AB%AF%E8%99%9A%E6%8B%9F%E6%9C%BAvCPU%E6%95%B0%E5%A4%A7%E4%BA%8E%E7%9B%AE%E7%9A%84%E7%AB%AF%E7%9A%84%E7%89%A9%E7%90%86%E6%9C%BACPU%E6%A0%B8%E6%95%B0%EF%BC%8C%E5%88%99%E8%BF%81%E7%A7%BB%E5%90%8E%E5%B0%86%E4%BC%9A%E5%BD%B1%E5%93%8D%E5%88%B0%E8%99%9A%E6%8B%9F%E6%9C%BA%E7%9A%84%E6%80%A7%E8%83%BD%EF%BC%8C%E5%BA%94%E4%BF%9D%E8%AF%81%E7%9B%AE%E7%9A%84%E7%AB%AF%E7%89%A9%E7%90%86%E6%9C%BACPU%E6%A0%B8%E6%95%B0%E5%A4%A7%E4%BA%8E%E7%AD%89%E4%BA%8E%E6%BA%90%E7%AB%AF%E8%99%9A%E6%8B%9F%E6%9C%BAvCPU%E6%95%B0%E3%80%82](https://docs.openeuler.org/zh/docs/20.09/docs/Virtualization/%E7%83%AD%E8%BF%81%E7%A7%BB%E8%99%9A%E6%8B%9F%E6%9C%BA.html#:~:text=%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9%E5%92%8C%E7%BA%A6%E6%9D%9F%E9%99%90%E5%88%B6%20*%20%E7%83%AD%E8%BF%81%E7%A7%BB%E8%BF%87%E7%A8%8B%E4%B8%AD%EF%BC%8C%E9%9C%80%E8%A6%81%E4%BF%9D%E8%AF%81%E7%BD%91%E7%BB%9C%E7%8A%B6%E6%80%81%E8%89%AF%E5%A5%BD%E3%80%82%20%E5%A6%82%E6%9E%9C%E5%8F%91%E7%94%9F%E7%BD%91%E7%BB%9C%E4%B8%AD%E6%96%AD%EF%BC%8C%E7%83%AD%E8%BF%81%E7%A7%BB%E4%BC%9A%E6%9A%82%E5%81%9C%EF%BC%8C%E7%9B%B4%E5%88%B0%E7%BD%91%E7%BB%9C%E6%81%A2%E5%A4%8D%E5%90%8E%E6%89%8D%E4%BC%9A%E7%BB%A7%E7%BB%AD%EF%BC%8C%E5%BD%93%E5%8F%91%E7%94%9F%E8%B6%85%E6%97%B6%EF%BC%8C%E7%83%AD%E8%BF%81%E7%A7%BB%E4%BC%9A%E5%A4%B1%E8%B4%A5%E3%80%82%20*%20%E8%BF%81%E7%A7%BB%E8%BF%87%E7%A8%8B%E4%B8%AD%EF%BC%8C%E4%B8%8D%E5%85%81%E8%AE%B8%E5%AF%B9%E8%99%9A%E6%8B%9F%E6%9C%BA%E8%BF%9B%E8%A1%8C%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F%E5%92%8C%E7%AE%A1%E7%90%86%E8%99%9A%E6%8B%9F%E6%9C%BA%E7%A1%AC%E4%BB%B6%E8%AE%BE%E5%A4%87%E7%AD%89%E6%93%8D%E4%BD%9C%E3%80%82%20*,%E8%99%9A%E6%8B%9F%E6%9C%BA%E6%AD%A3%E5%9C%A8%E8%BF%81%E7%A7%BB%E7%9A%84%E8%BF%87%E7%A8%8B%E4%B8%AD%EF%BC%8C%E4%B8%8D%E5%85%81%E8%AE%B8%E5%AF%B9%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%81%9A%E5%85%B3%E6%9C%BA%E3%80%81%E9%87%8D%E5%90%AF%E6%88%96%E6%81%A2%E5%A4%8D%E6%93%8D%E4%BD%9C%EF%BC%8C%E5%90%A6%E5%88%99%E5%8F%AF%E8%83%BD%E4%BC%9A%E5%AF%BC%E8%87%B4%E7%83%AD%E8%BF%81%E7%A7%BB%E5%A4%B1%E8%B4%A5%EF%BC%8C%E5%BD%93%E6%89%A7%E8%A1%8CACPI%E6%96%B9%E5%BC%8F%E9%87%8D%E5%90%AF%E6%97%B6%EF%BC%8C%E5%86%8D%E6%89%A7%E8%A1%8C%E7%83%AD%E8%BF%81%E7%A7%BB%E4%BC%9A%E5%AF%BC%E8%87%B4%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%85%B3%E9%97%AD%E3%80%82%20*%20%E5%8F%AA%E6%94%AF%E6%8C%81%E5%90%8C%E6%9E%84%E7%83%AD%E8%BF%81%E7%A7%BB%EF%BC%8C%E5%8D%B3%E6%BA%90%E7%AB%AF%E5%92%8C%E7%9B%AE%E7%9A%84%E7%AB%AFCPU%E5%9E%8B%E5%8F%B7%E9%9C%80%E8%A6%81%E7%9B%B8%E5%90%8C%E3%80%82%20*%20%E8%B7%A8%E4%B8%9A%E5%8A%A1%E7%BD%91%E6%AE%B5%E8%99%9A%E6%8B%9F%E6%9C%BA%E8%BF%81%E7%A7%BB%E5%8F%AF%E4%BB%A5%E6%88%90%E5%8A%9F%EF%BC%8C%E4%BD%86%E6%98%AF%E5%88%B0%E7%9B%AE%E7%9A%84%E7%AB%AF%E5%90%8E%E4%BC%9A%E5%87%BA%E7%8E%B0%E7%BD%91%E7%BB%9C%E5%BC%82%E5%B8%B8%EF%BC%8C%E4%B8%BA%E4%BA%86%E9%98%B2%E6%AD%A2%E8%AF%A5%E6%83%85%E5%86%B5%E5%8F%91%E7%94%9F%EF%BC%8C%E9%9C%80%E8%A6%81%E7%94%A8%E6%88%B7%E4%BF%9D%E8%AF%81%E8%BF%81%E7%A7%BB%E4%B8%9A%E5%8A%A1%E7%BD%91%E6%AE%B5%E4%B8%80%E8%87%B4%E3%80%82%20*%20%E5%A6%82%E6%9E%9C%E6%BA%90%E7%AB%AF%E8%99%9A%E6%8B%9F%E6%9C%BAvCPU%E6%95%B0%E5%A4%A7%E4%BA%8E%E7%9B%AE%E7%9A%84%E7%AB%AF%E7%9A%84%E7%89%A9%E7%90%86%E6%9C%BACPU%E6%A0%B8%E6%95%B0%EF%BC%8C%E5%88%99%E8%BF%81%E7%A7%BB%E5%90%8E%E5%B0%86%E4%BC%9A%E5%BD%B1%E5%93%8D%E5%88%B0%E8%99%9A%E6%8B%9F%E6%9C%BA%E7%9A%84%E6%80%A7%E8%83%BD%EF%BC%8C%E5%BA%94%E4%BF%9D%E8%AF%81%E7%9B%AE%E7%9A%84%E7%AB%AF%E7%89%A9%E7%90%86%E6%9C%BACPU%E6%A0%B8%E6%95%B0%E5%A4%A7%E4%BA%8E%E7%AD%89%E4%BA%8E%E6%BA%90%E7%AB%AF%E8%99%9A%E6%8B%9F%E6%9C%BAvCPU%E6%95%B0%E3%80%82) |
| q_074 | openEuler Compass-CI 持续集成平台如何使用？如何提交自动化测试任务？ | maillist | tutorial | [https://atomgit.com/openeuler/compass-ci](https://atomgit.com/openeuler/compass-ci) |
| q_076 | openEuler sig-K8sDistro 如何在 openEuler 上维护和发布 Kubernetes 发行版？ | maillist | technical | — |
| q_077 | openEuler AI SIG（ai-infra）在 openEuler 上支持哪些 AI 推理和训练框架？ | maillist | feature | [https://gitee.com/openeuler/community/tree/master/sig/ai-infra](https://gitee.com/openeuler/community/tree/master/sig/ai-infra) |
| q_078 | openEuler 元戎（yuanrong）SIG 的职责是什么？ | maillist | technical | [https://www.openeuler.org/zh/sig/sig-YuanRong](https://www.openeuler.org/zh/sig/sig-YuanRong) |
| q_079 | openEuler 发行版兼容性认证的申请流程是什么？需要满足哪些条件？ | maillist | governance | [https://www.openeuler.org/zh/compatibility/hardware/](https://www.openeuler.org/zh/compatibility/hardware/) |
| q_080 | 如何向 openEuler 安全委员会报告 CVE 漏洞？安全漏洞披露流程是什么？ | maillist | governance | [https://www.openeuler.org/zh/security/vulnerability-reporting/](https://www.openeuler.org/zh/security/vulnerability-reporting/) |
| q_081 | openEuler openDesign SIG 在社区视觉设计中扮演什么角色？如何参与 UI/UX 贡献？ | maillist | governance | [https://gitee.com/openeuler/community/tree/master/sig/openDesign](https://gitee.com/openeuler/community/tree/master/sig/openDesign) |

---

## 一、安装与环境配置

### 1.1 系统安装

- **q_001** — 如何在个人电脑（PC）上安装 openEuler 操作系统？安装前需要做哪些准备？
- **q_004** — 如何在飞腾 D2000 处理器平台上安装 openEuler？有哪些已知兼容性问题？
- **q_019** — 鲲鹏 920 处理器的服务器应该安装哪个架构版本的 openEuler（X86 还是 AArch64）？
- **q_011** — 安装 openEuler 时 Anaconda 安装程序卡住无法继续，如何排查解决？

### 1.2 驱动与硬件

- **q_002** — 在 VMware 中安装 openEuler 22.03 时无法识别网卡，应如何安装虚拟机网卡驱动？
- **q_003** — openEuler 如何安装 WiFi 无线网卡驱动？
- **q_006** — openEuler 是否支持飞腾 E2000Q 处理器平台？如何验证硬件兼容性？
- **q_025** — openEuler 24.03 SP1 上安装英伟达显卡驱动时如何选择合适的 CUDA 版本？
- **q_031** — openEuler 24.03 LTS SP1 无法安装 NVIDIA 显卡驱动，如何解决？

### 1.3 软件配置

- **q_015** — openEuler 上如何安装 VirtualBox 虚拟机软件？
- **q_017** — openEuler 22.03 SP3 如何安装 XFCE 桌面环境？
- **q_029** — openEuler 如何禁用 /tmp 目录挂载为 tmpfs？有什么影响？

---

## 二、迁移与升级

- **q_009** — 如何使用 x2openEuler 工具将系统从 openEuler 20.03 原地升级到 22.03？
- **q_010** — CentOS 7.x 能否直接迁移到 openEuler 22.03 LTS？完整的迁移步骤和注意事项是什么？
- **q_013** — openEuler 22.03 SP3 如何升级到 24.03 版本？有哪些官方推荐迁移方式？
- **q_024** — Red Hat 7.9 迁移到 openEuler 时出现 'can not clean repo info before upgrade' 错误，如何解决？
- **q_023** — 安装 x2openEuler 工具后找不到 service_start.sh 脚本，如何解决？

---

## 三、故障排查

### 3.1 包管理器 / 仓库

- **q_014** — openEuler 22.03-lts 容器镜像启动后执行 yum update 报错，如何排查解决？
- **q_018** — 配置 openEuler 本地 DNF 仓库源时提示下载元数据失败，如何排查？
- **q_022** — openEuler 22.03 SP2 执行 dnf upgrade 失败，常见原因和解决方法有哪些？
- **q_030** — 将系统 Python 版本升级到 3.11 后导致 dnf/yum 命令不可用，如何恢复？

### 3.2 系统工具

- **q_008** — 安装 openEuler 后系统中找不到 man 命令，是什么原因？如何安装 man 帮助手册？
- **q_028** — openEuler 升级过程中网络中断导致 SSH 无法连接，如何恢复升级并修复系统？
- **q_032** — 误将 /usr 目录设置 chmod 777 导致无法切换 root 用户，如何修复 openEuler 系统权限？
- **q_027** — openEuler 系统强制关机后重启速度极慢（7-8 分钟），如何优化系统启动时间？

---

## 四、部署与运维

- **q_005** — openEuler 的 A-Ops 智能运维工具 gala-ops 如何安装和部署？
- **q_012** — openEuler 22.03 LTS 上如何搭建 Mail 邮件服务器（Postfix/Dovecot）？
- **q_020** — openEuler 22.03 ARM 架构上如何部署 Zabbix 监控系统？
- **q_007** — 如何通过 Open Build Service（OBS）为 openEuler 社区构建和发布软件包？

---

## 五、功能特性

- **q_016** — openEuler 22.03 LTS SP2 上如何修复 CVE-2024-1086 内核提权漏洞？
- **q_021** — openEuler 22.03 SP1 是否支持将内核升级到 6.x 版本？如何操作？
- **q_026** — openEuler Embedded 是否支持通过 yum/dnf 在线安装软件包？

---

## 六、社区治理与参与（SIG）

- **q_033** — openEuler 社区有哪些 SIG 组（特别兴趣小组），如何查看完整的 SIG 列表？
- **q_034** — 如何订阅 openEuler 社区邮件列表（如 dev@openeuler.org）参与技术讨论？
- **q_035** — 如何加入 openEuler sig-Migration SIG，参与跨平台 OS 迁移相关开发贡献？
- **q_037** — openEuler AI SIG（ai-infra@openeuler.org）的目标是什么？支持哪些 AI 基础设施框架？
- **q_038** — openEuler sig-QA 如何进行版本质量测试？如何参与社区 QA 贡献？
- **q_039** — openEuler Embedded 操作系统有哪些应用场景？支持哪些嵌入式硬件平台？
- **q_040** — 如何向 openEuler TSC 提交 SIG 申请，新建特别兴趣小组的流程是什么？
- **q_041** — openEuler 社区版本的生命周期是如何规划的？LTS 版本与创新版本在支持周期和适用场景上有何区别？
- **q_044** — 如何加入 openEuler A-Tune SIG 组参与系统性能自调优工具的开发？
- **q_055** — 如何参与 openEuler 版本 RC 测试阶段？issue 提交和修复流程是什么？
- **q_056** — openEuler 新版本分支初始化时，SIG maintainer 如何参与 PR 检视流程？
- **q_057** — openEuler 版本发布前如何处理降级的 issue？release 公告会包含哪些内容？
- **q_060** — 如何参与 openEuler CloudNative SIG 双周例会？议题如何提交？
- **q_062** — 如何向 openEuler dev 邮件列表提交技术提案（RFC）或发起社区讨论？
- **q_063** — 如何申请在 openEuler 官方网站添加新的全球镜像节点？
- **q_064** — openEuler 社区版本生命周期变更和发布节奏调整的公示流程是什么？
- **q_079** — openEuler 发行版兼容性认证的申请流程是什么？需要满足哪些条件？
- **q_080** — 如何向 openEuler 安全委员会报告 CVE 漏洞？安全漏洞披露流程是什么？
- **q_081** — openEuler openDesign SIG 在社区视觉设计中扮演什么角色？如何参与 UI/UX 贡献？

---

## 七、SIG 技术领域

### 7.1 系统性能与硬件加速

- **q_042** — A-Tune 自调优工具在分布式场景下如何将客户端和服务端部署在不同机器上？
- **q_043** — openEuler A-Tune 如何对 MySQL 数据库进行自动性能调优？
- **q_045** — openEuler 上如何使用 UADK 进行用户态硬件加速开发？
- **q_046** — openEuler 鲲鹏 UADK 支持哪些加密算法（SM4、AES、RSA、SHA 等）？
- **q_047** — openEuler 如何查询鲲鹏加速器（hisilicon qm）的硬件故障状态？

### 7.2 云原生与虚拟化

- **q_058** — openEuler CloudNative SIG 支持哪些云原生组件（containerd、iSula、kata-containers）？
- **q_059** — openEuler 上如何引入和使用 composefs 实现容器镜像只读挂载文件系统？
- **q_070** — 如何在 openEuler 24.03 LTS 上部署 OpenStack Antelope 版本？
- **q_068** — openEuler 22.03 LTS-SP3 是否支持 DevStack 部署 OpenStack？
- **q_071** — openEuler Virt SIG 支持哪些虚拟化技术（KVM、QEMU、libvirt）？
- **q_073** — openEuler 虚拟机如何支持 vNMI 热迁移？
- **q_076** — openEuler sig-K8sDistro 如何在 openEuler 上维护和发布 Kubernetes 发行版？

### 7.3 大数据与 AI

- **q_048** — openEuler BigData SIG 支持哪些大数据组件（Hadoop、Spark、Flink 等）？
- **q_049** — 如何在 openEuler 上快速搭建大数据集群？BigData SIG 提供哪些工具支持？
- **q_077** — openEuler AI SIG（ai-infra）在 openEuler 上支持哪些 AI 推理和训练框架？
- **q_078** — openEuler 元戎（yuanrong）SIG 的职责是什么？

### 7.4 内核与存储

- **q_053** — openEuler SDS SIG 中 Lustre 文件系统如何适配 openEuler 6.6 内核？
- **q_054** — openEuler 分布式存储（sig-SDS）SIG 支持哪些存储组件？
- **q_065** — openEuler OLK-6.6 内核 CPPC 调频驱动使用 ktime 替代 jiffies 的背景是什么？
- **q_066** — openEuler xSched 调度器的 xcu cmdline 参数如何动态切换 cgroup 调度模式？
- **q_067** — 向 openEuler OLK 内核树提交补丁的格式要求是什么？

### 7.5 软件包与基础设施

- **q_050** — 如何从头开始本地构建 openEuler ISO 镜像？EulerMaker 如何使用？
- **q_052** — openEuler RPM 包的 spec 文件在哪个仓库管理？如何贡献新软件包？
- **q_061** — openEuler 24.03-LTS-SP4 中 OpenSSL 升级到 3.5.x 对应用兼容性有哪些影响？
- **q_074** — openEuler Compass-CI 平台如何使用？如何提交自动化测试任务？
