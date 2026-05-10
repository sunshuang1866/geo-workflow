# openEuler GEO 引用评估报告

> 匹配规则：URL 精确匹配（response_text 子串 + citations 前缀匹配），归一化去除 http/https、www.、尾部斜杠，不区分大小写，排除纯域名匹配（防误报）；引用阈值 ≥ 75%
> ✅ 引用官方链接 ｜ ❌ 未引用 ｜ 🔘 无官方链接（P1）｜ — 该轮未采样

| 采样轮次 | 日期 | 平台 | 采样方式 |
|----------|------|------|----------|
| Run 1 | 2026-04-02 | DeepSeek · Qwen | 浏览器 |
| Run 2 | 2026-04-07 | DeepSeek · Qwen | 浏览器 |
| Run 3 | 2026-05-10 | DeepSeek · Qwen | 浏览器|

---

## 对比总表

| ID | 问题 | DS(04-02) | Qw(04-02) | DS(04-07) | Qw(04-07) | DS-web(05-10) | Qw-web(05-10) | 官方链接 |
|---|---|---|---|---|---|---|---|---|
| q_001 | 如何在个人电脑（PC）上安装 openEuler 操作系统？ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | [6872](https://forum.openeuler.org/t/topic/6872) |
| q_002 | 在 VMware 中安装 openEuler 22.03 时无法识别网卡，应如何安装虚拟机网卡驱动？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [7378](https://forum.openeuler.org/t/topic/7378) |
| q_003 | openEuler 如何安装 WiFi 无线网卡驱动？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [294](https://forum.openeuler.org/t/topic/294) |
| q_004 | 如何在飞腾 D2000 处理器平台上安装 openEuler？有哪些已知兼容性问题？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [19010](https://forum.openeuler.org/t/topic/19010) |
| q_005 | openEuler 的 A-Ops 智能运维工具 gala-ops 如何安装和部署？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [deploying_aops.html](https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/server/aops/deploying_aops.html) |
| q_007 | 如何通过 Open Build Service（OBS）为 openEuler 社区构建和发布软件包？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [875](https://forum.openeuler.org/t/topic/875) |
| q_008 | 安装 openEuler 后系统中找不到 man 命令，是什么原因？如何安装 man 帮助手册？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [220](https://forum.openeuler.org/t/topic/220) |
| q_009 | 如何使用 x2openEuler 工具将系统从 openEuler 20.03 原地升级到 22.03？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [migration](https://www.openeuler.openatom.cn/zh/migration/) |
| q_010 | CentOS 7.x 直接迁移到 openEuler 22.03 LTS 的完整的迁移步骤和注意事项是什么？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [migration](https://www.openeuler.openatom.cn/zh/migration/) |
| q_011 | 安装 openEuler 时 Anaconda 安装程序卡住无法继续，如何排查解决？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [3222](https://forum.openeuler.org/t/topic/3222) |
| q_012 | openEuler 22.03 LTS 上如何搭建 Mail 邮件服务器（Postfix/Dovecot）？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [246](https://forum.openeuler.org/t/topic/246) |
| q_013 | openEuler 22.03 SP3 如何升级到 24.03 版本？有哪些官方推荐迁移方式？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [4572](https://forum.openeuler.org/t/topic/4572) |
| q_014 | openEuler 22.03-lts 容器镜像启动后执行 yum update 报错，如何排查解决？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [2200](https://forum.openeuler.org/t/topic/2200) |
| q_015 | openEuler 上如何安装 VirtualBox 虚拟机软件？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [4549](https://forum.openeuler.org/t/topic/4549) |
| q_016 | openEuler 22.03 LTS SP2 上如何修复 CVE-2024-1086 内核提权漏洞？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [4537](https://forum.openeuler.org/t/topic/4537) |
| q_017 | openEuler 22.03 SP3 如何安装 XFCE 桌面环境？ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | [18345](https://forum.openeuler.org/t/topic/18345) |
| q_018 | 配置 openEuler 本地 DNF 仓库源时提示下载元数据失败，如何排查？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [2964](https://forum.openeuler.org/t/topic/2964) |
| q_020 | openEuler 22.03 ARM 架构上如何部署 Zabbix 监控系统？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [4780](https://forum.openeuler.org/t/topic/4780) |
| q_022 | openEuler 22.03 SP2 执行 dnf upgrade 失败，常见原因和解决方法有哪些？ | ❌ | ❌ | ❌ | ❌ | — | — | [2](https://forum.openeuler.org/t/topic/4897/2) |
| q_023 | 安装 x2openEuler 工具后找不到 service_start.sh 脚本，如何解决？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [3396](https://forum.openeuler.org/t/topic/3396) |
| q_024 | Red Hat 7.9 迁移到 openEuler 时出现 'can not clean repo info before upgrade' 错误，如何解决？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [3959](https://forum.openeuler.org/t/topic/3959) |
| q_025 | openEuler 24.03 SP1 上安装英伟达显卡驱动时如何选择合适的 CUDA 版本？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [6895](https://forum.openeuler.org/t/topic/6895) |
| q_026 | openEuler Embedded 是否支持通过 yum/dnf 在线安装软件包？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [4365](https://forum.openeuler.org/t/topic/4365) |
| q_027 | openEuler 系统强制关机后重启速度极慢（7-8 分钟），如何优化系统启动时间？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [3612](https://forum.openeuler.org/t/topic/3612) |
| q_028 | openEuler 升级过程中网络中断导致 SSH 无法连接，如何恢复升级并修复系统？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [3328](https://forum.openeuler.org/t/topic/3328) |
| q_029 | openEuler 如何禁用 /tmp 目录挂载为 tmpfs？有什么影响？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [4266](https://forum.openeuler.org/t/topic/4266) |
| q_030 | 将系统 Python 版本升级到 3.11 后导致 dnf/yum 命令不可用，如何恢复？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [6230](https://forum.openeuler.org/t/topic/6230) |
| q_031 | openEuler 24.03 LTS SP1 无法安装 NVIDIA 显卡驱动，如何解决？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [6960](https://forum.openeuler.org/t/topic/6960) |
| q_032 | 误将 /usr 目录设置 chmod 777 导致无法切换 root 用户，如何修复 openEuler 系统权限？ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | [4337](https://forum.openeuler.org/t/topic/4337) |
| q_033 | openEuler 社区有哪些 SIG 组（特别兴趣小组），如何查看完整的 SIG 列表？ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | [sig-list](https://www.openeuler.openatom.cn/zh/sig/sig-list/) |
| q_034 | 如何订阅 openEuler 社区邮件列表（如 dev@openeuler.org）参与技术讨论？ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | [dev-utils](https://www.openeuler.openatom.cn/zh/sig/dev-utils) |
| q_035 | 如何加入 openEuler sig-Migration SIG，参与跨平台 OS 迁移相关开发贡献？ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | [sig-Migration](https://www.openeuler.openatom.cn/zh/sig/sig-Migration) |
| q_037 | openEuler AI SIG（ai-infra@openeuler.org）的目标是什么？支持哪些 AI 基础设施框架？ | ❌ | ❌ | ❌ | ❌ | — | — | [ai](https://www.openeuler.openatom.cn/zh/sig/ai) |
| q_038 | openEuler sig-QA 如何进行版本质量测试？如何参与社区 QA 贡献？ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | [sig-QA](https://www.openeuler.openatom.cn/zh/sig/sig-QA) |
| q_039 | openEuler Embedded 操作系统有哪些应用场景？支持哪些嵌入式硬件平台？ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | [index.html](https://docs.openeuler.openatom.cn/zh/docs/24.03_LTS_SP3/embedded/index.html) |
| q_041 | openEuler LTS 版本与创新版本在支持周期和适用场景上有何区别？ | — | — | ❌ | ❌ | ✅ | ❌ | [lifecycle](https://www.openeuler.org/zh/other/lifecycle/) |
| q_044 | 如何加入 openEuler A-Tune SIG 组参与系统性能自调优工具的开发？ | — | — | ❌ | ❌ | ❌ | ✅ | [general_faq.html](https://docs.openeuler.org/zh/docs/common/faq/general/general_faq.html) |
| q_046 | openEuler 鲲鹏 UADK 支持哪些加密算法（SM4、AES、RSA、SHA 等）？如何调用加速接口？ | — | — | ❌ | ❌ | ❌ | ❌ | [uadk_quick_start.html](https://docs.openeuler.org/zh/docs/22.03_LTS_SP4/tools/community_tools/uadk/uadk_quick_start.html) |
| q_050 | EulerMaker 构建系统的使用流程是什么？ | — | — | ❌ | ❌ | ✅ | ❌ | [eulermaker.compass-ci.openeule](https://eulermaker.compass-ci.openeuler.openatom.cn/) |
| q_052 | openEuler RPM 包的 spec 文件在哪个仓库管理？如何为 openEuler 贡献新的软件包？ | — | — | ❌ | ❌ | ✅ | ❌ | [contribution](https://www.openeuler.org/zh/wiki/contribution/) |
| q_062 | 如何向 openEuler dev 邮件列表提交技术提案（RFC）或发起社区讨论？ | — | — | ✅ | ✅ | ✅ | ✅ | [0630-newcomer.html](https://www.openeuler.org/zh/blog/20230630-newcomer/0630-newcomer.html) |
| q_063 | 如何申请在 openEuler 官方网站添加新的全球镜像节点（public mirror）？有哪些申请条件？ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | [list](https://www.openeuler.org/zh/mirror/list/) |
| q_064 | openEuler 社区版本生命周期是什么？ | — | — | ❌ | ❌ | ✅ | ✅ | [lifecycle](https://www.openeuler.org/zh/other/lifecycle/) |
| q_070 | 如何在 openEuler 24.03 LTS 上使用官方 sig-OpenStack 工具部署 OpenStack Antelope？ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | [antelope.html](https://docs.openeuler.org/zh/docs/25.03/virtualization/virtualization_platform/openstack/install/antelope.html) |
| q_074 | openEuler Compass-CI 持续集成平台如何使用？如何提交自动化测试任务验证软件包？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [compass-ci](https://atomgit.com/openeuler/compass-ci) |
| q_079 | openEuler 发行版兼容性认证（OS 兼容性认证）的申请流程是什么？需要满足哪些条件？ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | [hardware](https://www.openeuler.org/zh/compatibility/hardware/) |
| q_080 | 如何向 openEuler 安全委员会（security@openeuler.org）报告 CVE 安全漏洞？漏洞披露流程是什么？ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | [vulnerability-reporting](https://www.openeuler.org/zh/security/vulnerability-reporting/) |

---

## 🔘 无官方链接（P1，6 题）

官方目前尚无对应内容，无法评估引用情况。

| ID | 问题 | 备注 |
|----|------|------|
| q_048 | openEuler BigData SIG 支持哪些大数据组件（Hadoop、Spark、Flink 等）？ | 采样期内无官方内容 |
| q_049 | 如何在 openEuler 上利用 EulerLauncher 或 BigData SIG 工具快速搭建大数据集群？ | 采样期内无官方内容 |
| q_054 | openEuler 分布式存储（sig-SDS）SIG 支持哪些存储组件（Ceph、Lustre、DBS）？ | 采样期内无官方内容 |
| q_056 | openEuler 新版本分支初始化时，SIG maintainer 如何参与 PR 检视流程？ | 采样期内无官方内容 |
| q_058 | openEuler CloudNative SIG 支持哪些云原生组件（containerd、iSula、kata-containers 等）？ | 采样期内无官方内容 |
| q_059 | openEuler 上如何引入和使用 composefs 实现容器镜像的只读挂载文件系统？ | 采样期内无官方内容 |
