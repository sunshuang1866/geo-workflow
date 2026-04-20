# GEO 问题集

> 生成时间: 2026-04-20
> 社区: openEuler
> 总数: 119

## 概览

| 意图 | 数量 |
|------|------|
| 认知 | 51 |
| 选型 | 0 |
| 趋势 | 0 |
| 场景 | 21 |
| 教程 | 30 |
| 故障 | 15 |
| 特性 | 0 |
| 迁移 | 2 |

| 来源 | 数量 |
|------|------|
| 手动输入 | 0 |
| 论坛 | 53 |
| Issue | 0 |
| 邮件列表 | 0 |
| 网站搜索 | 0 |

## 筛选标准

| 来源 | 评分算法 | 筛选方式 | 获取时间 |
|------|----------|----------|----------|
| 论坛 | sorted by views descending | top 100 from 1147 ranked topics (views > 50) | 2026-04-20 |

---

### 认知

| # | 问题 | 来源 | Views |
|---|------|------|-------|
| 1 | 如何在个人电脑（PC）上安装 openEuler 操作系统？安装前需要做哪些准备？ | - | - |
| 2 | 如何在飞腾 D2000 处理器平台上安装 openEuler？有哪些已知兼容性问题？ | - | - |
| 3 | openEuler 是否支持飞腾 E2000Q 处理器平台？如何验证硬件兼容性？ | - | - |
| 4 | 如何通过 Open Build Service（OBS）为 openEuler 社区构建和发布软件包？ | - | - |
| 5 | CentOS 7.x 能否直接迁移到 openEuler 22.03 LTS？完整的迁移步骤和注意事项是什么？ | - | - |
| 6 | openEuler 22.03 SP3 如何升级到 24.03 版本？有哪些官方推荐迁移方式？ | - | - |
| 7 | 鲲鹏 920 处理器的服务器应该安装哪个架构版本的 openEuler（X86 还是 AArch64）？ | - | - |
| 8 | openEuler 22.03 SP1 是否支持将内核升级到 6.x 版本？如何操作？ | - | - |
| 9 | openEuler 24.03 SP1 上安装英伟达显卡驱动时如何选择合适的 CUDA 版本？ | - | - |
| 10 | openEuler Embedded 是否支持通过 yum/dnf 在线安装软件包？ | - | - |
| 11 | 将系统 Python 版本升级到 3.11 后导致 dnf/yum 命令不可用，如何恢复？ | - | - |
| 12 | openEuler 社区有哪些 SIG 组（特别兴趣小组），如何查看完整的 SIG 列表？ | - | - |
| 13 | 如何订阅 openEuler 社区邮件列表（如 dev@openeuler.org）参与技术讨论？ | - | - |
| 14 | 如何加入 openEuler sig-Migration SIG，参与跨平台 OS 迁移相关开发贡献？ | - | - |
| 15 | openEuler AI SIG（ai-infra@openeuler.org）的目标是什么？支持哪些 AI 基础设施框架？ | - | - |
| 16 | openEuler sig-QA 如何进行版本质量测试？如何参与社区 QA 贡献？ | - | - |
| 17 | openEuler Embedded 操作系统有哪些应用场景？支持哪些嵌入式硬件平台？ | - | - |
| 18 | 如何向 openEuler TSC 提交 SIG 申请，新建特别兴趣小组的流程是什么？ | - | - |
| 19 | openEuler LTS 版本与创新版本在支持周期和适用场景上有何区别？ | - | - |
| 20 | 如何加入 openEuler A-Tune SIG 组参与系统性能自调优工具的开发？ | - | - |
| 21 | openEuler 鲲鹏 UADK 支持哪些加密算法（SM4、AES、RSA、SHA 等）？如何调用加速接口？ | - | - |
| 22 | openEuler BigData SIG 支持哪些大数据组件（Hadoop、Spark、Flink 等）？ | - | - |
| 23 | EulerMaker 构建系统的使用流程是什么？ | - | - |
| 24 | openEuler RPM 包的 spec 文件在哪个仓库管理？如何为 openEuler 贡献新的软件包？ | - | - |
| 25 | openEuler 分布式存储（sig-SDS）SIG 支持哪些存储组件（Ceph、Lustre、DBS）？ | - | - |
| 26 | openEuler 新版本分支初始化时，SIG maintainer 如何参与 PR 检视流程？ | - | - |
| 27 | openEuler 版本发布 release公告会包含哪些内容？ | - | - |
| 28 | openEuler CloudNative SIG 支持哪些云原生组件（containerd、iSula、kata-containers 等）？ | - | - |
| 29 | 如何参与 openEuler CloudNative SIG 双周例会？议题如何提交和跟踪？ | - | - |
| 30 | 如何向 openEuler dev 邮件列表提交技术提案（RFC）或发起社区讨论？ | - | - |
| 31 | 如何申请在 openEuler 官方网站添加新的全球镜像节点（public mirror）？有哪些申请条件？ | - | - |
| 32 | openEuler 社区版本生命周期是什么？ | - | - |
| 33 | 向 openEuler Kernal SIG 提交补丁的格式要求是什么？ | - | - |
| 34 | openEuler 支持哪些虚拟化技术（KVM、QEMU、libvirt）？ | - | - |
| 35 | openEuler 虚拟机如何支持 vNMI（虚拟 NMI）热迁移？ | - | - |
| 36 | openEuler AI SIG 在 openEuler 上支持哪些 AI 推理框架？ | - | - |
| 37 | openEuler 元戎（yuanrong）SIG 的职责是什么？ | - | - |
| 38 | openEuler 发行版兼容性认证（OS 兼容性认证）的申请流程是什么？需要满足哪些条件？ | - | - |
| 39 | 如何向 openEuler 安全委员会（security@openeuler.org）报告 CVE 安全漏洞？漏洞披露流程是什么？ | - | - |
| 40 | openEuler openDesign SIG 在社区视觉设计中扮演什么角色？ | - | - |
| 41 | 如何获取和使用 openEuler 官方容器镜像？支持哪些架构的容器镜像？ | 论坛 | 9290 |
| 42 | 如何在 openEuler 上从源码编译安装自定义内核？内核编译的基本流程是什么？ | 论坛 | 7439 |
| 43 | openEuler 各常用组件和服务的默认用户名与密码分别是什么？ | 论坛 | 6400 |
| 44 | 如何在 openEuler 中使用 NetworkManager 管理和重启网络服务？nmcli 常用命令有哪些？ | 论坛 | 6334 |
| 45 | openEuler 各发行版本（20.03/22.03/24.03 等）对应的默认内核版本分别是什么？ | 论坛 | 4550 |
| 46 | 如何在 openEuler 上将 OpenSSL 升级到指定版本？ | 论坛 | 4345 |
| 47 | openEuler 的 oec-hardware 硬件兼容性测试工具如何使用？如何通过它提交硬件兼容性认证？ | 论坛 | 3815 |
| 48 | 学习 openEuler Linux 内核有哪些推荐的入门路径和参考资源？ | 论坛 | 3679 |
| 49 | HCIP-openEuler 认证考试涵盖哪些内容？如何报名和备考？ | 论坛 | 3507 |
| 50 | 企业如何签署 openEuler 社区 CLA（贡献者许可协议），正式加入 openEuler 社区？ | 论坛 | 3307 |
| 51 | openEuler 支持运行中不重启升级内核（内核热升级）吗？如何使用相关功能？ | 论坛 | 3216 |

