# GEO Search Assessment

GEO（Generative Engine Optimization）搜索能力诊断系统 —— 自动评估开源社区在主流 AI 搜索平台中的表现，并生成可执行的改进建议。

初始目标社区：**MindSpore**（AI 计算框架，竞品：TensorFlow / PyTorch / PaddlePaddle）。

## 系统架构

本系统是一个由 Claude Code 驱动的 **Skill 链式流水线**，纯 CLI 运行，无 Web 界面。

3 步流水线 + Issue 创建，每步对应一个独立 Skill：

```
questions.json        responses.json     scoring-results.json + suggestions.md
     │                     │                     │
     ▼                     ▼                     ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────────────────┐
│ get-question │─▶│ platform-sampler │─▶│            scoring-engine            │
└──────────────┘  └──────────────────┘  │  评分诊断 + 事实覆盖 + 模式分析     │
                                        │  + 目录匹配建议（72 条 GEO 建议库） │
                                        └──────────────────────────────────────┘
   生成问题集          采样 AI 平台         评分 → 诊断 → 建议 → 路线图
```

**数据流**：Skill 之间通过 JSON 文件传递数据，同时输出 Markdown 供人工审阅。

**评估平台（MVP）**：ChatGPT · 豆包（火山引擎）· 千问（阿里云百炼）· DeepSeek


## 使用 Claude Code 开发

本仓库使用 [Claude Code](https://claude.ai/code) 作为主要开发工具，配置了自动化工作流和会话恢复机制。

### CLAUDE-RESUME.md —— 会话恢复

每次开启新的 Claude Code 会话时，Claude 会自动读取 `CLAUDE-RESUME.md` 来恢复项目上下文，无需重复说明背景。

该文件包含以下段落，**每次任务完成后自动更新**：

- **Project Overview** — 项目概述和架构
- **Current Status** — 当前开发阶段
- **TODO** — 待办事项清单
- **Recent Changes** — 近期变更记录
- **Key Decisions** — 已确定的关键决策

**约束**：
- 不要手动编辑此文件，由 Claude Code 自动维护
- 如需修正内容，在会话中告知 Claude 更新即可

### /release-skills —— 发布与变更日志

在 Claude Code 中执行 `/release-skills`，自动完成版本管理和 CHANGELOG.md 更新。

```
/release-skills              # 自动检测版本变更
/release-skills --dry-run    # 仅预览，不执行
/release-skills --major      # 强制主版本号升级
/release-skills --minor      # 强制次版本号升级
/release-skills --patch      # 强制补丁版本号升级
```

**约束**：
- 每次 git commit 前**必须**先执行 `/release-skills` 更新 CHANGELOG.md

### /skill-creator —— 创建新 Skill

在 Claude Code 中执行 `/skill-creator`，按照规范模版创建新的 skill。

**约束**：
- 创建新 skill 时**必须**使用 `/skill-creator`，不允许手动创建
- `SKILL.md` 主体逻辑不超过 500 行，超出部分拆分到 `references/`
- `name` 仅允许小写字母、数字和单连字符，1-64 字符
- `description` 不超过 1024 字符，使用第三人称，包含反向触发条件

## License

MIT
