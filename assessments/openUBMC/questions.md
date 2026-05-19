# GEO 问题集

> 生成时间: 2026-05-17
> 社区: openUBMC
> 总数: 172

## 目录

- [认知](#认知)（11 条）
- [教程](#教程)（12 条）
- [场景](#场景)（19 条）
- [特性](#特性)（50 条）
- [故障](#故障)（80 条）


## 筛选标准

| 来源 | 占比 | 评分算法 | 筛选方式 | 获取时间 |
|------|------|----------|----------|----------|
| MongoDB | 85.0% | consult_count DESC | consult-filter（remaining_count>0 即保留） | 2026-05-17 |
| 论坛（Discourse） | 15.0% | views DESC | views>50，top 30 | 2026-05-17 |

## MongoDB 来源渠道

| 渠道 | 来源数量 | 状态 |
|------|----------|------|
| 论坛帖子 | 165 | ✅ 有数据 |
| 仓库 Issue | 1078 | ✅ 有数据 |
| 邮件列表 | 0 | ❌ 无数据 |

---

### 认知

| # | 问题 | 频率 |
|---|------|------|
| 20 | 如何向openUBMC社区提交接口评审议题？有哪些规范要求和操作流程？ | 1041views |
| 21 | 如何向openUBMC社区提交代码Pull Request？有哪些审核要求？ | 637views |
| 22 | openUBMC社区代码贡献流程有哪些自动化合规检查？如何确保合规性？ | 3次 |
| 23 | openUBMC社区每日工程答疑纪要在哪里可以查看？ | 1001views |
| 96 | openUBMC有哪些常见基础问题和解决方案？官方FAQ在哪里查看？ | 1170views |
| 97 | openUBMC的代码规范有哪些要求？如何进行cleancode检查？ | 9次 |
| 98 | openUBMC版本发布前的必测项有哪些？如何确定测试覆盖边界？ | 8次 |
| 99 | openUBMC各组件的开发文档和使用场景说明在哪里可以找到？ | 4次 |
| 100 | openUBMC代码库中iBMC与BMC命名如何规范统一？ | 3次 |
| 119 | openUBMC如何跟踪和管理开源组件漏洞？依赖库的安全修复周期是多久？ | 2次 |
| 122 | openUBMC社区如何贡献集成测试用例？有哪些自动化测试评审标准？ | 2次 |

### 教程

| # | 问题 | 频率 |
|---|------|------|
| 1 | 如何在openUBMC中使用QEMU进行BMC仿真调试？有哪些使用步骤和注意事项？ | 1456views |
| 2 | 如何快速搭建并启动openUBMC的QEMU仿真开发环境？ | 1279views |
| 3 | 有哪些openUBMC QEMU开发相关的官方文档和学习资料？ | 563views |
| 4 | openUBMC的hpm固件包格式是什么？如何对hpm包进行重新签名？ | 1317views |
| 5 | 如何创建自签名CA证书并为openUBMC的HPM固件包进行签名？ | 950views |
| 6 | openUBMC中如何对HPM包进行CMS外层重签名？如何兼容SignServer签名流程？ | 3次 |
| 12 | openUBMC中CPLD固件升级时如何将VME格式文件转换为SVF格式并打包为HPM升级包？ | 4次 |
| 14 | openUBMC社区镜像中如何一键部署QEMU和Bingo开发工具？ | 3次 |
| 16 | openUBMC有哪些官方调试工具？如何安装和使用这些调试工具？ | 883views |
| 17 | openUBMC开发中有哪些I2C调试工具？如何使用I2C扫描和读写工具？ | 722views |
| 18 | 如何在openUBMC中开发并新增一个功能组件？有哪些规范和步骤？ | 663views |
| 19 | openUBMC接口设计与开发的标准流程是什么？有哪些规范要求？ | 647views |

### 场景

| # | 问题 | 频率 |
|---|------|------|
| 7 | 如何将BMC固件从旧版本升级到openUBMC？有哪些升级步骤和注意事项？ | 1227views |
| 11 | openUBMC多模组固件升级时如何通过分阶段方式提高升级可靠性？ | 4次 |
| 15 | openUBMC的CI/CD流水线如何配置非root用户构建？接口文档如何自动生成？ | 10次 |
| 29 | openUBMC支持通过哪些接口（Redfish/Web/CLI）导入导出系统配置包？ | 5次 |
| 30 | openUBMC如何实现BMC客户化配置的完整导入和导出以支持运维批量管理？ | 3次 |
| 55 | openUBMC的一键日志收集功能支持收集哪些信息？如何使用？ | 4次 |
| 56 | openUBMC一键日志收集如何包含RAID卡固件日志和设备树信息？ | 4次 |
| 64 | openUBMC中如何为单个风扇单独配置调速策略而不影响其他风扇？ | 7次 |
| 65 | openUBMC中如何配置风扇调速策略？调速参数有哪些？ | 920次 |
| 66 | openUBMC如何配置多签名信任链以支持不同厂商固件包的兼容升级？ | 5次 |
| 67 | openUBMC品牌包如何定制？有哪些定制项和流程？ | 919views |
| 68 | 如何配置和使用openUBMC社区的Conan软件包仓库？ | 722views |
| 72 | openUBMC中如何通过定制配置统一管控BMC账户密码修改策略？ | 4次 |
| 74 | 如何通过配置导入导出实现openUBMC VNC最大会话数的定制化设置？ | 3次 |
| 101 | openUBMC中风扇工作模式如何切换？切换后配置如何持久保存？ | 3次 |
| 112 | openUBMC中如何在蓝区合入固件联盟认证测试用例并覆盖关键功能项？ | 3次 |
| 117 | openUBMC新增OCP网卡调速策略时如何确保CoolingPolicy ID的唯一性和正确关联？ | 2次 |
| 128 | openUBMC中CPLD自检异常可自动恢复，如何配置避免误触发告警？ | 2次 |
| 159 | 920s模组升级openUBMC后如何通过VPD配置获取CPU和内存信息并实现电源控制？ | 2次 |

### 特性

| # | 问题 | 频率 |
|---|------|------|
| 13 | openUBMC如何实现CPLD固件的无感升级？GPIO控制和寄存器状态如何保持一致？ | 10次 |
| 24 | openUBMC的Redfish接口规范是什么？有哪些核心规则和学习资料？ | 1401views |
| 25 | openUBMC的Redfish接口设计有哪些合规性必检项？ | 576views |
| 26 | openUBMC如何适配Redfish最新标准的Power资源模型？ | 40次 |
| 27 | openUBMC如何扩展Redfish资源属性以支持更多硬件设备类型？ | 14次 |
| 28 | openUBMC的Redfish接口中WriteableProperties属性是什么？如何确认哪些配置项可写？ | 5次 |
| 31 | openUBMC支持通过Redfish接口查询BIOS版本、CPU和内存信息吗？如何使用？ | 7次 |
| 32 | openUBMC Redfish接口如何查询NPU和HBM的硬件信息和功耗数据？ | 10次 |
| 33 | openUBMC的Redfish遥测服务如何配置？数据如何安全上报？ | 5次 |
| 34 | openUBMC支持通过Redfish接口查询内存故障预测规则并进行配置吗？ | 3次 |
| 35 | openUBMC的Redfish接口如何进行BMC和BIOS账户密码复杂度验证？ | 3次 |
| 36 | openUBMC中PCIe卡和OCP网卡在Redfish接口中如何保持对象配置一致性？ | 137次 |
| 37 | openUBMC如何实现对多型号网卡的CSR适配以及Redfish/SNMP接口的集成？ | 49次 |
| 38 | openUBMC CSR1.0架构下如何支持多类型总线和器件驱动？访问安全机制如何实现？ | 35次 |
| 39 | openUBMC中如何实现CSR1.0多路复用的拓扑管理与动态切换？ | 3次 |
| 40 | openUBMC的IPMI接口支持哪些标准命令？如何通过IPMI进行权限管理和配置查询？ | 15次 |
| 41 | openUBMC的IPMI接口支持哪些SDR（传感器数据记录）相关命令？如何查询传感器事件？ | 5次 |
| 42 | openUBMC如何通过IPMI接口读取PCIe网卡的VPD数据（序列号、PN等）？ | 3次 |
| 44 | openUBMC中VRD固件版本如何查询？如何安全地对VRD进行固件升级？ | 13次 |
| 45 | openUBMC是否支持MCTP over SMBus协议进行带外管理？ | 594views |
| 46 | openUBMC中SMC命令字的含义是什么？如何正确使用SMC命令？ | 583views |
| 47 | openUBMC如何实现对NVIDIA GPU的硬件信息采集和故障监控？ | 7次 |
| 48 | openUBMC如何通过带外I2C接口采集GPU温度、功耗等传感器数据？ | 6次 |
| 49 | openUBMC 25.06版本中QEMU仿真如何支持多路转换器和EEPROM的模拟读写？ | 5次 |
| 50 | openUBMC如何监控光模块的故障告警并采集光模块信息？ | 5次 |
| 51 | openUBMC如何实时获取和更新网卡光模块的在位状态？ | 4次 |
| 52 | openUBMC中安全协处理器心跳丢失时会触发什么级别的告警？如何恢复？ | 3次 |
| 54 | openUBMC上电超时或VRD故障时，如何自动触发日志收集？ | 7次 |
| 57 | openUBMC中如何导入导出PEF、SEL和Sensor相关的IPMI配置？ | 4次 |
| 58 | openUBMC支持通过Web界面或Redfish接口恢复出厂配置吗？如何操作？ | 3次 |
| 59 | openUBMC Web界面是否支持查看服务器入出风口的实时温度曲线？ | 4次 |
| 60 | openUBMC Web管理界面支持哪些主流浏览器？如何测试浏览器兼容性？ | 5次 |
| 62 | openUBMC在双路KP920处理器平台上是否能正确显示CPU、内存、PCIe和GPU信息？ | 3次 |
| 63 | openUBMC如何新增NVMe硬盘型号的支持？需要完善哪些驱动和配置？ | 3次 |
| 69 | openUBMC中如何配置和管理网卡？支持哪些网卡型号？ | 653views |
| 70 | openUBMC中如何修改FRU信息？修改时有哪些注意事项？ | 589views |
| 71 | openUBMC中FRU信息管理有哪些常见问题？如何进行FRU数据的读写和修改？ | 662views |
| 73 | openUBMC中新增RAID卡时如何配置PCIe属性和带外管理接口以确保正常识别？ | 3次 |
| 106 | openUBMC Redfish EventService中EventTypes和Context属性是否必填？如何配置为可选？ | 3次 |
| 113 | openUBMC Web界面如何查询UB接口卡和FC光模块的详细信息？ | 3次 |
| 116 | openUBMC中如何验证双CPLD硬盘背板的I2C配置，两个CPLD能否独立控制？ | 2次 |
| 120 | openUBMC中如何修改SMBIOS信息Type字段并自定义固件刷写路径？ | 2次 |
| 125 | openUBMC中CANBUS电源升级时如何保证级联顺序执行和固件版本自动更新？ | 2次 |
| 127 | openUBMC中如何通过硬件配置或EEPROM动态获取IPMB地址，而不依赖硬编码？ | 2次 |
| 135 | openUBMC中如何在Redfish接口的POST响应中添加自定义字段？ | 2次 |
| 139 | openUBMC中如何实现南向设备对象的自发现、动态加载和卸载？ | 2次 |
| 140 | openUBMC在电源故障时如何确保黑匣子日志被可靠保护不被覆盖？ | 2次 |
| 160 | openUBMC CPLD升级中断后如何通过备份固件自动恢复（自愈）？ | 2次 |
| 164 | openUBMC新机型内存适配时如何动态识别和配置不同规格的内存参数？ | 2次 |
| 172 | openUBMC Redfish固件升级时如何通过Targets参数精确指定升级目标部件（网卡、NPU等）？ | 3次 |

### 故障

| # | 问题 | 频率 |
|---|------|------|
| 8 | openUBMC 25.06版本BMC固件升级失败的原因是什么？如何解决？ | 632views |
| 9 | openUBMC固件升级失败后如何进行回滚恢复？升级机制和兼容性如何保障？ | 35次 |
| 10 | openUBMC固件升级前如何验证固件包与目标硬件的兼容性？ | 4次 |
| 43 | openUBMC中通过带内IPMI操作用户账户时channel getaccess返回unknown或error，如何解决？ | 3次 |
| 53 | openUBMC自定义事件配置完成后无法触发告警，如何排查事件定义和路由配置问题？ | 4次 |
| 61 | openUBMC高可用版本裁剪SNMP接口后出现MIB同步缺失和snmpwalk失败，如何解决？ | 6次 |
| 75 | 安装iBMA后openUBMC首页为什么不显示CPU和内存信息？如何解决？ | 899views |
| 76 | OS侧安装iBMA后为什么openUBMC界面不显示iBMA版本等信息？ | 634views |
| 77 | openUBMC Redfish接口中管理员和操作员账户获取的认证token为什么相同？ | 633views |
| 78 | openUBMC通过Redfish接口读取NPU卡温度传感器数据异常，如何排查和解决？ | 8次 |
| 79 | openUBMC中三星NVMe盘的厂商调速策略不生效，CSR加载逻辑错误如何排查？ | 7次 |
| 80 | 如何调试openUBMC中PCIe插卡的I2C读写功能？有哪些方法和工具？ | 618views |
| 81 | openUBMC Web界面axios组件存在原型污染漏洞，如何升级修复？ | 32次 |
| 82 | openUBMC Web界面中vue i18n组件的XSS漏洞如何修复？ | 6次 |
| 83 | openUBMC开发时Conan仓库配置异常或构建签名失败，如何排查和解决？ | 19次 |
| 84 | openUBMC Conan包迁移到自建Artifactory仓库时出现二进制缺失或检索异常，如何解决？ | 3次 |
| 85 | openUBMC构建高可用组件时出现依赖版本不兼容问题，如何解决？ | 17次 |
| 86 | 执行bingo build -sc qemu时提示qemu rootfs目录权限不足导致编译失败，如何解决？ | 12次 |
| 87 | openUBMC固件构建时提示环境配置错误或依赖缺失，如何排查和解决？ | 5次 |
| 88 | openUBMC组件适配gcc14.3编译器时出现编译错误，如何解决兼容性问题？ | 9次 |
| 89 | openUBMC运行时日志输出过多导致刷屏，如何定位源头并调整日志级别？ | 5次 |
| 90 | openUBMC中OS上电或下电时BMC日志大量刷屏，如何抑制冗余日志？ | 3次 |
| 91 | openUBMC中thermal.log日志转储不生效如何修复？ | 3次 |
| 92 | openUBMC中电源告警0x03000069在非电源接入时误报，如何调整误报逻辑？ | 3次 |
| 93 | openUBMC修改FRU Board Extra字段后显示乱码，如何排查编码格式问题？ | 3次 |
| 94 | openUBMC Web界面在更换NVMe为SATA SSD后不自动刷新硬盘信息，如何解决？ | 3次 |
| 95 | openUBMC启动时NVMe盘信息获取失败或显示异常，如何解决时序问题？ | 3次 |
| 102 | openUBMC非天池架构下通过EXU升级主板CPLD时，I2C拓扑配置和无SMC场景的访问路径如何适配？ | 3次 |
| 103 | openUBMC构建时出现libsoc adapter路径缺失错误，如何定位和修复？ | 3次 |
| 104 | openUBMC中电源按键测试时状态查询返回Unknown，如何排查？ | 3次 |
| 105 | openUBMC AC上电后BMC初始化延迟导致RAID卡信息获取失败，如何解决时序问题？ | 3次 |
| 107 | openUBMC中网卡SR配置错误导致初始化失败，如何修复并完善校验逻辑？ | 3次 |
| 108 | openUBMC中BCM网卡在IO2槽位因CSR类型误配为PCIe模式导致带外通信失败，如何排查？ | 3次 |
| 109 | openUBMC HBM动态巡检参数配置时提示接口缺失导致下发失败，如何解决？ | 3次 |
| 110 | openUBMC主备模式切换失效或电源额定功率读取异常，如何排查？ | 3次 |
| 111 | openUBMC线缆告警触发后普通告警消息缺失或日志大量刷屏，如何修复告警逻辑？ | 3次 |
| 114 | openUBMC告警码信息与官方文档不一致，如何确认正确的告警码定义？ | 3次 |
| 115 | openUBMC devmon组件加载新增芯片时因ID注册或兼容性问题失败，如何解决？ | 3次 |
| 118 | 在Ubuntu WSL2环境中构建openUBMC QEMU时权限不足，如何调整文件系统权限和shared目录配置？ | 2次 |
| 121 | openUBMC Web界面和Redfish接口显示的NVMe温度数据不一致，如何修复解析逻辑？ | 2次 |
| 123 | openUBMC中风扇在位状态判断错误导致系统功率异常，如何排查和修复？ | 3次 |
| 124 | openUBMC通过SMC forward进行级联CPLD升级时I2C传输长度超限，如何解决？ | 2次 |
| 126 | openUBMC通过Redfish接口无法获取电源状态信息，如何排查？ | 2次 |
| 129 | openUBMC中Atlas 300I A2卡在多卡或高温场景下调速策略失效，如何修复？ | 2次 |
| 130 | openUBMC中RAID卷因跨controller关联导致Web界面硬盘重复显示，如何解决？ | 2次 |
| 131 | openUBMC中NC-SI over MCTP over SMBus通信切换时出现超时，如何排查？ | 2次 |
| 132 | openUBMC固件SATA子系统配置错误导致带内管理无法识别SATA硬盘，如何修复？ | 2次 |
| 133 | openUBMC中OCP网卡多端口切换后Port2无法识别导致网络中断，如何解决？ | 2次 |
| 134 | openUBMC在M2平台适配时出现硬件识别异常，驱动兼容性和device tree如何配置？ | 2次 |
| 136 | openUBMC Web界面中DDR5内存信息显示不正确或被脱敏处理，如何修复？ | 2次 |
| 137 | openUBMC中ThresholdSensor传感器值停止更新，如何排查事件上报和驱动同步问题？ | 2次 |
| 138 | openUBMC网络压力测试后BMC失联或网口环回测试失败，如何排查？ | 2次 |
| 141 | openUBMC资源全检时包含未配置组件导致升级因CSR缺失直接报错，如何配置跳过未配置组件？ | 2次 |
| 142 | openUBMC VRD固件升级失败后重试时出现通信中断或校验异常，如何解决？ | 2次 |
| 143 | openUBMC使用的Protobuf组件存在解析嵌套消息导致DoS的漏洞，如何升级修复？ | 2次 |
| 144 | openUBMC中长按面板按钮时操作日志概率性不记录，如何解决？ | 2次 |
| 145 | openUBMC重启后风扇转速传感器显示NA，如何修正PowerState配置？ | 2次 |
| 146 | openUBMC执行SNMP Walk时Export CSR失败，Lua脚本userdata处理异常如何排查？ | 2次 |
| 147 | openUBMC重启后看门狗（watchdog）配置被清除且无法关闭，如何解决？ | 2次 |
| 148 | openUBMC开启SSL加密后VNC无法连接，如何排查SSL配置问题？ | 2次 |
| 149 | openUBMC在双路鲲鹏920主板上无法开机，如何排查兼容性和初始化问题？ | 2次 |
| 150 | openUBMC LDAP认证失败时如何区分是BMC配置问题、LDAP服务问题还是网络问题？ | 2次 |
| 151 | openUBMC通过Redfish查询支持MCTP的网卡时出现SupportMctp属性缺失导致KeyError，如何解决？ | 2次 |
| 152 | openUBMC Web界面lodash组件旧版本原型污染漏洞未彻底修复，如何解决？ | 2次 |
| 153 | 初始化openUBMC开发环境时因超时限制导致依赖安装失败，如何解决？ | 2次 |
| 154 | openUBMC中风扇转速持续满转或频繁波动，如何排查调速异常根因？ | 2次 |
| 155 | openUBMC长时间带内重启压力测试后出现内存和网卡识别异常及温度告警，如何定位稳定性问题？ | 2次 |
| 156 | openUBMC BMC启动失败提示配置错误或镜像损坏，如何排查固件完整性和依赖问题？ | 2次 |
| 157 | openUBMC Redfish Reset操作未校验AC供电状态就返回200成功，如何修复？ | 2次 |
| 158 | openUBMC下电后网卡仍在上报温度数据，如何同步传感器读取和电源状态？ | 2次 |
| 161 | openUBMC Redfish电源固件查询结果中备用电源信息重复且部分电源数据缺失，如何修复？ | 2次 |
| 162 | openUBMC AC上电后概率性无法获取网卡资产信息，如何优化监听时序？ | 2次 |
| 163 | openUBMC中硬盘定位指示灯状态修改后Web界面不实时刷新，如何解决？ | 2次 |
| 165 | 鲲鹏920模组上的VRD温度传感器在openUBMC中数据采集异常，如何排查？ | 2次 |
| 166 | openUBMC的OpenTelemetry组件HTTP标签未限制导致内存耗尽风险，如何修复？ | 2次 |
| 167 | openUBMC多用户并发执行SNMP Walk时触发安全日志库错误，如何解决？ | 2次 |
| 168 | openUBMC中IPMI强制开启密码复杂度策略后Web界面仍可关闭导致策略失效，如何同步策略？ | 2次 |
| 169 | openUBMC中紫光CPLD升级后版本号未更新且级联场景升级失败，如何解决？ | 2次 |
| 170 | openUBMC中风扇板热插拔后引发全组风扇转速误告警，如何解决？ | 2次 |
| 171 | openUBMC中BMC固件与特定NVMe盘交互时偶发丢失累计通电时间和协商速率信息，如何解决？ | 2次 |