### 场景

| # | 问题 | 来源 | Views |
|---|------|------|-------|
| 52 | 安装 x2openEuler 工具后找不到 service_start.sh 脚本，如何解决？ | - | - |
| 53 | openEuler 系统强制关机后重启速度极慢（7-8 分钟），如何优化系统启动时间？ | - | - |
| 54 | openEuler 如何禁用 /tmp 目录挂载为 tmpfs？有什么影响？ | - | - |
| 55 | openEuler 上如何引入和使用 composefs 实现容器镜像的只读挂载文件系统？ | - | - |
| 56 | openEuler Compass-CI 持续集成平台如何使用？如何提交自动化测试任务验证软件包？ | - | - |
| 57 | 忘记 openEuler root 密码后如何在不重装系统的情况下重置密码？ | 论坛 | 11418 |
| 58 | 如何在离线（无网络）环境下将 Docker 安装到 openEuler 系统？ | 论坛 | 6602 |
| 59 | 如何在 openEuler 上关闭防火墙（firewalld）和 SELinux？ | 论坛 | 5779 |
| 60 | 如何在 openEuler ISO 镜像中添加自定义 RPM 包并重新构建 ISO 安装镜像？ | 论坛 | 4931 |
| 61 | 如何在 openEuler 上安装 DDE（深度桌面环境）图形界面？ | 论坛 | 4709 |
| 62 | openEuler 安装后系统缺少 tar、make 等基础开发工具，如何在离线内网环境中安装这些工具？ | 论坛 | 4032 |
| 63 | 如何在配备 RAID 控制卡的服务器上安装 openEuler 操作系统？ | 论坛 | 3834 |
| 64 | 如何在 openEuler 上安装 MongoDB 数据库？ | 论坛 | 3799 |
| 65 | 如何查询硬件设备与 openEuler 的兼容性？官方硬件兼容性列表在哪里查看？ | 论坛 | 3796 |
| 66 | 如何在 openEuler 22.03 上使用 yum/dnf 安装 PostgreSQL 数据库单机环境？ | 论坛 | 3579 |
| 67 | openEuler 22.03 LTS 系统重启后磁盘盘符（如 sda/sdb）发生变化，如何通过 UUID 或 by-id 固定磁盘标识符？ | 论坛 | 3507 |
| 68 | 如何在 openEuler 上测试 InfiniBand 网卡的连通性和带宽性能？ | 论坛 | 3274 |
| 69 | 如何在 openEuler 上开启 SSH 的 X11 Forwarding，通过 SSH 转发图形界面应用？ | 论坛 | 3106 |
| 70 | 如何在 openEuler 上安装 ROS2 Humble 机器人操作系统框架？ | 论坛 | 2993 |
| 71 | 如何在 openEuler 22.03 LTS SP1（x86_64）上将 Intel 网卡驱动源码编译打包成 RPM 包？ | 论坛 | 2929 |
| 72 | 如何在 openEuler 22.03 aarch64 架构上安装 Qt Creator 开发环境？ | 论坛 | 2852 |

