# openEuler 问题集

## 概览

- 社区: openEuler
- 生成时间: 2026-04-27
- 问题总数: 143

### 来源渠道

| 渠道 | 状态 |
|------|------|
| 论坛帖子 | ✅ 有数据 |
| 仓库 Issue | ✅ 有数据 |
| 邮件列表 | ✅ 有数据 |

## 分类目录

- [安装与部署](#安装与部署)（54 条，#1–#54）
- [系统管理](#系统管理)（43 条，#55–#97）
- [内核与驱动](#内核与驱动)（7 条，#98–#104）
- [安全与漏洞](#安全与漏洞)（7 条，#105–#111）
- [软件包与构建](#软件包与构建)（10 条，#112–#121）
- [社区与生态](#社区与生态)（18 条，#122–#139）
- [嵌入式与边缘](#嵌入式与边缘)（4 条，#140–#143）

## 安装与部署

| # | 问题 | 频率 |
|---|------|------|
| 1 | openEuler部署组件因依赖缺失或版本不兼容导致服务启动失败，如何解决？ | 8c/0e/8t |
| 2 | openEuler QEMU ARM虚拟机因zImage兼容性及UEFI安全启动问题导致启动失败，如何解决？ | 7c/0e/7t |
| 3 | openEuler RISC-V架构QEMU 8.2.0 KVM虚拟机ACPI启动失败，如何解决？ | 4c/0e/4t |
| 4 | openEuler部署etcd启用证书与鉴权时worker因缺少用户名密码参数启动失败，如何解决？ | 3c/0e/3t |
| 5 | openEuler LoongArch版桌面环境依赖包缺失导致安装失败，如何解决？ | 3c/0e/3t |
| 6 | openEuler cobbler buildiso在ARM/RISC-V架构下解包返回值异常，如何解决？ | 3c/0e/3t |
| 7 | euler-copilot-framework依赖管理缺失致安装阻塞，如何解决？ | 3c/0e/3t |
| 8 | openEuler RDMA服务ibacm与iwpmd启动失败致功能异常，如何解决？ | 2c/0e/2t |
| 9 | RK3588刷写openEuler后启动链配置异常导致无法启动，如何解决？ | 2c/0e/2t |
| 10 | openEuler RISC-V架构下lcr运行时因seccomp缺少syscall支持致容器启动失败，如何解决？ | 2c/0e/2t |
| 11 | devstation不支持Ventoy导致USB启动和ISO引导失败，如何解决？ | 2c/0e/2t |
| 12 | openEuler下VMware Workstation挂载U盘启动物理硬盘存在引导失败问题，如何解决？ | 2c/0e/2t |
| 13 | openEuler多工作区下任务栏软件跨区启动失败，如何解决？ | 2c/0e/2t |
| 14 | openEuler缺少MySQL开发库导致mysqlclient安装失败，如何解决？ | 2c/0e/2t |
| 15 | openEuler显卡驱动管理器安装因依赖冲突失败，如何解决？ | 2c/0e/2t |
| 16 | openEuler RISC-V版因缺失run/initramfs/state目录导致import-state.service启动失败，如何解决？ | 2c/0e/2t |
| 17 | openEuler中kae-driver与libwd因头文件路径冲突导致安装失败，如何解决？ | 2c/0e/2t |
| 18 | openEuler嵌入式安装因缺少mkswap及空间不足导致920机型引导失败，如何解决？ | 2c/0e/2t |
| 19 | openEuler Java 21安装因pretrans脚本Lua引用nil值失败，如何解决？ | 2c/0e/2t |
| 20 | gazelle在dpdk-24.11中因结构体变更和初始化缺失导致编译启动失败，如何解决？ | 2c/0e/2t |
| 21 | openEuler下TensorFlow XLA编译因Reshape维度不匹配致启动失败，如何解决？ | 2c/0e/2t |
| 22 | mintlocale启动失败因locale配置错误或文件权限异常，如何解决？ | 2c/0e/2t |
| 23 | 如何在个人电脑（PC）上安装 openEuler 操作系统？安装前需要做哪些准备？ | manual |
| 24 | 在 VMware 中安装 openEuler 22.03 时无法识别网卡，应如何安装虚拟机网卡驱动？ | manual |
| 25 | openEuler 的 A-Ops 智能运维工具 gala-ops 如何安装和部署？ | manual |
| 26 | 安装 openEuler 后系统中找不到 man 命令，是什么原因？如何安装 man 帮助手册？ | manual |
| 27 | CentOS 7.x 能否直接迁移到 openEuler 22.03 LTS？完整的迁移步骤和注意事项是什么？ | manual |
| 28 | openEuler 22.03 SP3 如何升级到 24.03 版本？有哪些官方推荐迁移方式？ | manual |
| 29 | openEuler 22.03-lts 容器镜像启动后执行 yum update 报错，如何排查解决？ | manual |
| 30 | openEuler 22.03 ARM 架构上如何部署 Zabbix 监控系统？ | manual |
| 31 | openEuler 22.03 SP1 是否支持将内核升级到 6.x 版本？如何操作？ | manual |
| 32 | openEuler Embedded 是否支持通过 yum/dnf 在线安装软件包？ | manual |
| 33 | 如何申请在 openEuler 官方网站添加新的全球镜像节点（public mirror）？有哪些申请条件？ | manual |
| 34 | 如何在 openEuler 24.03 LTS 上使用官方 sig-OpenStack 工具部署 OpenStack Antelope？ | manual |
| 35 | openEuler 虚拟机如何支持 vNMI（虚拟 NMI）热迁移？ | manual |
| 36 | 如何获取和使用 openEuler 官方容器镜像？支持哪些架构的容器镜像？ | manual |
| 37 | 如何在 openEuler 上从源码编译安装自定义内核？内核编译的基本流程是什么？ | manual |
| 38 | 如何在离线（无网络）环境下将 Docker 安装到 openEuler 系统？ | manual |
| 39 | 如何在 openEuler ISO 镜像中添加自定义 RPM 包并重新构建 ISO 安装镜像？ | manual |
| 40 | 如何在 openEuler 上安装 DDE（深度桌面环境）图形界面？ | manual |
| 41 | 如何在 openEuler 上安装和配置 DPDK（数据平面开发套件）？ | manual |
| 42 | 如何在 openEuler 上将 OpenSSL 升级到指定版本？ | manual |
| 43 | openEuler 安装后系统缺少 tar、make 等基础开发工具，如何在离线内网环境中安装这些工具？ | manual |
| 44 | 如何在 openEuler 22.03 上使用 yum/dnf 安装 PostgreSQL 数据库单机环境？ | manual |
| 45 | 如何基于 Cobbler 实现 openEuler 系统的自动化批量网络安装部署？ | manual |
| 46 | 如何在 openEuler 上搭建本地 Docker 私有镜像仓库（Registry）？ | manual |
| 47 | 如何在 openEuler 22.03 LTS SP1（x86_64）上将 Intel 网卡驱动源码编译打包成 RPM 包？ | manual |
| 48 | 在openEuler 24.03上安装VMware Workstation时启动报找不到gcc编译器，如何解决？ | manual |
| 49 | 如何在 openEuler 上安装 Nvidia 显卡驱动？ | 8468 |
| 50 | 如何在 openEuler 上安装 Xfce 桌面环境并配置 xrdp 远程桌面？ | 6867 |
| 51 | openEuler 如何安装无线网卡（WiFi）驱动？ | 6042 |
| 52 | 如何在飞腾 D2000 处理器平台上安装 openEuler 系统，有哪些常见问题？ | 6017 |
| 53 | openEuler 是否支持飞腾 E2000Q 处理器平台？如何确认硬件兼容性并完成安装？ | 4501 |
| 54 | 如何在 openEuler 22.03 LTS 上使用 kubeadm 部署 Kubernetes 集群？ | 4213 |


## 系统管理

| # | 问题 | 频率 |
|---|------|------|
| 55 | openEuler Python包卸载后遗留site-packages文件未清理，如何解决？ | 7c/0e/7t |
| 56 | openEuler系统X100显卡驱动存在飞腾平台兼容性问题，导致UKUI界面卡顿，如何解决？ | 6c/0e/6t |
| 57 | openEuler FaaS函数互调因调度异常和初始化超时致调用失败，如何解决？ | 5c/0e/5t |
| 58 | openEuler上gtk3/gtk4-demo运行时出现错误日志影响GUI功能验证，如何解决？ | 4c/0e/4t |
| 59 | openEuler英文版软件包跳转路径异常导致访问失败，如何解决？ | 3c/0e/3t |
| 60 | openEuler精简安装后因仓库不兼容无法匹配CentOS OpenStack包，如何解决？ | 3c/0e/3t |
| 61 | openEuler分布式存储跨节点容错切换存在连接超时与读写失败问题，如何解决？ | 3c/0e/3t |
| 62 | openEuler因cgroup版本差异导致块IO数据采集失败，如何解决？ | 2c/0e/2t |
| 63 | 如何使用 x2openEuler 工具将系统从 openEuler 20.03 原地升级到 22.03？ | manual |
| 64 | 配置 openEuler 本地 DNF 仓库源时提示下载元数据失败，如何排查？ | manual |
| 65 | openEuler 22.03 SP2 执行 dnf upgrade 失败，常见原因和解决方法有哪些？ | manual |
| 66 | openEuler 系统强制关机后重启速度极慢（7-8 分钟），如何优化系统启动时间？ | manual |
| 67 | openEuler 升级过程中网络中断导致 SSH 无法连接，如何恢复升级并修复系统？ | manual |
| 68 | openEuler 如何禁用 /tmp 目录挂载为 tmpfs？有什么影响？ | manual |
| 69 | 将系统 Python 版本升级到 3.11 后导致 dnf/yum 命令不可用，如何恢复？ | manual |
| 70 | 误将 /usr 目录设置 chmod 777 导致无法切换 root 用户，如何修复 openEuler 系统权限？ | manual |
| 71 | openEuler LTS 版本与创新版本在支持周期和适用场景上有何区别？ | manual |
| 72 | openEuler 鲲鹏 UADK 支持哪些加密算法（SM4、AES、RSA、SHA 等）？如何调用加速接口？ | manual |
| 73 | openEuler RPM 包的 spec 文件在哪个仓库管理？如何为 openEuler 贡献新的软件包？ | manual |
| 74 | 如何配置 openEuler 的软件仓库（repo 源）？有哪些常用的官方 repo 源地址？ | manual |
| 75 | 忘记 openEuler root 密码后如何在不重装系统的情况下重置密码？ | manual |
| 76 | openEuler 系统 DNS 域名解析失败（ping 域名提示 Name or service not known），如何排查和修复网络 DNS 配置？ | manual |
| 77 | 如何在 openEuler 中使用 NetworkManager 管理和重启网络服务？nmcli 常用命令有哪些？ | manual |
| 78 | 如何在 openEuler 上关闭防火墙（firewalld）和 SELinux？ | manual |
| 79 | 如何在 openEuler 上搭建 Samba 文件共享服务，实现与 Windows 的文件共享？ | manual |
| 80 | 在 openEuler 中修改 ifcfg-ethX 网卡配置文件后网络设置不生效，如何通过 NetworkManager 正确应用配置？ | manual |
| 81 | 如何在 openEuler 上搭建 FTP 服务器（vsftpd）？配置虚拟账户后无法登录如何排查？ | manual |
| 82 | 如何使用 x2openEuler 管理升级任务，包括删除、修改或重新执行已有升级任务？ | manual |
| 83 | 如何在 openEuler 上配置 sudo，为普通用户授予特定命令的 root 执行权限？ | manual |
| 84 | 如何查询硬件设备与 openEuler 的兼容性？官方硬件兼容性列表在哪里查看？ | manual |
| 85 | openEuler 普通用户执行 su root 时提示 Permission denied，原因是什么，如何解决？ | manual |
| 86 | 在 openEuler 上修改 IP 地址后，如何刷新网络配置使其立即生效？ | manual |
| 87 | openEuler syscare 内核热补丁工具如何使用？支持哪些在线热修复场景？ | manual |
| 88 | openEuler 内核崩溃时如何配置 kdump 记录崩溃现场？如何分析生成的 vmcore 文件？ | manual |
| 89 | 如何在 openEuler 上配置 Mellanox 网卡的 SR-IOV VF（虚拟功能）？ | manual |
| 90 | 如何在 openEuler 上测试 InfiniBand 网卡的连通性和带宽性能？ | manual |
| 91 | openEuler 虚拟机非正常关机后重启出现文件系统错误，如何修复？ | manual |
| 92 | 如何在 openEuler 上搭建 NFS 网络文件系统服务供其他主机挂载使用？ | manual |
| 93 | 如何在openEuler中配置本地软件源（YUM/DNF本地repo）并从本地源安装软件包？ | manual |
| 94 | 如何在openEuler系统中升级OpenSSH到指定版本？ | manual |
| 95 | openEuler 24.03上LibreOffice与JodConverter集成后文档转换失败，如何解决？ | manual |
| 96 | openEuler 各组件和服务的默认用户名和密码是什么？ | 6465 |
| 97 | 如何使用 FinalShell 工具连接 openEuler 服务器进行远程管理？ | 4247 |


## 内核与驱动

| # | 问题 | 频率 |
|---|------|------|
| 98 | openEuler上Spark OmniRuntime多算子因指针类型不匹配导致coredump及结果不一致，如何解决？ | 64c/0e/64t |
| 99 | openEuler PCIe热插拔枚举阻塞导致系统假死问题，如何解决？ | 10c/0e/10t |
| 100 | openEuler内核RAID模块未正确处理REQ_NOWAIT标志导致写性能下降及存储不稳定，如何解决？ | 8c/0e/8t |
| 101 | openEuler RISC-V架构下sysmonitor组件CPU与网卡监控功能缺失，如何解决？ | 5c/0e/5t |
| 102 | openEuler启用IMA摘要列表后因EVM属性缺失和密钥环为空导致启动panic，如何解决？ | 4c/0e/4t |
| 103 | openEuler perf bench缺失numa参数支持导致NUMA性能测试无法执行，如何解决？ | 3c/0e/3t |
| 104 | openEuler 各发行版本（20.03/22.03/24.03 等）对应的默认内核版本分别是什么？ | manual |


## 安全与漏洞

| # | 问题 | 频率 |
|---|------|------|
| 105 | openEuler NFSv4并发加锁与文件打开触发UAF漏洞，如何解决？ | 4c/0e/4t |
| 106 | openEuler CIFS客户端rsize为0导致读流程空指针panic，如何解决？ | 3c/0e/3t |
| 107 | openEuler JWT解析器因未指定padding导致RS签名验证失败，如何解决？ | 2c/0e/2t |
| 108 | openEuler x86_64 legacy启动缺失GRUB密码防护，如何解决？ | 2c/0e/2t |
| 109 | openEuler 22.03 LTS SP2 上如何修复 CVE-2024-1086 内核提权漏洞？ | manual |
| 110 | 如何向 openEuler 安全委员会（security@openeuler.org）报告 CVE 安全漏洞？漏洞披露流程是什么？ | manual |
| 111 | openEuler中发现OpenSSL安全漏洞，什么时候会发布修复补丁？ | manual |


## 软件包与构建

| # | 问题 | 频率 |
|---|------|------|
| 112 | openEuler多个组件因CMake 4.0移除旧兼容性导致构建失败，如何解决？ | 26c/0e/26t |
| 113 | Rust 1.82升级导致openEuler多组件构建失败，如何解决？ | 6c/0e/6t |
| 114 | openEuler升级Rust 1.91后宏中尾随分号引发构建失败，如何解决？ | 4c/0e/4t |
| 115 | Clang工具链未适配openEuler衍生版target triples致路径匹配失败，如何解决？ | 4c/0e/4t |
| 116 | openEuler使用clang-17编译时因优化导致指针计算异常引发段错误，如何解决？ | 4c/0e/4t |
| 117 | eulermaker因cmake升级导致sundials及ament cmake依赖无法解析，如何解决？ | 3c/0e/3t |
| 118 | openEuler中python-pyusb与pyusb包名冲突导致二进制包重复无法共存，如何解决？ | 3c/0e/3t |
| 119 | openEuler官方仓库python3-vllm包缺失PyTorch等运行时依赖，如何解决？ | 3c/0e/3t |
| 120 | 如何通过 Open Build Service（OBS）为 openEuler 社区构建和发布软件包？ | manual |
| 121 | EulerMaker 构建系统的使用流程是什么？ | manual |


## 社区与生态

| # | 问题 | 频率 |
|---|------|------|
| 122 | openEuler 社区有哪些 SIG 组（特别兴趣小组），如何查看完整的 SIG 列表？ | manual |
| 123 | 如何订阅 openEuler 社区邮件列表（如 dev@openeuler.org）参与技术讨论？ | manual |
| 124 | openEuler sig-QA 如何进行版本质量测试？ | manual |
| 125 | 如何向 openEuler TSC 提交 SIG 申请，新建特别兴趣小组的流程是什么？ | manual |
| 126 | openEuler 分布式存储（sig-SDS）SIG 支持哪些存储组件（Ceph、Lustre、DBS）？ | manual |
| 127 | openEuler 版本发布 release公告会包含哪些内容？ | manual |
| 128 | openEuler 社区版本生命周期是什么？ | manual |
| 129 | 向 openEuler Kernal SIG 提交补丁的格式要求是什么？ | manual |
| 130 | openEuler Compass-CI 持续集成平台如何使用？ | manual |
| 131 | openEuler AI SIG 在 openEuler 上支持哪些 AI 推理框架？ | manual |
| 132 | openEuler 发行版兼容性认证（OS 兼容性认证）的申请流程是什么？ | manual |
| 133 | openEuler 的 oec-hardware 硬件兼容性测试工具如何使用？ | manual |
| 134 | HCIP-openEuler 认证考试涵盖哪些内容？如何报名和备考？ | manual |
| 135 | 企业如何签署 openEuler 社区 CLA（贡献者许可协议），正式加入 openEuler 社区？ | manual |
| 136 | 如何通过 mailweb（https://mailweb.openeuler.org）在线浏览 openEuler 社区邮件列表的历史归档？ | manual |
| 137 | openEuler 各 SIG 组的例会时间、频率和在线参会链接如何查询？ | manual |
| 138 | 如何订阅 openEuler 版本发布公告邮件列表，及时接收新版本发布通知？ | manual |
| 139 | 在 openEuler 邮件列表中发起新话题或回复时，有哪些基本的邮件礼仪规范（如正确引用、使用纯文本等）？ | manual |


## 嵌入式与边缘

| # | 问题 | 频率 |
|---|------|------|
| 140 | openEuler在Lichee Pi 4A上因th1520 i2s驱动未校验用户内存致内核崩溃，如何解决？ | 6c/0e/6t |
| 141 | openEuler RISC-V平台PowerAPI接口获取CPU频率与性能数据失败，如何解决？ | 3c/0e/3t |
| 142 | openEuler RISC-V架构下libvirt缺失AIA配置支持，如何解决？ | 2c/0e/2t |
| 143 | openEuler Embedded 支持哪些嵌入式硬件平台？ | manual |

