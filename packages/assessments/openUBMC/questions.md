# GEO 问题集

> 生成时间: 2026-03-23
> 社区: openUBMC
> 总数: 52

## 概览

| 意图 | 数量 |
|------|------|
| 认知 | 5 |
| 选型 | 3 |
| 趋势 | 1 |
| 场景 | 6 |
| 教程 | 9 |
| 故障 | 23 |
| 特性 | 4 |
| 迁移 | 2 |

| 来源 | 数量 |
|------|------|
| 手动输入 (manual) | 43 |
| 论坛 (forum, fallback) | 2 |
| Issue | 0 |
| 行业 (industry) | 6 |
| Maillist | 0 |

> **路径说明**: manual=✅(108条重写) forum=⚠️(无forum_url, 使用fallback) issue=❌(GitCode未找到openUBMC仓库) maillist=⚠️(脚本错误, 使用fallback) industry=✅(LLM生成)

---

### 认知

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_004 | openUBMC的Redfish接口规范是什么？有哪些设计原则？ | zh | manual |
| q_033 | openUBMC社区中可以通过PR评论触发哪些机器人自动化操作？ | zh | manual |
| q_036 | openUBMC中BusinessConnector是什么？有什么作用？ | zh | manual |
| q_044 | What is openUBMC and how does it differ from traditional BMC firmware solutions? | en | industry |
| q_050 | 如何为openUBMC社区贡献代码？贡献流程和规范是什么？ | zh | forum |

### 选型

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_045 | What are the main open-source BMC firmware projects available for enterprise server management? | en | industry |
| q_046 | How does openUBMC compare to OpenBMC from the Linux Foundation? | en | industry |
| q_049 | Alternatives to proprietary BMC firmware for Huawei or HiSilicon servers? | en | industry |

### 趋势

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_048 | 服务器BMC固件开源化的趋势是什么？openUBMC在其中处于什么定位？ | zh | industry |

### 场景

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_006 | openUBMC的Redfish OEM字段如何在不使用装备项和白牌包的情况下定制？ | zh | manual |
| q_018 | openUBMC如何适配MiniSAS接口及其下挂接的硬盘？ | zh | manual |
| q_019 | openUBMC中如何适配NCSI网卡？ | zh | manual |
| q_022 | openUBMC中如何通过I2C与自定义协议的芯片通信？ | zh | manual |
| q_039 | openUBMC的USB管理功能有哪些使用场景？ | zh | manual |
| q_047 | openUBMC支持哪些服务器硬件平台和处理器架构？ | zh | industry |

### 教程

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_001 | 如何在openUBMC中快速启动QEMU进行仿真开发？ | zh | manual |
| q_009 | 如何使用IPMI命令查询openUBMC中NPU模组的FRU ID？ | zh | manual |
| q_020 | openUBMC中如何使用SMC协议封装I2C数据？具体配置方法是什么？ | zh | manual |
| q_034 | 如何在openUBMC中新增一个组件？详细步骤是什么？ | zh | manual |
| q_035 | openUBMC的风扇调速配置文档在哪里？如何配置调速策略？ | zh | manual |
| q_037 | openUBMC中如何将第三方库文件和头文件集成到组件代码中？ | zh | manual |
| q_038 | openUBMC中如何调整app.log的日志打印等级？ | zh | manual |
| q_042 | openUBMC中通过CPLD管理EEPROM和PSU的方式是什么？ | zh | manual |
| q_051 | openUBMC的版本发布周期和LTS支持策略是什么？ | zh | forum |

### 故障

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_002 | openUBMC QEMU仿真环境中，用Administrator可以SSH登录但Web登录失败，如何解决？ | zh | manual |
| q_007 | openUBMC中管理员与操作员执行Get auth token获取到的token值为什么一致？ | zh | manual |
| q_008 | 进行IPMI与SNMP压测时openUBMC概率性出现IPMI访问BMC失败，如何排查？ | zh | manual |
| q_010 | openUBMC中ipmcset/ipmcget出现无回显且coredump，重启BMC才能恢复，如何解决？ | zh | manual |
| q_011 | 带外执行chassis status命令时openUBMC低概率出现Close Session failed，原因是什么？ | zh | manual |
| q_012 | 如何通过ipmitool mc命令获取BIOS版本信息？openUBMC中不支持时如何解决？ | zh | manual |
| q_013 | openUBMC 25 LTS SP1构建失败，如何排查和解决？ | zh | manual |
| q_014 | openUBMC中使用Conan构建时有哪些常见问题？如何解决？ | zh | manual |
| q_015 | openUBMC bingo build时本地Conan仓有缓存，为什么还会触发源码构建？ | zh | manual |
| q_016 | openUBMC 25.12 LTS编译时常见问题有哪些？ | zh | manual |
| q_017 | openUBMC中I2C通道扫描不到设备，如何排查？ | zh | manual |
| q_023 | openUBMC中无法获取CPU温度、电压等健康信息，如何排查？ | zh | manual |
| q_024 | openUBMC传感器数值不更新，如何定位和修复？ | zh | manual |
| q_025 | openUBMC中脚本轮询sensor和fan信息导致NAND Flash写入过多告警，如何优化？ | zh | manual |
| q_026 | openUBMC同一传感器在门限传感器界面和温度海洋界面显示阈值不一致，原因是什么？ | zh | manual |
| q_027 | openUBMC中NVMe盘获取不到SMART信息，如何解决？ | zh | manual |
| q_028 | openUBMC中支持MCTP协议的直通NVMe获取不到SMART信息，如何处理？ | zh | manual |
| q_032 | openUBMC BMC NandFlash写入量过大问题的定位思路是什么？ | zh | manual |
| q_039b | openUBMC中属性无法自动更新，如何排查问题根因？ | zh | manual |
| q_040 | WSL环境下BMC Studio启动报错，如何解决？ | zh | manual |
| q_041 | openUBMC中PCIe卡无法正常加载，如何排查？ | zh | manual |
| q_043 | openUBMC固件升级后无法再次更新固件，如何排查和解决？ | zh | manual |
| q_052 | openUBMC中如何通过mdbctl setprop修改资源树属性信息？修改失败如何排查？ | zh | manual |

### 特性

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_003 | openUBMC社区如何生成Redfish接口说明文档？ | zh | manual |
| q_005 | openUBMC中Redfish TelemetryService接口是如何实现的？ | zh | manual |
| q_021 | openUBMC提供哪些I2C扫描和读写工具？ | zh | manual |
| q_030 | openUBMC是否支持对AI卡（如昇腾300I A2）进行带外固件升级？ | zh | manual |

### 迁移

| # | 问题 | 语言 | 来源 |
|---|------|------|------|
| q_029 | 如何从BMC 3.x版本升级到openUBMC？升级步骤是什么？ | zh | manual |
| q_031 | 从iBMC升级到openUBMC后，Web页面无法读取传感器、CPU、内存信息，如何解决？ | zh | manual |