### 教程

| # | 问题 | 来源 | Views |
|---|------|------|-------|
| 73 | 在 VMware 中安装 openEuler 22.03 时无法识别网卡，应如何安装虚拟机网卡驱动？ | - | - |
| 74 | openEuler 如何安装 WiFi 无线网卡驱动？ | - | - |
| 75 | openEuler 的 A-Ops 智能运维工具 gala-ops 如何安装和部署？ | - | - |
| 76 | 安装 openEuler 后系统中找不到 man 命令，是什么原因？如何安装 man 帮助手册？ | - | - |
| 77 | openEuler 22.03 LTS 上如何搭建 Mail 邮件服务器（Postfix/Dovecot）？ | - | - |
| 78 | openEuler 上如何安装 VirtualBox 虚拟机软件？ | - | - |
| 79 | openEuler 22.03 SP3 如何安装 XFCE 桌面环境？ | - | - |
| 80 | 配置 openEuler 本地 DNF 仓库源时提示下载元数据失败，如何排查？ | - | - |
| 81 | openEuler 22.03 ARM 架构上如何部署 Zabbix 监控系统？ | - | - |
| 82 | 误将 /usr 目录设置 chmod 777 导致无法切换 root 用户，如何修复 openEuler 系统权限？ | - | - |
| 83 | 如何在 openEuler 上利用 EulerLauncher 或 BigData SIG 工具快速搭建大数据集群？ | - | - |
| 84 | 如何在 openEuler 24.03 LTS 上使用官方 sig-OpenStack 工具部署 OpenStack Antelope？ | - | - |
| 85 | 如何配置 openEuler 的软件仓库（repo 源）？有哪些常用的官方 repo 源地址？ | 论坛 | 38170 |
| 86 | 如何在 openEuler 上安装 Xfce 桌面环境并配置 xrdp 实现 Windows 远程桌面连接？ | 论坛 | 6847 |
| 87 | openEuler 系统 DNS 域名解析失败（ping 域名提示 Name or service not known），如何排查和修复网络 DNS 配置？ | 论坛 | 6562 |
| 88 | 如何在 openEuler 上搭建 Samba 文件共享服务，实现与 Windows 的文件共享？ | 论坛 | 5156 |
| 89 | 在 openEuler 中修改 ifcfg-ethX 网卡配置文件后网络设置不生效，如何通过 NetworkManager 正确应用配置？ | 论坛 | 4547 |
| 90 | 如何在 openEuler 上安装和配置 DPDK（数据平面开发套件）？ | 论坛 | 4453 |
| 91 | 如何在 openEuler 22.03 LTS 上使用 kubeadm 部署 Kubernetes 集群？ | 论坛 | 4210 |
| 92 | 如何在 openEuler 上搭建 FTP 服务器（vsftpd）？配置虚拟账户后无法登录如何排查？ | 论坛 | 4090 |
| 93 | 如何在 openEuler 上配置 sudo，为普通用户授予特定命令的 root 执行权限？ | 论坛 | 3925 |
| 94 | 如何在 openEuler 22.03 LTS 上以二进制方式部署 MySQL 5.7？ | 论坛 | 3887 |
| 95 | 在 openEuler 上修改 IP 地址后，如何刷新网络配置使其立即生效？ | 论坛 | 3576 |
| 96 | openEuler 系统中出现中文显示乱码，如何设置正确的系统语言和字符编码？ | 论坛 | 3563 |
| 97 | openEuler 内核崩溃时如何配置 kdump 记录崩溃现场？如何分析生成的 vmcore 文件？ | 论坛 | 3430 |
| 98 | 如何在 openEuler 上配置 Mellanox 网卡的 SR-IOV VF（虚拟功能）？ | 论坛 | 3390 |
| 99 | 如何基于 Cobbler 实现 openEuler 系统的自动化批量网络安装部署？ | 论坛 | 3371 |
| 100 | 如何在 openEuler 上搭建本地 Docker 私有镜像仓库（Registry）？ | 论坛 | 3132 |
| 101 | openEuler 22.03 LTS 如何通过配置限制 SSH 登录的允许 IP 地址（访问控制白名单）？ | 论坛 | 3044 |
| 102 | 如何在 openEuler 上搭建 NFS 网络文件系统服务供其他主机挂载使用？ | 论坛 | 2837 |

