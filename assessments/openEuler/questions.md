# openEuler 问题集

## 概览

- 社区: openEuler
- 生成时间: 2026-04-27
- 问题总数: 240

### 来源渠道

| 渠道 | 状态 |
|------|------|
| 论坛帖子 | ✅ 有数据 |
| 仓库 Issue | ✅ 有数据 |
| 邮件列表 | ✅ 有数据 |

### 筛选标准

| 来源 | 评分算法 | 筛选方式 | 获取时间 |
|------|----------|----------|----------|
| MongoDB 聚合话题 | 咨询数 ≥ 2，按咨询数降序 | consult-filter + 白名单过滤（仅保留用户导向问题） | 2026-04-23 |
| 论坛（Discourse/PG） | 按 created_at 降序 | top 30 后过滤新闻/公告/建议，取 top 20，去重 | 2026-04-27 |
| 人工整理 | — | 历史导入 | 2026-04-21 |

## 分类目录

- [安装与部署](#安装与部署)（81 条）
- [系统管理](#系统管理)（66 条）
- [内核与驱动](#内核与驱动)（10 条）
- [安全与漏洞](#安全与漏洞)（12 条）
- [虚拟化与容器](#虚拟化与容器)（11 条）
- [软件包与构建](#软件包与构建)（16 条）
- [社区与生态](#社区与生态)（33 条）
- [嵌入式与边缘](#嵌入式与边缘)（11 条）


## 安装与部署

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler部署组件因依赖缺失或版本不兼容导致服务启动失败，如何解决？ | 8c/0e/8t |
| 2 | openEuler QEMU ARM虚拟机因zImage兼容性及UEFI安全启动问题导致启动失败，如何解决？ | 7c/0e/7t |
| 3 | openEuler RISC-V架构QEMU 8.2.0 KVM虚拟机ACPI启动失败，如何解决？ | 4c/0e/4t |
| 4 | openEuler部署etcd启用证书与鉴权时worker因缺少用户名密码参数启动失败，如何解决？ | 3c/0e/3t |
| 5 | openEuler LoongArch版桌面环境依赖包缺失导致安装失败，如何解决？ | 3c/0e/3t |
| 6 | openEuler cobbler buildiso在ARM/RISC-V架构下解包返回值异常，如何解决？ | 3c/0e/3t |
| 7 | euler-copilot-framework依赖管理缺失致安装阻塞，如何解决？ | 3c/0e/3t |
| 8 | openEuler RDMA服务ibacm与iwpmd启动失败致功能异常，如何解决？ | 2c/0e/2t |
| 9 | openEuler系统服务因依赖配置错误导致启动失败，如何解决？ | 2c/0e/2t |
| 10 | IPM软件因缺失DOWNLOAD配置项导致jarvis安装失败，如何解决？ | 2c/0e/2t |
| 11 | RK3588刷写openEuler后启动链配置异常导致无法启动，如何解决？ | 2c/0e/2t |
| 12 | openEuler RISC-V架构下lcr运行时因seccomp缺少syscall支持致容器启动失败，如何解决？ | 2c/0e/2t |
| 13 | devstation不支持Ventoy导致USB启动和ISO引导失败，如何解决？ | 2c/0e/2t |
| 14 | x2openEuler升级检查因rpm解析索引越界导致冲突信息收集失败，如何解决？ | 2c/0e/2t |
| 15 | loongarch64架构直接内核引导失败需修复架构适配缺陷，如何解决？ | 2c/0e/2t |
| 16 | openEuler下VMware Workstation挂载U盘启动物理硬盘存在引导失败问题，如何解决？ | 2c/0e/2t |
| 17 | openEuler多工作区下任务栏软件跨区启动失败，如何解决？ | 2c/0e/2t |
| 18 | openEuler缺少MySQL开发库导致mysqlclient安装失败，如何解决？ | 2c/0e/2t |
| 19 | openEuler显卡驱动管理器安装因依赖冲突失败，如何解决？ | 2c/0e/2t |
| 20 | openEuler RISC-V版因缺失run/initramfs/state目录导致import-state.service启动失败，如何解决？ | 2c/0e/2t |
| 21 | x2openeuler迁移工具Windows文档链接失效或文件损坏？ | 2c/0e/2t |
| 22 | openEuler中kae-driver与libwd因头文件路径冲突导致安装失败，如何解决？ | 2c/0e/2t |
| 23 | UltraISO烧录导致openEuler U盘引导失败，如何解决？ | 2c/0e/2t |
| 24 | kf5-akonadi-server因依赖版本冲突无法安装，如何解决？ | 2c/0e/2t |
| 25 | petsc软件安装失败因依赖项或编译环境配置问题，如何解决？ | 2c/0e/2t |
| 26 | openEuler嵌入式安装因缺少mkswap及空间不足导致920机型引导失败，如何解决？ | 2c/0e/2t |
| 27 | openEuler Java 21安装因pretrans脚本Lua引用nil值失败，如何解决？ | 2c/0e/2t |
| 28 | gazelle在dpdk-24.11中因结构体变更和初始化缺失导致编译启动失败，如何解决？ | 2c/0e/2t |
| 29 | openEuler下TensorFlow XLA编译因Reshape维度不匹配致启动失败，如何解决？ | 2c/0e/2t |
| 30 | mintlocale启动失败因locale配置错误或文件权限异常，如何解决？ | 2c/0e/2t |
| 31 | 如何在个人电脑（PC）上安装 openEuler 操作系统？安装前需要做哪些准备？ | — |
| 32 | 在 VMware 中安装 openEuler 22.03 时无法识别网卡，应如何安装虚拟机网卡驱动？ | — |
| 33 | openEuler 如何安装 WiFi 无线网卡驱动？ | — |
| 34 | 如何在飞腾 D2000 处理器平台上安装 openEuler？有哪些已知兼容性问题？ | — |
| 35 | openEuler 的 A-Ops 智能运维工具 gala-ops 如何安装和部署？ | — |
| 36 | 安装 openEuler 后系统中找不到 man 命令，是什么原因？如何安装 man 帮助手册？ | — |
| 37 | CentOS 7.x 能否直接迁移到 openEuler 22.03 LTS？完整的迁移步骤和注意事项是什么？ | — |
| 38 | 安装 openEuler 时 Anaconda 安装程序卡住无法继续，如何排查解决？ | — |
| 39 | openEuler 22.03 SP3 如何升级到 24.03 版本？有哪些官方推荐迁移方式？ | — |
| 40 | openEuler 22.03-lts 容器镜像启动后执行 yum update 报错，如何排查解决？ | — |
| 41 | openEuler 上如何安装 VirtualBox 虚拟机软件？ | — |
| 42 | openEuler 22.03 SP3 如何安装 XFCE 桌面环境？ | — |
| 43 | 鲲鹏 920 处理器的服务器应该安装哪个架构版本的 openEuler（X86 还是 AArch64）？ | — |
| 44 | openEuler 22.03 ARM 架构上如何部署 Zabbix 监控系统？ | — |
| 45 | openEuler 22.03 SP1 是否支持将内核升级到 6.x 版本？如何操作？ | — |
| 46 | 安装 x2openEuler 工具后找不到 service_start.sh 脚本，如何解决？ | — |
| 47 | Red Hat 7.9 迁移到 openEuler 时出现 'can not clean repo info before upgrade' 错误，如何解决？ | — |
| 48 | openEuler 24.03 SP1 上安装英伟达显卡驱动时如何选择合适的 CUDA 版本？ | — |
| 49 | openEuler Embedded 是否支持通过 yum/dnf 在线安装软件包？ | — |
| 50 | openEuler 24.03 LTS SP1 无法安装 NVIDIA 显卡驱动，如何解决？ | — |
| 51 | 如何加入 openEuler sig-Migration SIG，参与跨平台 OS 迁移相关开发贡献？ | — |
| 52 | openEuler 上如何引入和使用 composefs 实现容器镜像的只读挂载文件系统？ | — |
| 53 | 如何申请在 openEuler 官方网站添加新的全球镜像节点（public mirror）？有哪些申请条件？ | — |
| 54 | 如何在 openEuler 24.03 LTS 上使用官方 sig-OpenStack 工具部署 OpenStack Antelope？ | — |
| 55 | openEuler 虚拟机如何支持 vNMI（虚拟 NMI）热迁移？ | — |
| 56 | 如何获取和使用 openEuler 官方容器镜像？支持哪些架构的容器镜像？ | — |
| 57 | 如何在 openEuler 上从源码编译安装自定义内核？内核编译的基本流程是什么？ | — |
| 58 | 如何在 openEuler 上安装 Xfce 桌面环境并配置 xrdp 实现 Windows 远程桌面连接？ | — |
| 59 | 如何在离线（无网络）环境下将 Docker 安装到 openEuler 系统？ | — |
| 60 | 如何在 openEuler ISO 镜像中添加自定义 RPM 包并重新构建 ISO 安装镜像？ | — |
| 61 | 如何在 openEuler 上安装 DDE（深度桌面环境）图形界面？ | — |
| 62 | 如何在 openEuler 上安装和配置 DPDK（数据平面开发套件）？ | — |
| 63 | 如何在 openEuler 上将 OpenSSL 升级到指定版本？ | — |
| 64 | 如何在 openEuler 22.03 LTS 上使用 kubeadm 部署 Kubernetes 集群？ | — |
| 65 | 如何在 openEuler 22.03 LTS 上安装 Docker CE？安装时常见错误如何解决？ | — |
| 66 | openEuler 安装后系统缺少 tar、make 等基础开发工具，如何在离线内网环境中安装这些工具？ | — |
| 67 | 如何在 openEuler 22.03 LTS 上以二进制方式部署 MySQL 5.7？ | — |
| 68 | 如何在配备 RAID 控制卡的服务器上安装 openEuler 操作系统？ | — |
| 69 | 如何在 openEuler 上安装 MongoDB 数据库？ | — |
| 70 | 在 openEuler 上使用 yum/dnf 安装软件时报 'GPG check FAILED' 错误，如何解决？ | — |
| 71 | 如何在 openEuler 22.03 上使用 yum/dnf 安装 PostgreSQL 数据库单机环境？ | — |
| 72 | 如何基于 Cobbler 实现 openEuler 系统的自动化批量网络安装部署？ | — |
| 73 | 如何在 openEuler 上搭建本地 Docker 私有镜像仓库（Registry）？ | — |
| 74 | 在 openEuler 上安装 UKUI 桌面环境后重启无法进入登录界面，如何排查解决？ | — |
| 75 | 如何在 openEuler 上安装 ROS2 Humble 机器人操作系统框架？ | — |
| 76 | 如何在 openEuler 22.03 LTS SP1（x86_64）上将 Intel 网卡驱动源码编译打包成 RPM 包？ | — |
| 77 | 如何在 openEuler 22.03 aarch64 架构上安装 Qt Creator 开发环境？ | — |
| 78 | 如何在openEuler中制作Ironic Python Agent（IPA）裸机镜像？常见失败原因有哪些？ | — |
| 79 | 如何对openEuler 22.03 LTS-SP2 aarch64版本进行离线升级？ | — |
| 80 | 在openEuler 24.03上安装VMware Workstation时启动报找不到gcc编译器，如何解决？ | — |
| 81 | openEuler 24.03 LTS-SP3如何安装GNOME桌面环境？有无官方安装脚本？ | — |

## 系统管理

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler面临HPC多软件编译兼容与运行适配难题？ | 19c/0e/19t |
| 2 | openEuler兆芯KH-50000 CPU驱动兼容性与微码更新支持问题？ | 14c/0e/14t |
| 3 | openEuler Python包卸载后遗留site-packages文件未清理，如何解决？ | 7c/0e/7t |
| 4 | openEuler系统X100显卡驱动存在飞腾平台兼容性问题，导致UKUI界面卡顿，如何解决？ | 6c/0e/6t |
| 5 | openEuler FaaS函数互调因调度异常和初始化超时致调用失败，如何解决？ | 5c/0e/5t |
| 6 | openEuler显示缩放仅支持100%和200%且设置响应慢？ | 4c/0e/4t |
| 7 | atune-check工具在openEuler下网卡信息采集不全？ | 4c/0e/4t |
| 8 | openEuler开启大页预热时共享内存配置引发worker启动性能与兼容性问题？ | 4c/0e/4t |
| 9 | openEuler核心包与软件包差异源于文档迁移及依赖升级，不影响兼容性？ | 4c/0e/4t |
| 10 | openEuler上MySQL 8.0.17存在Sysbench基准性能优化需求？ | 4c/0e/4t |
| 11 | openEuler上gtk3/gtk4-demo运行时出现错误日志影响GUI功能验证，如何解决？ | 4c/0e/4t |
| 12 | openEuler英文版软件包跳转路径异常导致访问失败，如何解决？ | 3c/0e/3t |
| 13 | openEuler精简安装后因仓库不兼容无法匹配CentOS OpenStack包，如何解决？ | 3c/0e/3t |
| 14 | openEuler分布式存储跨节点容错切换存在连接超时与读写失败问题，如何解决？ | 3c/0e/3t |
| 15 | openEuler因cgroup版本差异导致块IO数据采集失败，如何解决？ | 2c/0e/2t |
| 16 | openEuler 5.10内核cat /proc/numa_maps引发用户进程卡顿？ | 2c/0e/2t |
| 17 | po4a升级后命令名变更引发脚本兼容性问题？ | 2c/0e/2t |
| 18 | librdkafka升级至2.11.0引发兼容性问题？ | 2c/0e/2t |
| 19 | openEuler kernel 6.6.0-105+版本在Hyper-V下引发sshd连接重置？ | 2c/0e/2t |
| 20 | gdal从3.10.3升级至3.11.0需解决兼容性与依赖问题？ | 2c/0e/2t |
| 21 | openEuler在鲲鹏920/950上lscpu显示CPU基频未反映实际睿频状态，如何解决？ | 2c/0e/2t |
| 22 | openEuler暗色模式下大模型图标显示不清晰需优化？ | 2c/0e/2t |
| 23 | openEuler 是否支持飞腾 E2000Q 处理器平台？如何验证硬件兼容性？ | — |
| 24 | 如何使用 x2openEuler 工具将系统从 openEuler 20.03 原地升级到 22.03？ | — |
| 25 | openEuler 22.03 LTS 上如何搭建 Mail 邮件服务器（Postfix/Dovecot）？ | — |
| 26 | 配置 openEuler 本地 DNF 仓库源时提示下载元数据失败，如何排查？ | — |
| 27 | openEuler 22.03 SP2 执行 dnf upgrade 失败，常见原因和解决方法有哪些？ | — |
| 28 | openEuler 系统强制关机后重启速度极慢（7-8 分钟），如何优化系统启动时间？ | — |
| 29 | openEuler 升级过程中网络中断导致 SSH 无法连接，如何恢复升级并修复系统？ | — |
| 30 | openEuler 如何禁用 /tmp 目录挂载为 tmpfs？有什么影响？ | — |
| 31 | 将系统 Python 版本升级到 3.11 后导致 dnf/yum 命令不可用，如何恢复？ | — |
| 32 | 误将 /usr 目录设置 chmod 777 导致无法切换 root 用户，如何修复 openEuler 系统权限？ | — |
| 33 | openEuler LTS 版本与创新版本在支持周期和适用场景上有何区别？ | — |
| 34 | 如何加入 openEuler A-Tune SIG 组参与系统性能自调优工具的开发？ | — |
| 35 | openEuler 鲲鹏 UADK 支持哪些加密算法（SM4、AES、RSA、SHA 等）？如何调用加速接口？ | — |
| 36 | openEuler RPM 包的 spec 文件在哪个仓库管理？如何为 openEuler 贡献新的软件包？ | — |
| 37 | 如何参与 openEuler 版本 RC 测试阶段，发现问题后的 issue 提交和修复流程是什么？ | — |
| 38 | 如何配置 openEuler 的软件仓库（repo 源）？有哪些常用的官方 repo 源地址？ | — |
| 39 | 忘记 openEuler root 密码后如何在不重装系统的情况下重置密码？ | — |
| 40 | openEuler 系统 DNS 域名解析失败（ping 域名提示 Name or service not known），如何排查和修复网络 DNS 配置？ | — |
| 41 | openEuler 各常用组件和服务的默认用户名与密码分别是什么？ | — |
| 42 | 如何在 openEuler 中使用 NetworkManager 管理和重启网络服务？nmcli 常用命令有哪些？ | — |
| 43 | 如何在 openEuler 上关闭防火墙（firewalld）和 SELinux？ | — |
| 44 | 如何在 openEuler 上搭建 Samba 文件共享服务，实现与 Windows 的文件共享？ | — |
| 45 | 在 openEuler 中修改 ifcfg-ethX 网卡配置文件后网络设置不生效，如何通过 NetworkManager 正确应用配置？ | — |
| 46 | 如何在 openEuler 上搭建 FTP 服务器（vsftpd）？配置虚拟账户后无法登录如何排查？ | — |
| 47 | 如何使用 x2openEuler 管理升级任务，包括删除、修改或重新执行已有升级任务？ | — |
| 48 | 如何在 openEuler 上配置 sudo，为普通用户授予特定命令的 root 执行权限？ | — |
| 49 | 如何查询硬件设备与 openEuler 的兼容性？官方硬件兼容性列表在哪里查看？ | — |
| 50 | openEuler 普通用户执行 su root 时提示 Permission denied，原因是什么，如何解决？ | — |
| 51 | 学习 openEuler Linux 内核有哪些推荐的入门路径和参考资源？ | — |
| 52 | 在 openEuler 上修改 IP 地址后，如何刷新网络配置使其立即生效？ | — |
| 53 | openEuler 系统中出现中文显示乱码，如何设置正确的系统语言和字符编码？ | — |
| 54 | openEuler 22.03 LTS 系统重启后磁盘盘符（如 sda/sdb）发生变化，如何通过 UUID 或 by-id 固定磁盘标识符？ | — |
| 55 | openEuler syscare 内核热补丁工具如何使用？支持哪些在线热修复场景？ | — |
| 56 | openEuler 内核崩溃时如何配置 kdump 记录崩溃现场？如何分析生成的 vmcore 文件？ | — |
| 57 | 如何在 openEuler 上配置 Mellanox 网卡的 SR-IOV VF（虚拟功能）？ | — |
| 58 | 如何在 openEuler 上测试 InfiniBand 网卡的连通性和带宽性能？ | — |
| 59 | 如何在 openEuler 上开启 SSH 的 X11 Forwarding，通过 SSH 转发图形界面应用？ | — |
| 60 | openEuler 22.03 LTS 如何通过配置限制 SSH 登录的允许 IP 地址（访问控制白名单）？ | — |
| 61 | openEuler 虚拟机非正常关机后重启出现文件系统错误，如何修复？ | — |
| 62 | 如何在 openEuler 上搭建 NFS 网络文件系统服务供其他主机挂载使用？ | — |
| 63 | 如何在openEuler中配置本地软件源（YUM/DNF本地repo）并从本地源安装软件包？ | — |
| 64 | 如何在openEuler系统中升级OpenSSH到指定版本？ | — |
| 65 | openEuler 24.03上LibreOffice与JodConverter集成后文档转换失败，如何解决？ | — |
| 66 | openEuler系统中磁盘出现报错如何排查和解决？ | — |

## 内核与驱动

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler上Spark OmniRuntime多算子因指针类型不匹配导致coredump及结果不一致，如何解决？ | 64c/0e/64t |
| 2 | openEuler PCIe热插拔枚举阻塞导致系统假死问题，如何解决？ | 10c/0e/10t |
| 3 | openEuler内核RAID模块未正确处理REQ_NOWAIT标志导致写性能下降及存储不稳定，如何解决？ | 8c/0e/8t |
| 4 | openEuler RISC-V架构下sysmonitor组件CPU与网卡监控功能缺失，如何解决？ | 5c/0e/5t |
| 5 | openEuler默认IOMMU非严格模式以提升NVMe与网络性能？ | 4c/0e/4t |
| 6 | openEuler启用IMA摘要列表后因EVM属性缺失和密钥环为空导致启动panic，如何解决？ | 4c/0e/4t |
| 7 | openEuler 4.19内核在高版本GCC下存在编译兼容性问题？ | 3c/0e/3t |
| 8 | openEuler perf bench缺失numa参数支持导致NUMA性能测试无法执行，如何解决？ | 3c/0e/3t |
| 9 | openEuler 各发行版本（20.03/22.03/24.03 等）对应的默认内核版本分别是什么？ | — |
| 10 | openEuler 支持运行中不重启升级内核（内核热升级）吗？如何使用相关功能？ | — |

## 安全与漏洞

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler SELinux组件升级引发ABI兼容性风险？ | 6c/0e/6t |
| 2 | openEuler NFSv4并发加锁与文件打开触发UAF漏洞，如何解决？ | 4c/0e/4t |
| 3 | openEuler服务间通信缺少双向认证安全机制？ | 3c/0e/3t |
| 4 | openEuler CIFS客户端rsize为0导致读流程空指针panic，如何解决？ | 3c/0e/3t |
| 5 | openEuler ksmbd持久化v2重放存在use-after-free漏洞？ | 3c/0e/3t |
| 6 | openEuler JWT解析器因未指定padding导致RS签名验证失败，如何解决？ | 2c/0e/2t |
| 7 | openEuler x86_64 legacy启动缺失GRUB密码防护，如何解决？ | 2c/0e/2t |
| 8 | openEuler 5.10内核IMA安全策略限制摘要列表写入？ | 2c/0e/2t |
| 9 | openEuler 22.03 LTS SP2 上如何修复 CVE-2024-1086 内核提权漏洞？ | — |
| 10 | 如何向 openEuler 安全委员会（security@openeuler.org）报告 CVE 安全漏洞？漏洞披露流程是什么？ | — |
| 11 | openEuler 社区安全漏洞修复通知（安全通告）是通过哪个邮件列表发布的？如何订阅？ | — |
| 12 | openEuler中发现OpenSSL安全漏洞，什么时候会发布修复补丁？ | — |

## 虚拟化与容器

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler下poc_gluten的ShuffleExchange与Join算子不支持struct等复杂类型，如何解决？ | 4c/0e/4t |
| 2 | openEuler中gazelle与DPDK协同的UDP数据路径存在异常导致高概率带宽为0，如何解决？ | 4c/0e/4t |
| 3 | openEuler多节点Worker缩容时客户端切换延迟高且连接全断？ | 3c/0e/3t |
| 4 | openEuler多租户实例调度存在亲和性策略失效问题？ | 3c/0e/3t |
| 5 | openEuler vfio hisilicon驱动在热迁移中RAS与FLR并发引发系统不稳定？ | 2c/0e/2t |
| 6 | openEuler容器因seccomp策略差异导致Ascend平台配置文件访问失败，如何解决？ | 2c/0e/2t |
| 7 | openEuler销毁机密虚机时因私有内存遍历引发soft lockup？ | 2c/0e/2t |
| 8 | openEuler CloudNative SIG 支持哪些云原生组件（containerd、iSula、kata-containers 等）？ | — |
| 9 | 如何参与 openEuler CloudNative SIG 双周例会？议题如何提交和跟踪？ | — |
| 10 | openEuler 支持哪些虚拟化技术（KVM、QEMU、libvirt）？ | — |
| 11 | 在 openEuler 22.03 上使用 KVM 创建虚拟机时报 qxl 显卡相关错误，如何解决？ | — |

## 软件包与构建

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler多个组件因CMake 4.0移除旧兼容性导致构建失败，如何解决？ | 26c/0e/26t |
| 2 | Rust 1.82升级导致openEuler多组件构建失败，如何解决？ | 6c/0e/6t |
| 3 | openEuler升级Rust 1.91后宏中尾随分号引发构建失败，如何解决？ | 4c/0e/4t |
| 4 | Clang工具链未适配openEuler衍生版target triples致路径匹配失败，如何解决？ | 4c/0e/4t |
| 5 | openEuler使用clang-17编译时因优化导致指针计算异常引发段错误，如何解决？ | 4c/0e/4t |
| 6 | eulermaker因cmake升级导致sundials及ament cmake依赖无法解析，如何解决？ | 3c/0e/3t |
| 7 | openEuler Gluten Omni中regr聚合函数执行结果与Spark不一致？ | 3c/0e/3t |
| 8 | openEuler中python-pyusb与pyusb包名冲突导致二进制包重复无法共存，如何解决？ | 3c/0e/3t |
| 9 | openEuler官方仓库python3-vllm包缺失PyTorch等运行时依赖，如何解决？ | 3c/0e/3t |
| 10 | openEuler Spark SQL中Extract函数仅支持hour字段需扩展？ | 3c/0e/3t |
| 11 | openEuler环境中Clang构建存在编译兼容性问题？ | 3c/0e/3t |
| 12 | openEuler需升级Eclipse至4.34以解决RuyiSDK IDE兼容性问题？ | 3c/0e/3t |
| 13 | openEuler使用gcc-14.3编译时需处理-Wimplicit-function-declaration警告？ | 3c/0e/3t |
| 14 | 如何通过 Open Build Service（OBS）为 openEuler 社区构建和发布软件包？ | — |
| 15 | EulerMaker 构建系统的使用流程是什么？ | — |
| 16 | 在openEuler Docker镜像中安装llvm-toolset-19后缺失enable脚本，如何解决？ | — |

## 社区与生态

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler 社区有哪些 SIG 组（特别兴趣小组），如何查看完整的 SIG 列表？ | — |
| 2 | 如何订阅 openEuler 社区邮件列表（如 dev@openeuler.org）参与技术讨论？ | — |
| 3 | openEuler AI SIG（ai-infra@openeuler.org）的目标是什么？支持哪些 AI 基础设施框架？ | — |
| 4 | openEuler sig-QA 如何进行版本质量测试？如何参与社区 QA 贡献？ | — |
| 5 | 如何向 openEuler TSC 提交 SIG 申请，新建特别兴趣小组的流程是什么？ | — |
| 6 | openEuler BigData SIG 支持哪些大数据组件（Hadoop、Spark、Flink 等）？ | — |
| 7 | 如何在 openEuler 上利用 EulerLauncher 或 BigData SIG 工具快速搭建大数据集群？ | — |
| 8 | openEuler 分布式存储（sig-SDS）SIG 支持哪些存储组件（Ceph、Lustre、DBS）？ | — |
| 9 | openEuler 新版本分支初始化时，SIG maintainer 如何参与 PR 检视流程？ | — |
| 10 | openEuler 版本发布 release公告会包含哪些内容？ | — |
| 11 | 如何向 openEuler dev 邮件列表提交技术提案（RFC）或发起社区讨论？ | — |
| 12 | openEuler 社区版本生命周期是什么？ | — |
| 13 | 向 openEuler Kernal SIG 提交补丁的格式要求是什么？ | — |
| 14 | openEuler Compass-CI 持续集成平台如何使用？如何提交自动化测试任务验证软件包？ | — |
| 15 | openEuler AI SIG 在 openEuler 上支持哪些 AI 推理框架？ | — |
| 16 | openEuler 元戎（yuanrong）SIG 的职责是什么？ | — |
| 17 | openEuler 发行版兼容性认证（OS 兼容性认证）的申请流程是什么？需要满足哪些条件？ | — |
| 18 | openEuler openDesign SIG 在社区视觉设计中扮演什么角色？ | — |
| 19 | openEuler 的 oec-hardware 硬件兼容性测试工具如何使用？如何通过它提交硬件兼容性认证？ | — |
| 20 | HCIP-openEuler 认证考试涵盖哪些内容？如何报名和备考？ | — |
| 21 | 企业如何签署 openEuler 社区 CLA（贡献者许可协议），正式加入 openEuler 社区？ | — |
| 22 | 如何退订 openEuler 社区邮件列表？退订操作在哪里完成？ | — |
| 23 | 如何通过 mailweb（https://mailweb.openeuler.org）在线浏览 openEuler 社区邮件列表的历史归档？ | — |
| 24 | openEuler 各 SIG 组的例会时间、频率和在线参会链接如何查询？ | — |
| 25 | openEuler 社区技术委员会（TC）例会如何参与和跟踪决策结果？ | — |
| 26 | openEuler 社区的技术讨论应优先使用邮件列表还是 Gitee Issue？二者的适用场景各是什么？ | — |
| 27 | 如何订阅 openEuler 版本发布公告邮件列表，及时接收新版本发布通知？ | — |
| 28 | 在 openEuler 邮件列表中发起新话题或回复时，有哪些基本的邮件礼仪规范（如正确引用、使用纯文本等）？ | — |
| 29 | 如何通过 Web 界面查看 openEuler 邮件列表内容而无需订阅？ | — |
| 30 | openEuler 社区补丁提交和代码审核是否通过邮件列表进行？还是完全依赖 Gitee PR？ | — |
| 31 | openEuler 社区有哪些面向开发者的核心邮件列表（如 dev、kernel、infra），它们各自的讨论范围是什么？ | — |
| 32 | 如何将 openEuler 邮件列表的消息导入到邮件客户端（如 Thunderbird、Outlook）中统一管理？ | — |
| 33 | 如何在openEuler社区GitCode上将Issue与Pull Request关联起来？ | — |

## 嵌入式与边缘

| # | 问题 | 咨询数/排除数/总数 |
|---|------|--------------------|
| 1 | openEuler在Lichee Pi 4A上因th1520 i2s驱动未校验用户内存致内核崩溃，如何解决？ | 6c/0e/6t |
| 2 | openEuler RISC-V平台PowerAPI接口获取CPU频率与性能数据失败，如何解决？ | 3c/0e/3t |
| 3 | bisheng_autotuner在openEuler-24.03-LTS-SP1中默认强制编译且不支持RISC-V架构，如何解决？ | 2c/0e/2t |
| 4 | pango Python绑定在RISC-V64架构下模块加载失败，如何解决？ | 2c/0e/2t |
| 5 | openEuler RISC-V64环境下gazellectl lstack指令因套接字连接失败无法响应，如何解决？ | 2c/0e/2t |
| 6 | openEuler RISC-V架构下libvirt缺失AIA配置支持，如何解决？ | 2c/0e/2t |
| 7 | openEuler Embedded 操作系统有哪些应用场景？支持哪些嵌入式硬件平台？ | — |
| 8 | 如何使用oebuild构建包含分布式软总线功能的qemu-aarch64镜像？构建失败应如何排查？ | — |
| 9 | 在边缘AI盒子上部署openEuler系统和CANN推理框架需要多大的硬盘空间？ | — |
| 10 | 如何将openEuler系统移植到全志A401（Allwinner A401）处理器平台？ | — |
| 11 | 将openEuler移植到RK3588开发板时系统在内核启动阶段卡死，如何排查和解决？ | — |