### 故障

| # | 问题 | 来源 | Views |
|---|------|------|-------|
| 103 | 安装 openEuler 时 Anaconda 安装程序卡住无法继续，如何排查解决？ | - | - |
| 104 | openEuler 22.03-lts 容器镜像启动后执行 yum update 报错，如何排查解决？ | - | - |
| 105 | openEuler 22.03 LTS SP2 上如何修复 CVE-2024-1086 内核提权漏洞？ | - | - |
| 106 | openEuler 22.03 SP2 执行 dnf upgrade 失败，常见原因和解决方法有哪些？ | - | - |
| 107 | Red Hat 7.9 迁移到 openEuler 时出现 'can not clean repo info before upgrade' 错误，如何解决？ | - | - |
| 108 | openEuler 升级过程中网络中断导致 SSH 无法连接，如何恢复升级并修复系统？ | - | - |
| 109 | openEuler 24.03 LTS SP1 无法安装 NVIDIA 显卡驱动，如何解决？ | - | - |
| 110 | 如何参与 openEuler 版本 RC 测试阶段，发现问题后的 issue 提交和修复流程是什么？ | - | - |
| 111 | 在 openEuler 22.03 上使用 KVM 创建虚拟机时报 qxl 显卡相关错误，如何解决？ | 论坛 | 4132 |
| 112 | 如何在 openEuler 22.03 LTS 上安装 Docker CE？安装时常见错误如何解决？ | 论坛 | 4081 |
| 113 | openEuler 普通用户执行 su root 时提示 Permission denied，原因是什么，如何解决？ | 论坛 | 3769 |
| 114 | 在 openEuler 上使用 yum/dnf 安装软件时报 'GPG check FAILED' 错误，如何解决？ | 论坛 | 3700 |
| 115 | openEuler syscare 内核热补丁工具如何使用？支持哪些在线热修复场景？ | 论坛 | 3465 |
| 116 | 在 openEuler 上安装 UKUI 桌面环境后重启无法进入登录界面，如何排查解决？ | 论坛 | 3069 |
| 117 | openEuler 虚拟机非正常关机后重启出现文件系统错误，如何修复？ | 论坛 | 2972 |

### 迁移

| # | 问题 | 来源 | Views |
|---|------|------|-------|
| 118 | 如何使用 x2openEuler 工具将系统从 openEuler 20.03 原地升级到 22.03？ | - | - |
| 119 | 如何使用 x2openEuler 管理升级任务，包括删除、修改或重新执行已有升级任务？ | 论坛 | 4001 |
